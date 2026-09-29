import unittest
from datetime import datetime, timezone

from git_worklog.filtering import recent_commits
from git_worklog.model import Commit
from git_worklog.render import render_markdown
from git_worklog.summary import summarize


class SummaryTests(unittest.TestCase):
    def test_filter_and_aggregate(self):
        now = datetime(2026, 9, 30, tzinfo=timezone.utc)
        commits = [
            Commit("a" * 40, datetime(2026, 9, 29, tzinfo=timezone.utc), "Ada", "Add parser"),
            Commit("b" * 40, datetime(2026, 9, 20, tzinfo=timezone.utc), "Bob", "Old work"),
        ]
        selected = recent_commits(commits, 7, "ada", now=now)
        summary = summarize(selected)
        self.assertEqual(summary["total"], 1)
        self.assertEqual(summary["by_day"], {"2026-09-29": 1})
        self.assertIn("Add parser", render_markdown(summary, "example", 7))

    def test_empty_summary(self):
        self.assertIn("No commits", render_markdown(summarize([]), "example", 7))


if __name__ == "__main__":
    unittest.main()
