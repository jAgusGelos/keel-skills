#!/bin/bash
# sql.sh <file.sql>...: run pass data scripts on the local database, stopping at the first failure.
# QA_SQL is the command from docs/qa-setup.md that reads SQL on stdin, stops on the first error and prints
# rows as |-separated columns, e.g. QA_SQL="docker exec -i app-db psql -U app -d app -v ON_ERROR_STOP=1 -At -F'|'".
# Credentials stay inside that command (or the container); this script never prints them.
set -u
if [ -z "${QA_SQL:-}" ]; then
  echo "QA_SQL is not set: copy the command from docs/qa-setup.md -> Database" >&2
  exit 2
fi
for f in "$@"; do
  bash -c "$QA_SQL" < "$f" || { echo "FAILED: $f" >&2; exit 1; }
done
