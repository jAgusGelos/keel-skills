---
name: qa-run
description: |
  Run a qa-plan regression plan against the local branch with Playwright: one recorded spec per case
  (dark and light themes when the app has both), role batches, each case's status written back into
  the plan, and a local bug-issue draft per failure. qa-triage publishes the bugs. Second step of the
  qa-plan -> qa-run -> qa-triage chain. Use when the user says "qa run", "run the QA pass", "run the
  regression plan", "execute the qa plan", or "/qa-run".
version: 1.0.0
category: development
depends: [qa-plan, qa-triage]
disable-model-invocation: true
---

# qa-run

`/qa-run [plan-path] [QA-ids...]`: the plan defaults to the newest `qa-plan` file in `.qa/`; ids narrow one invocation to those cases, never the pass.

Turn a `qa-plan` file into a **pass**: every case driven in a real browser against the local branch, recorded, and judged against its Expected Result. The plan file is the ledger: its **Actual Result** and **Bug Issue** columns hold the outcome. A case is **run** when its Actual Result reads `pass` or `bug`; the pass ends only when every case in the plan is run. Report only: this skill writes the plan, gitignored artifacts, local drafts, the local database (role switches, data scripts, a legacy database swap), and any flag override the user approves in step 2. Step 7 restores the role, persona, actor-swap, legacy and flag changes; seeded blocks stay for reruns. `qa-triage` owns every bug publication. The one GitHub write here is optional: when the user names a tracking issue for progress, each case's verdict is commented on it when the case is run (step 6).

Everything project-specific (start command, URLs, login, roles, database access, design rules) comes from `docs/qa-setup.md`, shaped by [`references/project-setup.md`](references/project-setup.md). `<frontend>` below is its frontend directory.

`<key>` below is the plan file's name without `.qa/`, the `manual-e2e-` prefix and `.md` (for example `2026-10-01-to-2026-10-20-2`, or `branch-<branch-short-name>-2`). Take it from the file name, never from the plan's dates or branch, so a `-2` plan gets its own run folder. Artifacts:

| What | Where (all gitignored) |
|---|---|
| Generated specs | `<frontend>/e2e/evidence/qa-<key>/QA-NN-<slug>.spec.ts` |
| Raw Playwright output per batch | `.qa/run-<key>/raw/<batch>/` |
| Evidence per test | `.qa/run-<key>/QA-NN/<Role>/`: screenshots, `video.webm`, `storyboard.md`; the light pass in its `light/` subfolder |
| Bug drafts | `.qa/run-<key>/issues/QA-NN.md`, and `issues/local-data-fixture.md` for fixture gaps |
| Supplemental data scripts | `.qa/run-<key>/data/`, named and structured by [`references/data-scripts.md`](references/data-scripts.md) |
| Ids of seeded records | `<frontend>/e2e/evidence/qa-<key>/ids.json`, rewritten after every seed or reset |
| Progress page, when asked for | `.qa/run-<key>/progress.html`, built from the plan and `.qa/run-<key>/progress.json` (step 6) |

The pass's tools are in [`scripts/`](scripts/): `sql.sh` runs data scripts, `ids.py` writes the ids, `steps.py` reads a report, `collect.py` files the evidence, `verdict.py` writes a plan row, `progress.py` renders a progress page, and `post.py` comments a case on a tracking issue. Run `python3 scripts/verdict.test.py` after editing `verdict.py`.

## 1. Preflight: stop on the first gap

Check in order; a missing tool is a blocker, reported with its fix:

