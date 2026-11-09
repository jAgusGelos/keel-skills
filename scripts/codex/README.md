# Codex helpers (shared by review-changes, spec-first-cc-cc, three-experts, own-pr-reviews)

Three scripts, Python 3 stdlib only. Tests: `python3 -m unittest discover -s ${CLAUDE_PLUGIN_ROOT}/scripts/codex/tests`.

| Script | Purpose |
|---|---|
| `codex-status.py preflight` | May Codex run now? `status=ready` (exit 0), or `not-installed` / `quota` from a cached usage limit (exit 3). |
| `codex-status.py classify --exit N --out F.jsonl [--answer-file F]` | Status of a finished `codex exec --json` run: `ok` (exit 0, answer written) or `quota` / `capacity` / `auth` / `timeout` / `failed` (exit 3). |
| `checklist.py parse --checklist C --answer A [--missing-out M]` | Did the answer cover every checklist ID? `complete` (0) / `partial` (4) / `invalid-output` (5). |
| `checklist.py merge --checklist C --primary A --primary-label L --secondary B --secondary-label L2` | One line per ID, tagged with the engine that answered it. |
| `evidence.py fingerprint` / `evidence.py check E` | HEAD + working-tree hash; `check` exits 6 when the evidence file is stale. |

## The unavailable-Codex policy (one place, every consumer follows it)

1. **Preflight.** Run `codex-status.py preflight`. Exit 3 means skip the call and go to step 4 with that status.
   Never ping Codex to "test" quota.
2. **One hardened attempt.** `codex exec --json ... < /dev/null > OUT 2> ERR` with the caller's timeout, then
   `codex-status.py classify --exit $? --out OUT --answer-file ANSWER`. Never re-invoke Codex for the same gate,
   whatever the status. Never wait for a quota reset.
3. **Checklist coverage** (checklist audits only). `checklist.py parse --checklist C --answer ANSWER
   --missing-out MISSING`. `complete` = done. `partial` keeps Codex's valid lines and sends only the IDs in
   MISSING to the fallback. `invalid-output` is treated like an unavailable run (full list to the fallback).
4. **Claude fallback, once, same checklist.** The fallback answers the full checklist (unavailable /
   invalid-output) or only the missing IDs (partial), in the same per-item line format. Then
   `checklist.py merge` produces the final table.
5. **Verdict.** Computed with the caller's normal rules from what the engines found. Codex being unavailable
   never adds a WARN or BLOCK, never prompts the user, never schedules a later re-check.
6. **Label it honestly.**
   - Codex answered fully: no label.
   - Codex partial: `Claude-led; Codex partial: <reason>` and its lines tagged `[Codex (partial)]`.
   - No usable Codex output: `Claude-only; Codex unavailable: <status>[ until <time>]`.
   Never write "Codex-approved" or "cross-validated by Codex" without a valid `ok` answer.

Classification reads only terminal protocol events (`error`, `turn.failed`, `turn.completed`) and the exit code,
never agent prose, command output or stderr (stderr carries MCP OAuth noise on healthy runs). A non-fatal
`"type":"error"` warning ("Skill descriptions were shortened...") on a completed run is still `ok`.

The quota memo (`~/.cache/codex-status.json`, override with `CODEX_STATUS_CACHE`) is written only when the message
carries an absolute reset time ("try again at Sep 29th, 2026 9:40 PM", read as local time). "resets 8pm" has no
date, so nothing is cached and the next distinct gate makes its one attempt.

## Snippet for a caller

```bash
CODEX=${CLAUDE_PLUGIN_ROOT}/scripts/codex
if python3 "$CODEX/codex-status.py" preflight > "$WORK/codex-status.txt"; then
  timeout 600 codex exec --json -C "$REPO_ROOT" --skip-git-repo-check \
    --dangerously-bypass-approvals-and-sandbox "$(cat "$PROMPT_FILE")" \
    < /dev/null > "$WORK/codex.jsonl" 2> "$WORK/codex.err"
  python3 "$CODEX/codex-status.py" classify --exit $? --out "$WORK/codex.jsonl" \
    --answer-file "$WORK/codex-answer.md" > "$WORK/codex-status.txt"
fi
cat "$WORK/codex-status.txt"   # status=ok, or quota | capacity | auth | timeout | failed | not-installed
```

Run it with `run_in_background: true` when other reviewers work in parallel; read `codex-status.txt` when it
finishes.
