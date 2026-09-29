"""Render a human-readable Markdown worklog."""


def render_markdown(summary: dict, repository_name: str, days: int) -> str:
    lines = [
        f"# Worklog: {repository_name}", "",
        f"Last {days} day(s), UTC · {summary['total']} commit(s)", "",
        "## Commits by day", "",
    ]
    if summary["by_day"]:
        lines.extend(f"- {day}: {count}" for day, count in summary["by_day"].items())
    else:
        lines.append("- No commits in this period.")
    lines.extend(["", "## Authors", ""])
    if summary["by_author"]:
        lines.extend(f"- {author}: {count}" for author, count in summary["by_author"].items())
    else:
        lines.append("- No authors in this period.")
    lines.extend(["", "## Changes", ""])
    for commit in summary["commits"]:
        day = commit["date_utc"][:10]
        subject = commit["subject"].replace("\n", " ").replace("\r", " ")
        lines.append(f"- {day} `{commit['sha'][:7]}` {subject} ({commit['author']})")
    if not summary["commits"]:
        lines.append("- No changes in this period.")
    return "\n".join(lines) + "\n"
