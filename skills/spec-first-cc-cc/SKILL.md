---
name: spec-first-cc-cc
description: |
  Dual-engine specification workflow that extends spec-first with cc-cc cross-validation.
  Runs the full spec-first pipeline (brainstorm, capture, research, three-experts, design
  gate, plan, todo, findings, checkpoint, next-session prompt) and adds an adversarial
  Codex audit once both plan.md and todo.md are drafted: Claude DRAFTS them, a deterministic
  lint checks the template, Codex AUDITS both against an 18-item checklist of what really
  escaped in past runs, Claude REVISES. The second engine audits; it does not co-generate. Produces a cross-validated plan.md and todo.md
  plus the standard spec-first artifacts (findings.md with a Codex Audit Summary, and
  NEXT_SESSION_PROMPT.md so the user can start a fresh implementation session by
  copy-pasting one path). For UI-touching features, runs the design-alternatives skill as
  a mandatory design gate (Step 5b) before plan.md — the user picks a visual direction
  from an HTML mockup of 2-4 alternatives, recorded as DESIGN.md, so implementation never
  starts with an undecided or generic UI. Supports optional worktree mode (trigger words:
  "worktree", "--worktree", "in a worktree", "separate worktree") that bakes worktree
  setup, dependency install, and env copy instructions into NEXT_SESSION_PROMPT.md so the
  implementation runs in isolation. Use this skill when the user says "spec first cc-cc",
  "dual engine planning", "plan with codex", "cross-validated spec", "cc-cc planning",
  "dual spec", or when `/simple-feature-workflow` Phase 2 selects the dual-engine option.
version: 1.1.0
category: development
depends: [spec-first, three-experts, design-alternatives, review-changes]
---

# Spec First CC-CC — Dual-Engine Planning with Adversarial Review

This skill is a **delta over `spec-first`**: the entire pipeline, templates, output
format, implementation-phase rules, anti-patterns, and quality checklist come from the
`spec-first` skill. This file defines ONLY what changes. Do not restate or re-derive the
base pipeline from memory — load it.

**How to run:**

1. **Invoke the `spec-first` skill** (Skill tool) to load the base pipeline.
2. Follow it step by step, applying the **Deltas** below at the steps they name.
3. Everything not mentioned in the Deltas section is identical to `spec-first`.

## Why This Exists

`spec-first` produces excellent plans through a disciplined uncertainty-reduction
pipeline. The dual-engine addition targets the specific steps where a second perspective
adds value: **auditing generated artifacts against checklists, anti-patterns, and
templates**. It does NOT replace structured reasoning (three-experts) with generic
parallel generation, because role-differentiated adversarial deliberation is
categorically better than two generic engines producing monologues.

**Core principle:** Draft/Audit, not Co-Author. Merging two independently generated
plans destroys the internal coherence (assumption chains, AD-ID traceability, task
dependency ordering) that makes a plan useful.

## The Cycle (deltas marked with ★)

```
[0]  Brainstorm (skippable)          — as spec-first
[1]  Capture and Confirm (+1b worktree) — as spec-first
[2]  Parallel Research               — as spec-first
[3]  Synthesize and Classify Gaps    — as spec-first
[4]  Clarify Critical Unknowns       — as spec-first
[5]  Three Experts Reasoning         — as spec-first (NEVER replaced by dual-engine)
[5b] Design Alternatives Gate        — as spec-first (★ explicitly NO Codex audit here)
[6]  plan.md   ★ Claude DRAFTS (no audit yet)
[7]  todo.md   ★ Claude DRAFTS → lint-plan.py → ONE Codex audit of plan+todo → Claude REVISES both
[8]  findings.md ★ + Codex Audit Summary section (draft-only, no audit)
[9]  Plan Checkpoint ★ + audit summary in the checkpoint
[10] NEXT_SESSION_PROMPT.md ★ + audit results, cc-cc labels
[IMPLEMENTATION] per-milestone /review-changes --light --fix gate and final FULL
                 review — exactly as spec-first defines them
```

## Deltas

### Step 5b — Design gate: no Codex audit

The gate runs exactly as in `spec-first`. **Do not add a Codex audit phase to it** — the
gate's reviewer is the USER looking at rendered alternatives in a browser; Codex cannot
see the rendered output, and the decision is a taste/product call, not an
artifact-consistency check. Codex will still audit the plan.md that encodes the chosen
direction (Step 7 Phase B).

### Step 6 — plan.md is drafted, not audited yet

