---
name: qa-plan
description: |
  Build a manual end-to-end regression plan (one table of ordered, role-scoped test cases) from the
  PRs merged into the integration branch since a given date, or from the current branch's changes.
  First step of the qa-plan -> qa-run -> qa-triage chain. Use when the user says "qa plan",
  "regression plan", "plan a QA pass", "manual e2e plan", "what should we test from this release",
  "test plan for this branch", or "/qa-plan".
version: 1.0.0
category: development
depends: [qa-run]
---

# qa-plan

`/qa-plan <since> [until]`: dates as `YYYY-MM-DD`; `until` defaults to today. No argument, no run: ask for one.

`/qa-plan branch`: plan the current branch's changes instead, by [`references/branch-plan.md`](references/branch-plan.md). It reuses steps 3 to 6 below and writes the shape [`references/test-case-template.md`](references/test-case-template.md) owns.

Turn the window's merged work into a **regression pass**: the ordered set of manual end-to-end cases a tester runs against a local build of the integration branch to confirm that what shipped actually behaves. Report only: the single deliverable is `.qa/manual-e2e-<since>-to-<until>.md`, written in English. Add `.qa/` to `.gitignore`: the plan is a working artifact of one pass, so it stays out of the repo and out of every commit.

`gh` must be installed and authenticated. If it is not, stop and say so.

## 0. Project setup

Read the repository's QA setup file, `docs/qa-setup.md` (shape in [`../qa-run/references/project-setup.md`](../qa-run/references/project-setup.md)). This skill uses its **integration branch**, **frontend source directory**, **roles**, **spec sources** and **domain docs**. When the file does not exist, use these defaults and say so in the plan's Environment section: integration branch `develop` when `origin/develop` exists, else the remote default branch (`git remote show origin`); frontend directory found from the repo layout; roles from the authorization code; spec sources as listed in step 3. Offer to write the setup file from the template once the pass is planned.

`<integration>` below is the integration branch.

## 1. Collect what actually landed

The integration branch's history is the ground truth for what landed. A PR search is not, because stacked PRs merge through their parent branch and mid-stack bases move.

```
git fetch origin <integration>
git log origin/<integration> --no-merges --since='<since> 00:00:00' --until='<until> 23:59:59' --format='%h %s'
```

Give each bound a time of day: a bare date makes `git log` use the current time, which drops part of the first and last day. `--no-merges` skips pure merge commits; the commits they bring in are listed on their own.

Each squash-merge subject ends in `(#<pr>)`. A commit without that suffix (a direct push, for example a migration fix) is still part of what landed. Resolve its PR:

```
gh api repos/{owner}/{repo}/commits/<sha>/pulls --jq '.[].number'
```

When that returns a PR number, add it to the set. When it returns nothing, the commit becomes its own window entry, named by its short sha. Steps 2 and 3 read it with `git show <sha>` in place of a PR body, and it fills every PR column and Issue / PR cell with the sha linked to `/commit/<sha>`. The PR numbers and these sha entries are the window. For each PR:

```
gh pr view <pr> --json number,title,body,mergedAt,url,labels,files,closingIssuesReferences,headRefName
```

An **epic PR** (its `headRefName` is a long-lived feature branch that other PRs targeted, such as `epic/*` or `feature/*`) squashes many child PRs into one commit, and its body rarely describes each one. Read its children too:

```
gh pr list --base <headRefName> --state merged --limit 200 --json number,title,body,url,files,closingIssuesReferences
```

The children feed steps 2 and 3 as part of the epic PR. The epic PR stays the one window entry: the coverage matrix and the exit count name it, and its row's Issue / PR cell links the children it covers.

## 2. Triage every PR

Sort each one into **in scope** (a human can observe the change through the UI or an API response) or **excluded**: CI, tooling, agent skills, docs, test-only work, and refactors with no behavioural surface. An excluded PR keeps a one-line reason and stays in the file, so a reader can see nothing was silently dropped.

When a PR's user-visible surface is unclear, put it in scope and let the case say what to look for.

## 3. Read each in-scope PR for testable behaviour

Establish four things per PR before writing any case:

- **Flow**: the user journey it touches, by module and screen. Use the domain docs the setup file names (architecture overview, glossary) for the module map and the terminology the case must use.
- **Role**: who sees it. When the app is role-scoped, a case that does not name the role it runs as is not runnable. When a PR moves a policy or a scoped surface, add the negative check: a role that must *not* see it. When a row runs as a narrow role, read the server-side authorization rule (an `[Authorize]` policy, a route guard, a middleware check) of every endpoint the screen calls on load. When that role does not satisfy one of those rules, name the endpoint and its rule in the row's Description ("loads `GET /settings/levels`, which requires `ReportingPolicy`"). The tester then knows the screen may refuse the role.
- **Data prerequisite**: the records that must already exist (an order, a price list, an invoice), named so that several rows can share them. A PR carrying a schema migration also names the pre-existing records that must survive it: list them in the Data plan, and assert in the row's Expected Result that they still read correctly after the deploy.
- **Observable**: what changes on screen, in a number, or in an export.

