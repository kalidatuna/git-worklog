"""Aggregate selected commits for a report."""

from collections import Counter
from datetime import timezone

from .model import Commit


def summarize(commits: list[Commit]) -> dict:
    by_day = Counter(commit.authored_at.astimezone(timezone.utc).date().isoformat() for commit in commits)
    by_author = Counter(commit.author for commit in commits)
    return {
        "total": len(commits),
        "by_day": dict(sorted(by_day.items(), reverse=True)),
        "by_author": dict(sorted(by_author.items(), key=lambda item: (-item[1], item[0]))),
        "commits": [
            {
                "sha": commit.sha,
                "date_utc": commit.authored_at.astimezone(timezone.utc).isoformat(),
                "author": commit.author,
                "subject": commit.subject,
            }
            for commit in commits
        ],
    }
