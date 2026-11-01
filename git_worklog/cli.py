"""Command line interface for local worklogs."""

import argparse
import json
from pathlib import Path

from . import __version__
from .filtering import recent_commits
from .git import GitError, read_commits
from .render import render_markdown
from .summary import summarize


def positive_days(value: str) -> int:
    try:
        days = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("days must be an integer") from error
    if days < 1:
        raise argparse.ArgumentTypeError("days must be at least 1")
    return days


def nonnegative_limit(value: str) -> int:
    try:
        limit = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("limit must be an integer") from error
    if limit < 0:
        raise argparse.ArgumentTypeError("limit must be at least 0")
    return limit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize local Git history", allow_abbrev=False)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("repository", type=Path)
    parser.add_argument("--name", help="override the Markdown report repository name")
    parser.add_argument("--days", type=positive_days, default=7)
    parser.add_argument("--author", help="case-insensitive author name filter")
    parser.add_argument("--include-merges", action="store_true")
    parser.add_argument("--limit", type=nonnegative_limit, help="maximum individual commits to display; totals remain complete")
    parser.add_argument("--summary-only", action="store_true", help="omit individual commits from the report")
    parser.add_argument("--json", action="store_true", help="output JSON instead of Markdown")
    parser.add_argument("--output", type=Path, help="write report to this file")
    args = parser.parse_args(argv)
    if not args.repository.is_dir():
        parser.error("repository must be a directory")
    try:
        commits = read_commits(args.repository, include_merges=args.include_merges)
    except GitError as error:
        parser.error(str(error))
    selected = recent_commits(commits, args.days, args.author)
    summary = summarize(selected)
    if args.limit is not None and not args.summary_only:
        omitted = max(0, summary["total"] - args.limit)
        summary["commits"] = summary["commits"][:args.limit]
        if omitted:
            summary["omitted_commits"] = omitted
    if args.summary_only:
        summary.pop("commits")
    result = (
        json.dumps(summary, indent=2) + "\n" if args.json
        else render_markdown(summary, args.name if args.name is not None else args.repository.resolve().name, args.days, include_changes=not args.summary_only)
    )
    if args.output:
        try:
            args.output.write_text(result, encoding="utf-8")
        except OSError as error:
            parser.error(str(error))
    else:
        print(result, end="")
    return 0
