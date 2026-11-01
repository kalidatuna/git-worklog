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
