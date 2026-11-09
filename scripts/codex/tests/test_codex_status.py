import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "codex-status.py"
FIXTURES = HERE / "fixtures"


def run(*args: str, cache: Path, path: str | None = None) -> tuple[int, dict[str, str]]:
    env = {**os.environ, "CODEX_STATUS_CACHE": str(cache)}
    if path is not None:
        env["PATH"] = path
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)
    fields = {}
    for token in proc.stdout.strip().split(" "):
        if "=" in token:
            key, value = token.split("=", 1)
            fields.setdefault(key, value.strip('"'))
    return proc.returncode, fields


class ClassifyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.cache = self.tmp / "codex-status.json"

    def classify(self, fixture: str, exit_code: int, *extra: str) -> tuple[int, dict[str, str]]:
        return run("classify", "--exit", str(exit_code), "--out", str(FIXTURES / fixture), *extra, cache=self.cache)

    def test_success_writes_last_agent_message(self) -> None:
        answer = self.tmp / "answer.md"
        code, fields = self.classify("success.jsonl", 0, "--answer-file", str(answer))
        self.assertEqual((code, fields["status"]), (0, "ok"))
        self.assertEqual(answer.read_text(), "P01 | PASS | CRIT | plan.md:12 | - | -")

    def test_quota_words_in_command_output_do_not_count(self) -> None:
        self.assertEqual(self.classify("success.jsonl", 0)[1]["status"], "ok")

    def test_review_discussing_429_stays_ok(self) -> None:
        self.assertEqual(self.classify("success-mentions-429.jsonl", 0)[1]["status"], "ok")

    def test_non_fatal_error_event_on_healthy_run_stays_ok(self) -> None:
        self.assertEqual(self.classify("healthy-with-warning.jsonl", 0)[1]["status"], "ok")

    def test_quota_with_future_date_is_cached(self) -> None:
        code, fields = self.classify("quota.jsonl", 1)
        self.assertEqual((code, fields["status"]), (3, "quota"))
        self.assertTrue(fields["until"].startswith("2099-09-29T21:40"))
        self.assertNotIn("chatgpt.com", fields["diag"])
        self.assertTrue(json.loads(self.cache.read_text())["until"].startswith("2099-09-29"))

    def test_quota_without_parseable_date_is_not_cached(self) -> None:
        code, fields = self.classify("quota-weekly-nodate.jsonl", 1)
        self.assertEqual((code, fields["status"], fields["until"]), (3, "quota", "-"))
        self.assertFalse(self.cache.exists())

    def test_no_cache_flag(self) -> None:
        self.classify("quota.jsonl", 1, "--no-cache")
        self.assertFalse(self.cache.exists())

    def test_capacity(self) -> None:
        self.assertEqual(self.classify("capacity.jsonl", 1)[1]["status"], "capacity")

    def test_auth(self) -> None:
        self.assertEqual(self.classify("auth.jsonl", 1)[1]["status"], "auth")

    def test_timeout_by_exit_code(self) -> None:
        code, fields = self.classify("timeout.jsonl", 124)
        self.assertEqual((code, fields["status"]), (3, "timeout"))

    def test_malformed_output(self) -> None:
        self.assertEqual(self.classify("malformed.jsonl", 0)[1]["status"], "failed")

    def test_completed_without_message(self) -> None:
        self.assertEqual(self.classify("completed-no-message.jsonl", 0)[1]["status"], "failed")

    def test_success_events_with_nonzero_exit_is_not_ok(self) -> None:
        self.assertEqual(self.classify("success.jsonl", 1)[0], 3)

    def test_missing_output_file(self) -> None:
        code, fields = run("classify", "--exit", "1", "--out", str(self.tmp / "nope.jsonl"), cache=self.cache)
        self.assertEqual((code, fields["status"]), (3, "failed"))


class PreflightTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.cache = self.tmp / "codex-status.json"
        self.fake_bin = self.tmp / "bin"
        self.fake_bin.mkdir()
        fake = self.fake_bin / "codex"
        fake.write_text("#!/bin/sh\nexit 0\n")
        fake.chmod(0o755)

    def test_ready_without_cache(self) -> None:
        self.assertEqual(run("preflight", cache=self.cache, path=str(self.fake_bin))[1]["status"], "ready")

    def test_not_installed(self) -> None:
        code, fields = run("preflight", cache=self.cache, path=str(self.tmp))
        self.assertEqual((code, fields["status"]), (3, "not-installed"))

    def test_cached_quota_in_force_skips(self) -> None:
        run("classify", "--exit", "1", "--out", str(FIXTURES / "quota.jsonl"), cache=self.cache)
        code, fields = run("preflight", cache=self.cache, path=str(self.fake_bin))
        self.assertEqual((code, fields["status"]), (3, "quota"))

    def test_expired_quota_does_not_skip(self) -> None:
        self.cache.write_text(json.dumps({"status": "quota", "until": "2020-01-01T00:00:00+00:00"}))
        self.assertEqual(run("preflight", cache=self.cache, path=str(self.fake_bin))[1]["status"], "ready")

    def test_corrupt_cache_does_not_skip(self) -> None:
        self.cache.write_text("{oops")
        self.assertEqual(run("preflight", cache=self.cache, path=str(self.fake_bin))[1]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
