import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "checklist.py"

CHECKLIST = """# Plan checklist
| ID | Check | Sev |
|---|---|---|
| P01 | Trace scenarios | CRIT |
| P02 | Map ACs | CRIT |
| P03 | Acceptance step | HIGH |
| P04 | Validators | HIGH |
"""


def run(*args: str) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    return proc.returncode, proc.stdout


class ChecklistTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.checklist = self.tmp / "checklist.md"
        self.checklist.write_text(CHECKLIST)

    def answer(self, name: str, text: str) -> Path:
        path = self.tmp / name
        path.write_text(text)
        return path

    def parse(self, text: str, *extra: str) -> tuple[int, str]:
        return run("parse", "--checklist", str(self.checklist), "--answer", str(self.answer("a.md", text)), *extra)

    def test_ids(self) -> None:
        self.assertEqual(run("ids", str(self.checklist))[1].split(), ["P01", "P02", "P03", "P04"])

    def test_complete(self) -> None:
        code, out = self.parse(
            "Intro prose.\n"
            "P01 | PASS | CRIT | plan.md:3 | - | -\n"
            "| P02 | FAIL | CRIT | plan.md:9 | AC-3 has no Verify | add step |\n"
            "- P03 | n/a | HIGH | - | library, no runnable surface | -\n"
            "`P04` | pass | HIGH | Makefile | - | -\n"
        )
        self.assertEqual(code, 0)
        self.assertIn("result=complete answered=4/4", out)
        self.assertIn("fails=P02", out)

    def test_partial_lists_missing_and_not_checked(self) -> None:
        missing = self.tmp / "missing.txt"
        code, out = self.parse(
            "P01 | PASS | CRIT | x | - | -\nP02 | NOT-CHECKED | CRIT | - | ran out of time | -\n",
            "--missing-out",
            str(missing),
        )
        self.assertEqual(code, 4)
        self.assertIn("result=partial", out)
        self.assertEqual(missing.read_text().split(), ["P02", "P03", "P04"])

    def test_prose_only_is_invalid_output(self) -> None:
        code, out = self.parse("The plan looks fine overall. P01 seems ok.\n")
        self.assertEqual(code, 5)
        self.assertIn("result=invalid-output", out)

    def test_na_without_reason_is_malformed_and_missing(self) -> None:
        code, out = self.parse("P01 | N-A | CRIT | - | - | -\nP02 | PASS | CRIT | x | - | -\n")
        self.assertEqual(code, 4)
        self.assertIn("malformed=1", out)
        self.assertIn("missing=P01,P03,P04", out)

    def test_duplicate_keeps_worst_status(self) -> None:
        code, out = self.parse(
            "P01 | PASS | CRIT | x | - | -\nP01 | FAIL | CRIT | y | broken | fix\n"
            "P02 | PASS | CRIT | x | - | -\nP03 | PASS | HIGH | x | - | -\nP04 | PASS | HIGH | x | - | -\n"
        )
        self.assertEqual(code, 0)
        self.assertIn("fails=P01", out)
        self.assertIn("duplicates=P01", out)

    def test_unknown_ids_reported_not_counted(self) -> None:
        _, out = self.parse("Z99 | PASS | LOW | x | - | -\n")
        self.assertIn("unknown=Z99", out)
        self.assertIn("answered=0/4", out)

    def test_merge_fills_missing_from_secondary(self) -> None:
        primary = self.answer("codex.md", "P01 | FAIL | CRIT | x | gap | fix\nP02 | PASS | CRIT | x | - | -\n")
        secondary = self.answer(
            "claude.md",
            "P01 | PASS | CRIT | x | - | -\nP03 | PASS | HIGH | x | - | -\nP04 | N-A | HIGH | - | no validators | -\n",
        )
        code, out = run(
            "merge", "--checklist", str(self.checklist), "--primary", str(primary), "--primary-label", "Codex (partial)",
            "--secondary", str(secondary), "--secondary-label", "Claude-Auditor",
        )
        self.assertEqual(code, 0)
        self.assertIn("P01 | FAIL | CRIT | x | gap | fix [Codex (partial)]", out)
        self.assertIn("P03 | PASS | HIGH | x | - | - [Claude-Auditor]", out)
        self.assertIn("coverage=4/4 Codex (partial)=2 Claude-Auditor=2", out)

    def test_merge_without_primary_reports_gaps(self) -> None:
        secondary = self.answer("claude.md", "P01 | PASS | CRIT | x | - | -\n")
        code, out = run("merge", "--checklist", str(self.checklist), "--secondary", str(secondary))
        self.assertEqual(code, 4)
        self.assertIn("P02 | NOT-CHECKED", out)
        self.assertIn("missing=P02,P03,P04", out)


if __name__ == "__main__":
    unittest.main()
