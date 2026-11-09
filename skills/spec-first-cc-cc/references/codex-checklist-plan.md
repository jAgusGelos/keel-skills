# Codex plan audit checklist (plan.md + todo.md, one audit)

18 items, derived from what escaped every gate in real runs: frozen contracts that could not answer the core
user question, acceptance criteria without proof, no real-stack check, integration nobody owned, launch order
that ignored real dependencies, destructive operations without a guard. Template completeness (sections, AD
fields, AD-ID sequence) is NOT here: `scripts/lint-plan.py` checks it deterministically before this audit.

Tier 1 (P01-P10) must be finished before Tier 2. `N-A` with a concrete reason is a valid answer when an item
does not apply to this feature.

## Answer format (mandatory)

Exactly one line per ID, no ID skipped, in this order:

    ID | PASS|FAIL|N-A|NOT-CHECKED | severity | plan.md/todo.md section or repo path:line | issue (or N-A reason) | fix

- Use `NOT-CHECKED` honestly if you ran out of time; never guess `PASS`.
- Do not propose splitting tasks that are cohesive or that would leave the repo non-importable in between.
- After the table, an optional `OTHER (max 5)` section for issues outside the list with >80% confidence.

## Tier 1

| ID | Check | Sev |
|---|---|---|
| P01 | List the core user scenarios from the goal/issue. Trace each one through every frozen contract value in the plan and its contract docs (caps, top-k, ranking rule, filters, row limits, timeouts). FAIL if any scenario cannot produce a correct answer under those values. | CRIT |
| P02 | Every acceptance criterion in the goal/issue maps to a plan conformance item AND a todo Verify step that exercises behavior (not file creation). FAIL on any AC missing either. | CRIT |
| P03 | The plan declares an applicable acceptance step before the final review: the exact command and scenario that exercise the feature on the real stack (app booted, real model/DB/UI) where a runnable surface exists; UI work names the real route and at least one browser scenario. | HIGH |
| P04 | Discover the repo's own validators (build, typecheck, lint, test, spec validators, migration checks) from repo files. Each is assigned to a milestone gate, the final gate, or marked N/A with a reason. | HIGH |
| P05 | Every known gap, contract tension or "requires manual intervention" item names an owner and an escalation channel (done-signal note, needs-human file, issue). "Recorded" alone FAILs. | HIGH |
| P06 | The integration path is stated: base branch, who merges and when, which shared docs are updated, the full-suite command after merge. | HIGH |
| P07 | Every file or contract consumed from another feature exists on the named base or is a declared LAUNCH dependency (not only a logical one); deliverables that describe the product depend on every feature that changes it. | HIGH |
| P08 | Destructive or costly operations (migration revert, DB reset, data deletion, force-push, paid API calls) have a guard: explicit test database, USD cap, or Ask-First. | HIGH |
| P09 | Risky contract assumptions have a spike/prototype step or an explicit replan trigger with a measurable threshold. | HIGH |
| P10 | Defaults that change user-visible or money-moving behavior are flagged Ask-First or escalated, not silently decided. | HIGH |

## Tier 2

| ID | Check | Sev |
|---|---|---|
| P11 | New non-secret config has a template/example and deploy declaration; secrets stay gitignored; files needed at runtime are not ignored. | MED |
| P12 | Planned tests control nondeterministic inputs (clock, randomness, timezone, network, external services). | MED |
| P13 | The plan honors the run-level constraints given in the goal/prompt (test scope, cost caps, ownership/no-touch files, approvals policy). | MED |
| P14 | Every todo milestone ends in a Verify step with an executable command and its expected output, and leaves the repo runnable. | MED |
| P15 | Every plan AD and conformance item has a todo task, and every task traces to a plan item. | MED |
| P16 | Flag a milestone that touches more than about 15 files or more than one subsystem (it will outgrow one session's context). | MED |
| P17 | Evidence citations (path:line, symbol) exist in the repo: check all when there are 5 or fewer, otherwise sample 5 across sections. | MED |
| P18 | Planned deviations from the goal are listed explicitly; no unrequested scope. | LOW |
