# Codex review checklist (FULL review only)

31 items, derived from the problems that escaped every automated gate in real runs (human CHANGES_REQUESTED,
broken demos, bugs found by the user after "done"). Generic code-quality checks are NOT here on purpose: Agents
1A, 1B and 2 already own them; Codex's value is independent verification of behavior, requirements and
evidence.

Tier 1 (R01-R12) must be finished before Tier 2. Tier 2 items are conditional: `N-A` with a concrete reason is
the expected answer when the change does not touch that surface.

## Answer format (mandatory)

Exactly one line per ID, no ID skipped, in this order:

    ID | PASS|FAIL|N-A|NOT-CHECKED | severity | file:line or command | issue (or N-A reason) | fix

- `N-A` requires a reason. `PASS` on R01 and R03 requires the command you ran or the evidence line you checked.
- Use `NOT-CHECKED` honestly if you ran out of time; never guess `PASS`.
- After the table, an optional `OTHER (max 5)` section for issues outside the list with >80% confidence, each
  as `severity | file:line | issue | fix`.

## Tier 1

| ID | Check | Sev |
|---|---|---|
| R01 | The evidence file's validators and tests are green on the current HEAD (compare its `head:` with `git rev-parse HEAD`). Re-run at most 2 selected, bounded, deterministic commands (e.g. build or typecheck) to confirm. | CRIT |
| R02 | For each acceptance criterion in the spec/plan/issue, cite the test or evidence that proves it. FAIL any AC with no proof, or whose proof does not exercise the stated behavior. | CRIT |
| R03 | The core user scenarios declared in the plan ran on the real code path (per the evidence file) and their outputs are correct, not merely non-empty. Use evidence appropriate to the surface; boot or browser proof only when a runnable local path exists. | CRIT |
| R04 | Edits to tests, fixtures, golden sets or snapshots, new skip/xfail, loosened assertions or special-cased inputs have a matching spec change. FAIL otherwise. | HIGH |
| R05 | Run the shipped paths on seed/demo data where possible: no limit constant (cap, top-k, page size, threshold, id format) truncates or hides user-visible results the scenarios need. | HIGH |
| R06 | Changed public or semantic contracts (signatures, return shapes, config keys, routes, events): every direct consumer found by search (code, scripts, config, docs) is updated. | HIGH |
| R07 | Forbidden state transitions are blocked; state-changing actions keep their confirmation/guard on every entry path; stored legacy data (pre-change rows) is handled. | HIGH |
| R08 | When the change adds endpoints, queries or route guards: authorization, permission and tenant/customer isolation hold on all entry paths (direct URL, deep link, refresh, alternate API). | HIGH |
| R09 | Degraded and error paths keep a useful user outcome: no silent empty success, no swallowed errors, user-facing text does not leak internals. | HIGH |
| R10 | No secrets in source, logs or fixtures; no injection, path traversal or XSS through new inputs. | HIGH |
| R11 | Project convention files (listed in the prompt) are respected; report each violation citing the rule file. | HIGH |
| R12 | Review-fix commits after the reviewed baseline: inspect each fix's parent..commit diff and re-validate the checks it affects; flag regressions the fixes introduced. If base was merged after the baseline, confirm the reviewed fixes are still present in behavior. | HIGH |

## Tier 2 (conditional)

| ID | Check | Sev |
|---|---|---|
| R13 | Each new/changed test would fail if the behavior under test broke (targeted inspection; run mutation only if the repo already supports it). Flag tests that cannot fail, assert only on mocks, or depend on the current date or machine. | HIGH |
| R14 | The app boots with the documented command from the target branch and the changed path responds (no crash, no stuck loading state), when a runnable local path exists. | HIGH |
| R15 | When the change does external I/O plus a local write: transaction manager used, no check-then-act on shared state, retries idempotent. | HIGH |
| R16 | Stubs in shipped paths: TODO, NotImplemented, hardcoded returns, literals that match test inputs. | HIGH |
| R17 | New queries run against the real database engine in at least one test (no mocked repository hiding SQL errors). | MED |
| R18 | New non-secret config has a template/example and deploy declaration; secrets stay gitignored; files needed at runtime are not ignored. | MED |
| R19 | Unbounded concurrency, races on shared state, missing locks. | MED |
| R20 | N+1 or unbounded queries; missing unique/lookup indexes on new identity columns. | MED |
| R21 | UI changes: real-browser run with real data; loading, empty, error and retry states resolve; copy promises only what the backend does. | MED |
| R22 | README/doc claims touched by the diff match behavior; no volatile numbers (test counts, timings) pinned in prose. | MED |
| R23 | Every TODO, follow-up or "requires manual intervention" note the branch adds names an owner (issue, done-signal note, FINAL). | MED |
| R24 | Latency or cost NFRs in the plan were measured with a command and a number; paid API calls in tests are gated and capped. | MED |
| R25 | Out-of-diff global config the new surface relies on (body limits, CORS, prefixes, default middleware, auth defaults). | MED |
| R26 | When logging or telemetry is required by conventions or an NFR: failure logs carry correlation fields and no secrets or PII. | MED |
| R27 | When the change consumes webhooks, retries or late events: terminal states stay sticky against stale or duplicate events. | MED |
| R28 | Siblings sharing a guard (status fence, tenant/role filter, idempotency key) all apply it; FAIL the one that omits it. | MED |
| R29 | Committed run state or scratch (`.workspace/plandimp`, `.workspace/signals`, temp outputs) in `git log base..HEAD`. | LOW |
| R30 | Unsafe casts, `any`, missing null handling on new data paths. | LOW |
| R31 | Dead code, debug leftovers, commented-out code in the diff. | LOW |
