---
name: problem-solver
description: |
  Structured engineering problem-solving orchestrator. 7-step pipeline from understanding
  through decomposition, design, implementation, testing, review, and delivery. Invokes
  three-experts for architectural tradeoffs and multiple-iterations-reasoning for iterative
  dual-engine refinement. Use this skill when asked to: problem solver, solve this,
  structured problem solving, step by step solution, engineering problem, debug this
  systematically, find and fix, root cause, solve step by step, systematic debugging,
  break this down and solve it, methodical solution, analyze and solve, work through
  this problem, diagnose and fix, structured debugging, solve this end to end,
  comprehensive solution, full problem solving workflow, tackle this problem.
version: 1.0.0
category: reasoning
depends: [three-experts, multiple-iterations-reasoning]
---

# Problem Solver

A master orchestrator for structured engineering problem-solving. Breaks complex problems
into a 7-step pipeline that leverages specialized skills at the right moments: `three-experts`
for architectural deliberation and `multiple-iterations-reasoning` for iterative dual-engine
refinement.

## Why This Exists

Ad-hoc problem solving skips steps. Engineers jump to implementation without understanding
constraints, miss edge cases because they never decomposed the problem, or ship first-draft
code that needed iteration. This skill enforces a disciplined pipeline that mirrors how
senior engineers think — understand first, decompose, design with tradeoffs in mind,
implement with refinement, test thoroughly, review critically, then deliver with confidence.

## Pipeline Overview

```
[1 Understand]
      |
      v
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

---

## Step 1: Understand

Build a grounded understanding of the problem before any solution work.

**What to do:**

1. **Restate the problem** — Write a 2-3 sentence summary of what needs to be solved,
   including the user's stated goal and any implicit constraints.

2. **Explore the repository** — Use Glob, Grep, and Read to gather real context:
   - Check `CLAUDE.md`, `AGENTS.md`, `README.md`, `memory-bank/` for project conventions
   - Read config files (`package.json`, `tsconfig.json`, `pyproject.toml`, etc.)
   - Locate files, modules, and code paths relevant to the problem
   - Identify existing patterns, conventions, and constraints

3. **Build a context brief** — Compile findings into a structured summary:
   - Tech stack with versions
   - Relevant file paths (real, verified)
   - Existing patterns and conventions
   - Current state of the problem area
   - Known constraints (performance, security, compatibility)

**Effort cap:** ~8 targeted searches. Gather enough to understand the landscape, then move on.

### Output Format

```
## Step 1: Understand

### Problem Statement
[2-3 sentence restatement of what needs solving]

