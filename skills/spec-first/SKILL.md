---
name: spec-first
description: |
  Spec First Workflow — plan before you code. Use this skill whenever the user needs to plan
  a feature before implementation, when context or clarity is low, or when architectural
  decisions need to be made upfront. Trigger on: "spec first", "plan before code", "low clarity",
  "new feature planning", "architecture plan", "spec workflow", "plan.md", "todo.md generation",
  "feature specification", "implementation plan", "let's plan this", "I need a spec",
  "design this feature first". Produces plan.md and todo.md as outputs. Also trigger when
  the user describes a vague or complex feature and you assess that jumping into code would
  likely require significant rework.
version: 1.0.0
category: development
depends: [three-experts, stress-test, feature-context]
---

# Spec First Workflow

Build a shared mental model of a feature before writing code. Produce two artifacts:
`plan.md` (the spec) and `todo.md` (the execution checklist). Code comes after, never before.

This workflow follows five phases aligned with industry practice:
**Specify** (Step 1) → **Plan** (Steps 2–6) → **Tasks** (Step 7) → **Checkpoint** (Step 8) → **Implement** (post-approval).

## When to Trigger

- User asks for planning, architecture, or spec work
- Feature request is vague, broad, or touches unknown parts of the system
- User explicitly asks for plan.md or todo.md
- You assess that jumping into code would likely require significant rework

## Workflow

### Step 1: Capture and Confirm the Feature Request

Restate the user's request in one tight paragraph with explicit scope boundaries:

- Intended outcome
- In-scope behavior
- Out-of-scope assumptions (if known)

Present this restatement to the user and ask them to confirm before proceeding.

Why: framing prevents plan drift. Confirming early avoids wasted research on a
misunderstood request.

### Step 2: Parallel Research

Launch multiple Agent subagents simultaneously to gather context. If subagents are
unavailable, perform the same research sequentially using Glob, Grep, and Read directly.

**Thread A — Codebase Structure:**

- Use Glob to map directory layout and find relevant files
- Use Grep to locate features, routes, services, models related to the request
- Identify architectural entry points and coupling hotspots
- Record concrete file paths for every finding

**Thread B — Dependencies & Configuration:**

- Use Read on package.json, pyproject.toml, go.mod, or equivalent
- Check for relevant config files (tsconfig, docker-compose, CI configs)
- Identify what's available vs. what needs adding

**Thread C — Memory Bank Context:**

- Use Glob to check for `memory-bank/` directory (also check `docs/`, `.memory/`, `context/`)
- If found, use Read on (in priority order):
  - `memory-bank/project-brief.md`
  - `memory-bank/tech-context.md`
  - `memory-bank/system-patterns.md`
  - `memory-bank/active-context.md`
  - `memory-bank/core-flows.md`
- If files are absent, explicitly report missing context docs

Why: architecture decisions need evidence, not guesses. The memory bank prevents
proposing solutions that contradict established project decisions.

### Step 3: Synthesize and Classify Gaps

Create a short synthesis:

- What is known with confidence (cite file paths)
- What is inferred from code patterns (cite evidence)
- What is unknown

Classify each unknown:

- **Critical** — blocks correctness or safety, cannot proceed without it
- **Important** — affects architecture or sequencing, but can use reasonable defaults
- **Nice-to-have** — can proceed without

Why: separates true blockers from things resolved during implementation.

### Step 4: Clarify or Continue

If any Critical unknown exists:

- Ask up to 3 targeted, decision-oriented questions
- Make questions specific and multiple-choice when possible
- Bad: "What do you want?" Good: "Should this support batch operations or single-item only?"
- Then STOP and wait for answers

Once answers arrive, reclassify remaining unknowns. If all Critical gaps are resolved,
continue to Step 5. If not, inform the user which gaps remain.

If no Critical unknowns exist, proceed with explicit assumptions documented.

Why: prevents speculative design built on false assumptions.

### Step 5: Three Experts Reasoning (via `three-experts` skill)

**Invoke the `three-experts` skill** to reason about architecture decisions from multiple
perspectives. The skill will:

1. Use the repository context gathered in Step 2 (no need to re-explore)
2. Select 3 domain-specific experts based on the problem type
3. Run structured deliberation rounds with challenges, sub-point resolution, and dropouts
4. Conduct a formal voting round
5. Produce a consensus recommendation with tradeoffs and implementation approach

**Adaptation for spec-first:** When invoking three-experts, pass the following context:

- The confirmed feature request from Step 1
- The synthesis and gap classification from Steps 3-4
- The resolved context from Step 2 (file paths, tech stack, patterns)

The three-experts output feeds directly into the Architecture Decisions section of plan.md.
**Safety and correctness constraints always take priority** over convenience or speed.

Why: avoids one-dimensional architecture choices and surfaces tradeoffs early. Using the
full three-experts skill ensures structured deliberation with evidence-based challenges
instead of a simplified inline reasoning pass.

### Step 6: Generate plan.md

Before writing, check if plan.md already exists in the target location. If it does,
ask the user whether to overwrite or create a new version (e.g., plan-v2.md).

Write plan.md in the project root (or user-specified location) using this template:

```markdown
# Plan: [Feature Name]

> Generated via spec-first workflow on [date]

## Executive Summary

- **Problem:** [what needs solving]
- **Desired outcome:** [what success looks like]
- **Scope:** [what's included]
- **Non-goals:** [what's explicitly excluded]
- **Success criteria:** [how we know it's done]

## Commands

- **Build:** `[command]`
- **Test:** `[command, including single-file run]`
- **Lint:** `[command]`
- **Dev server:** `[command]`

## Architecture Decisions

### AD-1: [Title]

- **Context:** [why this decision is needed]
- **Options considered:** [alternatives]
- **Chosen approach:** [decision]
- **Rationale:** [why, referencing expert perspectives]
- **Evidence:** [file paths and patterns that informed this]
- **Tradeoffs:** [what we're giving up]
- **Consequences:** [what this commits us to]

### AD-2: [Title]

[Same structure]

## Dependencies

### New Dependencies

| Package/Module | Purpose      | Risk Level     |
| -------------- | ------------ | -------------- |
| [name]         | [why needed] | [low/med/high] |

### Existing Dependencies Leveraged

- [dependency] — used for [purpose]

### Internal Module Dependencies

- [module A] depends on [module B] — [why ordering matters]

## Non-Functional Requirements

- **Auth/Security:** [requirements or N/A]
- **Performance:** [SLOs, latency, throughput expectations]
- **Migration/Backward Compatibility:** [breaking changes, data migration needs]
- **Observability:** [logging, monitoring, alerting needs]

## Three-Tier Boundaries

### ✅ Always

- [Rules agents must always follow, e.g., run tests before commits]
- [Follow naming conventions from existing codebase]

### ⚠️ Ask First

- [Changes requiring human approval, e.g., DB schema changes]
- [API contract changes, new external dependencies]

### 🚫 Never

- [Hard prohibitions, e.g., commit secrets or API keys]
- [Delete production data, skip required tests, bypass auth]

## Risks & Mitigations

| Risk                  | Likelihood     | Impact         | Mitigation            |
| --------------------- | -------------- | -------------- | --------------------- |
| [what could go wrong] | [low/med/high] | [low/med/high] | [prevention/handling] |

## Strategy

### Phase 1: [Name — smallest shippable slice]

[What gets built first, why it comes first, exit criteria]

### Phase 2: [Name]

[What comes next, dependencies on Phase 1, exit criteria]

## Open Questions

- [ ] [Question] — Why it matters: [context]. Default if unanswered: [fallback]

## Conformance Criteria

Testable assertions that validate the plan was followed correctly:

- [ ] [e.g., "All API endpoints return consistent error format defined in types/errors.ts"]
- [ ] [e.g., "No direct DB queries outside the repository layer"]
- [ ] [e.g., "Every new route has integration test coverage"]
- [ ] [e.g., "Feature flags gate all user-visible changes"]
```

### Step 7: Generate todo.md

Before writing, check if todo.md already exists. Same overwrite rules as plan.md.