1. **Setup file**: `docs/qa-setup.md` exists. Missing: draft it from [`references/project-setup.md`](references/project-setup.md) and confirm it with the user before continuing.
2. **Playwright and helpers**: Playwright is installed in `<frontend>`, with the evidence config and the helpers from [`assets/`](assets/) (project-setup → One-time install).
3. **App up in dev mode** from the working tree that holds the branch under test, started with the setup's start command and its ready check passing. For a window plan (`manual-e2e-<from>-to-<to>...`), that branch is the integration branch at or after its remote: HEAD is the integration branch, and `git rev-list --count HEAD..origin/<integration>` is `0` after `git fetch`. Otherwise stop and ask the user to check it out. When an app instance is already serving the UI URL, confirm it runs from this checkout and started after HEAD last moved; one started earlier can serve old code, and one from another checkout is the user's: ask before stopping it.
4. **Login state**: the session file (or every per-role file the plan's roles need) exists and does not land on the login page. You never sign in and never type credentials: a missing or expired session is the user's login command. That recorded session is the sign-in of every case: a case that tests sign-in takes it as its sign-in steps and drives the rest (bearer token on API calls, reload, sign-out).
5. **Local data loaded**: the setup's local data check passes. An empty database means the local fixture is not loaded: stop and point the user to the fixture docs the setup names, since loading it usually needs their identity.
6. **Role strategy ready**: per-role sessions: every role file exists. Role-switch recipe: its identity step resolves.
7. **Effective flags**: read the feature flags where the setup says they live. A flag changes verdicts, so list each one against what the plan's "Before you start" assumes. A local override needs the user's yes in step 2, and step 7 reverts it.

## 2. Plan the batches: one grouped question

Read the plan's table (`qa-plan/references/test-case-template.md` owns its shape) and the "Before you start" section. Per case take the role from Preconditions, the steps, and the Expected Result.

- **Batches**: keep the plan's order and every run-order constraint it states; group *consecutive* cases with the same role. A case whose Expected Result checks that another role must *not* see something becomes a second test with the same id, in that role's batch.
- **Legacy cases**: a case that needs data from before a schema migration ([`references/legacy-migration.md`](references/legacy-migration.md)) is its own batch, tagged `@legacy` as well. Swap the legacy database in first, then switch the role (a restart can revert a switch), run, and swap back before the next batch.
- **Paths to ask for**: list every case you cannot yet see how to drive or judge, with what is missing. Examples: a scheduled job, a migration from a prior snapshot, an email, a feature flag the local build does not read, data the local fixture cannot provide, another user's own screen, or a sign-out that would end the recorded session. The user gives the path; the case joins its batch.
- **Themes**: when the setup lists one theme, there is no light pass; say so once.
- **Progress reporting**: ask whether to comment each case on a tracking issue and to keep a progress page.

Show the batches (role → ids), the effective flags that differ from the plan's assumptions, and the paths to ask for, then ask once: *run the pass as shown, and how do I run these?* Nothing below runs before a yes.

## 3. Back up the roles

Role-switch recipe only (per-role sessions skip this step). If `.qa/role.backup.sql` or `.qa/persona.backup.sql` already exists, an earlier run did not finish step 7. Show it to the user and restore from it before you take a new backup.

Follow the recipe's backup step. From here on, **restore is owed**: every exit path (success, failure, abort) runs step 7 before this skill ends.

## 4. Generate the specs

One spec per test, using `captionedStep` (from `e2e/evidence-caption.ts`) per step, viewport screenshots, and role- and text-based locators, per [`references/spec-patterns.md`](references/spec-patterns.md), which owns the shared helpers (`e2e/qa-evidence.ts`), the traps real passes hit, and the verdict techniques. Take locators from the component's template first (`aria-label`, `data-testid`, button text, the element a handler sits on); explore with the browser only where the template leaves it unclear. On top of that:

- Title `QA-NN <plan title>`, tags `@QA-NN @role:<Role>`, plus `@legacy` for a legacy case. The tags are how a batch selects its tests, and `collect.py` names the evidence folder after the `role:` tag. A persona batch tags `@role:<Role>-<Persona>` (for example `@role:Member-TeamLead`), one tag per persona, so its grep and its evidence folder stay apart from the plain role's. From here on, `<Role>` in evidence paths and script arguments (`collect.py`, `post.py`) is the `role:` tag value.
- With per-role sessions, `test.use({ storageState: "e2e/.auth/<Role>.json" })`.
- `test.use({ actionTimeout: 15_000 })`, so a stuck locator fails with its name instead of the test timeout; raise `test.setTimeout` for a case that builds data through the UI.
- `applyTheme(page)` first, and `contrastIssues` after each step's screenshot, attached to the test: the same spec serves both theme passes.
- One `captionedStep` per plan Execution Step, its description taken from the step, in English.
- Every clause of the Expected Result is an explicit `expect`. That assertion is the case's verdict; a spec that cannot state it marks the case `manual`.
- Every absence check (`toHaveCount(0)`, `not.toBeVisible`) follows a presence check on the same screen: its heading or a known control. A denied, empty or still-loading page passes any absence check, so the anchor is what makes it evidence.
- The first `captionedStep` is `Preconditions`: it starts from the local fixture, and asserts every precondition the plan row names before any Execution Step runs. Data the fixture lacks is a **fixture gap**: build it by [`references/data-scripts.md`](references/data-scripts.md) and continue. The flow under test itself is still driven through the UI. A case that consumes its block's data runs after that block's reset, so a rerun starts from the same state.

Explore an unfamiliar screen interactively (`npx playwright codegen <url> --load-storage=<session file>`, or the Playwright CLI/MCP when available). Exploration output is never evidence, and its traces stay on the machine.

## 5. Run batch by batch

For each batch:

1. **Switch** to its role: pick its session file, or run the recipe's switch, wait and verify steps. A role or persona that does not verify stops the batch; its cases stay unrun and say why.
2. **Run** from `<frontend>`, with the batch's own output directory, because Playwright empties its output directory at the start of every run:

   ```bash
   PLAYWRIGHT_JSON_OUTPUT_FILE=<abs>/.qa/run-<key>/raw/<batch>/report.json \
     npm run e2e:evidence -- qa-<key>/ --grep '@role:<Role>(?=\s|$)' --output <abs>/.qa/run-<key>/raw/<batch> --reporter=list,json
   ```

   `--grep` is a regex. A role name can prefix another (`Manager`, `ManagerReader`), so every grepped tag ends with `(?=\s|$)`, and a `+` in a combined role tag is escaped (`@role:Member\+Reporting`). To run some cases of a role, select both tags: `--grep '(?=.*@role:<Role>(?=\s|$))(?=.*(@QA-03|@QA-04)(?=\s|$))'`. When a role has more than one batch (a legacy batch counts), every batch of that role selects by role and ids this way, and a legacy batch selects `@legacy(?=\s|$)` too. Read the result with `scripts/steps.py <report.json>`: each test's steps, status and first error line.

3. **Light pass** (two-theme apps). When every dark verdict of the batch is `pass` or `bug`, rerun it with `QA_THEME=light` into `raw/<batch>-light/`:

   ```bash
   QA_THEME=light PLAYWRIGHT_JSON_OUTPUT_FILE=<abs>/.qa/run-<key>/raw/<batch>-light/report.json \
     npm run e2e:evidence -- qa-<key>/ --grep '<same grep as the dark run>' --output <abs>/.qa/run-<key>/raw/<batch>-light --reporter=list,json
   ```

   A case healed and rerun in dark later also reruns in light. A case's verdict is final only after its light run is collected and judged, or the light pass is waived. Until then, record it in `progress.json` as `partial`; write its plan row and post its comment only after that. Skip the light pass only when the user waives it for the pass, and then say so in every verdict line. (When the app's default theme is light, swap the roles: the default run is light and the second run sets `QA_THEME=dark`.)
