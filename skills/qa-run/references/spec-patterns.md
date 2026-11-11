# Spec patterns

Techniques and traps that recur across `qa-run` passes. Import the shared helpers from `e2e/qa-evidence.ts` and `captionedStep` from `e2e/evidence-caption.ts` (both copied from [`../assets/`](../assets/)) instead of copying them into a pass folder.

## Base rules

- One spec file per test, under `<frontend>/e2e/evidence/qa-<key>/`. Pass the folder on every run: `e2e/evidence/` is gitignored and keeps earlier passes.
- Every user-visible step goes through `captionedStep(page, "<step>", async () => { ... })`, so the Playwright report, the video caption and the storyboard share one description.
- Screenshot the **viewport**, not the full page, at the end of each step, numbered in step order (`01-open-orders.png`), after `scrollIntoViewIfNeeded()` on the element that proves the step. A full-page shot clips fixed drawers and overlays.
- Locate by role and visible text (`getByRole`, `getByLabel`), never by generated CSS classes.
- A failing step is evidence too: keep the failure screenshot. Never rerun until it passes by loosening the assertions.

## Helpers

| Helper | Use it for |
|---|---|
| `applyTheme(page)` | Every spec's first line: sets the pass theme (`QA_THEME`, dark by default) before the app loads, through `prefers-color-scheme` and the theme storage key when the app stores one. |
| `contrastIssues(scope)` | After each step's screenshot: text below WCAG AA against its effective background. Attach the list; judge it by SKILL.md step 6. |
| `spaNavigate(page, url)` | Moving between screens without a document load, when session-scoped state must survive (a reveal is masked again by any `goto` or reload). Works with history-based routers. |
| `apiCapture(page)` | A direct API call with the app's own bearer, for Expected Results about response fields or status codes. It captures only the API origin's token: the first authorized request of a page is often a third party's (an identity provider, Graph). |

`qa-evidence.ts` has no date helper: write a local `pickDate` for read-only calendar widgets in the pass's spec folder.

## Traps

- **The caption is on the page.** `captionedStep` injects its step text into the DOM, so a substring `getByText("Review Queue")` also finds the caption "Look for Review Queue". Match with `{ exact: true }` or inside a scoped container.
- **Escape travels.** Escape closes the open overlay and then the drawer or dialog under it, or raises "leave without saving?". Close a dropdown, split-button menu or picker with its own toggle; answer the leave prompt with its button.
- **A control that already holds the value.** A server draft may already select an option; clicking a selected toggle can clear it. Check `aria-pressed`, `aria-checked` or the library's selected class before clicking.
- **Autofocus opens pickers.** A dialog whose first field is a calendar opens its panel over the controls below. Click the dialog title to close it before acting.
- **Upper-case headers.** CSS `text-transform` makes `innerText` upper-case; read column headers with `allTextContents()`.
- **Paged lists.** A candidate or option list can page; search for the entry before asserting it is absent.
- **Row-shaped buttons.** Some table libraries render clickable rows as `<tr role="button">`, and a paginator's buttons share the region. Anchor on the row's accessible name, never on `getByRole('button').first()`.
- **Overlays can dismiss on a legit click.** A popover may close when the control under the cursor re-renders. Reopen it if hidden, click, reopen if hidden, then assert. Run such a spec twice before calling it green.
- **Signing out.** Sign out only in the test's own browser context, then wait for the identity provider to return to the app before the next navigation. A navigation that races the sign-out is signed in again silently by a still-valid SSO session. The recorded session file stays untouched (compare its checksum before and after).
- **Dashboards mask text.** A job dashboard may render job names and arguments masked; confirm a job's outcome in the rows it writes, in SQL.
- **Session-local state.** Settings the app keeps in browser storage (theme, layout, cached selections) are absent at the start of every test. Seed them with `addInitScript`.

## Verdict techniques

- **Soft assertions for defects.** Use `expect.soft` for a clause that exposes a defect when the rest of the case can still run. The run then yields the bug and the verdict of every other step. Hard `expect` stays for what later steps depend on.
- **The role the plan names is refused.** When the plan's role cannot even load the surface (a 403 on a lookup the page needs), record `bug` under that role with its evidence. Then add the smallest role that loads the surface and verify the remaining steps. The second test's tag names the session that ran (`@role:Member+Reporting`), so `collect.py` files it in its own folder (`QA-NN/Member+Reporting/`) and the refused run's evidence stays; its grep escapes the `+` (SKILL.md step 5). The verdict says which steps ran with the added role.
- **Provoke from the code.** When the plan's example data does not produce the observable (it names a "warning" the code never raises), read what the code actually raises (an enum of kinds, the guard that throws) and build the data that triggers it. Then correct the plan row's example with the user (SKILL.md step 6, the plan row fix).
- **A route smoke counts refused calls.** A route has loaded only when no API call it makes returns 401, 403 or 5xx and the console stays clean: a route guard can admit a role whose page then fails its own requests. Record the API origin's responses and the console per route, and attach the route matrix.
- **Find the failing request.** When a run shows a refused or failed request, read the failed test's `trace.zip` locally (`npx playwright show-trace`, or its `.network` entries) to name the endpoint in the draft. The trace itself stays on the machine.
- **One session, several actors.** With a single signed-in user, a case that needs that user as a record's author and as its subject swaps the record's actor columns in SQL between steps (`data-scripts.md → Actor swaps`). A case that needs *other* users' own screens takes the user's path from SKILL.md step 2: a per-role session, a SQL check of their data, or the user signs in.
