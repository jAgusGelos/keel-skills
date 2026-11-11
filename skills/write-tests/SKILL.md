---
name: write-tests
description: Use when you need to write or backfill unit and integration tests for existing code and want them complete, correct, and actually able to catch bugs — every behavior and edge case covered, every test proven to fail when the code is broken, no value-free tests. Triggers: "write tests for X", "backfill tests", "cover this with tests", "add unit/integration tests", "improve test coverage", "test this module".
version: 1.0.0
category: development
depends: []
---

# Write Tests That Catch Bugs

Generate unit and integration test suites for **code that already exists**. The goal is not coverage percentage — it is **completeness** (every behavior and edge case), **correctness** (tests assert the right thing), and **value** (every test would fail if the code regressed).

For test-first / TDD on brand-new code, this is not that skill — there you write the failing test before the production code. Here the code exists and you are characterizing and protecting its behavior.

## The Iron Law

```
A TEST THAT CANNOT FAIL IS NOT A TEST.
Every test you write must be proven to fail when the behavior it covers is broken.
```

If you never watched the test go red, you don't know it tests anything. A green test over broken code is worse than no test: it manufactures false confidence. Violating the letter of this rule is violating the spirit of it.

## When to use / when not

**Use when:** backfilling tests for untested code, hardening a module before a refactor, reproducing-and-locking a bug, or raising a suite from "it runs" to "it catches regressions."

**Don't use when:** writing new code from scratch (use a test-first/TDD flow instead), or when the user only wants a single throwaway repro — just write it.

## Process

### Choose a run mode first

- **Inline (default):** run every phase yourself in the main conversation. Simplest; keeps full context. `tokens_used` cannot be measured this way (a session has no programmatic access to its own token cost), so it stays `null`.
- **Subagent (measurable):** delegate the heavy phases to subagents. Use this when you want a real token cost per run, or to keep the main context clean. The orchestrator does almost no work itself — it dispatches subagents and reads the `subagent_tokens` each one reports back when it finishes, then sums them. Pick this mode when the user asks to log token usage.

The phases below are identical in both modes. The only differences live in **Phase 0b** (how subagent mode is wired) and **Phase 6** (whether `tokens_used` is populated).

### Phase 0b — Subagent wiring (subagent mode only; skip if inline)

The orchestrator runs no test work directly. It dispatches two subagents and captures their reported usage:

1. **`test-writer` subagent** — give it the target path, the framework + commands (from AGENTS.md), and Phases 1–3 + 5 (map, write, mutation check, verify). Require it to return a **structured result** with the Phase 6 counts: `behaviors_identified`, `behaviors_covered`, `behaviors_skipped_justified`, `mutations_introduced`, `mutations_killed`, `tests_total`, `suite_passed/failed`, `pristine`, `deterministic`, plus the list of tests written.
2. **`auditor` subagent** — Phase 4, the adversarial completeness audit. Returns gaps + value-free findings. If it surfaces real gaps, dispatch the `test-writer` again to close them (its tokens add to the total).

After each subagent finishes, read the `subagent_tokens` value from its tool result and keep a running sum. That sum is `tokens_used` in Phase 6.

- Subagents have **isolated context** — pass the target, framework, and conventions explicitly; they don't see this conversation.
- There is a **floor of ~20–25k tokens per subagent** (system prompt + tool schemas), independent of the work done. For tiny targets this overhead dominates; weigh it before splitting work across many subagents.
- The orchestrator's own tokens (dispatching, writing the log) are **not** counted — `tokens_used` reflects the test work, not orchestration overhead. Note this when reporting.

### Phase 0 — Establish the test environment (read, don't assume)

1. Read **AGENTS.md** for: the test framework, the unit-test command, the integration-test command (if separate), and any test directory conventions. Never hardcode `jest`/`pytest`/`vitest` — get it from AGENTS.md.
2. Read **2–3 existing test files** near the target. Match their structure, naming, helpers, fixtures, and assertion style. New tests should look like they were always there.
3. Confirm you can **run the suite green right now**. If the existing suite is red, stop and surface that first — you can't measure new tests against a broken baseline.

