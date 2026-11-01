# Development

Python 3.10 or newer and Git are required. The application has no runtime Python
dependencies. Run the tests from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q git_worklog
```

Integration tests create temporary repositories and use synthetic test identities.
They do not alter your Git identity or contact GitHub. The suite covers empty
histories, merge filtering, Unicode, local Git configuration, report formatting,
filter boundaries, module execution, and atomic output failures.

To test the installed command in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/git-worklog --version
```

On Windows, use `.venv\Scripts\python.exe` and
`.venv\Scripts\git-worklog.exe` for the last two commands.
