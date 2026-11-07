import contextlib
import io
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from git_worklog.cli import main
from git_worklog.filtering import recent_commits
from git_worklog.model import Commit


class ExcludedAuthorTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.commits = [
            Commit("a", self.now, "Ada", "Fix [API]"),
            Commit("b", self.now, "Release Bot", "Fix [API]"),
            Commit("c", self.now, "Dependency [BOT]", "Update packages"),
            Commit("d", self.now, "Ada", "Write docs"),
        ]

    def test_exclusions_are_case_insensitive_trimmed_literal_substrings(self):
        result = recent_commits(self.commits, 7, now=self.now,
                                exclude_authors=[" release ", "[bot]"])
        self.assertEqual([c.sha for c in result], ["a", "d"])

    def test_exclusion_takes_precedence_over_author_and_subject_matches(self):
        result = recent_commits(self.commits, 7, author="bot", now=self.now,
                                subject="[API]", exclude_authors=["Release"])
        self.assertEqual(result, [])

    def test_cli_repeated_exclusions_update_totals_before_display_limit(self):
        output = io.StringIO()
        with patch("git_worklog.cli.read_commits", return_value=self.commits), contextlib.redirect_stdout(output):
            code = main([".", "--exclude-author", "release", "--exclude-author", "[bot]",
                         "--limit", "1", "--json"])
        self.assertEqual(code, 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["by_author"], {"Ada": 2})
        self.assertEqual(sum(report["by_day"].values()), 2)
        self.assertEqual(report["omitted_commits"], 1)
        self.assertEqual(report["commits"][0]["sha"], "a")

    def test_empty_cli_exclusions_fail_before_reading_history(self):
        for value in ("", "   "):
            with self.subTest(value=value), patch("git_worklog.cli.read_commits") as read:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                    main([".", "--exclude-author", value])
                self.assertEqual(raised.exception.code, 2)
                read.assert_not_called()

    def test_python_api_rejects_empty_exclusions(self):
        with self.assertRaisesRegex(ValueError, "excluded author filters must not be empty"):
            recent_commits(self.commits, 7, now=self.now, exclude_authors=[" "])