Use spec-first's Step 6 template and overwrite rules unchanged, with the header line
reading `> Generated via spec-first-cc-cc workflow on [date]`. Write plan.md exactly as
spec-first specifies. The audit waits for todo.md (Step 7): one audit of both files
checks traceability and costs one Codex call instead of two. (The old separate todo.md
audit was about 45% rejected noise, mostly "split this task".)

### Step 7 — todo.md drafted, then one Draft/Audit/Revise over both

**Phase A — Claude Drafts:** write todo.md exactly as spec-first specifies. Then run
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/spec-first-cc-cc/scripts/lint-plan.py" .workspace/features/<feature-name>`
and fix every problem it lists (missing sections, AD fields, AD-ID sequence, milestones
without Verify, todo/AD traceability). Template completeness is checked here,
deterministically, never by an LLM.

**Phase B — Codex Audits:** read `references/codex-audit.md` and run its invocation. Codex
answers the 18 items of `references/codex-checklist-plan.md` (core scenarios traced
through frozen contracts, AC-to-Verify mapping, acceptance step on the real stack, repo
validators, owners for known gaps, integration path, launch dependencies, guards on
destructive or paid operations, ...) one line per ID. Route on the status file exactly
as that reference says: a partial or unavailable Codex run goes to the
`codex-fallback-auditor` for the missing IDs or the full list. One attempt; never
retry, never wait, never block.

**Phase C — Claude Revises:** for every `FAIL` line (and every `OTHER` item), fix plan.md
and/or todo.md with targeted `Edit` calls, one per finding (or one per section when a
finding adds a section). NEVER regenerate either file in full after the audit: a full
rewrite re-emits 20-35 KB through the orchestrator's context for a handful of changed
lines (measured: one run re-emitted a 35 KB plan.md and a 22 KB todo.md this way) and risks
silently dropping AD-IDs or reordering the assumption chain. For each FAIL:
- If it identifies a real gap: fix it
- If it is a false positive: note why and skip it
Re-run `lint-plan.py` after the edits; it must stay clean.

Show the user the audit summary and the revised artifacts.

### Step 8 — findings.md gains a Codex Audit Summary

findings.md stays **draft-only — no Codex audit phase** (it records research, not a
generated spec; the draft/audit loop adds no value there). Use spec-first's template
plus this extra section, placed after "Design Gate (Step 5b)":

```markdown
## Codex Audit Summary
- **Auditor:** Codex | Claude-led; Codex partial: <n> items | Claude-only; Codex unavailable: <status>
- **Checklist:** 18/18 answered: [P] PASS, [F] FAIL, [N] N-A
- **FAIL items:** [X] fixed, [Z] rejected (ID + one-line reason each)
- **lint-plan.py:** clean
```

Extra rule for good findings: the Codex Audit Summary must reflect the real audit
outcome from Step 7, including why rejected findings were rejected, and must never
say "Codex" when the fallback did the audit.

### Step 9 — Plan Checkpoint includes the audit

Add one bullet to the checkpoint plan file's contents:
- **Codex audit summary** — key findings from the adversarial review and how they were
  resolved

### Step 10 — NEXT_SESSION_PROMPT.md deltas

Use spec-first's template with these modifications:

1. The intro names the workflow: "planned via the spec-first-cc-cc workflow".
2. In Step 1's reading list, annotate plan.md and todo.md with
   `(audited against the 18-item plan checklist; see findings.md for who audited)`, and findings.md with
   `(… Codex audit outcomes)`.
3. Step 3 (Context summary) adds:
   ```
   - **Plan audit:** <auditor label>, 18/18 answered, [F] FAIL ([X] fixed, [Z] rejected)
   ```
4. The per-milestone gate's verbatim dispatch quote starts with
   "This is a spec-first-cc-cc milestone gate. …" (instead of "spec-first") — the
   override contract is otherwise identical.

### Implementation phase — milestone gate modes

The per-milestone `/review-changes --light --fix` gate and the final FULL review run
exactly as `spec-first` defines them (including the ALL-severity override and the
verify-before-fix semantics of the final review). This delta only makes the two
operating modes explicit:

**Default (autonomous) mode:**
1. Complete all tasks in the milestone.
2. Invoke `/review-changes --light --fix`. Dispatch the single Agent tool subagent with
   the **explicit override**: tell it to fix findings of **ALL severities** (CRITICAL,
   HIGH, MEDIUM, LOW), not just the default CRITICAL/HIGH, using the verbatim
   "spec-first-cc-cc milestone gate" quote from the Step 10 delta.
3. The subagent produces a light report, applies all-severity fixes, and commits them
   grouped by category.
4. Relay the subagent's summary (findings found, findings fixed, skipped items with
   reasons, commit SHAs) to the user.
5. Commit any remaining milestone work the subagent did not cover.
6. Proceed to the next milestone.

