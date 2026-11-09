"""End to end: Codex out of quota across two gates of the same run.

A fake `codex` binary prints the real usage-limit JSONL and exits 1. Gate 1 runs the README snippet:
one attempt, status=quota, memo written. Gate 2 must not call Codex at all. The Claude fallback answer
then completes the checklist, so the verdict can be taken from Claude alone.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HELPERS = Path(__file__).resolve().parent.parent
QUOTA_JSONL = (Path(__file__).resolve().parent / "fixtures" / "quota.jsonl").read_text()

GATE = """
set -u
WORK="$1"
if python3 "$HELPERS/codex-status.py" preflight > "$WORK/codex-status.txt"; then
  timeout 30 codex exec --json -C "$WORK" --skip-git-repo-check \\
    --dangerously-bypass-approvals-and-sandbox "review" \\
    < /dev/null > "$WORK/codex.jsonl" 2> "$WORK/codex.err"
  python3 "$HELPERS/codex-status.py" classify --exit $? --out "$WORK/codex.jsonl" \\
    --answer-file "$WORK/codex-answer.md" > "$WORK/codex-status.txt"
fi
cat "$WORK/codex-status.txt"
"""

CHECKLIST = "| ID | Check | Sev |\n|---|---|---|\n| R01 | a | CRIT |\n| R02 | b | CRIT |\n"


class QuotaEndToEndTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.calls = self.tmp / "codex-calls.txt"
        fake = self.bin / "codex"
        (self.tmp / "quota.jsonl").write_text(QUOTA_JSONL)
        fake.write_text(f"#!/bin/sh\necho call >> {self.calls}\ncat {self.tmp / 'quota.jsonl'}\nexit 1\n")
        fake.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "HELPERS": str(HELPERS),
            "CODEX_STATUS_CACHE": str(self.tmp / "codex-status.json"),
        }

    def gate(self, name: str) -> str:
        work = self.tmp / name
        work.mkdir()
        proc = subprocess.run(["bash", "-c", GATE, "gate", str(work)], capture_output=True, text=True, env=self.env)
        return proc.stdout

    def test_one_attempt_then_cached_skip_then_claude_completes(self) -> None:
        first = self.gate("gate1")
        self.assertIn("status=quota", first)
        self.assertIn("until=2099-09-29T21:40", first)

        second = self.gate("gate2")
        self.assertIn("status=quota", second)
        self.assertIn("cached usage limit", second)
        self.assertEqual(self.calls.read_text().count("call"), 1, "Codex must be called once across both gates")

        checklist = self.tmp / "checklist.md"
        checklist.write_text(CHECKLIST)
        fallback = self.tmp / "fallback.md"
        fallback.write_text("R01 | PASS | CRIT | make check exit 0 | - | -\nR02 | PASS | CRIT | test_x | - | -\n")
        merged = subprocess.run(
            [sys.executable, str(HELPERS / "checklist.py"), "merge", "--checklist", str(checklist),
             "--secondary", str(fallback), "--secondary-label", "Claude-Auditor"],
            capture_output=True, text=True,
        )
        self.assertEqual(merged.returncode, 0)
        self.assertIn("coverage=2/2", merged.stdout)
        self.assertNotIn("[Codex", merged.stdout)


if __name__ == "__main__":
    unittest.main()
