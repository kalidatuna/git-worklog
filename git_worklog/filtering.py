"""Select recent commits by author timestamp and optional name."""

from datetime import datetime, timedelta, timezone

from .model import Commit


def recent_commits(
    commits: list[Commit], days: int, author: str | None = None,
    now: datetime | None = None,
) -> list[Commit]:
    if days < 1:
        raise ValueError("days must be at least 1")
    now = now or datetime.now(timezone.utc)
    try:
        cutoff = now - timedelta(days=days)
    except OverflowError:
        cutoff = datetime.min.replace(tzinfo=timezone.utc)
    selected = [
        commit for commit in commits
        if cutoff <= commit.authored_at.astimezone(timezone.utc) <= now
        and (author is None or author.casefold() in commit.author.casefold())
    ]
    return sorted(selected, key=lambda item: item.authored_at, reverse=True)
