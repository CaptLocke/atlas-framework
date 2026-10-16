"""Tests for system/tools/redact_check.py (issue report leftovers)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tools", "redact_check.py"))

REPORT = """Atlas issue: brief missing meetings (v1.0.1)
At 2026-10-16 08:07:00 the daily-brief job failed after the Gmail and Google Calendar connectors timed out.
Commit 3994432. Contact atlas.framework.support@gmail.com or https://github.com/CaptLocke/atlas-framework/issues
[PERSON-1] asked about [ORG-1]; see [LINK].
"""


class RedactCheck(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/maya-chen/atlas.git"], cwd=self.repo,
                       check=True)
        os.makedirs(os.path.join(self.repo, "system", "tools"))
        with open(os.path.join(self.repo, "system", "manifest.yaml"), "w") as f:
            f.write("upstream: CaptLocke/atlas-framework\nsupport_email: atlas.framework.support@gmail.com\n")
        self.tool = os.path.join(self.repo, "system", "tools", "redact_check.py")
        shutil.copy(SRC, self.tool)
        idx = os.path.join(self.repo, "user", "knowledge", "_index")
        os.makedirs(idx)
        os.makedirs(os.path.join(self.repo, "user", "settings"))
        with open(os.path.join(idx, "people.md"), "w") as f:
            f.write("- [[people/dana-ruiz]] | Dana Ruiz | aliases: D. Ruiz | active | 2026-10-12 | x\n"
                    "- [[people/will-may]] | Will May | aliases: none | active | 2026-10-12 | x\n")
        with open(os.path.join(idx, "organizations.md"), "w") as f:
            f.write("- [[organizations/acme]] | Acme Corp | aliases: Acme | customer | 2026-10-12 | x\n"
                    "- [[organizations/google]] | Google | aliases: | vendor | 2026-10-12 | x\n")
        with open(os.path.join(self.repo, "user", "settings", "atlas.yaml"), "w") as f:
            f.write("user_display_name: Maya Chen\ncompany:\n  website: https://www.acme.com\n"
                    "  email_domains: [acme.com, acme.io]\n")

    def run_check(self, text):
        path = os.path.join(self.repo, "report.txt")
        with open(path, "w") as f:
            f.write(text)
        return subprocess.run([sys.executable, "-I", self.tool, path], cwd="/", capture_output=True, text=True)

    def test_clean_report_passes(self):
        r = self.run_check(REPORT)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_common_words_and_ids_not_flagged(self):
        r = self.run_check(REPORT + "It will retry; you may see it on the page. Run 20261016-093000 at 1760611200000.\n")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_joined_names_bare_links_lookalike_upstream(self):
        r = self.run_check("meetings/2026-10-13-acme-kickoff in #acme-deals, file Ruiz_MSA_v3.docx\n"
                           "docs.google.com/document/d/1Ab and https://evil.example/?q=captlocke/atlas-framework\n"
                           "host 10.0.0.12, Will May said hi\n")
        for found in ("organization: acme", "person: Ruiz", "link: docs.google.com/document/d/1Ab",
                      "link: https://evil.example/?q=captlocke/atlas-framework", "IP address: 10.0.0.12",
                      "person: Will May"):
            self.assertIn(found, r.stdout)

    def test_unreadable_report_fails(self):
        r = subprocess.run([sys.executable, "-I", self.tool, os.path.join(self.repo, "missing.txt")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_planted_details_flagged(self):
        r = self.run_check(REPORT + "Dana said acme.io sent it from dana@acme.example; "
                                    "https://docs.google.com/document/d/1Ab/edit; call 415-555-0100; repo maya-chen/atlas\n")
        self.assertEqual(r.returncode, 1)
        for found in ("email: dana@acme.example", "person: Dana", "employer domain: acme.io",
                      "link: https://docs.google.com/document/d/1Ab/edit", "phone number: 415-555-0100",
                      "repo: maya-chen/atlas"):
            self.assertIn(found, r.stdout)


if __name__ == "__main__":
    unittest.main()
