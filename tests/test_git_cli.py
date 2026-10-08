import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from git_worklog.cli import main
from git_worklog.git import GitError, read_commits


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
            utc_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            env["GIT_AUTHOR_DATE"] = utc_date
            env["GIT_COMMITTER_DATE"] = utc_date
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

    def test_empty_commit_subjects_survive_log_parsing_and_json_output(self):
        for subjects in ([""], ["", "Later work"], ["Earlier work", ""]):
            with self.subTest(subjects=subjects), tempfile.TemporaryDirectory() as directory:
                repo = Path(directory)
                subprocess.run(["git", "init", "-q", directory], check=True)
                env = os.environ.copy()
                env.update({
                    "GIT_AUTHOR_NAME": "Ada", "GIT_AUTHOR_EMAIL": "ada@example.test",
                    "GIT_COMMITTER_NAME": "Ada", "GIT_COMMITTER_EMAIL": "ada@example.test",
                })
                utc_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                env["GIT_AUTHOR_DATE"] = utc_date
                env["GIT_COMMITTER_DATE"] = utc_date
                for subject in subjects:
                    subprocess.run([
                        "git", "-C", directory, "commit", "-q", "--allow-empty",
                        "--allow-empty-message", "-m", subject,
                    ], check=True, env=env)
                expected = list(reversed(subjects))
                try:
                    commits = read_commits(repo)
                except GitError as error:
                    self.fail(f"Valid empty-message history should parse: {error}")
                self.assertEqual([commit.subject for commit in commits], expected)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main([directory, "--json"]), 0)
                summary = json.loads(output.getvalue())
                self.assertEqual(summary["total"], len(subjects))
                self.assertEqual([commit["subject"] for commit in summary["commits"]], expected)


if __name__ == "__main__":
    unittest.main()
