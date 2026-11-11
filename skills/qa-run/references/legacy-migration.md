# Legacy data through a migration

For a case that checks that data saved before a release survives its schema migrations: "orders created before the release still load", "a discount recorded before the release keeps its amount". The local fixture targets the current schema only, so the pass builds the old data itself. Commands use the migration tool named in `docs/qa-setup.md`.

1. **A second database.** Create `<db>_legacy` next to the local database. Migrate it to the last migration *before* the release under test (for example `dotnet ef database update <migration> --connection "<legacy connection>"`, `npx prisma migrate resolve` plus `migrate deploy` from that commit, or `alembic upgrade <revision>`). Read credentials from the container or env, and never print them.
2. **Old data.** Write it as `data/NN-legacy-<release>.sql` against that schema: the shape a user produced before the release. When several releases are under test, stop at each release's pre-migration, load its data, and continue.
3. **Migrate forward** to the current migration with the same tool. Every migration applies to the old rows here, which is what the case tests. Then make sure the legacy database holds the session user's row (copy it from the main database when the old data lacks it). Without it, the API refuses every call after the swap.
4. **Swap it in.** Stop the API. Point it at the legacy database: rename the two databases (`<db>` to `<db>_fixture`, `<db>_legacy` to `<db>`, closing other connections first), or change the API's connection string for this batch. Then start the API. Renaming databases is a destructive-looking step: confirm it with the user in the step 2 question of SKILL.md.
5. **Run** the cases tagged `@legacy` as usual. Their `Preconditions` step asserts the legacy rows.
6. **Swap back** before any other batch, on every exit path: stop the API, rename the two databases back (or restore the connection string), start the API. Keep the legacy database for reruns; drop it only when the user says the pass is done.

SQL-only survival checks (a threshold range, row counts) run against the legacy database directly, with a `QA_SQL` that targets it.
