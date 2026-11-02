import os
import shutil
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

    def test_output_encoding_config_cannot_damage_unicode(self):
        self.git("config", "i18n.logOutputEncoding", "ISO-8859-1")
        commit = read_commits(self.repo)[0]
        self.assertEqual(commit.author, "Zoë")
        self.assertEqual(commit.subject, "Résumé")

    @unittest.skipUnless(shutil.which("ssh-keygen"), "OpenSSH is required for signing fixture")
    def test_signature_display_configuration_does_not_corrupt_records(self):
        key = self.repo / "test-signing-key"
        subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
            check=True, capture_output=True,
        )
        signers = self.repo / "allowed-signers"
        signers.write_text("z@example.test " + key.with_suffix(".pub").read_text(), encoding="utf-8")
        self.git("config", "gpg.format", "ssh")
        self.git("config", "user.signingkey", str(key))
        self.git("config", "gpg.ssh.allowedSignersFile", str(signers))
        self.git("commit", "-q", "-S", "--allow-empty", "-m", "Signed change")
        sha = self.git("rev-parse", "HEAD").stdout.decode().strip()
        self.git("config", "log.showSignature", "true")

        commits = read_commits(self.repo)

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].sha, sha)
        self.assertEqual(commits[0].subject, "Signed change")
        self.assertEqual(commits[0].author, "Zoë")
        self.assertEqual(commits[1].subject, "Résumé")
