import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from git_worklog.git import GitError, read_commits


class RepositoryEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = self.make_repository("target", "Target change")
        self.foreign = self.make_repository("foreign", "Foreign change")

    def make_repository(self, name, subject=None):
        path = self.root / name
        subprocess.run(["git", "init", "-q", str(path)], check=True)
        if subject is not None:
            subprocess.run([
                "git", "-C", str(path), "-c", "user.name=Test Author",
                "-c", "user.email=test@example.test", "-c", "commit.gpgSign=false",
                "commit", "-q", "--allow-empty", "-m", subject,
            ], check=True)
        return path

    def test_exported_repository_location_cannot_override_selected_path(self):
        foreign_dir = str(self.foreign / ".git")
        with patch.dict(os.environ, {"GIT_DIR": foreign_dir, "GIT_WORK_TREE": str(self.foreign)}):
            commits = read_commits(self.target)
            self.assertEqual([c.subject for c in commits], ["Target change"])
            self.assertEqual(os.environ["GIT_DIR"], foreign_dir)

    def test_empty_repository_is_not_replaced_by_foreign_history(self):
        empty = self.make_repository("empty")
        with patch.dict(os.environ, {"GIT_DIR": str(self.foreign / ".git")}):
            self.assertEqual(read_commits(empty), [])

    def test_nonrepository_still_raises_with_exported_git_dir(self):
        plain = self.root / "plain"
        plain.mkdir()
        with patch.dict(os.environ, {"GIT_DIR": str(self.foreign / ".git")}):
            with self.assertRaises(GitError):
                read_commits(plain)

    def test_foreign_common_directory_does_not_redirect_object_lookup(self):
        with patch.dict(os.environ, {"GIT_COMMON_DIR": str(self.foreign / ".git")}):
            self.assertEqual([c.subject for c in read_commits(self.target)], ["Target change"])