4. **Collect** each run: `scripts/collect.py .qa/run-<key>/raw/<batch>/report.json .qa/run-<key>` for the dark run, and `QA_THEME=light scripts/collect.py .qa/run-<key>/raw/<batch>-light/report.json .qa/run-<key>` for the light run. It files each test's output folder (the folder of its `video` attachment) under `QA-NN/<Role>/`, or `QA-NN/<Role>/light/` when `QA_THEME=light` is set on the collect command, with a `storyboard.md`. The script empties its target folder first, so a light report collected without `QA_THEME=light` replaces the dark evidence. `trace.zip` stays in `raw/` and never leaves the machine: it carries the session's bearer token.

## 6. Judge each case

Read the JSON report: `suites[].specs[].tests[].results[]` carry the status, the error, the failed step, and the attachment paths. Exactly one status per case:

| Status | When |
|---|---|
| `pass` | Every step ran and every assertion held. The case is run. |
| `bug` | The preconditions held and an Expected-Result assertion failed on two runs of that case, or a theme defect shows (below). The case is run. |
| `runner-defect` | Open. The spec failed before its verdict: a locator, a timeout, a flaky overlay. Heal it and rerun, at most twice at the same failing step (a rerun that gets past that step starts a new count); still failing: this status, with the last error. |
| `blocked` | Open. The `Preconditions` step failed, or a case it depends on did not pass. Name the missing precondition or that case. |
| `manual` | Open. The verdict needs a human eye, or the plan contradicts itself (below). |

