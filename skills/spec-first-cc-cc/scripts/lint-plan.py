#!/usr/bin/env python3
"""Deterministic template check for spec-first plan.md and todo.md.

Usage: lint-plan.py <feature-dir>       (reads plan.md and todo.md inside it)

Replaces the template-completeness half of the old Codex plan audit: section presence, AD fields, AD-ID
sequence, todo milestones with Verify steps, todo-to-AD traceability. Exit 0 clean, 1 with one
`file: problem` line per failure. Headings follow the spec-first templates exactly (e.g. "Executive
Summary", "Risks & Mitigations"), so it never raises the old "Summary heading" false positive.
"""

import re
import sys
from pathlib import Path

PLAN_SECTIONS = [
    "Executive Summary",
    "Commands",
    "Architecture Decisions",
    "Dependencies",
    "Non-Functional Requirements",
    "Three-Tier Boundaries",
    "Risks & Mitigations",
    "Strategy",
    "Open Questions",
    "Conformance Criteria",
]
AD_FIELDS = ["Context", "Options considered", "Chosen approach", "Rationale", "Evidence", "Tradeoffs", "Consequences"]
TODO_SECTIONS = ["Hardening & Launch", "Verification"]


def headings(text: str, level: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(rf"^{level}\s+(.+)$", text, re.M)]


def sections(text: str, level: str) -> list[tuple[str, str]]:
    parts = re.split(rf"^({level}\s+.+)$", text, flags=re.M)
    return [(parts[i].lstrip("#").strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def lint_plan(text: str) -> list[str]:
    problems = []
    h2 = headings(text, "##")
    for section in PLAN_SECTIONS:
        if not any(heading.lower().startswith(section.lower()) for heading in h2):
            problems.append(f"plan.md: missing section '## {section}'")

    ads = [(title, body) for title, body in sections(text, "###") if re.match(r"AD-\d+", title)]
    if not ads:
        problems.append("plan.md: no '### AD-N' architecture decisions")
    numbers = [int(re.match(r"AD-(\d+)", title).group(1)) for title, _ in ads]
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        problems.append(f"plan.md: AD-IDs not sequential from 1: {numbers}")
    for title, body in ads:
        for field in AD_FIELDS:
            if not re.search(rf"\*\*[^*\n]*\b{re.escape(field)}\b[^*\n]*:\*\*", body, re.I):
                problems.append(f"plan.md: {title.split(':')[0]} missing field '{field}'")
    if re.search(r"\[(TBD|TODO|fill in)[^\]]*\]", text, re.I):
        problems.append("plan.md: unresolved template placeholders ([TBD]/[TODO])")
    return problems


def lint_todo(text: str, plan_ads: set[str]) -> list[str]:
    problems = []
    h2 = headings(text, "##")
    milestones = [(title, body) for title, body in sections(text, "##") if title.lower().startswith("milestone")]
    if not milestones:
        problems.append("todo.md: no '## Milestone N' sections")
    for title, body in milestones:
        if not re.search(r"\bverify\b", body, re.I):
            problems.append(f"todo.md: '{title}' has no Verify step")
    for section in TODO_SECTIONS:
        if not any(heading.lower().startswith(section.lower()) for heading in h2):
            problems.append(f"todo.md: missing section '## {section}'")
    referenced = set(re.findall(r"AD-\d+", text))
    unknown = sorted(referenced - plan_ads, key=lambda ad: int(ad[3:]))
    if unknown:
        problems.append(f"todo.md: references ADs not in plan.md: {', '.join(unknown)}")
    unused = sorted(plan_ads - referenced, key=lambda ad: int(ad[3:]))
    if unused:
        problems.append(f"todo.md: plan ADs with no task: {', '.join(unused)}")
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    feature = Path(sys.argv[1])
    plan_path, todo_path = feature / "plan.md", feature / "todo.md"
    problems = []
    plan = plan_path.read_text() if plan_path.is_file() else ""
    if not plan:
        problems.append("plan.md: missing or empty")
    else:
        problems += lint_plan(plan)
    plan_ads = {match for match in re.findall(r"^###\s+(AD-\d+)", plan, re.M)}
    if todo_path.is_file():
        problems += lint_todo(todo_path.read_text(), plan_ads)
    for problem in problems:
        print(problem)
    print(f"lint-plan: {'clean' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
