# Codex Plan Audit: hardened invocation (spec-first-cc-cc Step 7, Phase B)

One audit per feature, run after BOTH plan.md and todo.md are drafted and `scripts/lint-plan.py` is clean.
Codex answers the 18-item checklist in `references/codex-checklist-plan.md`, one line per ID. The shared
helpers and the unavailable-Codex policy are in `${CLAUDE_PLUGIN_ROOT}/scripts/codex/README.md`.

Shared rules:

- Codex reads every artifact from disk (`-C` gives it repo access). Do NOT inline plan/todo content into the
  prompt: long inline args break `codex exec`.
- One hardened attempt. Never re-invoke Codex for this audit, whatever the status. Never wait for a quota
  reset.
- Clean up `/tmp/spec-audit-*` after Phase C.

```bash
CODEX_HELPERS="${CLAUDE_PLUGIN_ROOT}/scripts/codex"
SKILL_DIR="${CLAUDE_PLUGIN_ROOT}/skills/spec-first-cc-cc"
CHECKLIST=$SKILL_DIR/references/codex-checklist-plan.md
REPO_ROOT=$(git rev-parse --show-toplevel)
FEATURE_DIR="$REPO_ROOT/.workspace/features/<feature-name>"
GOAL_FILE="<abs path of the goal/issue text: the orchestrator prompt, the issue body saved to a file, or the Step 1 capture>"
CONTRACT_DOCS="<abs paths of ARCHITECTURE.md or other contract docs the plan depends on, or 'none'>"
PROMPT_FILE=$(mktemp /tmp/spec-audit-XXXXXX.txt)
AUDIT_OUT=$(mktemp /tmp/spec-audit-XXXXXX.jsonl)
AUDIT_ERR=$(mktemp /tmp/spec-audit-XXXXXX.err)
AUDIT_ANSWER=$(mktemp /tmp/spec-audit-XXXXXX.answer.md)
AUDIT_STATUS=$(mktemp /tmp/spec-audit-XXXXXX.status)
AUDIT_MISSING=$(mktemp /tmp/spec-audit-XXXXXX.missing)

python3 "$SKILL_DIR/scripts/lint-plan.py" "$FEATURE_DIR"   # must be clean before the audit

{
  printf 'Read these files in full FIRST:\n'
  printf '1. The checklist you must answer: %s\n' "$CHECKLIST"
  printf '2. plan.md: %s\n' "$FEATURE_DIR/plan.md"
  printf '3. todo.md: %s\n' "$FEATURE_DIR/todo.md"
  printf '4. The goal / issue the plan must satisfy: %s\n' "$GOAL_FILE"
  printf '5. Contract docs: %s\n\n' "$CONTRACT_DOCS"
} > "$PROMPT_FILE"

cat >> "$PROMPT_FILE" <<'PROMPT_EOF'
You are auditing a feature plan (plan.md + todo.md) against the goal it must satisfy. Answer EVERY item of
the checklist in file 1, Tier 1 first, using its exact answer format: one line per ID,
`ID | PASS|FAIL|N-A|NOT-CHECKED | severity | location | issue | fix`. N-A needs a concrete reason. Do not
skip IDs; use NOT-CHECKED if you run out of time. Verify claims against the repository. Then the optional
`OTHER (max 5)` section. Do not modify any file.
PROMPT_EOF

if python3 "$CODEX_HELPERS/codex-status.py" preflight > "$AUDIT_STATUS"; then
  timeout 360 codex exec --json -C "$REPO_ROOT" --skip-git-repo-check \
    --dangerously-bypass-approvals-and-sandbox "$(cat "$PROMPT_FILE")" \
    < /dev/null > "$AUDIT_OUT" 2> "$AUDIT_ERR"
  python3 "$CODEX_HELPERS/codex-status.py" classify --exit $? --out "$AUDIT_OUT" \
    --answer-file "$AUDIT_ANSWER" > "$AUDIT_STATUS" \
  && python3 "$CODEX_HELPERS/checklist.py" parse --checklist "$CHECKLIST" \
    --answer "$AUDIT_ANSWER" --missing-out "$AUDIT_MISSING" >> "$AUDIT_STATUS"
fi
echo "status_file=$AUDIT_STATUS answer=$AUDIT_ANSWER missing=$AUDIT_MISSING"; cat "$AUDIT_STATUS"
```

## Routing on the status file

| Status file says | Next | Label in findings.md and the output header |
|---|---|---|
| `status=ok` + `result=complete` | Phase C | `Codex` |
| `status=ok` + `result=partial` | `codex-fallback-auditor` answers only the IDs in `$AUDIT_MISSING` | `Claude-led; Codex partial: <n> items` |
| `status=ok` + `result=invalid-output` | fallback answers the full checklist | `Claude-only; Codex unavailable: invalid-output` |
| any other `status=` | fallback answers the full checklist | `Claude-only; Codex unavailable: <status>[ until <until>]` |

The fallback is the `codex-fallback-auditor` subagent given the same prompt file plus the list of IDs to
answer; it writes its lines to `/tmp/spec-audit-<id>.fallback.md` (the main session saves its reply there).
Then build the final table:

```bash
python3 "$CODEX_HELPERS/checklist.py" merge --checklist "$CHECKLIST" \
  --primary "$AUDIT_ANSWER" --primary-label "<Codex | Codex (partial)>" \
  --secondary /tmp/spec-audit-<id>.fallback.md --secondary-label "Claude-Auditor"
```

Codex being unavailable never blocks the plan: Phase C proceeds on the merged table, and the label says
honestly who audited.
