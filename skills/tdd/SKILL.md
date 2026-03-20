---
name: tdd
description: >
  Guide Claude through strict Test-Driven Development (TDD) using red-green-refactor cycles.
  Use this skill whenever the user mentions "tdd", "test driven", "test first",
  "red green refactor", "write tests first", "TDD workflow", "test-driven development",
  "behavior-driven", "write the test before the code", or any variation of wanting tests
  written before implementation. Also use this skill when the user describes requirements
  that are best built incrementally with test-first methodology — pricing engines,
  rule-based validators, multi-condition workflows, state machines, parsers, or any logic
  with clear input/output contracts. Even if the user just says "build this with tests" or
  "I want good test coverage for this feature", default to this skill — unless the user
  is explicitly doing exploratory/spike work where TDD adds friction.
version: 1.0.0
category: development
depends: []
---

# TDD — Test Driven Development

Guide the user through strict red-green-refactor cycles. Tests are **behavior prompts** —
they define what the system should do before a single line of implementation exists.

## Why TDD Works with AI Agents

1. **RED forces design thinking.** Writing the test first means deciding the API before the
   implementation. You think about what the caller needs, not what is easy to build.
2. **GREEN forces simplicity.** Minimal code to pass means no speculative architecture. Every
   line exists because a test demanded it.
3. **REFACTOR forces quality.** With green tests as a safety net, restructure without fear.
   Tests catch regressions instantly.

The net result: code that does what it should, no more, no less, and stays clean over time.

## Step 0: Detect Environment

Scan the project root for config files to determine the test framework and run command.

### Framework Detection Table

| Config File      | Language | Framework       | Run Command (single)             | Run Command (full suite)         |
|------------------|----------|-----------------|----------------------------------|----------------------------------|
| `package.json`   | JS/TS    | jest            | `npx jest --testPathPattern`     | `npx jest`                       |
| `package.json`   | JS/TS    | vitest          | `npx vitest run`                 | `npx vitest run`                 |
| `package.json`   | JS/TS    | mocha           | `npx mocha`                      | `npx mocha`                      |
| `pyproject.toml` | Python   | pytest          | `pytest -xvs <file>`            | `pytest -xvs`                    |
| `setup.cfg`      | Python   | pytest/unittest | `pytest -xvs <file>`            | `pytest -xvs`                    |
| `Cargo.toml`     | Rust     | cargo test      | `cargo test <name>`              | `cargo test`                     |
| `go.mod`         | Go       | go test         | `go test -run <name> ./...`      | `go test ./...`                  |
| `build.gradle`   | Java/Kt  | JUnit           | `./gradlew test --tests <name>` | `./gradlew test`                 |
| `pom.xml`        | Java     | JUnit/Maven     | `mvn test -Dtest=<name>`        | `mvn test`                       |
| `mix.exs`        | Elixir   | ExUnit          | `mix test <file>:<line>`         | `mix test`                       |
| `Gemfile`        | Ruby     | RSpec/Minitest  | `bundle exec rspec <file>`       | `bundle exec rspec`              |
| `*.csproj`       | C#       | xUnit/NUnit     | `dotnet test --filter <name>`    | `dotnet test`                    |
| `deno.json`      | Deno     | Deno.test       | `deno test <file>`               | `deno test`                      |
| `build.zig`      | Zig      | zig test        | `zig build test`                 | `zig build test`                 |

### Detection Procedure

1. Use Glob to check for config files in the project root. For monorepos, also check for workspace files (`pnpm-workspace.yaml`, `lerna.json`, Cargo workspace) and scan nested `packages/*/` or subdirectories.
2. For `package.json`, Read it and inspect `devDependencies` and `scripts.test` to pick jest vs vitest vs mocha.
3. For Python, check `[tool.pytest.ini_options]` or `[tool.pytest]` in `pyproject.toml`, or fall back to `python -m pytest`.
4. If nothing is found, ask: "I didn't find a test framework. Which would you like to use?" Suggest the most common one for the detected language and offer to install it.
5. Store the run command — use it in every cycle.

### Command Policy

