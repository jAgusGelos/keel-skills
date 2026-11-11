#!/usr/bin/env python3
"""verdict.py <plan.md> <QA-NN> <actual> [bug-issue]: write a case's Actual Result and Bug Issue cells.

Only the row's last two cells change, so the plan keeps its shape. `actual` starts with the status
(`pass: ...`, `bug: ...`); a pipe in it is escaped.
"""
from pathlib import Path
import re, sys

plan, qa, actual = sys.argv[1:4]
bug = sys.argv[4] if len(sys.argv) > 4 else ""
lines = Path(plan).read_text().split("\n")
index = next((i for i, l in enumerate(lines) if l.startswith(f"| {qa} |")), None)
if index is None:
    sys.exit(f"{qa} is not a row of {plan}")
cell = lambda t: t.replace("|", "\\|").replace("\n", "<br>")
tail = re.compile(r"\|(?:\\\||[^|])*\|(?:\\\||[^|])*\|$")
lines[index] = tail.sub(lambda _: f"| {cell(actual)} | {cell(bug)} |".replace("|  |", "| |"), lines[index])
Path(plan).write_text("\n".join(lines))
