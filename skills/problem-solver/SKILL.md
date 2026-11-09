---
name: problem-solver
description: |
  Structured engineering problem-solving and debugging orchestrator. Adaptive pipeline that
  detects task type (bug/debugging vs feature/implementation) and routes accordingly.
  For bugs: enforces root cause investigation with 4-phase systematic debugging before any fix.
  For features: 7-step pipeline from understanding through delivery.
  Invokes three-experts for architectural tradeoffs, multiple-iterations-reasoning for iterative
  dual-engine refinement, and escalates via circuit breaker when debugging stalls.
  Use this skill when asked to: problem solver, solve this, structured problem solving,
  step by step solution, engineering problem, debug this systematically, find and fix,
  root cause, solve step by step, systematic debugging, break this down and solve it,
  methodical solution, analyze and solve, work through this problem, diagnose and fix,
  structured debugging, solve this end to end, comprehensive solution, full problem solving
  workflow, tackle this problem, why is this broken, fix this bug, investigate this issue,
  trace this error, find the root cause, this stopped working, regression, intermittent failure,
  race condition, debug, RCA, root cause analysis, bisect, what changed, why does this fail.
version: 1.1.0
category: reasoning
depends: [three-experts, multiple-iterations-reasoning]
---

# Problem Solver

A master orchestrator for structured engineering problem-solving **and** systematic debugging.
Detects whether the task is a bug/debugging scenario or a feature/implementation scenario,
then routes through the appropriate pipeline — always grounded in evidence, never guessing.

## Three Iron Laws

These override everything else in this skill:

1. **No fix without root cause.** Never patch symptoms. Understand *why* before changing *what*.
2. **Evidence before claims.** Run the actual command, read the actual output, confirm the actual
   exit code before declaring anything done. Ban hedging language ("should work", "probably fixed").
3. **Smallest possible change.** Test hypotheses with minimal modifications. One variable at a time.

## Pipeline Overview

```
[1 Understand] → detect task type
      |
      |--[BUG]------> [1.5 Root Cause Investigation]
      |                    |
      |                    v (root cause found)
      |                    |
      |--[FEATURE]--+------+
      |             |
      v             v
[2 Decompose]
      |
      v
[3 Design] --(architectural tradeoffs?)--> [three-experts]
      |                                         |
      |--------------------<--------------------|
      v
[3.5 Plan Checkpoint] --(EnterPlanMode / write plan / ExitPlanMode)
      |                    User may /clear context here
      v
[4 Implement] --(complex/non-trivial?)--> [multiple-iterations-reasoning]
      |                                         |
      |--------------------<--------------------|
      v
[5 Test]
      |
      v
[6 Review]
      |
      v
[7 Deliver]
```

## Operating Rules

1. Follow steps in order unless blocked by missing context.
2. Keep context gathering focused (~8 searches max) before design.
3. Prefer evidence from code, tests, docs, configs, logs, and reproducible behavior.
4. State assumptions explicitly when evidence is incomplete.
5. Do not skip testing/review on code-changing tasks.
6. Invoke specialist skills only when decision criteria are met, not by default.
7. Deliver with a confidence rating and unresolved risks.
8. **For debugging:** Root cause investigation (Step 1.5) is mandatory before any fix attempt.
9. **Circuit breaker:** After 3 failed hypotheses in debugging, STOP and escalate to three-experts.
10. **Verification is not optional.** Every claim of "fixed" must include fresh evidence.

---

## Step 1: Understand

Build a grounded understanding of the problem before any solution work.

**What to do:**

1. **Restate the problem** — Write a 2-3 sentence summary of what needs to be solved,
   including the user's stated goal and any implicit constraints.

2. **Detect task type** — Classify the task:
   - **BUG / DEBUGGING** — Something worked before and stopped, unexpected behavior,
     error messages, performance degradation, intermittent failures, regressions.
     → Route to Step 1.5 (Root Cause Investigation) after this step.
   - **FEATURE / IMPLEMENTATION** — New capability, refactoring, enhancement, migration.
     → Skip Step 1.5, proceed to Step 2 (Decompose).
   - **AMBIGUOUS** — Ask the user: "Is this a bug to fix or a feature to build?"