**Manual mode** (only if the user explicitly opts out of autonomous fixing):
1. Complete all tasks in the milestone.
2. Invoke `/review-changes --light` (NO `--fix`). The subagent returns the light report
   only.
3. Present findings to the user and wait for direction.
4. Fix as directed. Commit when the user approves.
5. Proceed to the next milestone.

The same mode split applies to the final FULL review: autonomous mode uses
`/review-changes --fix` on the verified-real CRITICAL/HIGH/MEDIUM findings and presents
a fixed-real vs rejected-as-false-positive summary; manual mode presents the findings
(including the false-positive verification notes) and waits.

### Output Format delta

Before spec-first's artifact summary, print the audit header:

```
SPEC-FIRST CC-CC — DUAL ENGINE PLANNING (Draft/Audit)

  PLAN AUDIT ({auditor label}):
  checklist: 18/18 answered, {F} FAIL ({X} fixed, {Z} rejected)
  lint-plan.py: clean

  CONFIDENCE: {high/medium/low}
```

Then the artifact list and the highlighted "NEXT SESSION PROMPT" block, exactly
as spec-first specifies (the highlighted block stays the last visible element).

### After Generating delta

When presenting the artifacts, also summarize the Codex audit findings and how they
were resolved.

## Codex Fallback

Follow `${CLAUDE_PLUGIN_ROOT}/scripts/codex/README.md` (the routing table is repeated in
`references/codex-audit.md`):

- Unavailable Codex (preflight says `not-installed` or a cached `quota`; classify says
  `quota`, `capacity`, `auth`, `timeout` or `failed`; or the answer is `invalid-output`):
  the **`codex-fallback-auditor` subagent** (`${CLAUDE_PLUGIN_ROOT}/agents/codex-fallback-auditor.md`)
  answers the full 18-item checklist in the same per-ID format. When installed as a plugin
  the type is namespaced `keel-skills:codex-fallback-auditor`; if neither name is available,
  use `general-purpose` with the same checklist.
- Partial Codex answer: keep Codex's valid lines; the fallback answers only the missing IDs.
- One Codex attempt per audit. Never retry, never wait for a quota reset, never block the
  plan because Codex was unavailable.
- Label honestly: "Claude-Drafter" / "Claude-Auditor" when no usable Codex output exists,
  "Claude-led; Codex partial" when it was partial.

## Additional Anti-Patterns (on top of spec-first's)

1. **Co-generating instead of draft/audit** — Never have both engines generate plans
   independently and merge. Merging destroys internal coherence. One engine drafts,
   the other audits.
2. **Replacing three-experts with dual-engine** — Architecture decisions need
   role-differentiated adversarial deliberation, not two generic engines producing
   parallel proposals. Never skip three-experts for architecture.
3. **Auto-accepting all audit findings** — Review each Codex finding critically. Some
   will be false positives. The goal is to catch blind spots, not to blindly
   incorporate every suggestion.
4. **Auditing findings.md or the design gate** — the draft/audit loop applies ONLY to
   plan.md and todo.md (one audit over both). Adding audit phases elsewhere burns time
   without value.
5. **Rewriting the audited artifact in full during Phase C**: apply findings with `Edit`.
   A regenerated file is a new draft that nobody audited.
6. **Asking the LLM to check the template** — section presence, AD fields and AD-ID order
   are `lint-plan.py`'s job. The Codex checklist is for what a script cannot judge.

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/spec-first-cc-cc/`
- **Checkpoint frequency:** After Steps 0 (brainstorm, if run), 2 (research),
  5 (three-experts), 6 (plan.md), 7 (todo.md + audit), 8 (findings.md)
- **Subagent delegation:** Parallel research threads (Step 2), three-experts
  deliberation (Step 5), Codex audit (Step 7)

## Additional Quality Checklist Items (on top of spec-first's)

- [ ] `lint-plan.py` clean on the final plan.md and todo.md
- [ ] One plan+todo audit ran (hardened invocation from `references/codex-audit.md`);
      the merged checklist has 18/18 IDs answered (fallback auditor for anything Codex
      did not answer)
- [ ] Every FAIL fixed with targeted edits or rejected with a one-line reason
- [ ] findings.md includes the Codex Audit Summary section with real outcomes
- [ ] NEXT_SESSION_PROMPT.md includes the Codex audit results and uses the
      "spec-first-cc-cc milestone gate" dispatch quote
- [ ] Output started with the PLAN AUDIT header and ended with the highlighted
      "NEXT SESSION PROMPT" block
- [ ] `/tmp/spec-audit-*` temp files cleaned up after each audit's Phase C
