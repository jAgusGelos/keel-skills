---
name: spec-first-cc-cc
description: |
  Dual-engine specification workflow that combines spec-first planning with cc-cc cross-validation.
  Every planning step runs through both Claude and Codex in parallel, producing a cross-validated
  plan.md and todo.md that benefits from two independent perspectives.
  Use this skill when the user says "spec first cc-cc", "dual engine planning", "plan with codex",
  "cross-validated spec", "cc-cc planning", "dual spec", or when `/simple-feature-workflow`
  Phase 2 selects the dual-engine option.
version: 1.0.0
category: development
depends: [three-experts, stress-test, feature-context, cc-cc-powerful-iterations]
---

# spec-first-cc-cc

Dual-engine specification workflow that combines spec-first planning with cc-cc cross-validation.
Every planning step runs through both Claude and Codex in parallel, producing a cross-validated
plan.md and todo.md that benefits from two independent perspectives.

Use this skill when the user says "spec first cc-cc", "dual engine planning", "plan with codex",
"cross-validated spec", "cc-cc planning", "dual spec", or when `/simple-feature-workflow`
Phase 2 selects the dual-engine option.

---

## WHY THIS EXISTS

`spec-first` produces excellent plans but from a single engine's perspective. `cc-cc` provides
cross-validation but isn't specialized for planning. This skill runs the full spec-first
pipeline with dual-engine validation at every critical decision point — research synthesis,
architecture decisions, and plan generation — so the final spec has been stress-tested by
two independent AI engines before a single line of code is written.

---

## THE CYCLE

```
Confirmed Feature Request (from caller or user)
     |
     v
[1] Parallel Research (Claude subagent + Codex)
     |
     v
[2] Synthesis & Gap Classification (cross-validated)
     |
     v
[3] Clarify Critical Unknowns (if any)
     |
     v
[4] Architecture Decisions (Claude + Codex propose independently, then merge)
     |
     v
[5] Generate plan.md (dual-engine, synthesized)
     |
     v
[6] Generate todo.md (dual-engine, synthesized)
     |
     v
[7] Plan Checkpoint
```

---

## STEP-BY-STEP

### Step 1: Parallel Research

Launch two independent research passes simultaneously:

**Claude Subagent (via Agent tool):**

```
Explore the codebase for context relevant to: {feature_request}

Research:
- Directory layout, relevant files, architectural entry points
- Dependencies, config files, tech stack
- memory-bank/ context (project-brief, tech-context, system-patterns, active-context)
- Existing patterns and conventions that affect this feature

Return: structured findings with file paths and evidence.
```

**Codex CLI:**

```bash
codex -a never exec "Explore this codebase for context relevant to: {feature_request}. Find relevant files, architectural patterns, dependencies, and conventions. Return structured findings with file paths."
```

### Step 2: Cross-Validated Synthesis

Once both research results are back:

1. **Compare findings** — note where both engines found the same patterns (high confidence)
   and where they diverged (investigate further).
2. **Merge into a unified synthesis:**
   - Known with confidence (cited by both engines)
   - Known with moderate confidence (cited by one, plausible)
   - Unknown (neither engine found evidence)
3. **Classify unknowns** as Critical / Important / Nice-to-have.
4. **Show the user** the cross-validated synthesis with agreement markers:

   ```
   CROSS-VALIDATED RESEARCH SYNTHESIS

   HIGH CONFIDENCE (both engines agree):
   - {finding_1} — files: {paths}
   - {finding_2} — files: {paths}

   MODERATE CONFIDENCE (one engine found):
   - {finding_3} — source: {Claude/Codex} — files: {paths}

   UNKNOWNS:
   - [CRITICAL] {unknown_1}
   - [IMPORTANT] {unknown_2}
   ```

### Step 3: Clarify Critical Unknowns

If any Critical unknowns exist:

- Ask up to 3 targeted, decision-oriented questions (multiple-choice when possible).
- STOP and wait for answers.
- Reclassify after answers arrive.

If no Critical unknowns, proceed with documented assumptions.

### Step 4: Dual-Engine Architecture Decisions

For each major architecture decision:

**Run both engines independently on the same question:**

**Claude Subagent:**

```
Given this context:
{synthesis_from_step_2}
{resolved_unknowns}

Propose architecture for: {decision_topic}
Consider at least 3 options. For each: describe approach, pros, cons, risk level.
Recommend one with rationale.
```

**Codex CLI:**

```bash
codex -a never exec "Given this codebase context: {synthesis_summary}. Propose architecture for: {decision_topic}. Consider 3+ options with pros/cons/risks. Recommend one."
```

**Then synthesize:**

1. Compare recommendations — if both agree, high confidence.
2. If they diverge, reason about which is more correct given the evidence.
3. Note where Codex caught something Claude missed and vice versa.

**Show the user each architecture decision:**

