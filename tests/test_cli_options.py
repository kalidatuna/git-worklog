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
