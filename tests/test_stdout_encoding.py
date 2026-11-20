import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


class StdoutEncodingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.author = "Zoë ქართველი"
        self.subject = "Résumé: ქართული"
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        env = dict(os.environ, GIT_AUTHOR_NAME=self.author, GIT_AUTHOR_EMAIL="test@example.test",
                   GIT_COMMITTER_NAME=self.author, GIT_COMMITTER_EMAIL="test@example.test",
                   GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        subprocess.run(["git", "-C", str(self.repo), "-c", "commit.gpgSign=false",
                        "commit", "-q", "--allow-empty", "-m", self.subject], check=True, env=env)

    def run_cli(self, encoding, *options):
        env = dict(os.environ, PYTHONIOENCODING=encoding + ":strict")
        return subprocess.run([sys.executable, "-m", "git_worklog", str(self.repo), *options],
                              capture_output=True, env=env)

    def test_json_round_trips_unicode_on_limited_encodings(self):
        for encoding in ("ascii", "cp1252"):
            with self.subTest(encoding=encoding):
                result = self.run_cli(encoding, "--json")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, b"")
                report = json.loads(result.stdout.decode("ascii"))
                self.assertEqual(report["commits"][0]["author"], self.author)
                self.assertEqual(report["commits"][0]["subject"], self.subject)
                self.assertEqual(report["by_author"], {self.author: 1})

    def test_utf8_stdout_keeps_readable_unicode(self):
        result = self.run_cli("utf-8", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(self.author.encode("utf-8"), result.stdout)
        self.assertIn(self.subject.encode("utf-8"), result.stdout)

    def test_markdown_encoding_failure_has_file_output_guidance(self):
        result = self.run_cli("ascii")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"--output", result.stderr)
        self.assertIn(b"UTF-8", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)

    def test_file_output_stays_utf8_regardless_of_terminal_encoding(self):
        for options, name in (([], "report.md"), (["--json"], "report.json")):
            with self.subTest(name=name):
                path = self.repo / name
                result = self.run_cli("ascii", *options, "--output", str(path))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, b"")
                text = path.read_text(encoding="utf-8")
                self.assertIn(self.author, text)
                self.assertIn(self.subject, text)
