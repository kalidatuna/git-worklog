# Git Worklog

Generate a concise work summary from a local Git repository. The tool groups
commits by UTC day, counts commits by author, and lists their subjects. It
reads local history only and has no third-party Python dependencies.

```sh
python3 -m git_worklog /path/to/repo --days 14
python3 -m git_worklog /path/to/repo --days 30 --author Datuna --json
python3 -m git_worklog /path/to/repo --days 7 --output weekly.md
```

`--days` selects commits with an author timestamp in the last N days. Merge
commits are skipped by default; use `--include-merges` to include them. The
command exits 0 on success and 2 for invalid input or Git errors. See
[behavior](docs/behavior.md) for timezone and history details.