Write todo.md to `.workspace/features/<feature-name>/todo.md` (NEVER to project root). Every task should be
atomic and independently testable. Order by dependency. Reference AD-IDs from plan.md
to maintain traceability.

```markdown
# TODO: [Feature Name]

> Tracks implementation. See plan.md for architecture context.

## Milestone 1: [Name — matches Phase from plan.md]

- [ ] Task 1.1: [clear, actionable description] `[refs: AD-1]`
  - [ ] [subtask — single concrete action]
  - [ ] [subtask]
  - [ ] Verify: [how to confirm this task is done — test, manual check, or other]
- [ ] Task 1.2: [description] `[refs: AD-2]`
  - [ ] [subtask]
  - [ ] [subtask]
  - [ ] Verify: [verification criteria]

## Milestone 2: [Name]

- [ ] Task 2.1: [description]
  - [ ] [subtask]
  - [ ] [subtask]
  - [ ] Verify: [verification criteria]

## Hardening & Launch

- [ ] Final regression sweep
  - [ ] Critical path test pass
  - [ ] Performance/security checks
- [ ] Documentation updates
- [ ] Rollout/rollback readiness

## Verification

- [ ] All tests pass
- [ ] Conformance criteria from plan.md satisfied
- [ ] Manual smoke test of [key user flow]
```

**Rules for good tasks:**

- Each task produces a testable artifact (a function, endpoint, component)
- Subtasks are single actions: "create file X", "add method Y", "write test for Z"
- Every task includes a **Verify** subtask with verification criteria
- Include appropriate verification per task (unit test, integration test, manual check,
  or other validation — not everything requires a unit test)
- If a task has more than 5 subtasks, split it into multiple tasks
- Never write "refactor" without specifying what changes and why
- Reference AD-IDs from plan.md so decisions are traceable to tasks

### Step 8: Plan Checkpoint

After generating plan.md and todo.md, create a plan checkpoint so the user can optionally
clear context before implementation.

**What to do:**

1. **Enter plan mode** — Use the `EnterPlanMode` tool to signal the start of a plan checkpoint.

2. **Write the plan file** — Include:
   - **Feature request summary** (from Step 1)
   - **Paths to generated artifacts** — full paths to plan.md and todo.md
   - **Key architecture decisions** — summary of AD-IDs and their chosen approaches (from Steps 5-6)
   - **Resolved vs. open questions** — which Critical/Important unknowns were answered and which remain
   - **Top risks** — from the Risks & Mitigations table
   - **Three-Tier Boundaries** — Always/Ask First/Never rules (needed for every implementation task)
   - **Commands** — build, test, lint, dev server (needed for agent self-verification)
   - **Approval status** — whether the user has approved the plan (pending/approved). After
     `/clear`, this prevents accidental implementation without explicit approval

   The plan file must give enough context that a fresh session can read plan.md, todo.md,
   and the plan file to begin implementation without any prior conversation history.

3. **Exit plan mode** — Use the `ExitPlanMode` tool to signal the plan is ready for review.

4. **Suggest adversarial validation** — Consider running `/stress-test` to adversarially
   validate this plan before implementation. This is optional but recommended for plans
   with unverified assumptions, external dependencies, or performance claims.

5. **Inform the user** — This is the ideal point to `/clear` context before starting
   implementation. After clearing, the implementation session should read the plan file
   first, then follow the "Using the Spec During Implementation" guidance below.

**This is a checkpoint, not a gate.** Users who do not want to clear context can proceed
directly to implementation approval without interruption.

## After Generating

Present both files with a brief summary of:

- Key architecture decisions and their rationale
- Top risks identified
- Open questions that need human input

Then wait. Do not proceed to implementation until the user explicitly approves the plan
or says to start coding. Remind the user that this is the ideal moment to `/clear` context
if the conversation has grown long — the plan checkpoint from Step 8 ensures all context
is preserved in the plan file, plan.md, and todo.md.

**Living artifacts:** plan.md and todo.md are not frozen after creation. Update them
when discoveries emerge during implementation. If a decision changes or a risk
materializes, revise the relevant section and note the change date. For major rewrites,
ask the user whether to version the old file (e.g., plan-v1.md) before overwriting.

