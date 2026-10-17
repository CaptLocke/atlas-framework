"""Tests for system/tools/index.py (indexes rebuilt from the records, formats.md section 5)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TODAY = "2026-10-17"


def record(folder, slug, rtype, title, status, updated, **extra):
    fm = {"id": "%s/%s" % (folder, slug), "type": rtype, "title": title, "summary": "%s." % title,
          "status": status, "created": "2026-09-01", "updated": updated}
    fm.update(extra)
    return "---\n%s\n---\nBody.\n" % "\n".join("%s: %s" % kv for kv in fm.items())


class IndexTool(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        for rel in ("system/tools/index.py", "system/schemas/schema.yaml"):
            os.makedirs(os.path.dirname(os.path.join(self.root, rel)), exist_ok=True)
            shutil.copy(os.path.join(REPO, rel), os.path.join(self.root, rel))
        shutil.copytree(os.path.join(REPO, "system", "tools", "vendor"), os.path.join(self.root, "system", "tools",
                                                                                         "vendor"))
        self.add("people", "dana-ruiz", "person", "Dana Ruiz", "active", "2026-10-12",
                 org='"[[organizations/acme]]"', role="legal counsel", relationship="customer",
                 aliases="[dana@acme.example]")
        self.add("organizations", "acme", "organization", "Acme", "active", "2026-10-12")
        self.add("commitments", "soon", "commitment", "Due soon", "open", "2026-09-01", due="2026-10-20")
        self.add("commitments", "later", "commitment", "Due later", "open", "2026-10-15", due="2026-12-20")
        self.add("commitments", "late", "commitment", "Slipped one", "slipped", "2026-09-01", due="2026-09-20")
        self.add("commitments", "done", "commitment", "Done one", "done", "2026-10-16", due="2026-10-18")
        self.add("events", "2026-10-19-review", "event", "Review", "scheduled", "2026-10-01",
                 start="2026-10-19T10:00:00-06:00")
        self.add("goals", "grow", "goal", "Grow", "active", "2026-08-01", rank=1)
        self.add("projects", "msa", "project", "MSA | fast", "active", "2026-10-15")
        self.add("projects", "old", "project", "Old", "active", "2026-10-15", archived="true")
        self.add("sources", "2026-10-12-email", "source", "Email", "captured", "2026-10-16")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def add(self, folder, slug, *args, **extra):
        d = os.path.join(self.root, "user", "knowledge", folder)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, slug + ".md"), "w", encoding="utf-8") as f:
            f.write(record(folder, slug, *args, **extra))

    def run_tool(self, *args):
        return subprocess.run([sys.executable, "-I", os.path.join(self.root, "system", "tools", "index.py"),
                               "--root", self.root, "--today", TODAY] + list(args), capture_output=True, text=True)

    def index(self, name):
        with open(os.path.join(self.root, "user", "knowledge", "_index", name + ".md"), encoding="utf-8") as f:
            return [l for l in f.read().splitlines() if l.startswith("- ")]

    def test_hot_holds_only_live_records_in_order(self):
        self.assertEqual(self.run_tool().returncode, 0)
        ids = [l.split("]]")[0][4:] for l in self.index("hot")]
        self.assertEqual(ids, ["commitments/late", "commitments/soon", "events/2026-10-19-review", "goals/grow",
                               "projects/msa"])

    def test_type_people_and_archive_indexes(self):
        self.run_tool()
        self.assertEqual(len(self.index("commitments")), 4)
        self.assertIn("- [[projects/msa]] | MSA / fast | aliases: - | active | 2026-10-15 | MSA / fast.",
                      self.index("projects"))
        self.assertEqual(self.index("people-map"),
                         ["- [[people/dana-ruiz]] | Dana Ruiz | Acme (customer) | legal counsel | dana@acme.example"])
        self.assertEqual([l.split("]]")[0][4:] for l in self.index("archive")], ["projects/old"])

    def test_rewrites_only_what_changed_and_check_mode(self):
        self.run_tool()
        self.assertIn("0 index file(s) rebuilt", self.run_tool().stdout)
        self.assertEqual(self.run_tool("--check").returncode, 0)
        self.add("commitments", "new", "commitment", "New one", "open", "2026-10-17", due="2026-10-18")
        r = self.run_tool("--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("commitments.md", r.stdout)
        self.assertNotIn("people.md", r.stdout)

    def test_cap_of_75_lines(self):
        for i in range(90):
            self.add("ideas", "idea-%02d" % i, "idea", "Idea %d" % i, "seed", "2026-10-%02d" % (4 + i % 13))
        self.run_tool()
        lines = self.index("hot")
        self.assertEqual(len(lines), 75)
        self.assertTrue(lines[-1].startswith("- … ") and lines[-1].endswith("more: see the type indexes"))


if __name__ == "__main__":
    unittest.main()