3. **Explore the repository** — Use Glob, Grep, and Read to gather real context:
   - Check `CLAUDE.md`, `AGENTS.md`, `README.md`, `memory-bank/` for project conventions
   - Read config files (`package.json`, `tsconfig.json`, `pyproject.toml`, etc.)
   - Locate files, modules, and code paths relevant to the problem
   - Identify existing patterns, conventions, and constraints

4. **Build a context brief** — Compile findings into a structured summary:
   - Tech stack with versions
   - Relevant file paths (real, verified)
   - Existing patterns and conventions
   - Current state of the problem area
   - Known constraints (performance, security, compatibility)

5. **For bugs — additional context:**
   - **Reproduce the failure** — Run the failing command/test, capture the actual error output
   - **Isolate the failure point** — Narrow down to the specific file, function, and line
   - **Identify the delta** — What changed? Check `git log`, `git diff`, recent commits
   - **Capture the error signature** — Exact error message, stack trace, affected inputs

**Effort cap:** ~8 targeted searches. Gather enough to understand the landscape, then move on.

### Output Format

```
## Step 1: Understand

### Problem Statement
[2-3 sentence restatement of what needs solving]

### Task Type: [BUG | FEATURE]

### Context Brief
- **Stack:** [tech stack with versions]
- **Relevant files:** [list of real file paths]
- **Patterns:** [existing conventions in this area]
- **Constraints:** [known limitations or requirements]
- **Current state:** [what exists now, what's broken/missing]
- **Context confidence:** Low | Medium | High

### [BUG ONLY] Failure Evidence
- **Error signature:** [exact error message or behavior]
- **Reproduction:** [command/steps to reproduce]
- **Failure point:** [file:line where it breaks]
- **Delta:** [what changed — commit, config, dependency, environment]
```

---

## Step 1.5: Root Cause Investigation (DEBUGGING ONLY)

**This step is mandatory for BUG tasks. Skip for FEATURE tasks.**

Systematic 4-phase debugging that finds the actual root cause before any fix is attempted.
This prevents the common failure mode where agents try random fixes, waste tokens, and
compound the problem.

**Prerequisite:** The bug must be reproducible before entering Phase 2. If reproduction
fails after 2 attempts, document the reproduction gap and adjust: use log analysis,
post-mortem data, or code inspection as the primary evidence source instead of live testing.

### Phase 1: Categorize the Failure

Before categorizing, gather all available telemetry: application logs, error tracking
(Sentry/Datadog/etc.), monitoring dashboards, and recent deploy history. This raw data
informs which category to select.

Classify the bug into one of these root cause categories to guide investigation:

| Category | Signals | Investigation approach |
|---|---|---|
| **Regression** | "It used to work", recent deploy/merge | `git bisect`, diff recent commits, check CI |
| **State corruption** | Wrong data, unexpected values, stale cache | Trace data flow from source to symptom |
| **Race condition** | Intermittent, timing-dependent, works on retry | Check async paths, shared state, concurrency |
| **Config drift** | Works in one env but not another | Diff configs, env vars, versions across environments |
| **Dependency change** | After upgrade, new lockfile, changed API | Check lockfile diff, dependency changelogs, API changes |
| **Edge case** | Specific inputs trigger the bug | Map input space, find the boundary condition |

### Phase 2: Pattern Analysis

Compare working vs broken states to narrow the root cause:

1. **Working reference** — Find a state where the behavior was correct:
   - Last known good commit (`git log`, `git bisect`)
   - Working environment or config
   - Passing test case with similar logic
   - Adjacent code that handles a similar case correctly

2. **Diff analysis** — Compare working vs broken:
   - Code diff between good and bad states
   - Config/environment differences
   - Data/input differences
   - Dependency version differences

3. **Narrow the scope** — Each comparison should halve the search space.
   After this phase, you should know the **specific subsystem** where the root cause lives.

### Phase 3: Hypothesis Testing

Form and test hypotheses about the root cause, one at a time:

1. **Form a hypothesis** — Based on Phase 2 evidence, state a specific, falsifiable hypothesis:
   - "The bug is caused by [specific mechanism] in [specific location]"
   - Not "something is wrong with the auth system" — too vague

