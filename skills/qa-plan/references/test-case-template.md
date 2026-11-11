# Test case table

The fixed shape of every `qa-plan` file. One row per test case, these nine columns, in this order. Add no column and drop none: a tester and a spreadsheet both read this table, so the shape stays stable across passes.

## The table

```md
| # | Test Case Title | Issue / PR | Description | Preconditions | Execution Steps | Expected Result | Actual Result | Bug Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA-01 | Cancel an order from Scheduled and from Active | [#<pr>](https://github.com/<owner>/<repo>/pull/<pr>) · [#<issue>](https://github.com/<owner>/<repo>/issues/<issue>) | Cancelling was reachable only after a prior step; it is now offered directly in both states. | Role: `Operator`. One Scheduled order and one Active order on the same customer. | 1. Open the Scheduled order → **Cancel** → confirm.<br>2. Open the Active order → **Cancel** → confirm. | Cancel is offered in both states with no prior step required, and the order reaches Cancelled from each. | | |
```

## Column rules

- **`#`**: `QA-01`, `QA-02`, ... in execution order. The id the coverage matrix and any raised bug point back to.
- **Test Case Title**: what the tester proves, in one line. Name the screen or flow so the row is findable without reading the steps.
- **Issue / PR**: every PR the row covers, as a Markdown link to `https://github.com/<owner>/<repo>/pull/<n>`, plus the closed issue as `/issues/<n>` when the PR closes one. Separate multiple links with `·`.
- **Description**: why the row exists: the behaviour that changed, in one or two sentences. The tester reads this to know what "wrong" would look like.
- **Preconditions**: **the role comes first**, as ``Role: `Operator`.`` (use the role names from `docs/qa-setup.md`), then the state that must exist before step 1 (records, view, browser state). In a role-scoped app, a row whose role is missing is not runnable. An app with a single kind of user writes ``Role: `User`.``
- **Execution Steps**: numbered, `1.`, `2.`, ... separated by `<br>` so they stay inside the cell. One action per step; bold the control the tester clicks.
- **Expected Result**: the observable outcome, specific enough to fail on. Where a PR moved a policy, the negative check belongs here too ("and `Viewer` sees no Price column").
- **Actual Result**: left **empty**. The tester (or `qa-run`) fills it during the pass.
- **Bug Issue**: left **empty**. The tester writes the issue number raised when Actual and Expected disagree.

## Sections around the table

The file carries these, in this order:

1. **Title and window line**: window dates, PRs merged, in scope, excluded, case count.
2. **Environment**: the local app of the branch under test (window plan: an up-to-date checkout of the integration branch), as `qa-run` runs it.
3. **Before you start**: what the pass needs before QA-01:
   - **Accounts** needed per role.
   - **Data plan**: the named records several rows share, grouped by block (for example "Order lifecycle: C1 with O1 Active and O2 Draft"), each marked *in the local fixture* or *to seed*. Anything a single row needs belongs in that row's Preconditions instead.
   - **Needs from the user**: the rows a pass cannot drive from one recorded session. These are rows that need another user's own screen, a sign-out, a real sign-in, an external job, or a feature flag change, with what each needs.
   - **Themes**: when the app has a light and a dark theme, every row with a screen is checked in both (`qa-run`); rows do not repeat it.
4. **Test cases**: the table above.
5. **Coverage matrix**: `| PR | Title | Cases |`, one row per in-scope PR. The reverse direction of the Issue / PR column, and the evidence for the exit gate.
6. **Excluded**: `| PR | Title | Why |`, one row per PR with no user-observable surface.
