"""Run Git without a shell and parse NUL-separated log fields."""

import subprocess
from datetime import datetime
from pathlib import Path

from .model import Commit


class GitError(Exception):
    """Git could not return a usable commit log."""


def read_commits(repository: Path, include_merges: bool = False) -> list[Commit]:
    command = [
        "git", "-C", str(repository), "log", "-z",
        "--format=%H%x00%aI%x00%an%x00%s",
    ]
    if not include_merges:
        command.append("--no-merges")
    try:
        result = subprocess.run(command, capture_output=True, check=False)
    except OSError as error:
        raise GitError(str(error)) from error
    if result.returncode:
        raise GitError(result.stderr.decode("utf-8", errors="replace").strip())
    if not result.stdout:
        return []
    fields = result.stdout.rstrip(b"\0").split(b"\0")
    if len(fields) % 4:
        raise GitError("unexpected Git log format")
    commits: list[Commit] = []
    try:
        for index in range(0, len(fields), 4):
            sha, authored, author, subject = (
                field.decode("utf-8", errors="replace") for field in fields[index:index + 4]
            )
            iso_date = authored.removesuffix("Z") + "+00:00" if authored.endswith("Z") else authored
            commits.append(Commit(sha, datetime.fromisoformat(iso_date), author, subject))
    except ValueError as error:
        raise GitError(f"invalid Git date: {error}") from error
    return commits