- **During RED:** Run the single test file/test to confirm failure.
- **During GREEN:** Run the single test to confirm it passes, then run the full suite to check for regressions.
- **During REFACTOR:** Run the full suite after each change.

## Step 1: Understand Requirements & Plan

### Load Context First

Before writing any test, read the relevant codebase context:
1. Identify files the new code will interact with (interfaces, types, adjacent modules).
2. Read them and note their signatures, patterns, and conventions.
3. Reference these in the test plan so cycles use real types and APIs, not invented ones.

This prevents the AI from generating code that conflicts with existing architecture.

### Single requirement
Go directly to the cycle.

### Multiple requirements
Create a numbered **Test Plan** ordered by business value:
1. **Core happy path** — the most important behavior that delivers value.
2. **Supporting behaviors** — secondary logic that builds on the core.
3. **Edge cases and boundaries** — error handling, limits, invalid inputs.

Each item is one behavior. Multi-condition requirements must be decomposed — one condition per cycle. The user can stop at any point and have something useful.

### Test Plan Template

```
## Test Plan

| # | Behavior                                    | Priority | Status |
|---|---------------------------------------------|----------|--------|
| 1 | [core happy path]                           | High     | [ ]    |
| 2 | [supporting behavior]                       | Medium   | [ ]    |
| 3 | [edge case / boundary]                      | Low      | [ ]    |
```

Present the plan to the user before starting cycles.

## Step 2: Execute Red-Green-Refactor Cycles

For each item in the plan, run one full cycle.

### Cycle Output Format

```
## Cycle N: [short behavior description]

### RED — Failing test
[Test code — one assertion per behavior, deterministic, no randomness]
[Bash: run test → paste output showing FAIL]

### GREEN — Minimal implementation
[Least code to pass. Hard-coded returns are valid at this stage.]
[Bash: run single test → PASS]
[Bash: run full suite → ALL PASS]

### REFACTOR
[Improve structure, remove duplication, rename — or "No refactoring needed."]
[Bash: run full suite → ALL PASS]

Cycle N complete. Committing checkpoint. Moving to Cycle N+1.
```

### Commit Cadence

**Recommended** (can be adjusted per team workflow):
- After GREEN: commit with `green(tdd): <behavior description>`
- After REFACTOR: commit with `refactor(tdd): <what changed>`
- These act as rollback points if a later cycle goes wrong.
- If the user prefers squashing later or is in a no-git context, skip commits but still track progress in the test plan.

**Optional TCR mode** (strict discipline, requires explicit user opt-in):
When enabled, after each save: run tests -> if green, auto-commit -> if red, `git checkout -- .` to revert to last green state.
Prerequisites: clean working tree, no unstaged changes outside the TDD files.
Enable with: "Let's use TCR mode." Confirm with user before first revert.

### Phase Rules

**RED phase:**
- Write ONE test for ONE behavior.
- The test must be deterministic — no network, no time-dependent logic unless mocked.
- **Test names are specifications.** Someone reading only test names should understand the full system behavior. Bad: `test_calc`. Good: `test_returns_free_shipping_when_cart_total_exceeds_50`. If the name doesn't describe the expected outcome, rename it before proceeding.
- **Spec verification gate:** After writing the test, ask: "Does this test encode the *specification* or does it describe what code currently does?" Could a buggy implementation pass this test? If yes, tighten the assertion. AI-generated tests risk encoding bugs as passing behavior — catch this here.
- For outputs that may legitimately vary in structure (e.g., error message wording, collection ordering), assert on structure and key properties rather than exact matches. Use `contains`, `toMatchObject`, `assertIn` over strict equality when the spec allows variation.
- Run the test. It MUST fail. If it passes, the behavior already exists — document this and move on.

**GREEN phase:**
- Write the LEAST code to make the test pass.
- Returning a hard-coded value that satisfies the test is correct. Generalization comes from the next failing test or refactor.
- Do NOT add code for behaviors not yet tested.

**REFACTOR phase:**
- Improve code quality: extract constants, remove duplication, improve naming.
- Do NOT change behavior — tests must stay green.
- If no improvement is needed, say so and move on.

## Rules — Non-Negotiable

