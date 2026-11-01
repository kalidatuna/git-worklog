"""Exercise merge selection against actual local Git history."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from git_worklog.git import read_commits

class MergeHistoryTests(unittest.TestCase):
    def test_merges_are_optional_and_branch_commits_remain_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            env = os.environ.copy()
            env.update(GIT_AUTHOR_NAME="Ada", GIT_AUTHOR_EMAIL="ada@example.test",
                       GIT_COMMITTER_NAME="Ada", GIT_COMMITTER_EMAIL="ada@example.test")
            def git(*args):
                return subprocess.run(["git", "-C", directory, *args],
                                      check=True, capture_output=True, env=env)
            git("init", "-q")
            git("commit", "-q", "--allow-empty", "-m", "Initial")
            branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip()
            git("checkout", "-qb", "topic")
            (repo / "topic.txt").write_text("topic")
            git("add", "topic.txt")
            git("commit", "-qm", "Topic work")
            git("checkout", "-q", branch)
            (repo / "main.txt").write_text("main")
            git("add", "main.txt")
            git("commit", "-qm", "Main work")
            git("merge", "--no-ff", "-m", "Merge topic", "topic")
            self.assertEqual({c.subject for c in read_commits(repo)},
                             {"Initial", "Topic work", "Main work"})
            self.assertEqual({c.subject for c in read_commits(repo, include_merges=True)},
                             {"Initial", "Topic work", "Main work", "Merge topic"})
