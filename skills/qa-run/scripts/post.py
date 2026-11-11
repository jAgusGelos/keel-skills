#!/usr/bin/env python3
"""post.py <issue> <plan.md> <run-dir> <QA-NN> <Role>…: comment one case's verdict on a tracking issue.

Only when the user named a tracking issue for per-case progress comments. The comment carries the plan row's
verdict, the last three step screenshots and the video of each role folder (and its light/ subfolder when the
light pass ran), attached through `gh --attach` (gh 2.99+). The video goes up as
H.264 MP4; over 10 MB, it stays local and the comment says so. trace.zip is never attached.
A local draft path in Bug Issue reads "drafted; published at triage".
"""
from pathlib import Path
import os, re, subprocess, sys

LIMIT = 10 * 1024 * 1024
issue, plan, run, qa, *roles = sys.argv[1:]
line = next(l for l in Path(plan).read_text().splitlines() if l.startswith(f"| {qa} |"))
cells = re.split(r"(?<!\\)\|", line.strip())[1:-1]
title, actual, bug = cells[1].strip(), cells[-2].strip(), cells[-1].strip()
status = "bug" if actual.startswith("bug") else "pass" if actual.startswith("pass") else "open"
detail = re.sub(r"^(pass|bug)\s*[:-]\s*", "", actual).replace("<br>", "\n")
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()

parts = [f"## {qa}: {title}", "", f"**Status:** `{status}` · **Roles:** {', '.join(roles)} · local app, `{branch}` @ `{commit}`", "", detail]
attach: list[str] = []
if bug:
    parts += ["", "**Bug report:** drafted; published at triage." if bug.startswith("draft") else f"**Bug report:** {bug}"]
for role in roles:
    for theme in ("", "light"):
        folder = os.path.join(run, qa, role, theme)
        if not os.path.isdir(folder):
            continue
        shots = sorted(f for f in os.listdir(folder) if re.match(r"\d\d-.*\.png$", f))
        picks = [f for f in shots if not f.startswith("00-")][-3:] or shots[:1]
        parts += ["", f"### {role}{' (light)' if theme else ''}", ""]
        for f in picks:
            parts.append(f"![{qa} {role} {f[:-4]}]({os.path.join(folder, f)})")
            attach.append(os.path.join(folder, f))
        # Every video goes up as H.264 MP4: GitHub embeds Playwright's VP8 WebM, but several browsers cannot play it.
        video = os.path.join(folder, "video.webm")
        mp4 = os.path.join(folder, "video.mp4")
        if os.path.exists(video) and not os.path.exists(mp4):
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", "-preset", "fast", "-movflags", "+faststart", "-an", mp4], check=False)
        video = mp4 if os.path.exists(mp4) and os.path.getsize(mp4) <= LIMIT else ""
        if video and os.path.exists(video):
            parts += ["", f"![]({video})"]
            attach.append(video)
        else:
            parts += ["", "_The run video stays local: no MP4 of 10 MB or less could be made._"]

body = os.path.join(run, "raw", f"comment-{qa}.md")
os.makedirs(os.path.dirname(body), exist_ok=True)
Path(body).write_text("\n".join(parts) + "\n")
cmd = ["gh", "issue", "comment", issue, "--body-file", body]
for f in attach:
    cmd += ["--attach", f]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout.strip() or result.stderr.strip())
sys.exit(result.returncode)
