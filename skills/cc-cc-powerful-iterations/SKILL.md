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
version: 1.0.0
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

Save the refined prompt — you will use the exact same version for both engines.

### Step 2: Parallel Execution

Launch both engines with the same refined prompt. Run them in parallel to save time.

**Claude Subagent:**
Use the Agent tool (general-purpose subagent) with the refined prompt. Tell it to produce
a complete, actionable result.

**Codex CLI (auto-detected):**

First, check if Codex CLI is available:
```bash
command -v codex >/dev/null 2>&1
```

**If Codex is available**, use Bash to run:
```bash
codex -a never exec "<refined-prompt>"
```

The `-a never` flag ensures Codex runs fully autonomously without approval prompts.
**Important:** `-a` is a global flag — it must come before the `exec` subcommand, not after.
If the prompt is long, write it to a temp file and pipe it:
```bash
echo '<refined-prompt>' | codex -a never exec -
```

For prompts that need file context, you can also use:
```bash
codex -a never exec -m o4-mini "<refined-prompt>"
```

**If Codex is NOT available**, launch a second Claude subagent (Agent tool, general-purpose) with the same refined prompt. Label outputs as "Claude-A" and "Claude-B" instead of "Claude" and "Codex".

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

Send the synthesized result back to Codex for validation:

```bash
codex -a never exec "Review the following output for correctness, completeness, and potential issues. Flag anything that looks wrong or could be improved. Be critical.\n\n<synthesized-result>"
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

## Configuration

The default model for Codex is whatever is configured in the user's Codex CLI.
To override, use `-m <model>` flag (e.g., `-m o4-mini`, `-m o3`).

## When to Skip Steps

- If the task is trivial, you can skip the Codex review (Step 4) and go straight to presentation
- If Codex CLI is unavailable (detected via `command -v codex`), use two Claude subagents instead
- If the user says "quick iteration", do Steps 1-3 only

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/cc-cc/`
- **Checkpoint frequency:** After Steps 1, 2, 3, 4 (before each major transition)
- **Subagent delegation:** Codex execution (Step 2), Claude validation (Step 3), Codex review (Step 4)

## Error Handling

- If `codex exec` times out, retry once with a simpler prompt or shorter context
- If Codex returns an error, inform the user and offer to proceed with Claude-only dual-subagent mode
- Always have a fallback — the workflow should never block completely on one engine
