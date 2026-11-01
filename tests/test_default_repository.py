import contextlib
import io
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from git_worklog.cli import main

class DefaultRepositoryTests(unittest.TestCase):
    def test_omitted_repository_uses_current_directory(self):
        output = io.StringIO()
        with patch('git_worklog.cli.read_commits', return_value=[]) as read, contextlib.redirect_stdout(output):
            self.assertEqual(main(['--json']), 0)
        self.assertEqual(read.call_args.args, (Path('.'),))
        self.assertEqual(json.loads(output.getvalue())['total'], 0)