**Theme defects.** Hold each light screenshot against the same step in dark, and read both runs' contrast attachments. It is a `bug` when: text or a control is below WCAG AA; an element keeps the other theme's colours (a literal colour where the design rules want a token); something visible in one theme is missing in the other; or the layout differs between themes. The draft carries a `[UI]` tag, both screenshots and the design rule it breaks.

An open case is not run. After each batch, ask the user one grouped question with every open case and what it lacks; take the path they give (data to build, a flag to set, a plan row to fix, a verdict from their eyes) and run the case again. A verdict the user gives is recorded as `pass` or `bug` with "judged by the user" in its line.

Before calling a case `bug`, hold its Expected Result against the plan's other rows, the domain docs and the current spec (the spec sources in the setup). The current spec is the arbiter. When the app matches the spec and the plan row does not (a later release changed the behaviour, a row contradicts another), the plan row is wrong: the case is `manual`. Name the spec requirement, fix the row with the user, and run the case again. When the app contradicts the spec, it is a `bug` that cites the requirement. A plan role that cannot even load the surface is handled by `spec-patterns.md → The role the plan names is refused`.

A `bug` is decided by the assertion, never by loosening it, and no spec ends as `test.fixme` or `skip`.

A case split into several tests (one per role) is run only when every test is `pass` or `bug`; it is then `bug` if any test is `bug`, else `pass`. While any test is open, the case takes that open status (the first of `runner-defect`, `blocked`, `manual` among its tests) and stays open. Its line names each role's status.

Write each verdict into the plan as soon as it is known, so a pass cut short still leaves the plan current. An open status goes into the plan when its batch ends; only `pass` and `bug` wait for the light run (step 5 → Light pass). Write it with `scripts/verdict.py <plan> QA-NN "<status>: <what happened, one line>" [draft]`. The **Actual Result** cell starts with the bare status word, no backticks: `progress.py` and `post.py` read a case as run only when the cell starts with `pass` or `bug`. **Bug Issue** = `draft` for a `bug`, empty otherwise. The plan keeps its shape: edit those two cells, nothing else. The one exception is a plan row fix the user approved (above): it may change that row's other cells.

When the user asked for a progress page, rebuild it at the same moment: `scripts/progress.py <plan> .qa/run-<key>/progress.json .qa/run-<key>/progress.html`. `progress.json` maps each open case id to `[state, note]`: state `partial` when some of its tests or themes ran, `pending` otherwise (the script accepts no other state); the note names its open status and what it lacks. Write `{}` when no case is open. When the user named a tracking issue, comment the case on it once its final verdict is `pass` or `bug`: `scripts/post.py <issue> <plan> .qa/run-<key> QA-NN <Role>...`.

## 7. Restore the local changes

Restore everything the pass changed, on every exit path:

- **Pass data**: reverse every actor swap still in effect (`data-scripts.md → Actor swaps`). Seeded blocks stay for reruns; report them in step 9 with their reset scripts.
- **Legacy database**: when the pass swapped it in, swap it back (`references/legacy-migration.md`, step 6).
- **Persona and role**: follow the recipe's restore steps (persona first, then role) from the backup files.
- **Flag overrides**: revert each local override the user approved in step 2.

After a successful restore, delete the backup files.

Stop the app only if this run started it.

## 8. Draft one issue per bug

`.qa/run-<key>/issues/QA-NN.md`: the title (with a theme tag reused from neighbouring issues, `gh issue list`, when one fits), type, labels and body per the bug report format the setup names (default: Summary, Steps, Expected, Actual, Environment), then an `Attachments:` line listing the case's evidence files. Steps come from the plan row, Expected from the plan row and the requirement it cites, Actual from the failed assertion, Environment from the run (branch, `git rev-parse --short HEAD`, mode, role, date).

Collect every fixture gap of the pass in `issues/local-data-fixture.md`: one bug report against the local fixture the setup names, listing per gap the cases that needed it and the script that supplied it. The published issue carries the scripts themselves, inline in fenced code blocks, so the fixture owner can fold them in.

## 9. Exit

Done when every case in the plan is run (each row's Actual Result reads `pass` or `bug`) in both themes unless the app has one or the user waived the light pass, every `bug` has a draft, and step 7 has restored any role switch, persona state, actor swap, legacy database swap and flag override. A case the user chooses to defer keeps the pass open: report it as not run, never as done. Report the counts per status, the plan path, the run folder, the seeded blocks left in place with their reset scripts, and the next step: `/qa-triage` once the pass is done, or the cases still open.