1. **NEVER write implementation before a failing test.** This is the core discipline.
2. **Run tests after EVERY change.** Every red, every green, every refactor. Use Bash.
3. **One behavior per test, one cycle per behavior.** Do not bundle.
4. **All tests must be green before starting the next cycle.** Fix regressions immediately.
5. **Label every phase** with RED/GREEN/REFACTOR markers.
6. **Minimal GREEN means minimal.** No speculative code.
7. **Tests are behavior prompts.** They define *what*, not *how*.

### Anti-Patterns to Reject

- Writing multiple tests before closing the first red-green cycle.
- Broad refactors during the GREEN phase.
- Adding "just in case" code not demanded by a test.
- Skipping the RED confirmation (running the test to see it fail).
- Refactoring without running the full suite afterward.

## Step 3: Continue or Finish

After each cycle:
- Update the test plan status `[x]`.
- If more behaviors remain, start the next cycle.
- When all cycles are done, present a summary:

```
## TDD Session Summary

| Cycle | Behavior                  | Tests | Status |
|-------|---------------------------|-------|--------|
| 1     | [description]             | 1     | PASS   |
| 2     | [description]             | 1     | PASS   |
| 3     | [description]             | 1     | PASS   |

Total: N tests, all green.
```

## Step 4: AI Smell Review

After the session summary, run a quick review checklist for AI-specific code smells:

1. **Automation bias** — Did we accept any test or implementation without questioning it? Re-read each test: does it test the *spec* or just mirror the implementation?
2. **Redundancy/bloat** — Are there duplicate functions, over-abstracted patterns, or code not demanded by any test? If yes, add a final refactor cycle.
3. **Anchoring** — Did an early implementation choice constrain later cycles unnecessarily? Could the design be simpler now that all behaviors are implemented?
4. **Context poisoning** — Did earlier cycle patterns leak into later cycles where they don't belong?

If any smell is detected, run one final refactor cycle to clean up. Then re-run the full suite.

## Edge Cases

### Existing code without tests
Write **characterization tests** first — tests that document current behavior. Run them
to confirm they pass. Then proceed with TDD for new behavior.

### Flaky or non-deterministic tests
Stop the cycle. Identify the source of flakiness (time, network, randomness). Mock the
dependency or make the test deterministic before continuing.

### User wants to skip ahead
Remind them: "TDD discipline means we write the test first. Want me to continue with the
cycle?" If they insist, comply but note which behaviors lack tests.

### No test framework detected
Ask the user which framework to use. Offer to install it:
- JS/TS: `npm install --save-dev jest` or `vitest`
- Python: `pip install pytest`
- Go/Rust: built-in, no install needed

### Test passes immediately at RED
The behavior already exists. Document it: "This behavior is already implemented.
The test still has value as a regression guard." Move to the next cycle.

### Fixing a broken test introduces new failures
When fixing a single failing test during GREEN or REFACTOR:
1. Run the full suite BEFORE fixing — record which tests are green.
2. Apply the fix.
3. Run the full suite AGAIN — confirm no previously-green test flipped to red.
4. If regressions appear, revert the fix and take a smaller step.

This prevents local fixes from cascading into collateral regressions.

## Context Management

This skill follows the context-management protocol.

- **Scratchpad:** `.workspace/ctx/tdd/`
- **Checkpoint frequency:** After each red-green-refactor cycle completes
- **Subagent delegation:** Test execution (full suite runs), lint/type checks

## When TDD Fits Best

**Ideal:**
- Pure logic with clear inputs/outputs — calculators, validators, parsers, formatters
- Rule-based systems — pricing engines, permission checkers, multi-condition workflows
- Incremental feature building — each requirement adds a testable behavior
- Bug fixes — write a test that reproduces the bug, then fix it
- Refactoring — lock behavior with tests, then restructure safely
- State machines — each transition is a cycle

**Less natural:**
- Exploratory UI work, one-off scripts, or spike prototyping — write tests after
- Integration with external systems where mocking is complex — consider integration tests separately

## Example Walkthrough — Shipping Cost Calculator (pytest)

