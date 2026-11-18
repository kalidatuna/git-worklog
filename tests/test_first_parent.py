import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from git_worklog.git import read_commits


class FirstParentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.env = dict(os.environ, GIT_AUTHOR_NAME="Ada", GIT_AUTHOR_EMAIL="ada@example.test",
                        GIT_COMMITTER_NAME="Ada", GIT_COMMITTER_EMAIL="ada@example.test",
                        GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/main")
        self.git("commit", "-q", "--allow-empty", "-m", "Base")
        self.git("checkout", "-qb", "topic")
        self.git("commit", "-q", "--allow-empty", "-m", "Topic change")
        self.git("checkout", "-q", "main")
        self.git("commit", "-q", "--allow-empty", "-m", "Main change")
        self.git("merge", "--no-ff", "-m", "Integrate topic", "topic")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), "-c", "commit.gpgSign=false",
                               "-c", "merge.gpgSign=false", *args],
                              check=True, capture_output=True, env=self.env)

    def test_first_parent_skips_topic_history_and_keeps_optional_merges(self):
        self.assertEqual({c.subject for c in read_commits(self.repo)},
                         {"Base", "Main change", "Topic change"})
        self.assertEqual({c.subject for c in read_commits(self.repo, first_parent=True)},
                         {"Base", "Main change"})
        self.assertEqual({c.subject for c in read_commits(self.repo, first_parent=True, include_merges=True)},
                         {"Base", "Main change", "Integrate topic"})

    def test_cli_filters_history_before_summary_and_display_limit(self):
        result = subprocess.run([sys.executable, "-m", "git_worklog", str(self.repo),
                                 "--first-parent", "--include-merges", "--limit", "1", "--json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_author"], {"Ada": 3})
        self.assertEqual(sum(report["by_day"].values()), 3)
        self.assertEqual(report["omitted_commits"], 2)
        self.assertEqual(report["commits"][0]["subject"], "Integrate topic")

    def test_all_refs_still_includes_topic_as_a_separate_root(self):
        commits = read_commits(self.repo, first_parent=True, include_merges=True, all_refs=True)
        self.assertEqual({c.subject for c in commits},
                         {"Base", "Main change", "Topic change", "Integrate topic"})
        self.assertEqual(len(commits), 4)
