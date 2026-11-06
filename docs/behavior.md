# Behavior

The report reads the current local repository history with `git log`. It
does not query GitHub, inspect uncommitted changes, or infer issue or pull
request activity. Merge commits are excluded unless requested.
The selected repository path takes precedence over inherited `GIT_DIR`,
`GIT_WORK_TREE`, and `GIT_COMMON_DIR` settings, including when run from a Git
hook. These variables are removed only from the child Git processes, leaving
the caller's environment intact.
Commits with empty messages are counted and keep an empty subject in the output.
An initialized repository whose current branch has no commits produces an empty
report. Directories outside a Git repository still produce an error.

Filtering uses author timestamps and a rolling interval of N 24-hour days.
The Python API converts timezone-aware reference times to UTC before calculating
the window. Ordering also uses UTC instants, so daylight-saving transitions and
repeated local hours do not change the window length or chronological order.
Dates in output are converted to UTC, so a commit near midnight may appear on
a different day than in your local timezone. Future-dated commits are omitted.
The author filter matches a case-insensitive substring of the author name.
A date window larger than the representable calendar includes all past commits
instead of overflowing; future-dated commits remain excluded.

The command reads HEAD-reachable commits, or all local refs with `--all`. Large repositories may take longer.
Markdown escapes report names, author names, and subjects as literal text and
collapses embedded whitespace onto a single line. JSON preserves original text
and writes readable Unicode. Review repository content before publishing.

## Report options

- `--name TEXT` overrides the Markdown heading only; it does not change filtering.
- `--limit N` accepts a nonnegative integer. Aggregates cover the full selected
  period. JSON adds `omitted_commits` when entries are hidden; Markdown reports
  the omitted count. Entries remain in newest author-timestamp order.
- `--summary-only` removes the Markdown changes section and the JSON `commits`
  key. When combined with `--limit`, aggregate-only output takes precedence.
- `--version` prints the package version without reading a repository.
- Option names must be spelled out; abbreviated flags are rejected.

Reports written with `--output` use UTF-8 and an atomic replacement in the
destination directory. Existing file permissions are retained. A failed write
leaves the previous report intact and removes the temporary file. The parent
directory must already exist, and symbolic-link output paths are rejected.
The command reports input, Git, and file-output failures with exit status 2.

Git notes and user-configured log output encodings do not alter parsed records.
Signature verification text is suppressed even when `log.showSignature` is enabled,
so signed commits retain their full commit IDs in reports. Worklog generation does
not verify signatures; use `git verify-commit` separately when verification is needed.
The Python filtering API requires timezone-aware reference and commit timestamps.
