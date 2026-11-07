# Git Worklog

Generate a concise work summary from a local Git repository. The tool groups
commits by UTC day, counts commits by author, and lists their subjects. It
reads local history only and has no third-party Python dependencies.

```sh
python3 -m git_worklog /path/to/repo --days 14
python3 -m git_worklog /path/to/repo --days 30 --author Datuna --json
python3 -m git_worklog /path/to/repo --days 7 --output weekly.md
python3 -m git_worklog /path/to/repo --exclude-author 'dependabot[bot]'
```

`--days` selects commits with an author timestamp in the last N days. Merge
commits are skipped by default; use `--include-merges` to include them. The
command exits 0 on success and 2 for invalid input or Git errors. See
[behavior](docs/behavior.md) for timezone and history details.

Report controls:

```sh
python3 -m git_worklog --version
python3 -m git_worklog /path/to/repo --name "Weekly engineering" --limit 20
python3 -m git_worklog /path/to/repo --summary-only --json
```

`--limit N` caps the individual changes shown while keeping all aggregate
counts. Use `--limit 0` to hide entries and retain an omission count, or
`--summary-only` to omit the changes section entirely. See
[development](docs/development.md) for local checks.

The repository path now defaults to the current directory. Use `--all` for all
local refs, `--until` for historical periods, `--grep` for subject matching,
`--oldest-first` for chronological entries, and `--output -` for stdout. See
[history selection](docs/history-selection.md) for examples and exact behavior.
