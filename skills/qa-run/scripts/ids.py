#!/usr/bin/env python3
"""ids.py <ids.sql> <out.json>: write the ids a reseed produced, by name, for the specs to read.

<ids.sql> SELECTs rows of `kind|name|id` (e.g. `engagement|E1|40`); the output is {kind: {name: id}}.
Specs never hardcode an id: a reseed changes them.
"""
from pathlib import Path
import json, subprocess, sys

sql, out = sys.argv[1:3]
rows = subprocess.run(["bash", f"{__file__.rsplit('/', 1)[0]}/sql.sh", sql], capture_output=True, text=True, check=True).stdout
ids: dict[str, dict[str, int]] = {}
for line in rows.splitlines():
    parts = line.strip().split("|")
    if len(parts) == 3 and parts[2].isdigit():
        ids.setdefault(parts[0], {})[parts[1]] = int(parts[2])
Path(out).write_text(json.dumps(ids, indent=1))
print(f"wrote {out}: " + ", ".join(f"{k} {len(v)}" for k, v in ids.items()))
