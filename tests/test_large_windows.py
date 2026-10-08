import unittest
from datetime import datetime, timezone
from git_worklog.filtering import recent_commits
from git_worklog.model import Commit

class LargeWindowTests(unittest.TestCase):
    def test_windows_larger_than_datetime_history_include_old_commits(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        old = Commit('a' * 40, datetime(1980, 1, 1, tzinfo=timezone.utc), 'Ada', 'Older work')
        future = Commit('b' * 40, datetime(2099, 1, 1, tzinfo=timezone.utc), 'Ada', 'Future work')
        for days in (1000000, 10**30):
            with self.subTest(days=days):
                try:
                    selected = recent_commits([old, future], days, now=now)
                except OverflowError as error:
                    self.fail('Large date windows should not crash: ' + str(error))
                self.assertEqual(selected, [old])
