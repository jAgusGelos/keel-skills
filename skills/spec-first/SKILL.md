---
name: spec-first
description: |
  Spec First Workflow — plan before you code. Use this skill whenever the user needs to plan
  a feature before implementation, when context or clarity is low, or when architectural
  decisions need to be made upfront. Trigger on: "spec first", "plan before code", "low clarity",
  "new feature planning", "architecture plan", "spec workflow", "plan.md", "todo.md generation",
  "feature specification", "implementation plan", "let's plan this", "I need a spec",
  "design this feature first". Produces plan.md, todo.md, findings.md, and NEXT_SESSION_PROMPT.md
  as outputs. The NEXT_SESSION_PROMPT.md path is printed in a highlighted block so the user
  can copy it and paste it as the first message of a fresh implementation session.
  For UI-touching features, runs the design-alternatives skill as a mandatory design gate
  (Step 5b) before plan.md — the user picks a visual direction from an HTML mockup of
  2-4 alternatives, recorded as DESIGN.md, so implementation never starts with an
  undecided or generic UI.
  Includes an optional brainstorm phase (Step 0) that explores alternative approaches before
  committing to a direction. Supports optional worktree mode (trigger words: "worktree",
  "--worktree", "in a worktree", "separate worktree") that bakes worktree setup, dependency
  install, and env copy instructions into NEXT_SESSION_PROMPT.md so the implementation runs
  in an isolated branch. Also trigger when the user describes a vague or complex feature
  and you assess that jumping into code would likely require significant rework.
version: 1.1.0
category: development
depends: [three-experts, design-alternatives, stress-test, review-changes, feature-context]
---

# Spec First Workflow

Build a shared mental model of a feature before writing code. Produce three artifacts:
`plan.md` (the spec), `todo.md` (the execution checklist), and `findings.md` (research
output, discoveries, and brainstorm results). Code comes after, never before.

This workflow follows six phases aligned with industry practice:
**Brainstorm** (Step 0, skippable) → **Specify** (Step 1) → **Plan** (Steps 2–6, with the
**Design Gate** at Step 5b for UI features) → **Tasks** (Step 7) → **Findings** (Step 8) → **Checkpoint** (Step 9) → **Implement** (post-approval).

## When to Trigger

- User asks for planning, architecture, or spec work
- Feature request is vague, broad, or touches unknown parts of the system
- User explicitly asks for plan.md or todo.md
- You assess that jumping into code would likely require significant rework

## Workflow

### Step 0: Brainstorm Alternative Approaches (skippable)

**Skip detection:** If the user's request already contains specific requirements, clear
technical constraints, named technologies, and defined scope boundaries, skip this step
and proceed directly to Step 1. A request like "Add a Redis-backed rate limiter to the
/api/upload endpoint, 100 req/min per user, with a 429 response" is already specific
enough. A request like "We need better caching" or "Build a notification system" is not.

**Purpose:** Before committing to a direction, explore the solution space. This prevents
tunnel vision and surfaces alternatives the user may not have considered.

**Process:**

1. **Generate 2-3 alternative approaches.** For each alternative, provide:
   - **Name:** A short, descriptive label (e.g., "Event-Driven Push", "Polling with Cache")
   - **Description:** 2-3 sentences explaining the approach, how it works, and what it optimizes for
   - **Pros:** 2-4 concrete advantages (performance, simplicity, extensibility, etc.)
   - **Cons:** 2-4 concrete disadvantages (complexity, cost, coupling, migration risk, etc.)

2. **Self-review for contradictions.** Before presenting alternatives to the user, check:
   - Do any two alternatives claim the same advantage? If so, differentiate more clearly.
   - Are the cons realistic or are they strawman weaknesses to make one option look better?
   - Does every alternative genuinely solve the stated problem, or is one a non-starter?
   Revise the alternatives if contradictions or bias are found.

3. **Present alternatives incrementally.** Show the alternatives to the user, then ask
   ONE narrowing question at a time. Do not batch multiple questions. Examples of good
   narrowing questions:
   - "Do you value simplicity over extensibility for this feature?"
   - "Is this expected to handle more than 10k concurrent users?"
   - "Does this need to integrate with the existing event bus or can it be standalone?"

   Wait for the user's answer before asking the next question. Each answer should
   eliminate at least one alternative or refine the remaining options.