2. **Design the smallest test** — What is the minimal change or observation that would
   confirm or refute this hypothesis?
   - Add a single log statement
   - Change one variable
   - Run with one different input
   - Comment out one block

3. **Execute and observe** — Run the test, capture the output, compare with prediction.

4. **Record the result** — Log the hypothesis and outcome:
   ```
   Hypothesis #N: [statement]
   Test: [what you did]
   Expected: [what you predicted]
   Actual: [what happened]
   Verdict: CONFIRMED | REFUTED | INCONCLUSIVE
   ```

5. **Iterate or escalate:**
   - **CONFIRMED** → Root cause found. Proceed to Step 2 with the root cause as input.
   - **REFUTED** → Form next hypothesis based on new evidence.
   - **INCONCLUSIVE** → Refine the test to be more discriminating.

6. **Clean up** — After each REFUTED or INCONCLUSIVE test, revert the test change
   before forming the next hypothesis. Never stack test modifications.

### Circuit Breaker: 3-Failure Escalation

**After 3 refuted or inconclusive hypotheses, STOP debugging and escalate:**

1. Compile all evidence gathered so far (failure signature, pattern analysis, hypothesis log)
2. Invoke `/three-experts` with the debugging context and ask:
   - "Given these 3 failed hypotheses and the evidence, what root cause categories haven't we explored?"
   - "Is the architecture itself the problem? Should we question assumptions?"
3. Use the expert deliberation to form the next hypothesis or pivot the investigation entirely.

This circuit breaker prevents the common failure mode of trying endless random approaches.

### Phase 4: Root Cause Statement

Once confirmed, write a precise root cause statement:

```
## Root Cause

**What:** [specific mechanism causing the bug]
**Where:** [exact file:line or component]
**Why:** [why this code/config is wrong — the logical error]
**When introduced:** [commit, date, or event that introduced it]
**Impact scope:** [what else might be affected by the same root cause]
```

**Only after writing the root cause statement, proceed to Step 2.**

---

## Step 2: Decompose

Break the problem into manageable sub-problems and map their relationships.

**What to do:**

1. **Identify sub-problems** — List every distinct piece of work needed to solve the
   full problem. Each sub-problem should be independently describable.
   - **For bugs:** The first sub-problem is always "fix the root cause" (from Step 1.5).
     Additional sub-problems may include: regression tests, fixing related occurrences,
     cleanup of workarounds.

2. **Map dependencies** — Which sub-problems must be solved before others? Which are
   independent and parallelizable?

3. **Classify each sub-problem:**
   - **Straightforward** — Clear solution path, no meaningful alternatives to weigh.
   - **Tradeoff** — Multiple viable approaches with different cost/benefit profiles.
     These are candidates for expert deliberation in Step 3.

4. **Estimate complexity** — For each sub-problem, rate as Simple / Moderate / Complex.
   This drives decisions about which skills to invoke later.

### Output Format

```
## Step 2: Decompose

### Sub-problems
1. [Sub-problem] — [Straightforward/Tradeoff] — [Simple/Moderate/Complex]
2. [Sub-problem] — [Straightforward/Tradeoff] — [Simple/Moderate/Complex]

### Dependency Map
- SP-1 -> SP-2 (SP-2 depends on SP-1's output)
- SP-3 is independent, can run in parallel

### Tradeoff Sub-problems (candidates for expert deliberation)
- SP-N: [Why this has meaningful tradeoffs worth deliberating]
```

---

## Step 3: Design

Produce the design for each sub-problem. Route complex tradeoffs to expert deliberation.

### Decision: When to Invoke Three-Experts

Invoke `/three-experts` with the design question and repository context when **any** of
these conditions are true:

- The sub-problem has **2+ viable approaches** with meaningfully different tradeoff profiles
- The decision **commits the project** to a pattern that is expensive to reverse
- The problem **spans multiple concerns** (e.g., performance vs. security vs. maintainability)
- **Cross-cutting impact** on security, performance, reliability, data model, or API contracts
- You are **uncertain** which approach is better after initial analysis
- The sub-problem was classified as **Tradeoff + Complex** in Step 2
- **Debugging escalation:** The circuit breaker fired in Step 1.5