User says: *"Build a shipping cost calculator. Free shipping over $50, otherwise $5.99
flat rate, and add $3 per item over 10 lbs."*

### Test Plan

| # | Behavior                                     | Status |
|---|----------------------------------------------|--------|
| 1 | Returns $5.99 for a cart under $50           | [ ]    |
| 2 | Returns $0 for a cart at or over $50         | [ ]    |
| 3 | Adds $3 surcharge per item over 10 lbs       | [ ]    |

---

### Cycle 1: Flat rate for cart under $50

**RED — Failing test**

```python
# tests/test_shipping.py
from decimal import Decimal
from shipping import calculate_shipping

def test_returns_flat_rate_when_cart_total_under_50():
    items = [{"name": "Book", "price": Decimal("12.00"), "weight_lbs": 1}]
    assert calculate_shipping(items) == Decimal("5.99")
```

```
$ pytest -xvs tests/test_shipping.py
FAILED — ModuleNotFoundError: No module named 'shipping'
```

**GREEN — Minimal implementation**

```python
# shipping.py
from decimal import Decimal

def calculate_shipping(items):
    return Decimal("5.99")
```

```
$ pytest -xvs tests/test_shipping.py
PASSED — 1 passed
```

**REFACTOR** — No refactoring needed. One function, one return.

---

### Cycle 2: Free shipping at or over $50

**RED — Failing test**

```python
def test_returns_free_shipping_when_cart_total_at_or_over_50():
    items = [{"name": "Jacket", "price": Decimal("65.00"), "weight_lbs": 2}]
    assert calculate_shipping(items) == Decimal("0")
```

```
$ pytest -xvs tests/test_shipping.py
FAILED — assert 5.99 == 0
```

**GREEN — Minimal implementation**

```python
from decimal import Decimal

def calculate_shipping(items):
    total = sum(item["price"] for item in items)
    if total >= Decimal("50"):
        return Decimal("0")
    return Decimal("5.99")
```

```
$ pytest -xvs tests/test_shipping.py
PASSED — 2 passed
```

**REFACTOR** — Extract constants for clarity.

```python
from decimal import Decimal

FREE_SHIPPING_THRESHOLD = Decimal("50")
FLAT_RATE = Decimal("5.99")

def calculate_shipping(items):
    total = sum(item["price"] for item in items)
    if total >= FREE_SHIPPING_THRESHOLD:
        return Decimal("0")
    return FLAT_RATE
```

```
$ pytest -xvs tests/test_shipping.py
PASSED — 2 passed
```

---

### Cycle 3: Weight surcharge for heavy items

**RED — Failing test**

```python
def test_adds_surcharge_per_item_over_10_lbs():
    items = [{"name": "Anvil", "price": Decimal("30.00"), "weight_lbs": 15}]
    assert calculate_shipping(items) == Decimal("8.99")  # 5.99 + 3.00
```

```
$ pytest -xvs tests/test_shipping.py
FAILED — assert 5.99 == 8.99
```

**GREEN — Minimal implementation**

```python
from decimal import Decimal

FREE_SHIPPING_THRESHOLD = Decimal("50")
FLAT_RATE = Decimal("5.99")
HEAVY_SURCHARGE = Decimal("3.00")
HEAVY_WEIGHT = 10

def calculate_shipping(items):
    total = sum(item["price"] for item in items)
    if total >= FREE_SHIPPING_THRESHOLD:
        return Decimal("0")
    surcharge = sum(HEAVY_SURCHARGE for item in items if item["weight_lbs"] > HEAVY_WEIGHT)
    return FLAT_RATE + surcharge
```

```
$ pytest -xvs tests/test_shipping.py
PASSED — 3 passed
```

**REFACTOR** — Code is clean, constants are named, logic is straightforward. No refactoring needed.

### Session Summary

| Cycle | Behavior                    | Tests | Status |
|-------|-----------------------------|-------|--------|
| 1     | Flat rate under $50         | 1     | PASS   |
| 2     | Free shipping >= $50        | 1     | PASS   |
| 3     | Heavy item surcharge        | 1     | PASS   |

Total: 3 tests, all green.