```
ARCHITECTURE DECISION: AD-{N} — {title}

CLAUDE RECOMMENDS: {option_A} — {rationale}
CODEX RECOMMENDS:  {option_B} — {rationale}

AGREEMENT: {agree/diverge}

SYNTHESIZED DECISION: {chosen_option}
RATIONALE: {why, incorporating best of both perspectives}
TRADEOFFS: {what we're giving up}

Confirm or override?
```

Wait for user approval on each decision.

### Step 5: Generate plan.md (Dual-Engine)

**Claude Subagent** generates plan.md using the spec-first template with all sections:
Executive Summary, Commands, Architecture Decisions (AD-IDs), Dependencies, NFRs,
Three-Tier Boundaries, Risks & Mitigations, Strategy (phased milestones), Open Questions,
Conformance Criteria.

**Codex CLI** independently generates a plan from the same inputs:

```bash
codex -a never exec "Generate a detailed implementation plan for: {feature_request}. Context: {synthesis + architecture_decisions}. Include: summary, architecture decisions, dependencies, risks, milestones, boundaries, conformance criteria. Use markdown."
```

**Synthesize the two plans:**

- Take the strongest sections from each.
- Resolve any conflicts in milestone ordering or scope.
- Ensure AD-IDs are consistent.
- Merge risk tables (union of risks from both engines).

Write the final synthesized `plan.md` to project root.

### Step 6: Generate todo.md (Dual-Engine)

Same dual-engine pattern:

**Claude Subagent** generates todo.md from plan.md following spec-first task rules:

- Milestones matching plan.md phases
- Atomic, testable tasks with Verify criteria
- AD-ID references for traceability
- Hardening & Launch section

**Codex CLI** independently generates a task breakdown:

```bash
codex -a never exec "Generate an implementation checklist for: {feature_request} based on this plan: {plan_summary}. Tasks should be atomic, testable, with verification criteria. Group by milestones."
```

**Synthesize:**

- Merge task lists, deduplicate.
- Take the more granular subtask breakdown where they differ.
- Ensure every task has a Verify criterion.
- Maintain AD-ID references from plan.md.

Write the final synthesized `todo.md` to project root.

### Step 7: Plan Checkpoint

1. **Enter plan mode** — Use `EnterPlanMode`.
2. **Write the plan file** including:
   - Feature request summary
   - Paths to plan.md and todo.md
   - Architecture decisions with engine agreement status
   - Cross-validation confidence notes
   - Top risks
   - Three-Tier Boundaries
   - Commands
   - Approval status
3. **Exit plan mode** — Use `ExitPlanMode`.
4. **Present to the user** — Summary of key decisions, risks, open questions.
5. **Offer `/stress-test`** — Optional adversarial validation before implementation.

---

## OUTPUT FORMAT

When this skill is invoked by `/simple-feature-workflow` or directly, always show:

```
┌─────────────────────────────────────────────────┐
│  SPEC-FIRST CC-CC — DUAL ENGINE PLANNING        │
├─────────────────────────────────────────────────┤
│                                                 │
│  ENGINE AGREEMENT SUMMARY:                      │
│  Research:     {agree%} agreement               │
│  Architecture: {N}/{total} decisions aligned    │
│  Plan:         {agree/diverge} on structure     │
│  Tasks:        {N} tasks (merged from both)     │
│                                                 │
│  ARTIFACTS:                                     │
│  - plan.md  ({path})                            │
│  - todo.md  ({path})                            │
│                                                 │
│  CONFIDENCE: {high/medium/low}                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## CODEX FALLBACK

If Codex CLI is unavailable or errors out:

- Fall back to running **two independent Claude subagents** instead.
- Label outputs as "Claude-A" and "Claude-B" instead of "Claude" and "Codex".
- The rest of the workflow remains identical.

---

## CONTEXT MANAGEMENT

- **Scratchpad:** `.workspace/ctx/spec-first-cc-cc/`
- **Checkpoint frequency:** After Steps 2, 4, 5, 6
- **Subagent delegation:** Research (Step 1), Architecture (Step 4), Plan gen (Step 5), Task gen (Step 6)

---

## MANDATORY: Keep todo.md Updated During Implementation

**As you complete each task, update todo.md immediately** — check off completed items
(`- [x]`), add notes about deviations, and append new tasks discovered during implementation.
The todo.md is a living document, not a frozen artifact. If a task was harder than expected,
split it. If review found new issues, add them. Never leave the todo.md stale — it should
always reflect the current state of progress so that any session (current or future) can
read it and know exactly where things stand.

---

## ANTI-PATTERNS — DO NOT

- Run only one engine and skip cross-validation (defeats the purpose)
- Auto-merge without showing the user where engines diverged
- Skip the architecture decision approval step
- Generate plan.md without AD-IDs and traceability
- Write code — this skill produces plan.md and todo.md ONLY
- Skip the plan checkpoint (Step 7)
- Leave todo.md unchecked after completing tasks — always update as you go