## Using the Spec During Implementation

This section is guidance for the **implementation phase after this skill completes**.
The spec-first skill itself only produces plan.md and todo.md — it does not write code.

**If context was cleared:** Start by reading the plan file from Step 8 to recover artifact
paths and key decisions, then read plan.md and todo.md before beginning any task.

Beware the "curse of instructions" — research shows model adherence drops as the number
of simultaneous requirements grows. Do not dump the entire plan.md into a single
implementation prompt.

When implementing tasks from todo.md:

- Feed only the **relevant plan.md section(s)** + the **specific task and its subtasks**
- Each task prompt should be self-contained with just enough context to execute
- Always include **Three-Tier Boundaries** — those apply to every task
- Always include **Commands** — so the agent can verify its own work
- Reference applicable **Conformance Criteria** for the current task

### MANDATORY: Keep todo.md Updated During Implementation

**As you complete each task, update todo.md immediately** — check off completed items
(`- [x]`), add notes about deviations, and append new tasks discovered during implementation.
The todo.md is a living document, not a frozen artifact. If a task was harder than expected,
split it. If review found new issues, add them. Never leave the todo.md stale — it should
always reflect the current state of progress so that any session (current or future) can
read it and know exactly where things stand.

## Anti-Patterns

Mistakes that undermine the spec-first approach — avoid these:

1. **Vague specs** — "Build something nice" is not a spec. Every section needs concrete,
   falsifiable statements.
2. **Monolithic prompts** — Dumping the entire spec into one implementation prompt
   overwhelms the model and degrades output quality.
3. **Skipping human review** — Never start coding from a plan the user hasn't approved.
   The plan exists to build shared understanding.
4. **Missing boundaries** — A plan without Never/Always rules leaves agents guessing
   what's safe. Make constraints explicit.
5. **Over-specifying implementation** — The spec defines WHAT and WHY, not HOW. Leave
   implementation details to the coding phase unless architecturally significant.
6. **Ignoring existing patterns** — Always check what conventions the codebase already
   follows. Proposing new patterns when working ones exist creates inconsistency.
7. **Skipping the plan checkpoint creation** — Always create the checkpoint (Step 8).
   The `/clear` afterward is optional, but creating the checkpoint is not — long spec
   conversations consume context, and without the checkpoint the user loses the ability
   to safely reset before implementation.

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/spec-first/`
- **Checkpoint frequency:** After Steps 2 (research), 5 (three-experts), 6 (plan.md), 7 (todo.md)
- **Subagent delegation:** Parallel research threads (Step 2), three-experts deliberation (Step 5)

## Quality Checklist

Before delivering plan.md and todo.md, verify:

- [ ] Research used Glob, Grep, Read to gather real evidence (not guesses)
- [ ] Every unknown classified as Critical / Important / Nice-to-have
- [ ] Three Experts reasoning documented with file path citations
- [ ] Safety/correctness constraints prioritized over convenience in decisions
- [ ] plan.md has all sections: Summary, Commands, Architecture, Dependencies, NFRs,
      Boundaries, Risks, Strategy, Open Questions, Conformance
- [ ] Architecture decisions have AD-IDs and todo.md tasks reference them
- [ ] todo.md has milestones, tasks with Verify criteria, Hardening, Verification
- [ ] Three-Tier Boundaries populated with project-specific rules
- [ ] Conformance criteria are testable assertions, not vague goals
- [ ] Checked for existing plan.md/todo.md before writing
- [ ] Plan presented for user approval before any implementation
- [ ] Plan checkpoint written via EnterPlanMode/ExitPlanMode with artifact paths and key context
- [ ] No implementation code was written — only plan.md and todo.md

---

## Feature Context Integration

When planning a named feature, this skill creates or resumes a `feature-context`:

1. **On init:** If no feature-context exists for this feature, create one via `/feature-context init <feature-name>`
2. **On resume:** If a feature-context already exists, resume it via `/feature-context resume <feature-name>`
3. **After planning:** Write the plan summary, architecture decisions, and milestone list to feature-context
4. **Data written:** plan.md path, todo.md path, AD-IDs, risk summary, milestone count
