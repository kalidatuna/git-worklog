"""Render a human-readable Markdown worklog."""


import html
import re


def _text(value: str) -> str:
    value = " ".join(value.split())
    value = html.escape(value, quote=False)
    return re.sub(r"([\\\x60*_{}\[\]()#+.!|>~-])", r"\\\1", value)


def render_markdown(summary: dict, repository_name: str, days: int, include_changes: bool = True) -> str:
    lines = [
        f"# Worklog: {_text(repository_name)}", "",
        f"Last {days} day(s), UTC · {summary['total']} commit(s)", "",
        "## Commits by day", "",
    ]
    if summary["by_day"]:
        lines.extend(f"- {day}: {count}" for day, count in summary["by_day"].items())
    else:
        lines.append("- No commits in this period.")
    lines.extend(["", "## Authors", ""])
    if summary["by_author"]:
        lines.extend(f"- {_text(author)}: {count}" for author, count in summary["by_author"].items())
    else:
        lines.append("- No authors in this period.")
    if not include_changes:
        return "\n".join(lines) + "\n"
    lines.extend(["", "## Changes", ""])
    for commit in summary["commits"]:
        day = commit["date_utc"][:10]
        subject = _text(commit["subject"])
        lines.append(f"- {day} `{commit['sha'][:7]}` {subject} ({_text(commit['author'])})")
    if not summary["commits"]:
        lines.append("- No changes in this period.")
    return "\n".join(lines) + "\n"