The PR body and its linked issue carry the intent; the diff is the fallback. The **change spec** carries the assertions: every in-scope PR gets one read, by one of the paths below.

### The change spec

A spec written in scenario form (WHEN/THEN, Given/When/Then, or acceptance criteria) holds test cases already written, sharper than any PR body. Look for it in this order, and take the first that applies:

- **Spec files the merge touched.** The setup file names where specs live. Common layouts: OpenSpec (`openspec/specs/` for the main specs, `openspec/changes/<name>/` for a change's delta, with `#### Scenario:` blocks), a feature planning folder (`.workspace/features/<ticket>/plan.md` from `spec-first`), or `*.feature` files. Read the lines the merge added, from the commit, never from the working tree:

```
git show --format= --unified=0 <commit> -- <spec paths> | grep '^+' | grep -v '^+++'
```

  A change folder is often renamed on archive or removed, so the path a merge added may no longer exist in the working tree.
- **No spec in the diff**: read the linked issue with its comments (`gh issue view <issue> --comments`); a plan comment or acceptance criteria there are the spec. Take the assertions from it, the PR body and the diff.

Keep the scenario whose **WHEN** a tester can provoke and whose **THEN** is observable through the UI or an API response. A later PR in the window can change what an earlier one shipped (a new column, a new grouping): the Expected Result states the behaviour of the spec at the window's end (`git show origin/<integration>:<spec file>` for a window plan, the working tree for a branch plan), not of the first PR. The other scenarios state internals (a partition key, a query shape); they sharpen the row's Description and go no further.

A kept scenario lands inside the row it belongs to: its THEN joins **Expected Result**, its WHEN adds an **Execution Step**. It never opens a row of its own. A window carries an order of magnitude more scenarios than cases, and one row per scenario yields a plan nobody runs.

## 4. Group into flows

Collapse PRs touching the same journey into one end-to-end case that walks the journey once and picks up each PR's observable along the way. Split when the roles differ, the preconditions conflict, or a case runs past roughly ten steps.

Order the file so a tester runs it top to bottom: setup-heavy flows first, flows that consume their output after. A row that builds on another names it in Preconditions ("O1 after QA-05"). Two rows that need incompatible states of the same records (one needs a team assigned, the other needs it absent) either get separate records or state the order and the change between them.

## 5. Check every row against the code

Search the frontend templates and routes at the window's end for every screen, route and control label a row names: `git grep -n '<label>' origin/<integration> -- <frontend dir>` for a window plan, and the working tree (`git grep -n '<label>' -- <frontend dir>`, which includes uncommitted edits) for a branch plan. A label a later PR renamed, a route that now redirects, or a control that moved is rewritten to what the code has now. Every row passes this check before the file is written.

## 6. Write the file

[`references/test-case-template.md`](references/test-case-template.md) owns the shape: one row per case, nine fixed columns, and the sections around the table. Follow it exactly: a pass compares against the previous one, so the shape stays stable. **Actual Result** and **Bug Issue** ship empty; the tester fills them.

Before you write, check the target path. When the file exists and any **Actual Result** or **Bug Issue** cell holds a value, a run has recorded verdicts in it: a re-plan renumbers the `QA-NN` ids and orphans that run's evidence and `.qa/run-<key>/issues/QA-NN.md` drafts. Stop and ask the user: write the new plan beside it under the next free suffix, or overwrite. The next free suffix is the first of `-2`, `-3`, ... before `.md` whose file does not exist; a suffixed file that exists already holds an earlier re-plan, so never overwrite it without this same verdict check and question. `qa-run` keys its run folder on the plan file name without `.qa/`, the `manual-e2e-` prefix and `.md`, so a suffixed plan gets its own folder (for example `.qa/run-<since>-to-<until>-2/`) and leaves the earlier run's evidence intact. When both columns are empty in every row, replace the file without asking.

## 7. Exit

Every window entry from step 1 (each PR number and each sha entry) appears exactly once, in the coverage matrix or in Excluded, and the two counts sum to the window's count. Verify that before handing off, then report the path, the window, the entry count, and the case count. The next step is `/qa-run <path>`.
