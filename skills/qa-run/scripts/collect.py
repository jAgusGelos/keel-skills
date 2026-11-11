#!/usr/bin/env python3
"""collect.py <report.json> <run-dir>: copy each test's output into <run-dir>/QA-NN/<Role>[/light]/ with a storyboard.

The folder is the one holding the test's video attachment. trace.zip stays behind: it carries the bearer token.
QA_THEME=light (the light pass) writes to the case's light/ subfolder.
"""
from pathlib import Path
import json, os, re, shutil, subprocess, sys

report, run = sys.argv[1:3]
theme = "light" if os.environ.get("QA_THEME") == "light" else ""
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
commit, branch = git("rev-parse", "--short", "HEAD"), git("branch", "--show-current")
first_line = lambda m: re.sub(r"\x1b\[[0-9;]*m", "", m or "").split("\n")[0]


def walk(suite):
    for spec in suite.get("specs", []):
        tags = spec.get("tags", [])
        qa = next(t for t in tags if re.fullmatch(r"QA-\d+", t))
        role = next(t[5:] for t in tags if t.startswith("role:"))
        for test in spec["tests"]:
            result = test["results"][-1]
            video = next((a["path"] for a in result.get("attachments", []) if a["name"] == "video"), None)
            if not video:
                continue
            src = os.path.dirname(video)
            dst = os.path.join(run, qa, role, theme) if theme else os.path.join(run, qa, role)
            shutil.rmtree(dst, ignore_errors=True)
            os.makedirs(dst)
            for f in os.listdir(src):
                if f != "trace.zip" and os.path.isfile(os.path.join(src, f)):
                    shutil.copy(os.path.join(src, f), dst)
            shots = sorted(f for f in os.listdir(dst) if f.endswith(".png"))
            steps = [s for s in result["steps"] if s["title"] not in ("Before Hooks", "After Hooks")]
            rows = []
            for i, step in enumerate(steps):
                shot = ", ".join(f for f in shots if f.startswith(f"{i:02d}-")) or ("test-failed-1.png" if step.get("error") else "")
                outcome = "FAILED: " + first_line(step["error"].get("message")) if step.get("error") else "ok"
                rows.append(f"| {i} | {step['title']} | {outcome} | {shot} |")
            with open(os.path.join(dst, "storyboard.md"), "w") as fh:
                fh.write(
                    f"# {spec['title']}: {role}{' (light)' if theme else ''}\n\n"
                    f"Recorded {result['startTime'][:10]} on {branch} @ {commit}. Status: {result['status']}.\n\n"
                    "| # | Step | Result | Screenshot |\n|---|---|---|---|\n" + "\n".join(rows) + "\n\nVideo: video.webm\n"
                )
            print(qa, role, theme or "dark", result["status"], dst)
    for child in suite.get("suites", []):
        walk(child)


for top in json.loads(Path(report).read_text())["suites"]:
    walk(top)