### Phase 1 — Map the behavior (this is where completeness is won or lost)

Before writing a single assertion, read the target code **completely** and enumerate every observable behavior. Completeness is a function of this list, not of how many tests you write. Produce an explicit checklist:

- **Happy path(s)** — each distinct successful outcome.
- **Every branch** — each `if`/`else`, `switch` case, ternary, early return, and guard clause is at least one scenario. Walk the code and tick each branch off.
- **Every error path** — each `throw`, rejected promise, error return, and failure of a dependency (network/DB/filesystem error, timeout).
- **Edge cases** — run the target against the checklist below.
- **Contracts & side effects** — return shape, what gets persisted, what gets called on collaborators, events emitted, state mutated.

**Edge cases you MUST consider for every input:**

| Category | Examples |
|---|---|
| Empty / absent | `null`, `undefined`, `""`, `[]`, `{}`, missing optional field, zero |
| Boundaries | min, max, off-by-one (length−1, length, length+1), first/last element |
| Wrong shape/type | unexpected type, extra fields, malformed payload |
| Size extremes | single element, very large input (10k+), deeply nested |
| Special values | negative numbers, floats, Unicode/emoji, whitespace-only, SQL/HTML metacharacters, duplicates |
| Ordering & concurrency | out-of-order events, duplicate calls (idempotency), simultaneous access, race on shared state |
| Time & state | stale data, expired token, timezone/DST, retried operation, partial failure mid-sequence |

Not every row applies to every function — but you must **decide and note** which apply and which you're deliberately skipping. A silent gap is an untested behavior.

### Phase 2 — Write the tests

**Unit vs integration — pick the right level:**
- **Unit:** one unit of logic in isolation. Mock only true external boundaries (network, clock, randomness, third-party SDKs).
- **Integration:** real collaborators wired together (real DB against a test instance/transaction, real repository, real module graph). Integration tests catch the bugs unit tests mock away — wiring, queries, serialization, transactions. Cover each cross-component contract at least once here.

**Quality bar for each test:**
- **One behavior per test.** If the name needs "and", split it.
- **Name states the behavior**, not the function: `returns 404 when the order is already archived`, not `test getOrder`.
- **AAA structure** — Arrange, Act, Assert; visually separated.
- **Assert behavior, not implementation.** Assert on outputs, persisted state, and observable effects — not on private fields or "was this internal method called." (Asserting a collaborator was called is fine when the call *is* the contract, e.g. "charges the card once.")
- **Specific assertions.** Assert the actual value/shape, not just "didn't throw" and not just "truthy." A no-throw test is usually a value-free test.
- **Independent & deterministic.** Each test seeds its own state and cleans up. No order dependency, no shared mutable state, no reliance on wall-clock or random without controlling them.
- **Wait for conditions, not time.** Poll for the awaited condition; never `sleep(500)` and hope. Arbitrary timeouts are the #1 source of flake.

