---
name: multiple-iterations-reasoning
description: >
  Iterative reasoning and progressive refinement skill with dual-engine validation.
  Guides AI through multiple rounds of self-improvement using Claude analysis and
  Codex cross-validation when solving complex problems. Use this skill when asked to:
  iterate on this, improve this solution, multiple iterations, reasoning iterations,
  self-improve, progressive refinement, iterative reasoning, refine this, make this
  better through iterations, analyze and improve, self-critique this solution, keep
  improving, iterate and refine, reason step by step and improve, do multiple passes,
  revise and enhance, critically evaluate and redo, rethink this, polish this
  solution, run improvement rounds, multi-round analysis, sharpen this solution,
  progressively enhance, self-review and fix, critique and iterate, optimize through
  iteration, reflect and revise, improve iteratively, redo with improvements, layered
  reasoning, successive refinement, incremental enhancement, converge on best solution,
  strengthen this answer, revise in rounds, make it better, dual engine iteration,
  claude and codex, cross-validate, dual engine refinement, codex validation,
  two engine iteration, cross-engine critique
version: 1.0.0
category: reasoning
depends: []
---

# Multiple Iterations Reasoning

Structured iterative reasoning workflow with dual-engine validation. When activated, work
through the problem in distinct phases: produce an initial solution, refine it through
multiple critical rounds with quality gates and Codex cross-validation, and deliver a final
polished result.

Default: **3 refinement rounds**, with adaptive early stop or extension up to 6.

**Dual-Engine Mode:** Each refinement round sends the current solution and Claude's critique
to Codex CLI for independent validation. This catches blind spots that single-model analysis
misses. If Codex CLI is unavailable, the skill falls back to Claude-only mode seamlessly.

**When NOT to use:** Trivial factual Q&A, one-shot transformations, or simple
lookups where iteration adds no value. If the user wants speed on a straightforward
task, do a single pass unless they explicitly request iterations.

---

## Phase 1 — Initial Solution

Produce a concise first-pass solution. The goal is correctness and coverage of
core requirements, not perfection.

### Guidelines by Task Type

- **Code tasks:** Write minimal working code that satisfies the primary
  requirements. Prefer clarity over cleverness. Skip optimizations.
- **Design tasks:** Outline the architecture — components, responsibilities,
  and key interactions. Do not flesh out every detail yet.
- **Analysis tasks:** State the core answer or recommendation with brief
  supporting reasoning.
- **Problem-solving tasks:** Provide a direct solution addressing the main
  constraints.

### State Assumptions

Before moving to refinement, explicitly list every assumption made. Number them.
These become inputs for the critique rounds.

### Output Format

```
## PHASE 1 — Initial Solution

[Solution content]

### Assumptions
1. [Assumption]
2. [Assumption]
```

### Socratic Decomposition (optional, recommended for math/logic/multi-step)

Optional checkpoint after Phase 1: decompose the initial solution into verifiable
(sub-question, sub-answer) pairs before moving to Phase 2. Each pair should be
independently checkable with explicit evidence/tests when possible. This makes
Phase 2 critiques more precise because weaknesses can be traced to specific
sub-steps rather than the whole solution.

```
### Decomposition
- Q1: [sub-question] → A1: [sub-answer] ✓/✗
- Q2: [sub-question] → A2: [sub-answer] ✓/✗
```

---

## Phase 2 — Iterative Refinement (Dual-Engine)

Perform **3 rounds by default**. This count is adaptive — see quality gate
rules for early stopping or extension.

### Each Round Structure

> **History Awareness:** Each round must reference and build on insights from
> prior rounds. Do not repeat analysis already covered — if a strength or
> weakness was noted in Round N-1, only mention it again if its status changed.
> Start each round with a 1-line delta from Round N-1 (what changed, what did not).
> This prevents redundant iterations and keeps each round focused on new insight.

#### a) Critical Analysis (Claude)

Evaluate the current solution honestly:

**Strengths** (up to 3 — only list genuine ones):
- What works well? What is correct, elegant, or robust?
- What requirements are solidly met?

