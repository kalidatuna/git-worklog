import contextlib, io, json, pathlib, subprocess, tempfile, unittest
from git_worklog.cli import main
from git_worklog.git import read_commits, GitError

class EmptyRepositoryTests(unittest.TestCase):
    def test_initialized_repository_without_commits_has_an_empty_report(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(['git', 'init', '-q', directory], check=True)
            try:
                commits = read_commits(pathlib.Path(directory))
            except GitError as error:
                self.fail('An initialized empty repository should produce a report: ' + str(error))
            self.assertEqual(commits, [])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([directory, '--json']), 0)
            self.assertEqual(json.loads(output.getvalue())['total'], 0)
