# Project setup: `docs/qa-setup.md`

`qa-plan`, `qa-run` and `qa-triage` work on any web app with a Playwright-drivable UI. What differs per repository (how the app starts, how a session signs in, how roles switch, where the local database lives) is written once in `docs/qa-setup.md`, committed to the repository. The skills read it on every run; nothing project-specific lives in the skills.

When the file is missing, `qa-run` preflight stops, offers to draft it from the template below by reading the repository (package scripts, compose files, README, auth code), and asks the user to confirm each value before the first pass.

## One-time install

1. **Playwright** as a devDependency of the frontend package (`@playwright/test`, pinned), plus the browser: `npx playwright install chromium`.
2. **Helpers**: copy [`../assets/qa-evidence.ts`](../assets/qa-evidence.ts) and [`../assets/evidence-caption.ts`](../assets/evidence-caption.ts) into the frontend's `e2e/` folder, and [`../assets/playwright.evidence.config.ts`](../assets/playwright.evidence.config.ts) next to them. Adjust `baseURL` and the storage-state path in the config.
3. **Package scripts** (names are a convention; the setup file records the real ones):

   ```json
   "e2e:login": "playwright codegen --save-storage=e2e/.auth/user.json http://localhost:4200",
   "e2e:evidence": "playwright test -c e2e/playwright.evidence.config.ts"
   ```

4. **Ignore** `.qa/`, `e2e/.auth/`, `e2e/evidence/` and `e2e/results/` in `.gitignore`. Evidence specs are per pass, the session file holds credentials, and a `trace.zip` holds bearer tokens.

## Template

```md
# QA setup

Read by the qa-plan, qa-run and qa-triage skills.

## Repository
- Integration branch: develop
- Frontend directory: src/ui
- Domain docs: docs/architecture.md, docs/glossary.md
- Spec sources: openspec/specs, openspec/changes   (or .workspace/features, features/*.feature, none)
- Design rules: src/ui/DESIGN.md   (theme tokens; omit when none)

## App
- Start command: docker compose up -d && npm run dev   (dev mode, from the checkout under test)
- Ready check: http://localhost:4200 answers, and http://localhost:5000/health returns 200
- UI URL: http://localhost:4200
- API origin: http://localhost:5000
- Themes: dark (default), light   (or: single theme)
- Theme storage: localStorage key `app-settings`, field `theme`   (or: prefers-color-scheme only)
- Feature flags: where the effective values are read (config files, env vars)

## Sessions and roles
- Login command: npm run e2e:login   (a human signs in; agents never type credentials)
- Session file: src/ui/e2e/.auth/user.json
- Roles: Admin, Operator, Viewer
- Role strategy: per-role sessions | role-switch recipe
  - per-role sessions: one recorded file per role, src/ui/e2e/.auth/<Role>.json
  - role-switch recipe: docs/local-role-switching.md (backup, switch, verify, restore steps)
- Local data check: how to confirm the local fixture is loaded and the session user exists

## Database (only when passes seed data)
- QA_SQL: docker exec -i app-db psql -U app -d app -v ON_ERROR_STOP=1 -At -F'|'
- Fixture: docs/local-data/README.md   (how a developer loads the local fixture)
- Migration tool: npx prisma migrate deploy | dotnet ef database update | ...

## Issues
- Bug report format: CONTRIBUTING.md#bug-reports   (title tags, labels, type)
- Board: project/iteration fields to set, or none
- Attachments: gh --attach (gh 2.99+); video as H.264 MP4 up to 10 MB

## Regression suite (for qa-triage)
- List command: npx playwright test -c e2e/regression/playwright.config.ts --list --reporter=json
- Unit/integration test locations: *.spec.ts next to components, tests/ for the API
```

## Role strategies

Every case runs as the role its Preconditions name. Pick one strategy per repository:

- **Per-role sessions** (default, no database writes). The user records one session per role with the login command, saved as `e2e/.auth/<Role>.json` with test accounts that hold that role. A batch selects its session with `test.use({ storageState: "e2e/.auth/<Role>.json" })` in the spec. Switching a batch means nothing more than picking the file. Missing file: the case is `blocked` until the user records it.
- **Role-switch recipe** (one account, the local database changes its role). The repository documents the recipe in the file the setup names, with numbered steps that `qa-run` follows: **(1)** identify the session's identity, **(2)** back up its role rows into `.qa/role.backup.sql` as the statements that restore them, **(3)** switch, **(4)** wait out any role cache or restart, **(5)** verify on a surface only the target role sees (or only it is denied), **(6)** restore from the backup. Personas (a team lead, an owner of a record) are extra rows of the same recipe, with their own backup file `.qa/persona.backup.sql` and restore step.

The steps below refer to these as *switch*, *backup* and *restore*; with per-role sessions the backup and restore are no-ops.
