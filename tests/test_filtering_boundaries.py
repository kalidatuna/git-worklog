import unittest
from datetime import datetime, timedelta, timezone
from git_worklog.filtering import recent_commits
from git_worklog.model import Commit

class FilteringBoundaryTests(unittest.TestCase):
    def test_naive_reference_time_has_an_actionable_error(self):
        with self.assertRaisesRegex(ValueError, "now must include a timezone"):
            recent_commits([], 7, now=datetime(2026, 1, 1))
    def test_naive_commit_time_is_rejected_without_using_host_timezone(self):
        commit = Commit("a", datetime(2026, 1, 1), "Ada", "Work")
        with self.assertRaisesRegex(ValueError, "author timestamps"):
            recent_commits([commit], 7)
    def test_exact_cutoff_and_now_are_inclusive_but_future_is_not(self):
        now = datetime(2026, 1, 8, tzinfo=timezone.utc)
        times = [now - timedelta(days=7, microseconds=1),
                 now - timedelta(days=7), now, now + timedelta(microseconds=1)]
        commits = [Commit(str(i), stamp, "Ada", "Work") for i, stamp in enumerate(times)]
        self.assertEqual([c.sha for c in recent_commits(commits, 7, now=now)], ["2", "1"])
