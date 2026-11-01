import argparse
import contextlib
import io
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from git_worklog.cli import main, utc_timestamp
from git_worklog.model import Commit

class UntilTests(unittest.TestCase):
    def test_historical_window_uses_requested_end(self):
        commits = [Commit('a' * 40, datetime(2020, 1, 1, tzinfo=timezone.utc), 'Ada', 'Old work'),
                   Commit('b' * 40, datetime(2020, 1, 3, tzinfo=timezone.utc), 'Ada', 'Later work')]
        output = io.StringIO()
        with patch('git_worklog.cli.read_commits', return_value=commits), contextlib.redirect_stdout(output):
            self.assertEqual(main(['.', '--json', '--days', '1', '--until', '2020-01-02T04:00:00+04:00']), 0)
        report = json.loads(output.getvalue())
        self.assertEqual([c['subject'] for c in report['commits']], ['Old work'])

    def test_naive_and_invalid_timestamps_are_argument_errors(self):
        for value in ('2020-01-01', 'yesterday', '2020-01-01T00:00:00'):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                utc_timestamp(value)

    def test_historical_endpoint_is_reported_in_json_and_markdown(self):
        for options in ([], ['--json']):
            output = io.StringIO()
            with patch('git_worklog.cli.read_commits', return_value=[]), contextlib.redirect_stdout(output):
                main(['.', '--until', '2020-01-02T00:00:00Z', *options])
            self.assertIn('2020-01-02T00:00:00+00:00', output.getvalue())

    def test_timestamp_outside_utc_range_is_an_argument_error(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            utc_timestamp('0001-01-01T00:00:00+04:00')
