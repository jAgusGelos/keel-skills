# Branch plan: `/qa-plan branch`

Plan the current branch's changes in the shape the test-case template owns (SKILL.md step 6), so `qa-run` and `qa-triage` read it the same way as a window plan.

## 1. Find the change

- **Branch and base**: the current branch, and its base: the base of its open PR (`gh pr view --json baseRefName`) when one exists, else the integration branch from `docs/qa-setup.md` (or the parent feature branch it was cut from). The diff is `git diff $(git merge-base origin/<base> HEAD)`: it compares the fork point with the working tree, so it includes committed and uncommitted edits. Add the untracked files that `git status --porcelain` lists with `??`.
- **Issue**: the issue id in the branch name or the PR's closing references.

## 2. Collect the requirements: every source that exists

Take the sources in this order, and read each one that exists:

1. **Spec files** the diff touches (SKILL.md step 3, *The change spec*): OpenSpec change folders, a `spec-first` plan under `.workspace/features/<ticket>/`, `*.feature` files. Their scenarios are the requirements. Keep a scenario, or fold it into a case, by that rule: a WHEN a tester can provoke and a THEN visible in the UI or an API response.
2. **Issue**: `gh issue view <id> --json title,body,comments`: the acceptance criteria, and any plan comment.
3. **The user**: when the first two give no browser-observable requirement, ask the user what to test. Show them the diff's user-facing surface (routes, components, endpoints) to answer against. Their answer is the requirement list.

The diff grounds each requirement in a screen, a role and the data it needs, as step 3 does for a PR.

## 3. Write the plan

Write `.qa/branch-<branch-short-name>.md` after the existing-plan check in SKILL.md step 6, group the cases into flows as step 4 does, and check every row against the code as step 5 does:

- **Title line**: in place of the window line, write exactly `Branch: <branch> · base <base> · <sha> · <n> cases`. `<branch>` is the full branch name (`git branch --show-current`), `<base>` the base as a bare branch name (no `origin/` prefix), `<sha>` the output of `git rev-parse --short HEAD`, and `<n>` the case count. `qa-triage` reads the branch from the `Branch:` label.
- **Environment**: the local app of this branch.
- **Issue / PR** column: the issue link, plus the spec or change name when there is one.
- **Coverage matrix**: `| Requirement | Source | Cases |`, with one row per kept scenario, criterion or user answer.
- **Excluded**: `| Requirement | Source | Why |`, with one row per requirement no browser can observe.

Done when every scenario and acceptance criterion found in step 2 appears exactly once, in the coverage matrix or in Excluded. Report the path, the branch, and the case count; the next step is `/qa-run <path>`.
