import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from git_worklog.output import write_report

class OutputTests(unittest.TestCase):
    def test_atomic_replacement_preserves_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.md"
            output.write_text("old")
            output.chmod(0o640)
            write_report(output, "Zoë\n")
            self.assertEqual(output.read_text(encoding="utf-8"), "Zoë\n")
            if os.name != "nt":
                self.assertEqual(output.stat().st_mode & 0o777, 0o640)
            self.assertEqual(list(output.parent.iterdir()), [output])
    def test_failed_replace_preserves_old_report_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.md"
            output.write_text("old")
            with patch("git_worklog.output.os.replace", side_effect=OSError("disk error")):
                with self.assertRaises(OSError):
                    write_report(output, "new")
            self.assertEqual(output.read_text(), "old")
            self.assertEqual(list(output.parent.iterdir()), [output])
    def test_invalid_unicode_does_not_truncate_an_existing_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.md"
            output.write_text("old")
            with self.assertRaises(UnicodeError):
                write_report(output, "\ud800")
            self.assertEqual(output.read_text(), "old")
            self.assertEqual(list(output.parent.iterdir()), [output])
    @unittest.skipIf(os.name == "nt", "symlinks may require elevated permissions")
    def test_symlinks_are_rejected_without_touching_the_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.write_text("old")
            link = Path(directory) / "report"
            link.symlink_to(target)
            with self.assertRaisesRegex(OSError, "symbolic link"):
                write_report(link, "new")
            self.assertEqual(target.read_text(), "old")
