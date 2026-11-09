#!/usr/bin/env python3
"""Parse and merge per-item checklist answers from Codex and the Claude fallback.

Checklist files are markdown tables whose rows start with `| <ID> |` (e.g. `| P01 |`).
Every answer line has the canonical form

    ID | PASS|FAIL|N-A|NOT-CHECKED | severity | file:line or command | issue | fix

(a leading `|` or list marker is tolerated). N-A needs a reason in the issue field.

Subcommands:
  ids   <checklist.md>                         -> the IDs, one per line
  parse --checklist F --answer F [--missing-out F]
        -> result=complete|partial|invalid-output; exit 0 / 4 / 5
  merge --checklist F --primary F --primary-label L --secondary F --secondary-label L
        -> one line per ID, each tagged with the engine that answered it; exit 0 when
           every ID is answered, 4 otherwise
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PARTIAL = 4
INVALID = 5

ROW_RE = re.compile(r"^\s*\|\s*`?([A-Z]{1,2}\d{2})`?\s*\|")
ANSWER_RE = re.compile(
    r"^\s*(?:[-*]\s+)?\|?\s*`?([A-Z]{1,2}\d{2})`?\s*\|\s*(PASS|FAIL|N[-/]?A|NOT[- ]CHECKED)\s*\|(.*)$",
    re.I,
)
RANK = {"FAIL": 3, "PASS": 2, "N-A": 1, "NOT-CHECKED": 0}


@dataclass
class Answer:
    item_id: str
    status: str
    fields: list[str]
    line: str

    @property
    def has_reason(self) -> bool:
        issue = self.fields[2] if len(self.fields) > 2 else ""
        return issue.strip() not in ("", "-")


def checklist_ids(path: Path) -> list[str]:
    ids = []
    for line in path.read_text().splitlines():
        match = ROW_RE.match(line)
        if match and match.group(1) not in ids:
            ids.append(match.group(1))
    return ids


def normalize_status(raw: str) -> str:
    upper = raw.upper().replace(" ", "-").replace("/", "-")
    return {"NA": "N-A", "NOTCHECKED": "NOT-CHECKED"}.get(upper.replace("-", ""), upper)


def parse_answers(path: Path, ids: list[str]) -> tuple[dict[str, Answer], list[str], list[str], list[str]]:
    """Return (answers by ID, duplicate IDs, malformed lines, unknown IDs)."""
    answers: dict[str, Answer] = {}
    duplicates, malformed, unknown = [], [], []
    text = path.read_text() if path.exists() else ""
    for line in text.splitlines():
        match = ANSWER_RE.match(line)
        if not match:
            continue
        item_id, status = match.group(1), normalize_status(match.group(2))
        fields = [field.strip() for field in match.group(3).rstrip("|").split("|")]
        if item_id not in ids:
            unknown.append(item_id)
            continue
        answer = Answer(item_id, status, fields, line.strip())
        if status == "N-A" and not answer.has_reason:
            malformed.append(line.strip())
            continue
        if item_id in answers:
            duplicates.append(item_id)
            if RANK[status] <= RANK[answers[item_id].status]:
                continue
        answers[item_id] = answer
    return answers, duplicates, malformed, unknown


def answered(answers: dict[str, Answer]) -> dict[str, Answer]:
    return {item_id: answer for item_id, answer in answers.items() if answer.status != "NOT-CHECKED"}


def cmd_parse(args: argparse.Namespace) -> int:
    ids = checklist_ids(args.checklist)
    answers, duplicates, malformed, unknown = parse_answers(args.answer, ids)
    done = answered(answers)
    missing = [item_id for item_id in ids if item_id not in done]
    fails = [item_id for item_id in ids if item_id in done and done[item_id].status == "FAIL"]
    if args.missing_out:
        args.missing_out.write_text("\n".join(missing) + ("\n" if missing else ""))

    result = "complete" if not missing else ("invalid-output" if not done else "partial")
    print(
        f"result={result} answered={len(done)}/{len(ids)} missing={','.join(missing) or '-'} "
        f"fails={','.join(fails) or '-'} duplicates={','.join(sorted(set(duplicates))) or '-'} "
        f"malformed={len(malformed)} unknown={','.join(sorted(set(unknown))) or '-'}"
    )
    return {"complete": 0, "partial": PARTIAL, "invalid-output": INVALID}[result]


def cmd_merge(args: argparse.Namespace) -> int:
    ids = checklist_ids(args.checklist)
    primary = answered(parse_answers(args.primary, ids)[0]) if args.primary else {}
    secondary = answered(parse_answers(args.secondary, ids)[0]) if args.secondary else {}
    missing = []
    for item_id in ids:
        if item_id in primary:
            print(f"{primary[item_id].line} [{args.primary_label}]")
        elif item_id in secondary:
            print(f"{secondary[item_id].line} [{args.secondary_label}]")
        else:
            missing.append(item_id)
            print(f"{item_id} | NOT-CHECKED | - | - | no engine answered | -")
    sources = f"{args.primary_label}={len(primary)} {args.secondary_label}={len([i for i in secondary if i not in primary])}"
    print(f"\ncoverage={len(ids) - len(missing)}/{len(ids)} {sources} missing={','.join(missing) or '-'}")
    return PARTIAL if missing else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    ids = sub.add_parser("ids")
    ids.add_argument("checklist", type=Path)
    parse = sub.add_parser("parse")
    parse.add_argument("--checklist", type=Path, required=True)
    parse.add_argument("--answer", type=Path, required=True)
    parse.add_argument("--missing-out", type=Path)
    merge = sub.add_parser("merge")
    merge.add_argument("--checklist", type=Path, required=True)
    merge.add_argument("--primary", type=Path)
    merge.add_argument("--primary-label", default="Codex")
    merge.add_argument("--secondary", type=Path)
    merge.add_argument("--secondary-label", default="Claude-Auditor")
    args = parser.parse_args()

    if args.command == "ids":
        print("\n".join(checklist_ids(args.checklist)))
        return 0
    return cmd_parse(args) if args.command == "parse" else cmd_merge(args)


if __name__ == "__main__":
    sys.exit(main())