**Weaknesses** (up to 3 — localized, actionable; not filler):
- Each weakness must pinpoint WHERE in the solution the issue is (specific
  section, line, step, or component), cite the exact claim/operation that fails,
  and state WHAT specifically to change.
- What is fragile, incorrect, or incomplete?
- What edge cases are missed?
- What assumptions from Phase 1 are questionable or invalidated?

**Improvement Opportunities** (1–2 actionable items):
- Each must be specific and implementable in this round.
- Prioritize by impact: correctness > performance > readability > style.
- Do NOT list vague ideas. State exactly what to change and why.

**Assumptions Status** (update from Phase 1 list):
- Note any assumptions validated, revised, or invalidated by this round's analysis.
- Skip this section if no assumption status changed.

#### b) Codex Validation

Send the current solution and Claude's critical analysis to Codex CLI for independent
critique. Codex reviews with fresh eyes, catching issues Claude may have missed.

**Pre-check:** Verify Codex is available: `command -v codex >/dev/null 2>&1`
If Codex is NOT available, skip to the **Fallback** below.

**How to invoke (when Codex is available):**

**Security: NEVER interpolate dynamic content (solutions, critiques) into shell command strings.**
Always use a single-quoted heredoc to prevent shell expansion:

```bash
cat <<'PROMPT_EOF' | codex -a never exec -
Review the following solution and the critique of it. Independently identify any
issues, bugs, edge cases, or improvements that the critique may have MISSED. Focus on
correctness, robustness, and subtle errors. Do NOT repeat issues already identified —
only add NEW findings.

=== CURRENT SOLUTION ===
<current solution>

=== CRITIQUE ===
<critical analysis from step (a)>

Respond with:
1. NEW issues not in the critique (if any)
2. Disagreements with the assessment (if any)
3. Validation of findings you agree with (brief)
PROMPT_EOF
```

**Important:** `-a` is a global flag — it must come before `exec`, not after.

**Parsing Codex output:**
- Extract new issues Codex found that Claude missed
- Note any disagreements between the two engines
- Record agreements (these are high-confidence findings)

**Fallback:** If Codex CLI is unavailable, errors out, or times out:
- Log: `"Codex unavailable — running in single-engine mode."`
- Skip this step and proceed to the Quality Gate with Claude-only analysis
- Do NOT block the workflow or retry more than once

#### c) Quality Gate

Before refining, evaluate based on findings from both engines:

| Condition | Action |
|---|---|
| No weaknesses with real functional impact (from either engine) | **Stop early.** Proceed to Phase 3. |
| All weaknesses are minor style/naming issues | **Stop early.** Note minor items in final solution. |
| Fundamental flaw discovered (wrong algorithm, violated constraint) | **Extend.** Continue past 3 rounds, up to 6 max. |
| Normal weaknesses with clear fixes | **Continue.** Apply improvements in step (d). |
| Refined solution is essentially the same as previous round | **Stop** (stubborn loop detected). No further rounds will produce meaningful change. |
| Solution oscillates (Round N undoes what Round N-1 did) | **Stop** (drift detected). Present both alternatives to the user and let them choose. |

State the gate result explicitly:

```
QUALITY GATE: [Continue / Stop Early / Extend (+N)] — [reason]
```

#### c.1) Self-Consistency Check (optional)

For complex reasoning tasks where confidence is uncertain, re-approach the problem
from a different angle (different algorithm, different decomposition, or different
assumptions) and check if the answer is consistent with the current solution.

- If consistent: confidence increases, proceed normally.
- If inconsistent: the lower-confidence path needs targeted refinement. Note the
  discrepancy in the Critical Analysis and address it in the refinement step.

This is most valuable for math, logic, and multi-step reasoning tasks.

#### d) Solution Refinement (Synthesis)

Synthesize improvements from both engines and implement the most critical ones. Rules:

- **Merge findings from both engines.** Combine Claude's identified improvements with
  Codex's independent critique into a unified improvement list.
- **Resolve conflicts by correctness priority.** If Claude and Codex disagree on a point,
  evaluate which assessment is factually correct. When in doubt, favor the more conservative
  (safer) recommendation.
