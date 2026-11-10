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
from git_worklog.git import read_commits


class MailmapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for name, email in (("Work Alias", "work@example.test"), ("Home Alias", "home@example.test")):
            env = dict(os.environ, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email,
                       GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email,
                       GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
            subprocess.run(["git", "-C", str(self.repo), "-c", "commit.gpgSign=false",
                            "commit", "-q", "--allow-empty", "-m", "Change by " + name],
                           check=True, env=env)
        (self.repo / ".mailmap").write_text(
            "Canonical Zoë <canonical@example.test> <work@example.test>\n"
            "Canonical Zoë <canonical@example.test> <home@example.test>\n", encoding="utf-8")

    def report(self, *options):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main([str(self.repo), *options]), 0)
        return output.getvalue()

    def test_mapping_is_opt_in_and_preserves_commit_identity_and_content(self):
        raw = read_commits(self.repo)
        mapped = read_commits(self.repo, use_mailmap=True)
        self.assertEqual([c.author for c in raw], ["Home Alias", "Work Alias"])
        self.assertEqual([c.author for c in mapped], ["Canonical Zoë"] * 2)
        self.assertEqual([(c.sha, c.authored_at, c.subject) for c in raw],
                         [(c.sha, c.authored_at, c.subject) for c in mapped])

    def test_cli_groups_mapped_names_before_author_filters_and_counts(self):
        report = json.loads(self.report("--mailmap", "--author", "canonical", "--json"))
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["by_author"], {"Canonical Zoë": 2})
        self.assertEqual({c["author"] for c in report["commits"]}, {"Canonical Zoë"})
        excluded = json.loads(self.report("--mailmap", "--exclude-author", "canonical", "--json"))
        self.assertEqual(excluded["total"], 0)
        self.assertEqual(excluded["by_author"], {})

    def test_mapping_without_a_mailmap_keeps_original_names(self):
        (self.repo / ".mailmap").unlink()
        self.assertEqual([c.author for c in read_commits(self.repo, use_mailmap=True)],
                         ["Home Alias", "Work Alias"])

    def test_markdown_uses_canonical_author_names(self):
        output = self.report("--mailmap")
        self.assertIn("- Canonical Zoë: 2", output)
        self.assertIn("(Canonical Zoë)", output)
