# Selecting history

The repository path is optional and defaults to the current directory. By
default, Git reads commits reachable from HEAD, excluding merge commits.

```sh
git-worklog
git-worklog /path/to/repo --all --include-merges
```

`--all` includes all refs visible in the local repository, including local
branches and remote-tracking refs. It does not fetch remote changes. Git notes
and other non-branch refs can also contribute reachable commits.

## Historical periods

```sh
git-worklog --days 7 --until 2026-10-01T00:00:00Z
```

`--until` requires a timezone-aware ISO 8601 timestamp. It ends the rolling
N-day interval at that instant. Both endpoints are inclusive. The Markdown
heading includes the requested endpoint; JSON adds `period_end_utc` in UTC.
Without `--until`, the endpoint is the current clock time.

## Names, subjects, and order

```sh
git-worklog --author Ada --grep '[API]' --oldest-first --limit 10
```

`--author` and `--grep` are case-insensitive literal substring filters. They
combine with the date window, and both must match when supplied together.
`--grep` searches the commit subject, not the message body. It does not use
regular expressions. Counts cover only matching commits.

Use repeatable `--exclude-author NAME` options to omit unwanted authors:

```sh
git-worklog --exclude-author 'dependabot[bot]' --exclude-author 'Release Bot'
```

Each exclusion is a case-insensitive literal substring of the author name, with
surrounding whitespace trimmed. A match against any exclusion removes the commit,
even if `--author` and `--grep` match it. Empty or whitespace-only exclusions are
argument errors. Exclusions apply before summary counts and display limits, so
totals, day counts, and author counts describe only the remaining commits.
The Python filtering API accepts the same filters through `exclude_authors`.

The default entry order is newest first. `--oldest-first` reverses matching
entries before `--limit` applies. Counts still cover all matching commits.
Aggregate day counts remain newest-day first, regardless of entry order.

## Output destination

```sh
git-worklog --json --output -
git-worklog --output weekly.md
```

`--output -` prints to standard output. To write a file literally named `-`,
supply its absolute path, such as `--output /path/to/-`. Other destinations
retain the atomic replacement behavior described in [behavior](behavior.md).