**Mock anti-patterns — do NOT:**
- Assert on the mock itself instead of real behavior (`expect(mock).toHaveBeenCalledTimes(3)` as the *only* assertion → you're testing the mock, not the code).
- Add test-only methods/hooks to production classes to make them testable. Fix the coupling or use a test helper instead.
- Mock a dependency you don't understand. Run the test with the real implementation first, observe what it actually needs, then mock at the right level.
- Ship an incomplete mock — model the **complete** data structure as it exists in reality, including the fields downstream code reads.
- Let mock setup grow longer than the test. That's a signal to write it as an integration test with real components.

### Phase 3 — Prove each test catches bugs (mutation check — mandatory)

This is the step that turns "tests that pass" into "tests that catch bugs." For each meaningful test (or tight group):

1. **Break the production code on purpose** — invert a condition, return a constant, skip the persist, delete the validation, off-by-one the boundary.
2. **Run the test.** It MUST fail, and fail for the *right reason* (the assertion you care about, not an unrelated crash).
3. **Restore the code.** Run again — green.

If a test stays green while the code is broken, it asserts nothing useful. Fix the assertion or delete the test. Do this especially for every regression test: a bug-repro test that doesn't fail on the un-fixed code is proving nothing.

You don't have to mutate every line — target one representative mutation per behavior on your Phase 1 list (a flipped branch, a weakened boundary, a dropped side effect). If a formal mutation-testing tool is configured in AGENTS.md, run it; otherwise do this by hand.

### Phase 4 — Adversarial completeness audit (subagent)

Spawn a **separate subagent** to audit the suite. This matters because the same blind spot that wrote the code (or the tests) tends to review them the same way — an independent pass catches what self-review won't. Give it the target source + the new tests (not this whole session) and have it answer:

- **Missing scenarios:** which branches, error paths, or edge-case rows from Phase 1 have no test? Name each gap with the file:line of the uncovered code.
- **Value-free tests:** which tests would still pass if the relevant code were broken? (Tautologies, no-throw-only checks, assertions on mocks, over-broad matchers.)
- **Wrong-level tests:** what is mocked that should be real (a bug hiding behind a mock), or real that should be mocked (slow/flaky)?
- **Correctness:** does any test assert behavior the code doesn't actually have (a test written to the wrong spec)?

Triage the findings: fix every real gap and every value-free test. Re-run Phase 3's mutation check on anything you add. If the audit surfaces nothing, that's a valid result — don't manufacture changes.

### Phase 5 — Final verification (evidence, not claims)

- Run the **full** unit + integration suite via the AGENTS.md commands. Read the actual output, exit code, and pass/fail counts — don't infer from "it should pass."
- Output must be **pristine**: no new warnings, no leaked logs, no open handles.
- Confirm tests are deterministic — run twice (or the framework's repeat flag) to catch order-dependence and flake.
- Never claim "tests pass" without having run them in this session.

### Phase 6 — Score and log the run (metrics)

Every run emits one JSON record so executions can be compared over time. The score is computed **mechanically** from counts the phases above already produced — no subjective grading — so the same suite always yields the same number.

**Collect these counts** (you already have them from Phases 1–5):

| Field | Source |
|---|---|
| `behaviors_identified` | size of the Phase 1 checklist |
| `behaviors_covered` | checklist items with ≥1 test |
| `behaviors_skipped_justified` | items deliberately skipped with a noted reason |
| `mutations_introduced` | mutations made in Phase 3 |
| `mutations_killed` | of those, how many turned a test red for the right reason |
| `tests_total` | tests in the final suite |
| `tests_value_free_remaining` | value-free tests still present after Phase 4 (should be 0) |
| `suite_passed` / `suite_failed` | from the Phase 5 run |
| `pristine`, `deterministic` | from Phase 5 (booleans) |
| `tokens_used` | **subagent mode only:** the summed `subagent_tokens` from every subagent dispatched in Phase 0b/4. **Inline mode:** `null` (not measurable). |

**The formula** (deterministic, range 0–100):

```
completeness   C = behaviors_covered / (behaviors_identified − behaviors_skipped_justified)
mutation_score M = mutations_killed / mutations_introduced
value_density  V = (tests_total − tests_value_free_remaining) / tests_total
hygiene_gate   H = 1 if (suite_failed == 0 AND pristine AND deterministic) else 0

quality_score = 100 × H × (0.40·M + 0.35·C + 0.25·V)
```

- **H is a hard gate**, not a weight: a suite that doesn't run green, clean, and deterministic scores **0** — a broken suite has no quality regardless of coverage. Report it as `0` with `"valid": false`.
- **M is weighted highest (0.40)** — catching bugs is the whole point. A suite with high coverage but a low mutation score is mostly theatre.
- Weights are intentionally visible here so they can be tuned per project. Keep them stable across a comparison set, or old runs aren't comparable.

**Efficiency** (subagent mode only): `efficiency = quality_score / (tokens_used / 1000)` — quality points per 1k tokens. Lets you tell "same quality, fewer tokens" runs apart. `null` in inline mode. Remember the ~20–25k/subagent floor (Phase 0b): efficiency on a tiny target is dominated by overhead, so only compare runs of similar size.

**Append one record** (don't overwrite) to a run log so all executions accumulate. Path: read it from AGENTS.md if defined, else default to `docs/test-metrics/runs.jsonl` (one JSON object per line — JSONL). Generate the timestamp with a real `date` call, not a guess.

```json
{
  "timestamp": "2026-06-24T14:03:00Z",
  "target": "src/orders/orderService.ts",
  "framework": "vitest",
  "run_mode": "subagent",
  "tokens_used": 142000,
  "counts": {
    "behaviors_identified": 18, "behaviors_covered": 17, "behaviors_skipped_justified": 1,
    "mutations_introduced": 14, "mutations_killed": 13,
    "tests_total": 24, "tests_unit": 18, "tests_integration": 6, "tests_value_free_remaining": 0,
    "suite_passed": 24, "suite_failed": 0, "pristine": true, "deterministic": true
  },
  "metrics": { "completeness": 1.0, "mutation_score": 0.93, "value_density": 1.0, "hygiene_gate": 1 },
  "quality_score": 96.9,
  "efficiency": 0.68,
  "valid": true,
  "coverage_reported": { "lines": 0.91, "branches": 0.88 }
}
```

`coverage_reported` is informational only — pulled from the framework's coverage output if it runs. It never feeds `quality_score` (coverage measures lines executed, not bugs caught).

Add the score line to the run's output summary so the user sees it without opening the file.

## Rationalizations — and the reality

| Excuse | Reality |
|---|---|
| "It's obviously correct, no need to break it." | Then the mutation check costs seconds and confirms it. If you won't run it, you're guessing. |
| "100% coverage, we're done." | Coverage measures lines executed, not behavior asserted. A test can execute a line and assert nothing. Completeness is the Phase 1 checklist, not a percentage. |
| "Asserting it didn't throw is enough." | A function returning the wrong value also doesn't throw. Assert the value. |
| "Mocking everything keeps it fast." | Over-mocking tests your mocks. The wiring bug lives exactly where you mocked. Keep one integration test honest. |
| "Setup is huge / it's hard to test." | Hard to test = hard to use. That's the code talking. Consider it a design signal, not a testing problem. |
| "I'll add edge cases later." | Later never comes and the gap reads as 'covered.' Decide now, even if the decision is a noted skip. |

## Output format

```
## Tests added

<framework> · <N> unit · <M> integration · target: <file/module>

### Behavior coverage (Phase 1 checklist)
- [x] <behavior / branch / edge case> → <test name>
- [ ] <deliberately skipped> — <one-line reason>

### Mutation check (Phase 3)
- <behavior>: broke <what> → test went red ✓

### Adversarial audit (Phase 4)
- <gaps found and fixed, or "no gaps">

### Verification (Phase 5)
- Command: <test command from AGENTS.md>
- Result: <N passed, 0 failed> · output pristine · ran 2× deterministic

### Score (Phase 6)
- Quality: <0–100> (M <mutation_score> · C <completeness> · V <value_density> · gate <0/1>)
- Run mode: <inline | subagent>[ · Tokens: <N> · Efficiency: <quality per 1k>]
- Logged to: <runs.jsonl path>
```

## Completion checklist

You are done only when every box is true. Can't check one? You're not done.

- [ ] Read AGENTS.md for framework + commands; matched existing test conventions.
- [ ] Enumerated every behavior, branch, error path, and applicable edge case (Phase 1).
- [ ] Each test: one behavior, behavior-named, AAA, specific assertion, independent, no arbitrary sleeps.
- [ ] No mock anti-patterns (no asserting on mocks-only, no test-only production methods, no incomplete mocks).
- [ ] Mutation check run: every meaningful test proven to fail on broken code, for the right reason.
- [ ] Adversarial subagent audit run; all real gaps and value-free tests resolved.
- [ ] Full suite run this session: all green, output pristine, deterministic across reruns.
- [ ] Run scored via the Phase 6 formula and one record appended to the run-log JSONL.
