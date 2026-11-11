---
name: qa-triage
description: |
  Close a qa-run pass: publish the confirmed bug drafts with their video, write the issue numbers back
  into the plan, propose durable regression tests for failed and critical green cases not already
  covered, and offer to delete the evidence nobody needs. Last step of the qa-plan -> qa-run ->
  qa-triage chain. Use when the user says "qa triage", "publish the QA bugs", "close the QA pass", or
  "/qa-triage".
version: 1.0.0
category: development
depends: [qa-run, create-pr, write-tests, tdd, spec-first]
disable-model-invocation: true
---

# qa-triage

`/qa-triage [plan-path]`: the plan defaults to the newest `.qa/*.md` plan whose Actual Result column `qa-run` has filled. Its run folder is `.qa/run-<key>/`, with `<key>` as `qa-run` defines it. Project conventions (bug report format, board fields, regression suite) come from `docs/qa-setup.md` (`qa-run/references/project-setup.md`).

A **branch plan** (`.qa/branch-*.md`) tests work that is not merged yet: in step 1, a confirmed case bug goes to the branch's pull request as a review, not to an issue, and in step 2, a bug's test ships with its fix.

Triage only a finished pass: every case in the plan is run (`qa-run` defines it). Check this before step 1. When any row is still open, stop here: list the open ids and give the command that finishes the pass, `/qa-run <plan-path> <open ids>`. Nothing below runs on an unfinished pass.

Three steps in order: **publish** what the user confirms, **propose** what the regression suite should keep, **clean** what neither needs. The only GitHub writes are step 1's, each after an explicit yes.

## 1. Publish the bugs

Load every draft in `issues/`: one `QA-NN.md` per plan row whose Bug Issue reads `draft`, and `local-data-fixture.md` when the pass had fixture gaps and its first line is not `Published: #<n>`. A fixture draft with that line is already published: skip it. The fixture draft always becomes an issue, on a branch plan too, because the fixture lives on the integration branch.

