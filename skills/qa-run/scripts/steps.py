#!/usr/bin/env python3
"""Print each test's steps with status and the first error line, from a Playwright JSON report."""
from pathlib import Path
import json, re, sys
d = json.loads(Path(sys.argv[1]).read_text())
def walk(s):
    for sp in s.get("specs", []):
        for t in sp["tests"]:
            r = t["results"][-1]
            print(f"== {sp['title'][:70]} [{r['status']}]")
            for x in r["steps"]:
                if x["title"] in ("Before Hooks", "After Hooks"): continue
                e = x.get("error")
                print(("  ERR " if e else "  ok  ") + x["title"][:90])
                if e: print("      " + re.sub(r"\x1b\[[0-9;]*m", "", e.get("message", "")).replace("\n", " ")[:500])
            if r.get("error") and not any(x.get("error") for x in r["steps"]):
                print("  TEST " + re.sub(r"\x1b\[[0-9;]*m", "", r["error"].get("message", "")).replace("\n", " ")[:300])
    for c in s.get("suites", []): walk(c)
for s in d["suites"]: walk(s)