4. **Converge on a direction.** Once the user has selected an approach (or a hybrid),
   confirm the chosen direction in one sentence: "Proceeding with [Approach Name]:
   [one-line summary]."

5. **Save brainstorm output.** Append the brainstorm results (all alternatives with
   pros/cons, the narrowing questions and answers, and the final selection) to the
   plan file. This becomes the "Brainstorm" section at the top of plan.md, providing
   a decision audit trail. Also record in `findings.md` under a "## Brainstorm" heading.

Why: exploring alternatives before planning prevents premature commitment and gives the
user genuine options instead of a single take-it-or-leave-it proposal. The incremental
questioning style avoids overwhelming the user with a wall of decisions.

### Step 1: Capture and Confirm the Feature Request

Restate the user's request in one tight paragraph with explicit scope boundaries:

- Intended outcome
- In-scope behavior
- Out-of-scope assumptions (if known)

Present this restatement to the user and ask them to confirm before proceeding.

Why: framing prevents plan drift. Confirming early avoids wasted research on a
misunderstood request.

#### Step 1b: Detect Worktree Mode (optional)

Scan the user's invocation for any of these signals:

- The literal word `worktree` (case-insensitive)
- `--worktree`, `--wt`, `wt:`, or `worktree:<path>`
- Phrases like "in a worktree", "use a worktree", "separate worktree",
  "isolated branch", "branch off"

If any signal is present, **worktree mode is enabled**. Record this in the
scratchpad and confirm with the user in a single short exchange:

1. **Propose path and branch.** Default path:
   `<repo-parent>/<repo-name>-<feature-slug>` (e.g. if repo is at
   `/home/x/project`, propose `/home/x/project-add-rate-limiter`). Default
   branch: derived from the feature slug, matching the repo's branch
   convention if detectable from recent branches (`git branch -a --sort=-committerdate | head -10`).

2. **Detect affected apps.** From the parallel research in Step 2 (codebase
   scan), record which app directories the feature touches (e.g. `apps/api`,
   `apps/web`). These drive the dependency-install and env-copy
   commands baked into NEXT_SESSION_PROMPT.md.

3. **Ask the user one question max.** Confirm path + branch in a single prompt,
   accepting "ok" / "default" as approval. Do NOT batch separate questions.

Worktree mode does NOT create the worktree during planning. The worktree
artifacts (plan.md, todo.md, findings.md, NEXT_SESSION_PROMPT.md) live in the
base repo's `.workspace/features/<feature>/`. The implementation session
(launched from NEXT_SESSION_PROMPT.md) is what actually creates the worktree,
installs deps, copies envs, and runs checks.

If no worktree signal is present, skip this step entirely — the implementation
will happen on the current branch in the base repo.

Why: worktree mode keeps a long implementation isolated from other work,
prevents accidental dirty state on the user's current branch, and gives the
implementation session a clean environment with its own `node_modules`.

### Step 2: Parallel Research

Launch the three threads below simultaneously as `explorer` subagents
(`subagent_type: explorer`, defined in `${CLAUDE_PLUGIN_ROOT}/agents/explorer.md`: Sonnet, effort
medium, read-only; when installed as a plugin the type is namespaced `keel-skills:explorer`). They are pure reading and never need the planning model; measured
over 30 sessions, research threads on the default model cost ~2.5x what Sonnet does for
the same brief. Each thread returns a compact brief (at most ~40 lines, verified file
paths, no file dumps); the orchestrator keeps the briefs, not the files. If the
`explorer` type is unavailable, use `Explore` with `model: sonnet`; if subagents are
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

### Step 5b: Design Alternatives Gate (MANDATORY for UI-touching features)

**Trigger detection:** the feature adds or reshapes any user-visible UI — a screen,
page, dialog, or significant component. **For features with UI the gate is mandatory —
no exceptions for size, "obvious" designs, or schedule pressure.** The only exemptions:
(1) no user-visible surface (backend, CLI, invisible refactor); (2) a bugfix that
restores already-decided behavior/appearance — though a "fix" that introduces a new
visual treatment or state is design work and the gate runs. Record any skip and its
reason in findings.md. "It's just a small table page" is NOT a skip reason.

**Invoke the `design-alternatives` skill.** Pass it the confirmed feature request
(Step 1), the research context (Step 2 — affected app, existing components, token
sources), and the feature folder `.workspace/features/<feature-name>/`. The skill:

1. Writes a design brief (the screen's one job, hero element, page archetype, data
   states, density).
2. Generates 2-4 genuinely different design directions — distinct strategies, not
   re-skins — built with the project's REAL design tokens, real copy, realistic ugly
   data, and all four data states (populated/empty/loading/error).
3. Produces `design-alternatives.html` (self-contained: ticket summary + side-by-side
   alternatives + tradeoffs table + recommendation + decision footer) in the feature
   folder, alongside the other planning artifacts.
4. **STOPS and waits for the user to pick a direction** (hybrid picks welcome).
5. Records the decision as `DESIGN.md` (ADR-style, with UI acceptance criteria) in the
   same folder.

**Gate semantics:** plan.md must NOT be drafted until the user has picked a direction.
The chosen direction feeds plan.md's "Design Direction" section, the UI acceptance
criteria feed the Conformance Criteria, and UI tasks in todo.md reference them in their
Verify subtasks.

Why: without this gate, design decisions happen implicitly inside code generation and
the user only sees the result when implementation is done — the two failure modes that
produce generic, intention-free UI.

### Step 6: Generate plan.md

Before writing, check if plan.md already exists in the target location. If it does,
ask the user whether to overwrite or create a new version (e.g., plan-v2.md).

Write plan.md to `.workspace/features/<feature-name>/plan.md` (NEVER to project root) using this template:

```markdown
# Plan: [Feature Name]

> Generated via spec-first workflow on [date]

## Brainstorm (if Step 0 was run)

### Alternatives Considered

#### Option A: [Name]
- **Approach:** [2-3 sentence description]
- **Pros:** [list]
- **Cons:** [list]

#### Option B: [Name]
[Same structure]

#### Option C: [Name] (if applicable)
[Same structure]

### Narrowing Questions & Answers
- Q: [question] → A: [user's answer]
- Q: [question] → A: [user's answer]

### Selected Approach
[Approach name and one-line rationale]

## Executive Summary

- **Problem:** [what needs solving]
- **Desired outcome:** [what success looks like]
- **Scope:** [what's included]
- **Non-goals:** [what's explicitly excluded]
- **Success criteria:** [how we know it's done]

## Design Direction (if Step 5b ran — UI-touching features)

- **Chosen direction:** [name + one-line strategy, incl. hybrid modifications]
- **Decision record:** `DESIGN.md` (same folder) — UI acceptance criteria live there
- **Mockup:** `design-alternatives.html` (same folder) — the visual reference the
  implementation is checked against
- **Rejected directions:** [name — one-line why, per alternative]

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

### Step 8: Generate findings.md

Write `findings.md` to `.workspace/features/<feature-name>/findings.md` alongside plan.md
and todo.md. This file captures research output and discoveries that informed the plan but
do not belong in the plan itself. It serves as a reference for future sessions and prevents
re-discovery of the same information.

Before writing, check if findings.md already exists. Same overwrite rules as plan.md.

```markdown
# Findings: [Feature Name]

> Research output from spec-first workflow on [date]
> See plan.md for architecture decisions. See todo.md for implementation tasks.

## Brainstorm (if Step 0 was run)

### Alternatives Explored
- **[Option A Name]:** [summary] — [selected/rejected, why]
- **[Option B Name]:** [summary] — [selected/rejected, why]
- **[Option C Name]:** [summary] — [selected/rejected, why]

### Narrowing Questions & User Responses
1. Q: [question] → A: [answer]
2. Q: [question] → A: [answer]

## Codebase Research

### Relevant Files Discovered
- `[path]` — [what it does, why it matters]
- `[path]` — [what it does, why it matters]

### Existing Patterns Identified
- [Pattern name]: [description, where found, how it affects this feature]

### Dependencies & Config
- [Dependency/config finding and its implications]

## Memory Bank Context
- [Key context from memory-bank that influenced decisions]
- [Missing context that was expected but absent]

## Gap Analysis
- **Critical (resolved):** [gap] — resolved by [answer/assumption]
- **Important (deferred):** [gap] — default assumption: [fallback]
- **Nice-to-have:** [gap] — not blocking

