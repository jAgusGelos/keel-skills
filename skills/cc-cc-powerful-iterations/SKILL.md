---
name: cc-cc-powerful-iterations
description: |
  Dual-engine iteration workflow that combines Claude Code subagents with OpenAI Codex CLI
  to produce high-quality, cross-validated outputs. Use this skill whenever the user wants
  to leverage both Claude and Codex together, when they mention "dual iteration", "cc-cc",
  "codex collaboration", "iterate with codex", or when they want a prompt refined and
  cross-checked by multiple AI engines before delivering a final result. Also trigger when
  the user says "powerful iterations", "double-check with codex", or asks for a workflow
  that combines both tools.
version: 1.1.0
category: development
depends: [prompt-refinement]
---

# CC-CC Powerful Iterations

A dual-engine iteration workflow that orchestrates Claude Code and OpenAI Codex CLI to produce
cross-validated, high-quality results through structured collaboration.

## Why This Exists

Single-model outputs have blind spots. By running the same refined prompt through two independent
engines (Claude subagent + Codex CLI), comparing their results, synthesizing the best of both,
and then having Codex review the synthesis, we get outputs that are more robust, creative, and
thoroughly validated than either engine alone.

## The Cycle

```
User Prompt
     |
     v
[1] Prompt Refinement (Claude main agent)
     |
     v
[2] Parallel Execution ----+---- Claude Subagent
     |                      |
     |                      +---- Codex CLI (exec mode)
     v
[3] Analysis & Synthesis (Claude main agent)
     |
     v
[4] Codex Review (Codex validates the synthesis)
     |
     v
[5] Final Presentation to User
```

## Codex Invocation Contract (applies to Steps 2 and 4)

Every Codex call in this skill uses the hardened `codex exec` pattern — sandbox bypass,
stdin redirect, timeout, file-based prompt and output. A bare `codex exec "..."` (or the
old `codex -a never exec` form) can hang: Codex's bubblewrap sandbox fails on some
kernels, and an open stdin makes Codex wait for EOF forever. NEVER interpolate generated content directly into the shell
command string — write it to a temp file and have Codex read it from disk.

Template:

```bash
PROMPT_FILE=$(mktemp /tmp/cc-cc-XXXXXX.txt)
CODEX_OUT=$(mktemp /tmp/cc-cc-XXXXXX.jsonl)
CODEX_ERR=$(mktemp /tmp/cc-cc-XXXXXX.err)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

# CONTENT_FILE = the input written with the Write tool beforehand (refined prompt in
# Step 2, synthesized result in Step 4). Its path expands OUTSIDE the quoted heredoc.
printf 'Read this file in full FIRST: %s\n\n' "$CONTENT_FILE" > "$PROMPT_FILE"

cat >> "$PROMPT_FILE" <<'PROMPT_EOF'
<static instructions for this step — see Steps 2 and 4>
PROMPT_EOF

timeout 600 codex exec --json -C "$REPO_ROOT" --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox "$(cat "$PROMPT_FILE")" \
  < /dev/null > "$CODEX_OUT" 2> "$CODEX_ERR"
echo "codex exit=$? out=$CODEX_OUT err=$CODEX_ERR"
```

- The final `agent_message` item in `$CODEX_OUT` holds Codex's answer.
- `--json` lets you `tail` the output file mid-run to watch progress.
- Run the Bash call with `run_in_background: true` so it owns its own lifecycle
  while Claude-side work proceeds in parallel.
- On non-zero exit or an empty output file, apply Error Handling below — do NOT
  retry a bare/unhardened invocation.
- Clean up `/tmp/cc-cc-*` temp files in Step 5.

## Step-by-Step Instructions

### Step 1: Prompt Refinement (via `prompt-refinement` skill)

When the user provides a prompt:

1. **Invoke the `prompt-refinement` skill** with the user's raw prompt. This skill will:
   - Explore the repository for real context (tech stack, file paths, patterns, conventions)
   - Analyze the prompt across 5 dimensions (Clarity, Specificity, Context Completeness, Actionability, Scope Control)
   - Score confidence and identify blockers
   - Rewrite the prompt into a structured, execution-ready version with verified context
