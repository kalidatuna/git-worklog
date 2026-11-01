import contextlib
import io
import unittest
from unittest.mock import patch
from git_worklog.cli import main

class InvalidPathsTests(unittest.TestCase):
    def test_invalid_output_path_is_an_argument_error(self):
        output = io.StringIO()
        with patch('git_worklog.cli.read_commits', return_value=[]), contextlib.redirect_stderr(output), self.assertRaises(SystemExit) as error:
            main(['.', '--output', 'bad\0path'])
        self.assertEqual(error.exception.code, 2)
        self.assertNotIn('Traceback', output.getvalue())

    def test_invalid_repository_path_is_an_argument_error(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(['bad\0path'])
        self.assertEqual(error.exception.code, 2)