- **Track attribution.** For each improvement applied, note which engine identified it
  (Claude, Codex, or Both). This feeds the Engine Agreement section in Phase 3.
- **Substance over cosmetics.** No variable renaming for style, no whitespace
  reformatting, no comments restating code.
- **One concern per round when possible.** If two improvements are independent,
  tackle both. If they conflict, pick higher-impact.
- **Watch diminishing returns.** If this round's improvement impact is notably
  smaller than last round's, consider stopping unless a correctness risk remains.
- **Validate when applicable.** For code tasks, briefly verify the change
  (run tests, check edge case, confirm constraint). State the validation result.
- **1-line changelog.** Summarize what changed and why.

### Round Output Format

```
## Round N

**Delta from Round N-1:** [1-line summary of what changed]

### Critical Analysis (Claude)

**Strengths:**
1. [Strength]
2. [Strength]

**Weaknesses:**
1. [Weakness]
2. [Weakness]

**Improvements:**
1. [Specific actionable improvement]

### Codex Validation
[Codex findings summary, or "Codex unavailable — running in single-engine mode."]
- New issues found: [list or "None"]
- Disagreements with Claude: [list or "None"]
- Agreements: [brief list]

### Quality Gate
[Continue / Stop Early / Extend] — [reason]

### Refined Solution (omit if Stop Early)

[Updated solution]

**Changelog:** [One-line summary]
**Attribution:** [Which engine(s) drove each change]
```

If the quality gate is **Stop Early**, skip the Refined Solution, Changelog, and
Attribution sections for that round and proceed directly to Phase 3.

---

## Phase 3 — FINAL SOLUTION

After all rounds complete (or quality gate triggers early stop), deliver the
final output.

### Required Sections

**The Solution:**
Complete, self-contained output. The user must be able to take this and use it
directly — no diffs, no references to previous rounds.

**Evolution Summary:**
3–5 sentences describing how the solution changed from Phase 1 to final form.
Mention which rounds had the biggest impact and why.

**Remaining Tradeoffs:**
List known tradeoffs or limitations deliberately accepted. If none, state
"No significant tradeoffs remain." Do not fabricate tradeoffs.

**Engine Agreement (Dual-Engine Tracking):**
When dual-engine mode was active during any round, include this section to
provide transparency on cross-validation results:

```
### Engine Agreement
- **Both agreed:** [issues/improvements both engines identified]
- **Claude-only catches:** [issues only Claude found]
- **Codex-only catches:** [issues only Codex found]
- **Disagreements resolved:** [conflicts and how they were resolved]
- **Rounds in dual-engine mode:** [N of M rounds]
```

If all rounds ran in single-engine mode, replace with:
`*All rounds ran in single-engine mode (Codex unavailable).*`

**Confidence Assessment:**

| Level | Meaning |
|---|---|
| **High** | Correct, robust, all requirements met, edge cases handled. Ready for use. |
| **Medium** | Likely correct for main cases. Some edge cases may need user validation. |
| **Low** | Addresses core problem but has known gaps. Strong starting point, not final. |

When dual-engine mode was active, factor agreement into confidence: issues caught by
both engines independently are highest confidence. Issues caught by only one engine
warrant a brief note on why confidence remains adequate.

### Output Format

```
## FINAL SOLUTION

[Complete final solution]

### Evolution Summary
[Narrative]

### Remaining Tradeoffs
- [Tradeoff or "No significant tradeoffs remain."]

### Engine Agreement
- Both agreed: [list]
- Claude-only catches: [list]
- Codex-only catches: [list]
- Disagreements resolved: [list or "None"]
- Rounds in dual-engine mode: [N of M]

### Confidence: [High / Medium / Low]
[Brief justification — reference dual-engine agreement where applicable]
```

---

## Adaptive Focus by Task Type

Adjust critical analysis focus based on the problem type:

### Algorithm / Code Implementation
- **Correctness:** All input classes? Off-by-one? Empty inputs? Overflow?
- **Complexity:** Time and space. Can it improve without losing readability?
- **Edge cases:** Enumerate and test boundary conditions explicitly.
- **Readability:** Understandable in 30 seconds by another developer?