2. Take the **Refined Prompt** from the skill's output — this is what both engines will receive
3. If the skill enters **Mode A** (critical questions remain), resolve those before proceeding to Step 2
4. Ensure the refined prompt is engine-agnostic — it should work well for both Claude and Codex

Save the refined prompt to a temp file (Write tool) — you will use the exact same version
for both engines, and the file doubles as Codex's `CONTENT_FILE`.

### Step 2: Parallel Execution

Launch both engines with the same refined prompt. **Launch Codex FIRST, in the
background** (it is the slower engine), then the Claude subagent — their runtimes overlap
instead of adding up.

**Codex CLI (auto-detected):**
First, check that Codex CLI is installed: `command -v codex >/dev/null 2>&1`. If it is not,
skip Codex and launch a second Claude subagent (Agent tool, general-purpose) with the same
refined prompt instead. Label the outputs "Claude-A" and "Claude-B" instead of "Claude" and
"Codex" in Steps 3 and 5.

If Codex is installed, use the hardened template above with `run_in_background: true`. `CONTENT_FILE` is the
refined-prompt file from Step 1; the static heredoc instructions are:

```
The file above contains your task prompt. Execute it completely and produce a full,
actionable result. Do not ask questions — make reasonable assumptions and state them.
```

**Claude Subagent:**
Use the Agent tool (general-purpose subagent) with the refined prompt. Tell it to produce
a complete, actionable result.

When the Claude subagent returns, read `$CODEX_OUT` (await the background task if it is
still running).

### Step 3: Analysis & Synthesis

Once both results are back:

1. **Analyze the Claude result** — identify strengths, gaps, and unique insights
2. **Analyze the Codex result** — identify strengths, gaps, and unique insights
3. **Compare** — note where they agree (high confidence), where they diverge (needs resolution),
   and where one clearly outperforms the other
4. **Synthesize** — produce a merged result that:
   - Takes the best elements from each
   - Resolves conflicts by reasoning about correctness
   - Fills gaps that one engine missed but the other caught
   - Maintains consistency and coherence in the final output

### Step 4: Codex Review

Write the synthesized result to a temp file (Write tool), then run the hardened template
with that file as `CONTENT_FILE` and these static heredoc instructions:

```
The file above contains a synthesized output produced from two independent AI engines.
Review it for correctness, completeness, and potential issues. Flag anything that looks
wrong or could be improved. Be critical and specific. For each issue: what is wrong,
why, and the concrete fix.
```

Analyze Codex's review:
- If it flags real issues, fix them
- If it suggests improvements that make sense, incorporate them
- If it has no significant objections, the result is ready

### Step 5: Final Presentation

Present to the user:

1. **Final Result** — the polished, cross-validated output
2. **Confidence Notes** — briefly mention where both engines agreed (high confidence)
   and any areas where you had to make judgment calls
3. **Iteration Offer** — ask if they want to refine further or if it meets their needs

Then clean up: `rm -f /tmp/cc-cc-*.txt /tmp/cc-cc-*.jsonl /tmp/cc-cc-*.err`

## Configuration

Codex runs with whatever default model is configured in the user's Codex CLI. Only pass
`-m <model>` if the user explicitly asks for a specific Codex model — never hardcode one
in this skill.

## When to Skip Steps

- If the task is trivial, you can skip the Codex review (Step 4) and go straight to presentation
- If Codex CLI is not installed (`command -v codex` fails), fall back to using two Claude
  subagents instead
- If the user says "quick iteration", do Steps 1-3 only

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/cc-cc/`
- **Checkpoint frequency:** After Steps 1, 2, 3, 4 (before each major transition)
- **Subagent delegation:** Codex execution (Step 2), Claude validation (Step 3), Codex review (Step 4)

## Error Handling

- If `codex exec` exits non-zero or its output file is empty while the process already
  finished, check `$CODEX_ERR` first. If the process is alive but the output stays at
  0 bytes, the almost-certain cause is a missing `< /dev/null` — kill it and re-run the
  hardened template, do not debug the prompt or the network.
- If Codex times out, retry once with a shorter prompt or a longer `timeout`
- If Codex keeps failing, inform the user and proceed with Claude-only dual-subagent mode
- Always have a fallback — the workflow should never block completely on one engine
