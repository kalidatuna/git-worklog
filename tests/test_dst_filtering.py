import unittest
from datetime import datetime, timedelta, timezone, tzinfo

from git_worklog.filtering import recent_commits
from git_worklog.model import Commit


class FallBackZone(tzinfo):
    """Self-contained test zone with a repeated hour on November 1, 2026."""

    def utcoffset(self, dt):
        wall = dt.replace(tzinfo=None)
        if wall < datetime(2026, 11, 1, 1):
            return timedelta(hours=-4)
        if wall < datetime(2026, 11, 1, 2) and dt.fold == 0:
            return timedelta(hours=-4)
        return timedelta(hours=-5)

    def dst(self, dt):
        return self.utcoffset(dt) - timedelta(hours=-5)


class DaylightSavingFilterTests(unittest.TestCase):
    def test_rolling_day_is_24_hours_across_offset_change(self):
        now = datetime(2026, 11, 1, 12, tzinfo=FallBackZone())
        # Noon is 17:00 UTC. The previous 24-hour window starts at 17:00 UTC,
        # not the previous local noon, which was 16:00 UTC.
        commits = [
            Commit("outside", datetime(2026, 10, 31, 16, 30, tzinfo=timezone.utc), "Ada", "Old"),
            Commit("inside", datetime(2026, 10, 31, 17, 30, tzinfo=timezone.utc), "Ada", "Recent"),
        ]
        self.assertEqual([c.sha for c in recent_commits(commits, 1, now=now)], ["inside"])

    def test_repeated_hour_is_sorted_by_instant_instead_of_wall_time(self):
        zone = FallBackZone()
        commits = [
            Commit("earlier", datetime(2026, 11, 1, 1, 45, tzinfo=zone, fold=0), "Ada", "First hour"),
            Commit("later", datetime(2026, 11, 1, 1, 15, tzinfo=zone, fold=1), "Ada", "Repeated hour"),
        ]
        now = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
        self.assertEqual([c.sha for c in recent_commits(commits, 2, now=now)], ["later", "earlier"])
