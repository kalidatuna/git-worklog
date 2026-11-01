import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from git_worklog.cli import main

class CliOptionsTests(unittest.TestCase):
    def invoke(self, *args, commits=None):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with patch("git_worklog.cli.read_commits", return_value=commits or []), contextlib.redirect_stdout(output):
                result = main([directory, *args])
            return result, output.getvalue()
    def test_abbreviated_flags_are_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main([".", "--auth", "Ada"])
        self.assertEqual(error.exception.code, 2)

    def test_version_works_without_a_repository(self):
        from git_worklog import __version__
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as error:
            main(["--version"])
        self.assertEqual(error.exception.code, 0)
        self.assertIn(__version__, output.getvalue())

    def test_report_name_can_be_overridden(self):
        result, output = self.invoke("--name", "Weekly [project]")
        self.assertEqual(result, 0)
        self.assertTrue(output.startswith(r"# Worklog: Weekly \[project\]"))

    def test_summary_only_omits_individual_commits_in_both_formats(self):
        _, markdown = self.invoke("--summary-only")
        self.assertIn("## Authors", markdown)
        self.assertNotIn("## Changes", markdown)
        _, output = self.invoke("--summary-only", "--json")
        report = json.loads(output)
        self.assertEqual(report["total"], 0)
        self.assertNotIn("commits", report)

    def test_limit_preserves_aggregate_counts_and_exposes_omissions(self):
        from datetime import datetime, timezone
        from git_worklog.model import Commit
        commits = [Commit(str(i) * 40, datetime.now(timezone.utc), "Ada", "Work") for i in range(3)]
        _, output = self.invoke("--limit", "1", "--json", commits=commits)
        report = json.loads(output)
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_author"], {"Ada": 3})
        self.assertEqual(len(report["commits"]), 1)
        self.assertEqual(report["omitted_commits"], 2)
        _, markdown = self.invoke("--limit", "0", commits=commits)
        self.assertIn("3 additional commit(s) omitted", markdown)
        self.assertNotIn("No changes", markdown)
    def test_invalid_limits_fail_as_cli_usage_errors(self):
        for value in ("-1", "no"):
            with self.subTest(value=value), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main([".", "--limit", value])
            self.assertEqual(error.exception.code, 2)

    def test_json_keeps_unicode_readable_without_losing_round_trip(self):
        from datetime import datetime, timezone
        from git_worklog.model import Commit
        commits = [Commit("a" * 40, datetime.now(timezone.utc), "Zoë", "ქართული")]
        _, output = self.invoke("--json", commits=commits)
        self.assertIn("ქართული", output)
        self.assertEqual(json.loads(output)["commits"][0]["author"], "Zoë")
