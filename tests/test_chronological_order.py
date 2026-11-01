import contextlib
import io
import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from git_worklog.cli import main
from git_worklog.model import Commit

class ChronologicalOrderTests(unittest.TestCase):
    def test_order_applies_before_display_limit_without_changing_totals(self):
        now = datetime.now(timezone.utc)
        commits = [Commit('a' * 40, now - timedelta(days=2), 'Ada', 'First'),
                   Commit('b' * 40, now - timedelta(days=1), 'Ada', 'Second')]
        for flags, expected in (([], 'Second'), (['--oldest-first'], 'First')):
            with self.subTest(flags=flags):
                output = io.StringIO()
                with patch('git_worklog.cli.read_commits', return_value=commits), contextlib.redirect_stdout(output):
                    self.assertEqual(main(['.', '--json', '--limit', '1', *flags]), 0)
                report = json.loads(output.getvalue())
                self.assertEqual(report['total'], 2)
                self.assertEqual(report['omitted_commits'], 1)
                self.assertEqual(report['commits'][0]['subject'], expected)
