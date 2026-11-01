import contextlib
import io
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from git_worklog.cli import main
from git_worklog.filtering import recent_commits
from git_worklog.model import Commit

class SubjectFilterTests(unittest.TestCase):
    def test_subject_filter_is_literal_case_insensitive_and_composes_with_author(self):
        now = datetime.now(timezone.utc)
        commits = [Commit('a', now, 'Ada', 'Fix [API]'), Commit('b', now, 'Bob', 'Fix [API]'),
                   Commit('c', now, 'Ada', 'Fix parser')]
        self.assertEqual([c.sha for c in recent_commits(commits, 7, 'ada', now, subject='[api]')], ['a'])
        output = io.StringIO()
        with patch('git_worklog.cli.read_commits', return_value=commits), contextlib.redirect_stdout(output):
            self.assertEqual(main(['.', '--grep', '[api]', '--author', 'ada', '--json']), 0)
        self.assertEqual(json.loads(output.getvalue())['total'], 1)
