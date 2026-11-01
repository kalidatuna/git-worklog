import unittest
from git_worklog.render import render_markdown

class RenderSafetyTests(unittest.TestCase):
    def test_repository_content_stays_literal_and_on_one_line(self):
        summary = {"total": 1, "by_day": {}, "by_author": {"<b>Ada</b>": 1},
                   "commits": [{"date_utc": "2026-11-01", "sha": "a" * 40,
                                "subject": "[click](https://example.test)\n<script>",
                                "author": "<b>Ada</b>"}]}
        result = render_markdown(summary, "repo\n# injected", 7)
        self.assertNotIn("<script>", result)
        self.assertNotIn("\n# injected", result)
        self.assertIn(r"\[click\]\(https://example\.test\)", result)
        self.assertIn("&lt;b&gt;Ada&lt;/b&gt;", result)
