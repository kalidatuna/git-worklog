import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from git_worklog.cli import main
from git_worklog.git import read_commits


class GitCliTests(unittest.TestCase):
    def test_reads_local_commit_and_json(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "note.txt").write_text("hello\n")
            subprocess.run(["git", "-C", directory, "add", "note.txt"], check=True)
            env = os.environ.copy()
            env.update({
                "GIT_AUTHOR_NAME": "Ada", "GIT_AUTHOR_EMAIL": "ada@example.test",
                "GIT_COMMITTER_NAME": "Ada", "GIT_COMMITTER_EMAIL": "ada@example.test",
            })
            subprocess.run(["git", "-C", directory, "commit", "-qm", "Add note"], check=True, env=env)
            self.assertEqual(read_commits(repo)[0].subject, "Add note")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([directory, "--json"]), 0)
            self.assertEqual(json.loads(output.getvalue())["total"], 1)

    def test_invalid_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main([directory])
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
