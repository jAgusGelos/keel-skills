#!/usr/bin/env python3
"""Fingerprint the working tree so review evidence can be checked for staleness.

Subcommands:
  fingerprint [--repo DIR]             -> "head=<sha> tree=<sha256>"
  check <evidence.md> [--repo DIR]     -> exit 0 fresh, 6 stale or unreadable

The tree hash covers uncommitted tracked changes and untracked files, excluding
`.workspace/` (where the evidence file and other planning scratch live), so writing
the evidence file never makes it stale. The evidence file must carry the two values
as lines `head: <sha>` and `tree: <sha256>` (see review-changes/references/review-evidence.md).
"""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

STALE = 6
EXCLUDE = ":(exclude).workspace"


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout


def fingerprint(repo: Path) -> tuple[str, str]:
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    digest = hashlib.sha256(git(repo, "diff", "HEAD", "--binary", "--", ".", EXCLUDE))
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z", "--", ".", EXCLUDE)
    for name in sorted(filter(None, untracked.split(b"\0"))):
        digest.update(b"\0untracked\0" + name + b"\0")
        path = repo / name.decode()
        if path.is_file():
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return head, digest.hexdigest()


def recorded(evidence: Path, key: str) -> str | None:
    match = re.search(rf"^\s*[-*]?\s*\**{key}\**\s*:\s*`?([0-9a-f]+)`?", evidence.read_text(), re.I | re.M)
    return match.group(1) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    fp = sub.add_parser("fingerprint")
    fp.add_argument("--repo", type=Path, default=Path("."))
    check = sub.add_parser("check")
    check.add_argument("evidence", type=Path)
    check.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()

    head, tree = fingerprint(args.repo)
    if args.command == "fingerprint":
        print(f"head={head} tree={tree}")
        return 0

    if not args.evidence.is_file():
        print(f"evidence=stale reason=missing file={args.evidence}")
        return STALE
    problems = []
    if recorded(args.evidence, "head") != head:
        problems.append(f"head {recorded(args.evidence, 'head')} != {head}")
    if recorded(args.evidence, "tree") != tree:
        problems.append("working tree changed since the evidence was written")
    if problems:
        print("evidence=stale reason=" + "; ".join(problems).replace(" ", "_"))
        return STALE
    print(f"evidence=fresh head={head}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