**Skip three-experts** when:

- There is a single obvious solution that follows existing project conventions
- The sub-problem was classified as **Straightforward** regardless of complexity
- The decision is easily reversible (low commitment, low blast radius)
- An established pattern already exists in the codebase for this exact case

### For Sub-problems Requiring Deliberation

Invoke `/three-experts` with:
- The specific design question
- The repository context from Step 1
- The dependency constraints from Step 2
- Any constraints that the solution must satisfy
- **For bugs:** Include the root cause statement and hypothesis log from Step 1.5

Take the recommendation and implementation approach from the three-experts output
as the design for that sub-problem.

### For Straightforward Sub-problems

Design directly:
- State the chosen approach
- Reference the existing pattern or convention it follows
- Note any constraints it satisfies

### Output Format

```
## Step 3: Design

### SP-1: [Name]
**Approach:** [chosen design]
**Rationale:** [why this approach, referencing conventions or expert deliberation]
**Key decisions:** [important implementation choices]

### SP-2: [Name] (via three-experts deliberation)
**Approach:** [recommendation from three-experts]
**Expert consensus:** [brief summary of deliberation outcome]
**Tradeoffs accepted:** [what we're giving up]
```

---

## Step 3.5: Plan Checkpoint

Pause the pipeline and write a self-contained plan so the user can optionally clear context
before implementation begins.

**What to do:**

1. **Enter plan mode** — Use the `EnterPlanMode` tool to signal the start of a plan checkpoint.

2. **Write the plan file** — Consolidate ALL outputs from Steps 1-3 into the plan file:
   - **Problem statement** (from Step 1)
   - **Task type** — BUG or FEATURE (from Step 1)
   - **Context brief** — stack, relevant files, patterns, constraints, current state (from Step 1)
   - **[BUG] Root cause statement** — full root cause with evidence chain (from Step 1.5)
   - **[BUG] Hypothesis log** — all hypotheses tested with outcomes (from Step 1.5)
   - **Sub-problems** with classifications and complexity ratings (from Step 2)
   - **Dependency map** between sub-problems (from Step 2)
   - **Design decisions** for every sub-problem, including three-experts output if invoked (from Step 3)
   - **Success criteria** — expected outcomes and acceptance criteria per sub-problem,
     so Step 5 (Test) can verify correctness even after context reset
   - **Verification commands** — exact commands to run to prove the fix/feature works
   - **Implementation handoff** — for each sub-problem, note whether it qualifies for
     multiple-iterations-reasoning based on Step 2 complexity classification, and include
     a "Next: Step 4 Implement" section so execution can resume without prior chat context

   The plan file must be **complete enough that Steps 4-7 can execute from it alone**,
   without access to any prior conversation context.

3. **Exit plan mode** — Use the `ExitPlanMode` tool to signal the plan is ready for review.

4. **Inform the user** — Let them know this is the ideal point to `/clear` context if needed.
   If they choose to clear, Step 4 will re-read the plan file to resume. If they choose not
   to clear, simply continue to Step 4 as normal.

**This is a checkpoint, not a gate.** Users who do not want to clear context can proceed
directly to Step 4 without interruption.

---

## Step 4: Implement

Write the solution code or artifact based on the designs from Step 3.

### Decision: When to Invoke Multiple-Iterations-Reasoning

Invoke `/multiple-iterations-reasoning` with the implementation for iterative dual-engine
refinement when **any** of these conditions are true:

- The implementation is **Moderate or Complex** (from Step 2 classification)
- The solution involves **algorithmic logic** that benefits from edge-case hardening
- The code has **multiple interacting parts** that could harbor subtle bugs
- **Correctness is critical** — errors would be costly or hard to detect later
- High **security or performance sensitivity**
- **Multi-file refactor** with regression risk
- The implementation is **>50 lines** of non-trivial logic

**Skip multiple-iterations** when:

- The implementation is a **Simple** configuration change, import, or one-liner
- The change follows a **direct template** from existing code (copy-adapt pattern)
- The implementation is **purely declarative** (e.g., adding a route, config entry)
- Total implementation is **<20 lines** of straightforward code
- Behavior is already **strongly covered by tests**

### Implementation Process

