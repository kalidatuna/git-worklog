import contextlib
import io
import json
import unittest
from unittest.mock import patch
from git_worklog.cli import main

class StdoutDestinationTests(unittest.TestCase):
    def test_dash_destination_prints_report_without_writing_a_file(self):
        output = io.StringIO()
        with patch('git_worklog.cli.read_commits', return_value=[]), patch('git_worklog.cli.write_report') as write, contextlib.redirect_stdout(output):
            self.assertEqual(main(['.', '--output', '-', '--json']), 0)
        write.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['total'], 0)
