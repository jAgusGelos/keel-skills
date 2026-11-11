#!/usr/bin/env python3
"""Self-check for verdict.py: writes, rewrites (with an escaped pipe), and refuses an unknown row."""
from pathlib import Path
import os, subprocess, sys, tempfile

here = os.path.dirname(os.path.abspath(__file__))
row = "| QA-01 | Title | [#1](x) | Why | Role: `A`. | 1. Do. | It works. | | |"
with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
    f.write("# Plan\n\n" + row + "\n")
run = lambda *a: subprocess.run([sys.executable, os.path.join(here, "verdict.py"), f.name, *a], capture_output=True, text=True)
assert run("QA-01", "bug: a|b").returncode == 0
assert Path(f.name).read_text().splitlines()[2].endswith("| It works. | bug: a\\|b | |"), Path(f.name).read_text()
assert run("QA-01", "pass: fine", "draft").returncode == 0
assert Path(f.name).read_text().splitlines()[2].endswith("| It works. | pass: fine | draft |"), Path(f.name).read_text()
assert run("QA-99", "pass").returncode != 0
os.unlink(f.name)
print("verdict.py: all checks passed")
