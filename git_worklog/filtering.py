"""Select recent commits by author timestamp and optional name."""

from datetime import datetime, timedelta, timezone
from collections.abc import Sequence

from .model import Commit


def recent_commits(
    commits: list[Commit], days: int, author: str | None = None,
    now: datetime | None = None, *, subject: str | None = None,
    exclude_authors: Sequence[str] = (),
    since: datetime | None = None,
) -> list[Commit]:
    if days < 1:
        raise ValueError("days must be at least 1")
    excluded = tuple(value.strip().casefold() for value in exclude_authors)
    if any(not value for value in excluded):
        raise ValueError("excluded author filters must not be empty")
    now = now or datetime.now(timezone.utc)
    if now.utcoffset() is None:
        raise ValueError("now must include a timezone")
    # Use elapsed time, not local wall time, across daylight-saving changes.
    now = now.astimezone(timezone.utc)
    if any(commit.authored_at.utcoffset() is None for commit in commits):
        raise ValueError("commit author timestamps must include a timezone")
    if since is not None:
        if since.utcoffset() is None:
            raise ValueError("since must include a timezone")
        try:
            cutoff = since.astimezone(timezone.utc)
        except OverflowError as error:
            raise ValueError("since must have a representable UTC date") from error
        if cutoff > now:
            raise ValueError("since must not be later than the period end")
    else:
        try:
            cutoff = now - timedelta(days=days)
        except OverflowError:
            cutoff = datetime.min.replace(tzinfo=timezone.utc)
    selected = [
        commit for commit in commits
        if cutoff <= commit.authored_at.astimezone(timezone.utc) <= now
        and (author is None or author.casefold() in commit.author.casefold())
        and (subject is None or subject.casefold() in commit.subject.casefold())
        and not any(value in commit.author.casefold() for value in excluded)
    ]
    return sorted(selected, key=lambda item: item.authored_at.astimezone(timezone.utc), reverse=True)
