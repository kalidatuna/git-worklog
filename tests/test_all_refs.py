import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from git_worklog.git import read_commits

class AllRefsTests(unittest.TestCase):
    def test_all_refs_includes_work_on_another_branch_once(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, GIT_AUTHOR_NAME='Ada', GIT_AUTHOR_EMAIL='a@example.test',
                       GIT_COMMITTER_NAME='Ada', GIT_COMMITTER_EMAIL='a@example.test')
            def git(*args):
                return subprocess.check_output(['git', '-C', directory, *args], env=env, text=True).strip()
            git('init', '-q')
            git('commit', '-q', '--allow-empty', '-m', 'Base')
            base = git('rev-parse', 'HEAD')
            git('checkout', '-qb', 'feature')
            git('commit', '-q', '--allow-empty', '-m', 'Feature')
            git('checkout', '-q', '--detach', base)
            self.assertEqual([c.subject for c in read_commits(Path(directory))], ['Base'])
            commits = read_commits(Path(directory), all_refs=True)
            self.assertEqual({c.subject for c in commits}, {'Base', 'Feature'})
            self.assertEqual(len(commits), 2)