1. **Load context if needed** — If context was cleared after Step 3.5, read the plan file
   to recover the problem statement, context brief, sub-problems, dependency map, and design
   decisions before proceeding.
2. **Write the initial implementation** for each sub-problem, following the design from Step 3
3. **For non-trivial implementations:** Invoke `/multiple-iterations-reasoning` with the
   implementation code and the quality criteria it must meet
4. **Take the final solution** from the iterations skill's Phase 3 output
5. **For bugs:** Apply the fix to the root cause location identified in Step 1.5.
   Do NOT apply the fix elsewhere until the root cause fix is verified.

### Output Format

```
## Step 4: Implement

### SP-1: [Name]
[Implementation code or artifact]
*Refinement: [Iterated via multiple-iterations-reasoning / Direct implementation]*

### SP-2: [Name]
[Implementation code or artifact]
*Refinement: [Iterated via multiple-iterations-reasoning / Direct implementation]*
```

---

## Step 5: Test

Verify the implementation against requirements, edge cases, and constraints.
**This step enforces the "Evidence Before Claims" iron law.**

**What to do:**

1. **Run existing tests** — Execute the project's test suite to check for regressions.
   Capture the actual output and exit code. Do not summarize — show evidence.

2. **For bugs — verify the fix:**
   - Re-run the exact reproduction steps from Step 1
   - Confirm the error no longer occurs (show the passing output)
   - Verify the root cause is actually fixed, not masked

3. **Write targeted tests** — For new functionality, write tests covering:
   - Happy path (main use case works)
   - Edge cases (empty inputs, boundaries, nulls, overflow)
   - Error cases (invalid inputs, failures, timeouts)
   - Integration points (does it work with adjacent components?)
   - **For bugs:** Write a regression test that would have caught this bug

4. **Verify constraints** — Check each constraint from Step 1:
   - Performance: measure if relevant (time, memory, query count)
   - Security: check for injection, auth bypass, data exposure
   - Compatibility: verify against stated requirements

5. **Verification evidence** — For every claim, include the actual command run and its output.

### Output Format

```
## Step 5: Test

### Verification Evidence
- Command: `[exact command]`
- Exit code: [0/1/etc]
- Output: [relevant output lines]

### Test Results
- Existing tests: [PASS/FAIL — details if fail]
- New tests written: [count and what they cover]
- Regression test: [for bugs — what it covers]
- Edge cases verified: [list]

### Constraint Verification
- [Constraint]: [Met/Not met — evidence]

### Issues Found
- [Issue — severity — fix applied or deferred]
```

---

## Step 6: Review

Final quality audit before delivery.

### Quality Checklist

| Category | Check |
|---|---|
| **Correctness** | Solves the stated problem? |
| **Correctness** | All edge cases handled? |
| **Correctness** | Error paths handled gracefully? |
| **Root Cause** | [BUG] Fix addresses root cause, not symptoms? |
| **Root Cause** | [BUG] No other instances of the same bug pattern? |
| **Security** | No hardcoded secrets, tokens, or credentials? |
| **Security** | Input validation present where needed? |
| **Security** | No injection, XSS, or path traversal risks? |
| **Performance** | No unnecessary loops, redundant queries, or O(n^2) traps? |
| **Performance** | Resource cleanup (connections, file handles, listeners)? |
| **DRY** | No duplicated logic that should be extracted? |
| **DRY** | Existing utilities/helpers used where applicable? |
| **Conventions** | Follows project naming, structure, and patterns? |
| **Conventions** | Consistent with surrounding code style? |
| **Observability** | Logs/errors/metrics adequate for diagnosing future issues? |
| **Operational** | Rollback/feature-flag strategy if needed? |
| **Evidence** | All claims of "working" backed by fresh verification output? |

### Review Process

1. Walk through the checklist systematically
2. For any failing item, fix the issue immediately
3. If a fix introduces risk, note it in the delivery

### Output Format

```
## Step 6: Review

### Quality Audit
[Completed checklist with pass/warn/fail per item]

### Issues Fixed During Review
- [Issue] — [Fix applied]

### Risks Accepted
- [Risk — why accepted — mitigation]
```

---

## Step 7: Deliver

Present the complete solution with full transparency on quality and confidence.

