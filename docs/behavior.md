# Behavior

The report reads the current local repository history with `git log`. It
does not query GitHub, inspect uncommitted changes, or infer issue or pull
request activity. Merge commits are excluded unless requested.
Commits with empty messages are counted and keep an empty subject in the output.

Filtering uses author timestamps and a rolling interval of N 24-hour days.
Dates in output are converted to UTC, so a commit near midnight may appear on
a different day than in your local timezone. Future-dated commits are omitted.
The author filter matches a case-insensitive substring of the author name.

The command reads all reachable commits. Large repositories may take longer.
Its Markdown output is intended for personal notes; commit subjects and author
names come from the repository and should be reviewed before publishing.
