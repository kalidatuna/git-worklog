import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from git_worklog.git import read_commits

class GitConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.env = os.environ.copy()
        self.env.update(GIT_AUTHOR_NAME="Zoë", GIT_AUTHOR_EMAIL="z@example.test",
                        GIT_COMMITTER_NAME="Zoë", GIT_COMMITTER_EMAIL="z@example.test")
        self.git("commit", "-q", "--allow-empty", "-m", "Résumé")
    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True, env=self.env)
    def test_notes_configuration_does_not_corrupt_log_records(self):
        self.git("notes", "add", "-m", "An attached note")
        self.git("config", "notes.displayRef", "refs/notes/commits")
        commits = read_commits(self.repo)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].subject, "Résumé")
