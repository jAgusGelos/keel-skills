import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "evidence.py"


def run(*args: str) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip()


class EvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path(tempfile.mkdtemp())
        for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", "-C", str(self.repo), *cmd], check=True)
        (self.repo / "app.py").write_text("print(1)\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "init"], check=True)
        self.evidence = self.repo / ".workspace" / "ctx" / "review" / "review-evidence.md"
        self.evidence.parent.mkdir(parents=True)

    def write_evidence(self) -> None:
        values = dict(token.split("=") for token in run("fingerprint", "--repo", str(self.repo))[1].split())
        self.evidence.write_text(f"# Review evidence\n- head: {values['head']}\n- tree: {values['tree']}\n")

    def check(self) -> int:
        return run("check", str(self.evidence), "--repo", str(self.repo))[0]

    def test_fresh_after_writing(self) -> None:
        self.write_evidence()
        self.assertEqual(self.check(), 0)

    def test_stale_after_source_edit(self) -> None:
        self.write_evidence()
        (self.repo / "app.py").write_text("print(2)\n")
        self.assertEqual(self.check(), 6)

    def test_stale_after_new_untracked_file(self) -> None:
        self.write_evidence()
        (self.repo / "new.py").write_text("x = 1\n")
        self.assertEqual(self.check(), 6)

    def test_stale_after_commit(self) -> None:
        self.write_evidence()
        (self.repo / "app.py").write_text("print(3)\n")
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qam", "fix"], check=True)
        self.assertEqual(self.check(), 6)

    def test_workspace_changes_do_not_count(self) -> None:
        self.write_evidence()
        (self.repo / ".workspace" / "notes.md").write_text("scratch\n")
        self.assertEqual(self.check(), 0)

    def test_missing_evidence_is_stale(self) -> None:
        self.assertEqual(self.check(), 6)


if __name__ == "__main__":
    unittest.main()
