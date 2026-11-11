# Data scripts

Data a case needs and the local fixture lacks is a **fixture gap**. This file owns how a pass writes, resets and addresses that data. Every script lives in `.qa/run-<key>/data/`, is idempotent, and runs through [`../scripts/sql.sh`](../scripts/sql.sh), which pipes each file into the `QA_SQL` command from `docs/qa-setup.md` (for example `docker exec -i app-db psql -U app -d app -v ON_ERROR_STOP=1 -At -F'|'`). The command must stop on the first error and print rows as `|`-separated columns.

## Naming

`NN-seed-<block>.sql` builds data; `NN-reset-<block>.sql` returns it to its seeded state; `NN-<case>-<what>.sql` is a one-case precondition. `NN` is the order they run in.

## Seed by block, reset by rebuild

Group the data that several cases share into one **block**, such as an order lifecycle block or a billing period. Each block gets one seed script. Give the block its own reset, which removes everything the block and its runs created, then reruns the seed. A rebuild returns the block to a known state after any run, a failed one included. Per-case resets drift as cases multiply.

- The seed opens with a guard (fail when the block already exists) or is written to run twice.
- The reset removes rows child-first and scopes itself to the block, for example by the block's customer or period name.
- Rows the product deletes softly (`deleted_at` columns) come back by clearing those columns. Recreating the row would give it a new id.
- A block that creates rows the product normally creates alongside (a blank answer per question of a review) creates them too. An incomplete seed shows as an empty screen, not as an error.

## Ids by name

A reseed changes identity values, so a spec never hardcodes an id. Each block has an `ids.sql` that SELECTs `kind|name|id` rows. After every seed or reset, [`../scripts/ids.py`](../scripts/ids.py) writes them to `<frontend>/e2e/evidence/qa-<key>/ids.json`. Specs read that file and address records by name: `ids.order["O1"]`.

## Actor swaps

With one signed-in session, a case can need that user in two roles on one record: the reviewer who writes a review, then the subject who reads it. A swap script moves the record's actor columns between steps. It moves everything keyed to the actor with them:

- rows authored by the actor (a comment's author id);
- the actor attributes the screen reads, such as the seniority that selects a review's questions. Give the session user the seeded actor's value while it plays that actor, and restore it afterwards.

Name each swap for the state it produces (`NN-<record>-session-as-subject.sql`). The case's `Preconditions` step asserts that state.

## Recording the gap

Every seed that fills a fixture gap opens with a comment naming the gap. The gap also gets a line in `issues/local-data-fixture.md`, which lists the cases that needed it and the script that supplied it.