1. **Attachments.** Prepare each file for `gh --attach` (gh 2.99+): images as they are; videos transcoded to H.264 MP4 (`ffmpeg -i video.webm -c:v libx264 -pix_fmt yuv420p -crf 28 -preset fast -movflags +faststart -an video.mp4`) within the size limit the setup names (10 MB by default); text files inline in fenced code blocks, never attached; `trace.zip` never, since it carries bearer tokens. A file that cannot meet these rules is dropped (screenshots go up, the video stays local); say in the draft which file was converted or dropped. Then remove the draft's `Attachments:` line, because its local paths must not reach GitHub. In its place, an issue draft gets one `![](<path>)` per attached file, each in its own paragraph; a review draft gets the link to the attachments comment (step 4).
2. **Find the pull request** (branch plan only). `gh pr view <branch> --json number,url,author` names it and its author. `<branch>` is the full branch name after the `Branch:` label in the plan's title line. When the branch has no pull request, ask the user before step 3: open one first with `/create-pr`, or publish those drafts as issues.
3. **Show and ask, once.** Show every draft in full, then ask one grouped question. It asks which drafts to publish and, for each issue draft, the board fields the setup lists (iteration or backlog, milestone, assignee). Take these answers per draft. A pull-request review needs none of them.
4. **Publish** each confirmed draft. Write the draft's body (everything after its title, type and label lines) to a temp file. Pass that file as `--body-file`, the title as `--title`, and each label as `--label`.
   - **Issue**: `gh issue create` with the draft's `--title`, `--body-file`, its `--label`s (and `--type Bug` when the repository uses issue types), `--milestone` and `--assignee` from that draft's answers (omit each one the user left empty), and one `--attach` per file.
   - **Pull-request review** (branch plan): `gh pr review <pr> --request-changes --body-file <temp file>`. GitHub refuses a request for changes on your own pull request: when the PR author equals `gh api user --jq .login`, use `--comment` instead. `gh pr review` takes no `--attach`. First post the files in `gh pr comment <pr>` with one `--attach` per file. Then post `gh pr review`, its body file ending with that comment's URL.
   - **Write back at once.** Right after each publish, before the next draft, write its `#<n>` or review link into the plan's Bug Issue cell. For the fixture issue, write `Published: #<n>` as the first line of `issues/local-data-fixture.md`. Then, for an issue, set the board fields with that draft's answers (`gh project item-add` and `gh project item-edit`, when the setup uses a project board). When `gh issue create` or `gh pr review` exits non-zero but the issue or review exists (an issue URL printed, or this draft's review visible in `gh pr view <pr> --json reviews`: authored by `gh api user --jq .login`, with this draft's body; an earlier draft's review does not count), count it as published: write its `#<n>` or review link back, and report the failed file. The attachments comment alone never counts as published. A rerun then never loads a published draft again. A draft the user declined keeps `draft`.

Done when every confirmed draft is published: each issue is on the board with its chosen fields, each case row carries its issue number or review link, each declined row still reads `draft`, and every failed upload is reported with the issue or review URL.

## 2. Propose regressions

**Candidates**: every `bug` row, published or not; and every `pass` row whose case walks a **critical journey**: a flow where a silent break costs money, data or access (sign-in, payments, invoicing, permissions, data export, anything that writes records other users depend on).

For each candidate, look for **existing coverage** before proposing anything: three reads, no test runs.

1. **Journey suite.** Run the regression suite's list command from the setup (for Playwright: `npx playwright test -c <regression config> --list --reporter=json`) to get every spec's file and title. Read each spec whose title or routes touch the case's screens. Follow its whole navigation: the `page.goto(` routes and the in-app clicks that change the page. The case is covered only when a spec walks the same journey and asserts the case's Expected Result.
2. **The case's PRs.** `gh pr view <n> --json files` for each PR in the row's Issue / PR cell; the test files it added are the lower-level tests of that behaviour. For a branch plan, read the test files in the branch diff instead.
3. **The failing code** (bugs only). The component, handler or controller the failing step touched, then its sibling test file: the "extend before adding" candidate.

Then choose the **lowest level that would have caught it**:

| Level | Choose it when |
|---|---|
| Unit | The defect lives in one function or component's logic (a calculation, a mapping, a condition, a rendered binding). |
| Integration | The defect needs a real boundary: a database query or constraint, an endpoint's authorization, serialization between API and UI, a transaction. |
| End-to-end journey | The defect only shows when the layers connect across screens, or the case is a critical green journey. One spec per journey, asserting only that the layers connect; the details stay in lower levels. |
| No test | The defect was data or configuration, not code, or the behaviour is already pinned at a lower level. Say why. |

Write one line per candidate: `QA-NN → <level> → <file to extend or create> → <assertion that fails today>`, or `QA-NN → covered → <spec:title>`, or `QA-NN → no test → <why>`. A **regression line** is a line that names a test to write or extend; a `covered` line or a `no test` line is not one. A bug's test is written red first with its fix; a green case's journey spec asserts only that the layers connect.

Write the lines to `.qa/run-<key>/triage.md` with their QA ids and issue numbers, and show them. Done when every candidate has exactly one line.

## 3. Clean the evidence

The evidence of a `pass` case with no regression line is **spent**: either the case was no candidate, or its line reads `covered` or `no test`. List the spent `QA-NN/` folders with their size and ask once: *delete these?* On a yes, delete exactly those folders. Delete a batch's `raw/<batch>/` and `raw/<batch>-light/` folders too, but only when every case in that batch is on the list; the batch's `report.json` names its cases. Everything else stays.

## 4. Exit

Report: issues published (numbers, the fixture issue among them), reviews posted (links), drafts declined, regression lines by level, folders deleted, and the next step for each regression line worth doing now:

- **Bug with an issue**: fix it test-first with `/tdd` (the regression line's test is the first red test), or plan it with `/spec-first` when the fix is not obvious.
- **Bug on a branch plan**: the fix and its test land on that branch before it merges.
- **Critical green case**: `/write-tests` with the line, to add the journey or lower-level test to the suite.
