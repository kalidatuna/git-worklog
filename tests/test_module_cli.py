"""Run the public module entry point as a separate process."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

class ModuleCliTests(unittest.TestCase):
    def run_cli(self, *args):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run([sys.executable, "-m", "git_worklog", *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8", env=env)
    def test_subdirectory_and_report_path_with_spaces(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "project with spaces"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            nested = repo / "nested"
            nested.mkdir()
            output = Path(directory) / "weekly report.json"
            result = self.run_cli(nested, "--json", "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["total"], 0)
    def test_missing_output_parent_returns_usage_error_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            result = self.run_cli(directory, "--output", Path(directory) / "missing" / "report.md")
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)
    def test_version_and_invalid_repository_exit_codes(self):
        version = self.run_cli("--version")
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("0.1.0", version.stdout)
        with tempfile.TemporaryDirectory() as directory:
            invalid = self.run_cli(directory)
            self.assertEqual(invalid.returncode, 2)
            self.assertNotIn("Traceback", invalid.stderr)
