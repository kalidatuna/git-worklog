import contextlib
import io
import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from git_worklog.cli import main
from git_worklog.filtering import recent_commits
from git_worklog.model import Commit


class SinceTests(unittest.TestCase):
    def setUp(self):
        self.start = datetime(2020, 1, 1, tzinfo=timezone.utc)
        self.end = datetime(2020, 2, 1, tzinfo=timezone.utc)
        stamps = [self.start - timedelta(microseconds=1), self.start,
                  self.end, self.end + timedelta(microseconds=1)]
        self.commits = [Commit(str(i) * 40, stamp, "Ada", "Work " + str(i))
                        for i, stamp in enumerate(stamps)]

    def report(self, *options):
        output = io.StringIO()
        with patch("git_worklog.cli.read_commits", return_value=self.commits), contextlib.redirect_stdout(output):
            self.assertEqual(main([".", *options]), 0)
        return output.getvalue()

    def test_api_uses_inclusive_exact_start_instead_of_rolling_days(self):
        start_with_offset = self.start.astimezone(timezone(timedelta(hours=4)))
        result = recent_commits(self.commits, 7, now=self.end, since=start_with_offset)
        self.assertEqual([c.sha for c in result], ["2" * 40, "1" * 40])

    def test_json_reports_utc_range_and_applies_limit_after_counts(self):
        report = json.loads(self.report("--since", "2020-01-01T04:00:00+04:00",
                                        "--until", "2020-02-01T00:00:00Z", "--limit", "0", "--json"))
        self.assertEqual(report["period_start_utc"], self.start.isoformat())
        self.assertEqual(report["period_end_utc"], self.end.isoformat())
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["by_author"], {"Ada": 2})
        self.assertEqual(report["omitted_commits"], 2)
        self.assertEqual(report["commits"], [])

    def test_markdown_labels_exact_range_instead_of_default_days(self):
        report = self.report("--since", self.start.isoformat(), "--until", self.end.isoformat())
        self.assertIn(f"From {self.start.isoformat()} to {self.end.isoformat()}", report)
        self.assertNotIn("7 day(s)", report)

    def test_since_without_until_captures_one_current_endpoint(self):
        with patch("git_worklog.cli.datetime", wraps=datetime) as clock:
            clock.now.return_value = self.end
            report = json.loads(self.report("--since", self.start.isoformat(), "--json"))
        self.assertEqual(report["period_end_utc"], self.end.isoformat())
        self.assertEqual(report["total"], 2)

    def test_invalid_ranges_and_conflicting_days_fail_before_git_reads(self):
        cases = [
            ["--since", "2020-01-01"],
            ["--since", "0001-01-01T00:00:00+04:00"],
            ["--since", self.end.isoformat(), "--until", self.start.isoformat()],
            ["--since", self.start.isoformat(), "--days", "7"],
        ]
        for options in cases:
            with self.subTest(options=options), patch("git_worklog.cli.read_commits") as read:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    main([".", *options])
                self.assertEqual(error.exception.code, 2)
                read.assert_not_called()

    def test_api_rejects_naive_start_and_reversed_range(self):
        with self.assertRaisesRegex(ValueError, "since must include a timezone"):
            recent_commits([], 7, now=self.end, since=datetime(2020, 1, 1))
        with self.assertRaisesRegex(ValueError, "since must not be later"):
            recent_commits([], 7, now=self.start, since=self.end)

    def test_equal_endpoints_select_only_that_instant(self):
        result = recent_commits(self.commits, 7, now=self.start, since=self.start)
        self.assertEqual([c.sha for c in result], ["1" * 40])
