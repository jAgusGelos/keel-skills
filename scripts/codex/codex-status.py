#!/usr/bin/env python3
"""Classify a hardened `codex exec --json` run and keep a quota memo.

Subcommands:
  preflight                 -> may Codex run now? (installed + no cached quota in force)
  classify --exit N --out F -> status of a finished run; writes the answer when ok

Output is one line of key=value pairs. Exit code 0 means "use Codex" (preflight) or
"Codex answered" (classify); 3 means "Codex unavailable, run the Claude fallback".

Statuses: ok, not-installed, quota, capacity, auth, timeout, failed.
Only terminal protocol events are read (top-level `error` and `turn.failed`), never
agent prose or command output, so a review that discusses "429" stays `ok`.
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

UNAVAILABLE = 3
TIMEOUT_EXIT = 124

QUOTA_RE = re.compile(r"hit your (usage|weekly) limit|usage limit|weekly limit|out of credits", re.I)
CAPACITY_RE = re.compile(r"at capacity|rate limit|too many requests|\b429\b", re.I)
AUTH_RE = re.compile(r"\b401\b|unauthori[sz]ed|not logged in|log ?in again|authentication (failed|required)", re.I)
UNTIL_RE = re.compile(r"try again at (.+?)\.?$", re.I)
ORDINAL_RE = re.compile(r"(\d+)(st|nd|rd|th)\b")
URL_RE = re.compile(r"https?://\S+")


def cache_path() -> Path:
    override = os.environ.get("CODEX_STATUS_CACHE")
    return Path(override) if override else Path.home() / ".cache" / "codex-status.json"


def emit(**fields: str) -> None:
    print(" ".join(f'{key}="{value}"' if " " in str(value) else f"{key}={value}" for key, value in fields.items()))


def parse_until(message: str) -> datetime | None:
    """Absolute reset time from 'try again at Sep 29th, 2026 9:40 PM.', in local time."""
    match = UNTIL_RE.search(message.strip())
    if not match:
        return None
    text = ORDINAL_RE.sub(r"\1", match.group(1).strip())
    for fmt in ("%b %d, %Y %I:%M %p", "%B %d, %Y %I:%M %p"):
        try:
            return datetime.strptime(text, fmt).astimezone()
        except ValueError:
            continue
    return None


def write_cache(until: datetime) -> None:
    path = cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": "quota", "until": until.isoformat(), "at": datetime.now().astimezone().isoformat()}
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".codex-status-")
    with os.fdopen(fd, "w") as handle:
        json.dump(payload, handle)
    os.replace(tmp, path)


def cached_quota() -> datetime | None:
    try:
        payload = json.loads(cache_path().read_text())
        until = datetime.fromisoformat(payload["until"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return until if until > datetime.now().astimezone() else None


def read_events(out: Path) -> tuple[list[dict], int]:
    events, malformed = [], 0
    try:
        lines = out.read_text(errors="replace").splitlines()
    except OSError:
        return [], 0
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(event, dict):
            events.append(event)
    return events, malformed


def last_answer(events: list[dict]) -> str:
    answer = ""
    for event in events:
        item = event.get("item") if event.get("type") == "item.completed" else None
        if isinstance(item, dict) and item.get("type") == "agent_message" and str(item.get("text", "")).strip():
            answer = item["text"]
    return answer


def failure_messages(events: list[dict]) -> list[str]:
    messages = []
    for event in events:
        if event.get("type") == "error":
            messages.append(str(event.get("message", "")))
        elif event.get("type") == "turn.failed":
            error = event.get("error")
            messages.append(str(error.get("message", "")) if isinstance(error, dict) else str(error or ""))
    return [message for message in messages if message]


def sanitize(message: str) -> str:
    return URL_RE.sub("<url>", message).replace('"', "'")[:200]


def classify(exit_code: int, out: Path, answer_file: Path | None, use_cache: bool) -> int:
    events, malformed = read_events(out)
    answer = last_answer(events)
    completed = any(event.get("type") == "turn.completed" for event in events)
    turn_failed = any(event.get("type") == "turn.failed" for event in events)

    if exit_code == 0 and completed and not turn_failed and answer:
        if answer_file:
            answer_file.write_text(answer)
        emit(status="ok", exit=exit_code, events=len(events), malformed=malformed)
        return 0

    if exit_code == TIMEOUT_EXIT:
        emit(status="timeout", exit=exit_code, until="-", diag=f"timed out after {len(events)} events")
        return UNAVAILABLE

    messages = failure_messages(events) if (turn_failed or exit_code != 0) else []
    joined = " | ".join(messages)
    diag = sanitize(messages[-1]) if messages else f"no final agent_message ({len(events)} events, {malformed} malformed)"

    if QUOTA_RE.search(joined):
        until = next((parsed for parsed in map(parse_until, messages) if parsed), None)
        if until and use_cache:
            write_cache(until)
        emit(status="quota", exit=exit_code, until=until.isoformat() if until else "-", diag=diag)
    elif CAPACITY_RE.search(joined):
        emit(status="capacity", exit=exit_code, until="-", diag=diag)
    elif AUTH_RE.search(joined):
        emit(status="auth", exit=exit_code, until="-", diag=diag)
    else:
        emit(status="failed", exit=exit_code, until="-", diag=diag)
    return UNAVAILABLE


def preflight() -> int:
    if not shutil.which("codex"):
        emit(status="not-installed", until="-")
        return UNAVAILABLE
    until = cached_quota()
    if until:
        emit(status="quota", until=until.isoformat(), diag="cached usage limit still in force")
        return UNAVAILABLE
    emit(status="ready")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    run = sub.add_parser("classify")
    run.add_argument("--exit", type=int, required=True, dest="exit_code")
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--err", type=Path, help="kept for the record; never used to classify (MCP auth noise)")
    run.add_argument("--answer-file", type=Path)
    run.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    if args.command == "preflight":
        return preflight()
    return classify(args.exit_code, args.out, args.answer_file, not args.no_cache)


if __name__ == "__main__":
    sys.exit(main())