## Three-Experts Deliberation Summary
- **Expert perspectives:** [brief summary of each expert's stance]
- **Key disagreements:** [what they argued about]
- **Consensus reached:** [what they agreed on and why]

## Design Gate (Step 5b)
- **Ran / skipped:** [ran → chosen direction + link to DESIGN.md | skipped → reason
  (no user-visible UI, or explicit user opt-out)]

## Unexpected Discoveries
- [Anything surprising found during research that may matter later]
```

**Rules for good findings:**
- Every file path must be real (verified via Glob/Grep/Read during Step 2)
- Brainstorm section is only included if Step 0 ran
- Design Gate section always states ran-or-skipped; a skip without a recorded reason
  is a workflow violation
- Gap analysis must match what was documented in Steps 3-4
- Three-Experts summary must reflect the actual deliberation from Step 5
- Unexpected discoveries should include things that did not fit into plan.md
  but might matter during implementation or future features

Why: findings.md prevents knowledge loss between planning and implementation. When a
developer picks up the feature days later, they can read findings.md to understand not
just what was decided (plan.md) but what was explored and why alternatives were rejected.

### Step 9: Plan Checkpoint

After generating plan.md and todo.md, create a plan checkpoint so the user can optionally
clear context before implementation.

**What to do:**

1. **Enter plan mode** — Use the `EnterPlanMode` tool to signal the start of a plan checkpoint.

2. **Write the plan file** — Include:
   - **Feature request summary** (from Step 1)
   - **Paths to generated artifacts** — full paths to plan.md, todo.md, and findings.md
   - **Key architecture decisions** — summary of AD-IDs and their chosen approaches (from Steps 5-6)
   - **Resolved vs. open questions** — which Critical/Important unknowns were answered and which remain
   - **Top risks** — from the Risks & Mitigations table
   - **Three-Tier Boundaries** — Always/Ask First/Never rules (needed for every implementation task)
   - **Commands** — build, test, lint, dev server (needed for agent self-verification)
   - **Worktree mode** — enabled/disabled. If enabled, include worktree path and branch name
   - **Approval status** — whether the user has approved the plan (pending/approved). After
     `/clear`, this prevents accidental implementation without explicit approval

   The plan file must give enough context that a fresh session can read plan.md, todo.md,
   findings.md, and the plan file to begin implementation without any prior conversation history.

3. **Exit plan mode** — Use the `ExitPlanMode` tool to signal the plan is ready for review.

4. **Suggest adversarial validation** — Consider running `/stress-test` to adversarially
   validate this plan before implementation. This is optional but recommended for plans
   with unverified assumptions, external dependencies, or performance claims.

5. **Inform the user** — This is the ideal point to `/clear` context before starting
   implementation. After clearing, the implementation session should read the plan file
   first, then follow the "Using the Spec During Implementation" guidance below.

**This is a checkpoint, not a gate.** Users who do not want to clear context can proceed
directly to implementation approval without interruption.

### Step 10: Generate NEXT_SESSION_PROMPT.md

After the checkpoint, generate `NEXT_SESSION_PROMPT.md` so the user can start a fresh
implementation session by copy-pasting **one path** as the first message. This is the
final artifact of the planning phase.

**Location:** `.workspace/features/<feature-name>/NEXT_SESSION_PROMPT.md` (next to plan.md,
todo.md, findings.md). Always use the absolute path when printing it for the user.

**Template:**

````markdown
# Implementation Session — [Feature Name]

You are starting a fresh implementation session for the feature planned via the
spec-first workflow. Follow these steps in order. Do NOT write code until you
have completed Steps 1–4.

## Step 1: Read the planning artifacts (MANDATORY)

Read all of these files completely before doing anything else:

1. `[ABS_PATH]/plan.md`       — architecture decisions, boundaries, conformance
2. `[ABS_PATH]/todo.md`       — milestone-by-milestone task list
3. `[ABS_PATH]/findings.md`   — research output, gap analysis, rejected alternatives
4. `[ABS_PATH]/DESIGN.md`     — [INCLUDE ONLY IF THE DESIGN GATE RAN] chosen design
                                direction + UI acceptance criteria. The visual
                                reference is `[ABS_PATH]/design-alternatives.html` —
                                UI work MUST match the chosen direction; deviations
                                require updating DESIGN.md with the reason.

Confirm understanding by stating the feature name, the selected approach, and
the list of milestones from todo.md in one short paragraph before proceeding.

## Step 2: Worktree setup [INCLUDE ONLY IF WORKTREE MODE WAS ENABLED]

This feature was planned for isolated worktree development. Set up the worktree
before any other action.

a. Create the worktree and branch:
   ```bash
   git -C [BASE_REPO_PATH] worktree add [WORKTREE_PATH] -b [BRANCH_NAME]
   ```

b. Move into the worktree:
   ```bash
   cd [WORKTREE_PATH]
   ```

c. Install dependencies for each affected app (derived from plan.md):
   ```bash
   [FOR EACH AFFECTED APP, e.g.:]
   cd [WORKTREE_PATH]/apps/api && nvm use && yarn install
   cd [WORKTREE_PATH]/apps/web && nvm use && yarn install
   ```

d. Copy env files from the base repo for each affected app (do not commit them):
   ```bash
   [FOR EACH AFFECTED APP, e.g.:]
   cp [BASE_REPO_PATH]/apps/api/.env* [WORKTREE_PATH]/apps/api/ 2>/dev/null || true
   cp [BASE_REPO_PATH]/apps/web/.env* [WORKTREE_PATH]/apps/web/ 2>/dev/null || true
   ```

e. Verify the worktree environment is healthy:
   ```bash
   [FOR EACH AFFECTED APP, e.g.:]
   cd [WORKTREE_PATH]/apps/api && nvm use && yarn check:all
   cd [WORKTREE_PATH]/apps/web && nvm use && yarn check:all
   ```

If any check in step (e) fails, STOP and investigate. Do not proceed with
implementation until every affected app's check command (e.g. `yarn check:all`)
passes against the unchanged baseline.

## Step 3: Context summary

- **Feature:** [SHORT DESCRIPTION FROM STEP 1]
- **Selected approach:** [APPROACH NAME, OR "n/a (no brainstorm)"]
- **Milestones:**
  - M1: [NAME]
  - M2: [NAME]
  - [...]
- **Top risks:**
  - [RISK 1 + MITIGATION]
  - [RISK 2 + MITIGATION]
- **Open questions still requiring user input (if any):**
  - [QUESTION]

## Step 4: Mandatory rules during implementation

These are non-negotiable. **If you skip the per-milestone review gate, the
entire implementation is considered invalid and must be discarded.**

### Three-Tier Boundaries (from plan.md)

**ALWAYS:**
- [ALWAYS RULES FROM plan.md]

**ASK FIRST:**
- [ASK-FIRST RULES FROM plan.md]

**NEVER:**
- [NEVER RULES FROM plan.md]

### Per-milestone review gate (MANDATORY)

After completing all tasks of any milestone, before moving to the next one:

1. Run `/review-changes --light --fix`, then **wait for the subagent's completion
   notification without polling**: no `sleep`, `until`, or `for … git status` loops
   in Bash, no re-reading the working tree "to see if the fixes landed". End your
   turn if there is nothing independent to do; the notification wakes you. Do not
   edit the milestone's files while the gate runs (the subagent is fixing and
   committing them). Measured over 30 sessions, gate polling burned 4.2 hours of
   wall clock and ~280 requests at 450k context each.
2. The light subagent runs ONLY Agent 1A and MUST fix EVERY finding —
   CRITICAL, HIGH, MEDIUM, and LOW. Include this verbatim in the dispatch
   message to the subagent:

   > "This is a spec-first milestone gate. Override the default --fix severity
   > scope: you MUST apply fixes for every CRITICAL, HIGH, MEDIUM, and LOW
   > finding Agent 1A reports. The only findings you may leave unfixed are
   > those that objectively require human judgment (ambiguous correct fix,
   > public API contract change, architectural decision). Log those under
   > 'requires manual intervention' and flag them for the caller."

3. **Skipping this review INVALIDATES the entire implementation.** No
   exceptions. "Build passes" is not a review. "I'll review at the end" is not
   acceptable.
4. Commit the milestone only after the light review is clean.
5. Update `todo.md` immediately — check off `- [x]` completed tasks, add any
   new tasks discovered during implementation under the relevant milestone.

### Final review gate (after the last milestone)

1. Run `/review-changes` in FULL mode (Stage 1 spec compliance + all 4 Stage 2
   agents). Do NOT substitute with `--light`.
2. For EACH finding marked CRITICAL, HIGH, or MEDIUM:
   - **Verify it is a real issue, not a false positive.** Re-read the cited
     code. Confirm the failure mode the finding describes is actually
     reachable. If the finding is wrong, document why in one sentence and skip
     the fix.
   - If the finding is real, apply the fix.
3. After fixing the real findings, re-run `/review-changes` once more to
   confirm the issues are resolved.
4. The feature is NOT complete until the final review is clean.

### Commands (for self-verification)

- **Build:** `[BUILD CMD FROM plan.md]`
- **Test:** `[TEST CMD FROM plan.md]`
- **Lint:** `[LINT CMD FROM plan.md]`
- **Dev server:** `[DEV CMD FROM plan.md]`

## Step 5: Begin Milestone 1

Open `todo.md`, locate the first unchecked task under Milestone 1, and start
implementing. Implement task by task, in order. After every milestone, apply
the per-milestone review gate from Step 4. Do not touch Milestone N+1 until
Milestone N has been reviewed and committed.
````

**How to fill the template:**

- Replace `[ABS_PATH]` with the absolute path to the feature directory.
- Replace `[BASE_REPO_PATH]`, `[WORKTREE_PATH]`, `[BRANCH_NAME]` with the values
  confirmed in Step 1b. **If worktree mode was NOT enabled, omit Step 2 from
  the prompt entirely** (the implementation runs on the current branch in the
  base repo).
- Replace `[AFFECTED APPS]` with the concrete apps touched by the plan,
  detected during Step 2 research. Bake the install/copy/check commands inline
  — do not leave generic placeholders.
- Replace `[ALWAYS/ASK FIRST/NEVER RULES]` with the actual bullets from
  plan.md's Three-Tier Boundaries section (verbatim, not paraphrased).
- Replace `[BUILD/TEST/LINT/DEV CMD]` with the actual commands from plan.md's
  Commands section.
- Replace `[FEATURE NAME]`, milestones, risks, and open questions with the real
  values from plan.md / todo.md.

The goal is a self-contained prompt: a fresh session that reads ONLY this file
must have enough context to begin implementation correctly.

---

## Output Format

When this skill completes, print the output in two parts: first the artifact
summary, then the highlighted copyable path block as the **last visible
element of the response**.

**Part 1 — artifact summary (printed first):**

```
ARTIFACTS:
- plan.md                     ([path])
- todo.md                     ([path])
- findings.md                 ([path])
- design-alternatives.html    ([path])   ← only if the design gate ran
- DESIGN.md                   ([path])   ← only if the design gate ran
- NEXT_SESSION_PROMPT.md      ([path])
```

**Part 2 — highlighted copyable block (printed last, after everything else):**

```
════════════════════════════════════════════════════════════════
 NEXT SESSION PROMPT
════════════════════════════════════════════════════════════════

 [ABSOLUTE_PATH]/NEXT_SESSION_PROMPT.md

 Copy that path and paste it as the first message
 of a new session to start the implementation.
════════════════════════════════════════════════════════════════
```

The highlighted block MUST be the last visible element. The path inside the
block MUST be on its own line so terminal selection picks it up cleanly.

## After Generating

Present the generated artifacts with a brief summary of:

- Key architecture decisions and their rationale
- Top risks identified
- Open questions that need human input

Then wait. Do not proceed to implementation until the user explicitly approves the plan
or says to start coding. Remind the user that this is the ideal moment to `/clear` context
if the conversation has grown long — the plan checkpoint from Step 9 ensures all context
is preserved in the plan file, plan.md, todo.md, and findings.md.

**Living artifacts:** plan.md and todo.md are not frozen after creation. Update them
when discoveries emerge during implementation. If a decision changes or a risk
materializes, revise the relevant section and note the change date. For major rewrites,
ask the user whether to version the old file (e.g., plan-v1.md) before overwriting.

## Using the Spec During Implementation

This section is guidance for the **implementation phase after this skill completes**.
The spec-first skill itself only produces plan.md, todo.md, findings.md, and
NEXT_SESSION_PROMPT.md — it does not write code.

**If context was cleared:** Start by reading NEXT_SESSION_PROMPT.md (and the plan
file from Step 9) to recover artifact paths and key decisions, then read plan.md,
todo.md, and findings.md before beginning any task.

Beware the "curse of instructions" — research shows model adherence drops as the number
of simultaneous requirements grows. Do not dump the entire plan.md into a single
implementation prompt.

When implementing tasks from todo.md:

- Feed only the **relevant plan.md section(s)** + the **specific task and its subtasks**
- Each task prompt should be self-contained with just enough context to execute
- Always include **Three-Tier Boundaries** — those apply to every task
- Always include **Commands** — so the agent can verify its own work
- Reference applicable **Conformance Criteria** for the current task

### MANDATORY: /review-changes --light --fix After Every Milestone

**This is the security layer of the implementation. Skipping it invalidates all
development work done so far.** A milestone is not complete until it has been
reviewed by Agent 1A and **every finding has been fixed** — CRITICAL, HIGH,
MEDIUM, and LOW alike. Zero leftover findings is the bar for moving on.

**Override vs. default `--fix` behavior:** In the base `/review-changes --fix`
contract, auto-fix targets CRITICAL and HIGH only. Inside the spec-first
implementation flow, the light-mode milestone gate is STRICTER — the subagent
must fix **all severities**. This is non-negotiable: the whole point of the
light gate between milestones is to prevent 1A issues from compounding across
milestones, and a MEDIUM DRY violation or a LOW naming nit left behind in
Milestone 1 becomes architecture debt by Milestone 4.

**The milestone cycle:**

```
[Implement Milestone N tasks]
        |
        v
[Run /review-changes --light --fix]   (single Agent 1A subagent + ALL-severity fixes)
        |
        v
[Wait for its notification: NO polling, end the turn if idle]
        |
        v
[Subagent returns: report + commit SHAs]
        |
        v
[Commit any remaining milestone changes the subagent didn't commit]
        |
        v
[Proceed to Milestone N+1]
```

The wait step is not decoration: the gate subagent runs in the background and the
harness notifies you when it finishes. A `sleep`/`until` loop or a `git status` every
40 seconds re-enters the model with the whole context each time and finds nothing the
notification would not have told you. If you have independent work that does not touch
the files under review, do it; otherwise end the turn.

When dispatching the light review, include this verbatim in the subagent prompt:

> "This is a spec-first milestone gate. Override the default --fix severity
> scope: you MUST apply fixes for every CRITICAL, HIGH, MEDIUM, and LOW finding
> Agent 1A reports. The only findings you may leave unfixed are those that
> objectively require human judgment (ambiguous correct fix, public API contract
> change, architectural decision). Log those under 'requires manual intervention'
> and flag them for the caller."

### MANDATORY: Final /review-changes (FULL MODE) After All Milestones

After the last milestone is committed, run **`/review-changes`** — the full
two-stage review (Stage 1 + all 4 Stage 2 agents), NOT light mode — one final
time covering the entire implementation scope. This catches what the
per-milestone light reviews intentionally skipped:

- Stage 1 spec compliance against the original plan.md / todo.md
- Agent 1B (framework patterns, data integrity, transaction boundaries)
- Agent 2 (security, performance, observability)
- Agent 3 (Codex external cross-validation)

**The final review uses "verify before fix" semantics:**

For each CRITICAL, HIGH, or MEDIUM finding:

1. **Verify the finding is real, not a false positive.** Re-read the cited code.
   Confirm the failure mode the finding describes is actually reachable. If the
   finding is wrong, document why in one short sentence and skip the fix.
2. If the finding is real, apply the fix.
3. After fixing the real findings, re-run `/review-changes` to confirm.

**A feature is NOT complete until the final FULL review passes.** Do not create
a PR, mark the feature as done, or suggest the user ship it until this review
is clean. Do NOT substitute the final full review with `--light` — the point of
the final pass is the coverage the light mode intentionally skips.

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
7. **Skipping the plan checkpoint creation** — Always create the checkpoint (Step 9).
   The `/clear` afterward is optional, but creating the checkpoint is not — long spec
   conversations consume context, and without the checkpoint the user loses the ability
   to safely reset before implementation.
8. **Skipping brainstorm when it would help** — If the user's request is vague or open-ended,
   always run Step 0. Jumping straight to planning with an unclear direction wastes time
   on a plan that may need to be scrapped when the user realizes they wanted something different.
9. **Skipping NEXT_SESSION_PROMPT.md generation** — Step 10 is mandatory. Without it,
   the user has to manually reconstruct the implementation context after `/clear`, which
   defeats the purpose of the planning phase.
10. **Generic worktree commands in the prompt** — When worktree mode is enabled, the
    install/copy/check commands baked into NEXT_SESSION_PROMPT.md must be concrete
    (real app paths, real env files), not generic placeholders. The next session should
    not have to derive the commands.
11. **Skipping /review-changes between milestones** — Without per-milestone review, the
    implementation is invalid. "Build passes" is not a review. "I'll review at the end"
    compounds issues until they become unfixable.
12. **Blindly fixing all final-review findings** — The final `/review-changes` (FULL mode)
    can surface false positives. Verify each CRITICAL/HIGH/MEDIUM finding is real before
    fixing. Document false positives in one sentence and skip them.
13. **Skipping the design gate on a UI feature** — Step 5b is mandatory whenever the
    feature has a user-visible surface. Skipping it means design decisions happen
    implicitly during code generation and the user first sees the UI when it's already
    built — the exact process failure that produces generic, intention-free screens.
    "It's just a small table page" is not a skip reason.

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/spec-first/`
- **Checkpoint frequency:** After Steps 0 (brainstorm, if run), 2 (research), 5 (three-experts), 6 (plan.md), 7 (todo.md), 8 (findings.md)
- **Subagent delegation:** Parallel research threads (Step 2), three-experts deliberation (Step 5)

## Quality Checklist

Before delivering plan.md, todo.md, findings.md, and NEXT_SESSION_PROMPT.md, verify:

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
- [ ] Brainstorm step either ran (vague request) or was explicitly skipped (specific request)
- [ ] Design gate (Step 5b) ran for any UI-touching feature — design-alternatives.html +
      DESIGN.md generated, user picked a direction BEFORE plan.md was drafted; or the skip
      reason (no user-visible UI / bugfix restoring decided behavior) is recorded in
      findings.md — those are the ONLY valid skips
- [ ] If the design gate ran: plan.md has the Design Direction section, Conformance
      Criteria include the UI acceptance criteria, and NEXT_SESSION_PROMPT.md lists
      DESIGN.md + design-alternatives.html as mandatory reading
- [ ] findings.md generated with research output, brainstorm results, and discoveries
- [ ] Worktree mode detected from user invocation; if enabled, path + branch confirmed
- [ ] NEXT_SESSION_PROMPT.md generated at `.workspace/features/<feature>/NEXT_SESSION_PROMPT.md`
- [ ] If worktree mode enabled, Step 2 of NEXT_SESSION_PROMPT.md has CONCRETE install/copy/check
      commands per affected app (no generic placeholders)
- [ ] If worktree mode disabled, Step 2 of NEXT_SESSION_PROMPT.md is omitted entirely
- [ ] NEXT_SESSION_PROMPT.md includes the mandatory per-milestone `/review-changes --light --fix`
      gate with the ALL-severity override
- [ ] NEXT_SESSION_PROMPT.md includes the mandatory final `/review-changes` (FULL) gate with
      "verify CRIT/HIGH/MED are real before fixing"
- [ ] NEXT_SESSION_PROMPT.md has the real Three-Tier Boundaries and Commands inlined, not
      placeholders
- [ ] Checked for existing plan.md / todo.md / findings.md / NEXT_SESSION_PROMPT.md before writing
- [ ] Plan presented for user approval before any implementation
- [ ] Plan checkpoint written via EnterPlanMode/ExitPlanMode with artifact paths and key context
- [ ] Output ended with the highlighted "NEXT SESSION PROMPT" block containing the
      absolute path to NEXT_SESSION_PROMPT.md on its own line
- [ ] No implementation code was written — only plan.md, todo.md, findings.md, and
      NEXT_SESSION_PROMPT.md

---

## Feature Context Integration

When planning a named feature, this skill creates or resumes a `feature-context`:

1. **On init:** If no feature-context exists for this feature, create one via `/feature-context init <feature-name>`
2. **On resume:** If a feature-context already exists, resume it via `/feature-context resume <feature-name>`
3. **After planning:** Write the plan summary, architecture decisions, and milestone list to feature-context
4. **Data written:** plan.md, todo.md, findings.md and NEXT_SESSION_PROMPT.md paths (plus DESIGN.md
   when the design gate ran), AD-IDs, risk summary, milestone count