### System Design / Architecture
- **Scalability:** Bottlenecks? Behavior at 10x, 100x load?
- **Failure modes:** What breaks first? Graceful degradation? SPOFs?
- **Coupling:** Loosely coupled? Independently replaceable/scalable?
- **Data flow:** Clean data model? Consistency concerns?

### Code Quality / Refactoring
- **DRY:** Duplicated logic that should be extracted?
- **SOLID:** Single responsibility? Open/closed? Dependency inversion?
- **Test coverage:** Critical paths tested? Testing behavior or implementation?
- **Naming:** Do signatures communicate intent? Preconditions clear?

### Problem-Solving / Analysis
- **Constraints:** All met? Any contradictory?
- **Tradeoffs:** Stated explicitly, not hidden?
- **Completeness:** All parts of the question addressed?
- **Assumptions:** Reasonable and stated?

### Test Coverage / Test Writing
- **Boundaries:** Min, max, zero, empty, null cases covered?
- **Gaps:** What paths have no test? What errors are untested?
- **Independence:** Tests depend on each other or execution order?
- **Assertions:** Specific? Testing the right thing?

---

## Behavioral Rules

1. **Never skip Phase 1.** Iteration without a baseline is guessing.

2. **Be genuinely critical.** Find real problems, not theater. If the solution
   is good, say so and stop early.

3. **Each round must change the solution.** If analysis finds nothing to change,
   trigger the quality gate's early stop — do not produce an identical solution.

4. **Phase 3 must be self-contained.** Not a diff. Directly usable.

5. **Max 6 rounds.** If not converging after 6, stop and state what remains
   unresolved in tradeoffs.

6. **Adapt round count to complexity.** Simple problems may need 1–2 rounds.
   Don't force 3 on a problem that converges after 1.

7. **Preserve working parts.** Do not introduce regressions. Noted strengths
   should remain strengths after changes.

8. **Surface uncertainty.** Don't hide it — reduce it each round.

9. **Watch for diminishing returns.** If Round N's improvements are significantly
   smaller than Round N-1's, consider stopping. The goal is convergence, not
   perfection.

10. **Codex is additive, not blocking.** If Codex CLI fails, continue with
    Claude-only analysis. Never let a Codex error halt the refinement pipeline.
    Log the fallback and proceed.

11. **Never collapse Claude and Codex findings into one undifferentiated list.**
    Keep engine attribution distinct throughout. Treat agreement as a confidence
    boost, not proof. Investigate disagreements — do not ignore them silently.

12. **Track attribution honestly.** When both engines find the same issue, credit
    both. Do not inflate or deflate either engine's contributions. The Engine
    Agreement section in Phase 3 must be accurate.

---

## Output Contract

Always produce output in this order:

1. `## PHASE 1 — Initial Solution`
2. `## Round 1`
3. `## Round 2` (unless stopped early)
4. `## Round 3` (unless stopped early)
5. `## FINAL SOLUTION`

Each round must include: Critical Analysis (Claude), Codex Validation (or fallback note),
Quality Gate, Refined Solution, Changelog, Attribution.

If stopping early, still produce `## FINAL SOLUTION` with a note explaining
why additional rounds are unnecessary.

---

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/iterations/`
- **Checkpoint frequency:** After each round completes (gate decision + changelog)
- **Subagent delegation:** Codex validation, self-consistency checks

## Quick Reference

```
Phase 1: Initial Solution + Assumptions
  |
  v
Phase 2: Round 1 -> Claude Analysis -> Codex Validation -> Gate -> Synthesize & Refine
         Round 2 -> Claude Analysis -> Codex Validation -> Gate -> Synthesize & Refine
         Round 3 -> Claude Analysis -> Codex Validation -> Gate -> Synthesize & Refine
         (adaptive: stop early or extend to max 6)
         (Codex fallback: single-engine mode if CLI unavailable)
  |
  v
Phase 3: FINAL SOLUTION + Evolution + Tradeoffs + Engine Agreement + Confidence
```