### Output Format

```
## Step 7: Deliver

### Solution
[Complete, self-contained solution. Directly usable without reading prior steps.]

### What Was Done
[3-5 bullet summary of what changed and why]

### [BUG] Root Cause Summary
- **Cause:** [one-sentence root cause]
- **Fix:** [one-sentence fix description]
- **Regression test:** [what test prevents recurrence]

### Skills Invoked
- three-experts: [Yes — for which sub-problem / No — why skipped]
- multiple-iterations-reasoning: [Yes — for which implementation / No — why skipped]
- [BUG] Circuit breaker fired: [Yes — at hypothesis #N / No]

### Confidence: [High / Medium / Low]
[Brief justification referencing test results and review findings]

| Level | Meaning |
|---|---|
| **High** | Correct, tested, all requirements met, edge cases handled. Production-ready. |
| **Medium** | Likely correct for main cases. Some edge cases may need validation. |
| **Low** | Addresses core problem but has known gaps. Strong starting point. |

### Verification Evidence
[The exact commands and outputs that prove the solution works]

### Known Limitations
- [Limitation or "None identified"]

### Follow-up Recommendations
- [Optional: things to watch, future improvements, or validations the user should do]
```

---

## Behavioral Rules

Rules 1-3 (Iron Laws) and debugging-specific rules are embedded in steps above. These additional rules govern overall behavior:

1. **Invoke skills at the right moment, not reflexively.** Use three-experts for real
   tradeoffs, not obvious decisions. Use multiple-iterations for non-trivial code, not
   config changes. The decision criteria exist — follow them.
2. **Ground everything in real code.** File paths, existing patterns, actual constraints.
   Abstract reasoning disconnected from the codebase is not useful.
3. **Each step must produce output.** No silent steps. The user should follow the full reasoning chain.
4. **Fix issues when found, not later.** If Step 5 or 6 reveals a problem, fix it before proceeding.
5. **Be honest about confidence.** "Medium" with clear limitations beats a false "High".
6. **Respect existing conventions.** Follow them unless the problem requires deviation, and document why.
7. **Adapt the pipeline to problem scale.** For simple problems, compress steps. The pipeline serves the solution.
8. **Self-contained delivery.** Step 7 must be usable without reading Steps 1-6.
9. **Context preservation.** The plan file in Step 3.5 must be fully self-contained for post-clear execution.

---

## Handling Special Cases

- **Refactoring:** Decompose into independent moves. Design target architecture (likely needs three-experts). Implement incrementally — each move should leave tests passing.
- **Performance:** Treat as BUG — root cause is "why is it slow?" Profile and capture baseline metrics before optimizing. Verify with benchmarks, not intuition.
- **Greenfield:** Consider `/spec-first` for planning-heavy work. Use problem-solver when the feature is well-defined and needs execution, not discovery.

---

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/problem-solver/`
- **Checkpoint frequency:** After each step (1-7), especially at Step 3.5 plan checkpoint
- **Subagent delegation:** Three-experts deliberation (Step 3), multiple-iterations-reasoning (Step 4), test execution (Step 5)
- **Hypothesis log persistence:** For debugging, write hypotheses to scratchpad after each test to survive context compaction

## Quick Reference

```
[1]   UNDERSTAND       ->  ~8 targeted searches, context brief, detect BUG vs FEATURE
[1.5] ROOT CAUSE       ->  [BUG ONLY] categorize → pattern analysis → hypothesis test → root cause statement
      (circuit breaker) ->  3 failed hypotheses → escalate to /three-experts
[2]   DECOMPOSE        ->  Sub-problems, dependencies, tradeoff classification
[3]   DESIGN           ->  /three-experts if tradeoffs, direct if straightforward
[3.5] PLAN CHECKPOINT  ->  EnterPlanMode, write plan, ExitPlanMode (user may /clear)
[4]   IMPLEMENT        ->  /multiple-iterations-reasoning if non-trivial, direct if simple
[5]   TEST             ->  Run tests, edge cases, constraint verification, SHOW EVIDENCE
[6]   REVIEW           ->  Quality checklist audit (17 checks)
[7]   DELIVER          ->  Complete solution + confidence + limitations + evidence
```