### Context Brief
- **Stack:** [tech stack with versions]
- **Relevant files:** [list of real file paths]
- **Patterns:** [existing conventions in this area]
- **Constraints:** [known limitations or requirements]
- **Current state:** [what exists now, what's broken/missing]
- **Context confidence:** Low | Medium | High
```

---

## Step 2: Decompose

Break the problem into manageable sub-problems and map their relationships.

**What to do:**

1. **Identify sub-problems** — List every distinct piece of work needed to solve the
   full problem. Each sub-problem should be independently describable.

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
   - **Context brief** — stack, relevant files, patterns, constraints, current state (from Step 1)
   - **Sub-problems** with classifications and complexity ratings (from Step 2)
   - **Dependency map** between sub-problems (from Step 2)
   - **Design decisions** for every sub-problem, including three-experts output if invoked (from Step 3)
   - **Success criteria** — expected outcomes and acceptance criteria per sub-problem,
     so Step 5 (Test) can verify correctness even after context reset
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

**What to do:**

1. **Run existing tests** — Execute the project's test suite to check for regressions.

2. **Write targeted tests** — For new functionality, write tests covering:
   - Happy path (main use case works)
   - Edge cases (empty inputs, boundaries, nulls, overflow)
   - Error cases (invalid inputs, failures, timeouts)
   - Integration points (does it work with adjacent components?)

3. **Verify constraints** — Check each constraint from Step 1:
   - Performance: measure if relevant (time, memory, query count)
   - Security: check for injection, auth bypass, data exposure
   - Compatibility: verify against stated requirements

4. **Manual verification** — For UI or behavioral changes, describe how to manually verify.

### Output Format

```
## Step 5: Test

### Test Results
- Existing tests: [PASS/FAIL — details if fail]
- New tests written: [count and what they cover]
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
| **Security** | No hardcoded secrets, tokens, or credentials? |
| **Security** | Input validation present where needed? |
| **Security** | No injection, XSS, or path traversal risks? |
| **Performance** | No unnecessary loops, redundant queries, or O(n^2) traps? |
| **Performance** | Resource cleanup (connections, file handles, listeners)? |
| **DRY** | No duplicated logic that should be extracted? |
| **DRY** | Existing utilities/helpers used where applicable? |
| **Conventions** | Follows project naming, structure, and patterns? |
| **Conventions** | Consistent with surrounding code style? |
| **Observability** | Logs/errors/metrics adequate? |
| **Operational** | Rollback/feature-flag strategy if needed? |

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

### Skills Invoked
- three-experts: [Yes — for which sub-problem / No — why skipped]
- multiple-iterations-reasoning: [Yes — for which implementation / No — why skipped]

### Confidence: [High / Medium / Low]
[Brief justification referencing test results and review findings]

| Level | Meaning |
|---|---|
| **High** | Correct, tested, all requirements met, edge cases handled. Production-ready. |
| **Medium** | Likely correct for main cases. Some edge cases may need validation. |
| **Low** | Addresses core problem but has known gaps. Strong starting point. |

### Known Limitations
- [Limitation or "None identified"]

### Follow-up Recommendations
- [Optional: things to watch, future improvements, or validations the user should do]
```

---

## Behavioral Rules

1. **Never skip Step 1.** Understanding before action. A wrong mental model produces
   wrong solutions regardless of implementation quality.

2. **Decompose before designing.** Step 2 before Step 3, always. Monolithic solutions
   hide complexity and miss edge cases.

3. **Invoke skills at the right moment, not reflexively.** Use three-experts for real
   tradeoffs, not obvious decisions. Use multiple-iterations for non-trivial code, not
   config changes. The decision criteria exist — follow them.

4. **Ground everything in real code.** File paths, existing patterns, actual constraints.
   Abstract reasoning disconnected from the codebase is not useful.

5. **Each step must produce output.** No silent steps. The user should be able to follow
   the reasoning chain from understanding to delivery.

6. **Fix issues when found, not later.** If Step 5 or 6 reveals a problem, fix it
   before proceeding. Do not defer known bugs to the user.

7. **Be honest about confidence.** A "Medium" confidence with clear limitations is more
   valuable than a false "High". Surface uncertainty — don't hide it.

8. **Respect existing conventions.** The project has patterns for a reason. Follow them
   unless the problem specifically requires deviation, and document why.

9. **Adapt the pipeline to problem scale.** For truly simple problems (single file fix,
   clear bug with obvious cause), compress Steps 2-3 into a brief note and proceed.
   The pipeline serves the solution, not the other way around.

10. **Self-contained delivery.** Step 7 must be usable without reading Steps 1-6.

11. **Context preservation at checkpoints.** The plan file written in Step 3.5 must be
    fully self-contained. If the user clears context after the checkpoint, every subsequent
    step must be executable from the plan file alone — no implicit knowledge from earlier
    conversation turns.

---

## Handling Special Cases

**Bug Debugging / Root Cause Analysis:**
- Step 1: Focus on reproducing the bug and locating the failure point
- Step 2: Decompose into "find root cause" and "fix root cause" sub-problems
- Step 3: Design the fix (may need three-experts if multiple fix strategies exist)
- Step 5: Verify the bug is fixed AND no regressions introduced

**Refactoring:**
- Step 1: Understand what exists and why it was built that way
- Step 2: Decompose into independent refactoring moves (extract, rename, restructure)
- Step 3: Design the target architecture (likely needs three-experts)
- Step 4: Implement incrementally — each move should leave tests passing

**Performance Problems:**
- Step 1: Profile and measure before optimizing
- Step 2: Decompose into bottlenecks (ranked by impact)
- Step 4: Implement fixes with before/after measurements
- Step 5: Verify improvements with benchmarks, not intuition

**Greenfield / New Feature:**
- Consider whether `/spec-first` is more appropriate for planning-heavy work
- Use problem-solver when the feature is well-defined and needs execution, not discovery

---

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/problem-solver/`
- **Checkpoint frequency:** After each step (1-7), especially at Step 3.5 plan checkpoint
- **Subagent delegation:** Three-experts deliberation (Step 3), multiple-iterations-reasoning (Step 4), test execution (Step 5)

## Quick Reference

```
[1]   UNDERSTAND       ->  ~8 targeted searches, context brief
[2]   DECOMPOSE        ->  Sub-problems, dependencies, tradeoff classification
[3]   DESIGN           ->  /three-experts if tradeoffs, direct if straightforward
[3.5] PLAN CHECKPOINT  ->  EnterPlanMode, write plan, ExitPlanMode (user may /clear)
[4]   IMPLEMENT        ->  /multiple-iterations-reasoning if non-trivial, direct if simple
[5]   TEST             ->  Run tests, edge cases, constraint verification
[6]   REVIEW           ->  Quality checklist audit (14 checks)
[7]   DELIVER          ->  Complete solution + confidence + limitations
```
