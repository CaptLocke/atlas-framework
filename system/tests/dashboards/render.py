#!/usr/bin/env python3
"""Render Atlas dashboard templates with fixture data and check them.

Standard library only (Playwright is used for screenshots only if installed).

    python3 system/tests/dashboards/render.py              # render + check all
    python3 system/tests/dashboards/render.py goals        # one dashboard
    python3 system/tests/dashboards/render.py --theme theme-sample.css
    python3 system/tests/dashboards/render.py --shots      # also screenshot (Playwright)
    python3 system/tests/dashboards/render.py --check      # verify templates only (no output)

Output goes to system/tests/dashboards/out/ (git-ignored).

The injection here mirrors what the atlas-dashboards skill does at publish time
(system/dashboards/README.md, "How a page is rendered"): serialize the JSON,
escape <, >, &, U+2028 and U+2029, and replace the single {{ATLAS_DATA}} and
{{ATLAS_THEME_CSS}} placeholders.
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
DASH = HERE.parent.parent / "dashboards"
OUT = HERE / "out"

NAMES = ["daily-brief", "commitments", "projects", "goals", "week-ahead", "people",
         "decisions-risks", "control-center", "about-you", "atlas-guide", "records", "project-page"]
DATA_PH = "{{ATLAS_DATA}}"
THEME_PH = "{{ATLAS_THEME_CSS}}"
REQUIRED_META = ["dashboard", "schema_version", "generated_at", "as_of", "timezone", "headline"]
BASE = {  # the shared files render.py puts into every page: (element, placeholder, source file)
    "css": ('<style id="atlas-base">', "{{ATLAS_BASE_CSS}}", DASH / "_base.css"),
    "js": ('<script id="atlas-base-js">', "{{ATLAS_BASE_JS}}", DASH / "_base.js"),
}


sys.path.insert(0, str(HERE.parent.parent / "tools"))
from render import safe_json, safe_css, inject  # noqa: E402  (the shipped renderer)


def contract_budget(name):
    contract = DASH / ("%s.contract.md" % name)
    if not contract.exists():
        return None
    m = re.search(r"^size_budget_kb:\s*(\d+)", contract.read_text(encoding="utf-8"), re.M)
    return int(m.group(1)) if m else None


class Checker(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.ids, self.data_json = [], [], set(), None
        self._in_data = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            if a["id"] in self.ids:
                self.errors.append("duplicate id %s" % a["id"])
            self.ids.add(a["id"])
        if tag == "script" and a.get("src"):
            self.errors.append("external script %s (templates must be self-contained)" % a["src"])
        if tag == "link" and a.get("rel") == "stylesheet":
            self.errors.append("external stylesheet %s" % a.get("href"))
        if tag not in self.VOID:
            self.stack.append(tag)
        self._in_data = tag == "script" and a.get("id") == "atlas-data"

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append("unexpected </%s> (open: %s)" % (tag, "/".join(self.stack[-3:])))
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
            return
        self.stack.pop()
        self._in_data = False

    def handle_data(self, data):
        if self._in_data:
            self.data_json = (self.data_json or "") + data


def check_template(name, text):
    problems = []
    for element, ph, src in BASE.values():
        if text.count(element + ph) != 1:
            problems.append("expected %s%s (the shared %s, filled by render.py)" % (element, ph, src.name))
    # the base files are part of every page: check them with the template
    text = text + "".join(src.read_text(encoding="utf-8") for _, _, src in BASE.values())
    for ph in (DATA_PH, THEME_PH):
        if text.count(ph) != 1:
            problems.append("expected exactly one %s" % ph)
    if '<script id="atlas-data" type="application/json">' + DATA_PH + "</script>" not in text:
        problems.append("data placeholder is not in the standard <script id=\"atlas-data\"> element")
    if '<style id="atlas-theme">' + THEME_PH + "</style>" not in text:
        problems.append("theme placeholder is not in <style id=\"atlas-theme\">")
    if re.search(r"https?://(?!www\.w3\.org/2000/svg)", text):
        problems.append("template references an external URL")
    if "Content-Security-Policy" not in text or "connect-src 'none'" not in text:
        problems.append("template is missing the content security policy meta tag")
    if "innerHTML" in text:
        problems.append("template uses innerHTML (render untrusted text with textContent)")
    return problems


def check_page(name, page, data):
    problems = []
    if "{{ATLAS_" in page:
        problems.append("placeholder left in rendered page")
    c = Checker()
    c.feed(page)
    c.close()
    problems += c.errors
    if c.stack:
        problems.append("unclosed tags: %s" % "/".join(c.stack))
    try:
        parsed = json.loads(c.data_json or "")
        if parsed != data:
            problems.append("embedded data does not round-trip")
    except ValueError as e:
        problems.append("embedded data is not valid JSON: %s" % e)
    meta = data.get("meta", {})
    for k in REQUIRED_META:
        if k not in meta:
            problems.append("meta.%s missing" % k)
    if meta.get("dashboard") != name:
        problems.append("meta.dashboard is %r, expected %r" % (meta.get("dashboard"), name))
    budget = contract_budget(name)
    page_kb = len(page.encode("utf-8")) / 1024
    if budget is None:
        problems.append("contract has no size_budget_kb")
    elif page_kb > budget:
        problems.append("rendered page %.1f KB exceeds budget %d KB" % (page_kb, budget))
    return problems, page_kb


def screenshots(names):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed; skipping screenshots.")
        return []
    shots = OUT / "shots"
    shots.mkdir(parents=True, exist_ok=True)
    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name in names:
            for label, width, height in (("desktop", 1280, 900), ("phone", 390, 844)):
                for scheme in ("light", "dark"):
                    ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme)
                    page = ctx.new_page()
                    errors = []
                    page.on("console", lambda m, e=errors: e.append(m.text) if m.type == "error" else None)
                    page.on("pageerror", lambda ex, e=errors: e.append(str(ex)))
                    page.goto((OUT / ("%s.html" % name)).as_uri())
                    page.wait_for_timeout(150)
                    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                    if overflow > 0:
                        problems.append("%s %s %s: horizontal overflow %dpx" % (name, label, scheme, overflow))
                    for e in errors:
                        problems.append("%s %s %s: console error: %s" % (name, label, scheme, e))
                    page.screenshot(path=str(shots / ("%s-%s-%s.png" % (name, label, scheme))), full_page=True)
                    ctx.close()
        browser.close()
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="dashboards to render (default: all)")
    ap.add_argument("--theme", help="CSS file to inject as the theme (path relative to this folder or absolute)")
    ap.add_argument("--check", action="store_true", help="check templates only; do not render")
    ap.add_argument("--shots", action="store_true", help="take screenshots with Playwright (desktop/phone, light/dark)")
    args = ap.parse_args()
    names = args.names or NAMES

    theme = ""
    if args.theme:
        tp = Path(args.theme)
        theme = (tp if tp.is_absolute() else HERE / tp).read_text(encoding="utf-8")

    failures = 0
    OUT.mkdir(exist_ok=True)
    for n in names:
        tpl_path = DASH / ("%s.html" % n)
        template = tpl_path.read_text(encoding="utf-8")
        problems = check_template(n, template)
        size = None
        if not args.check:
            data = json.loads((HERE / ("%s.json" % n)).read_text(encoding="utf-8"))
            page = inject(template, data, theme)
            (OUT / ("%s.html" % n)).write_text(page, encoding="utf-8")
            more, size = check_page(n, page, data)
            problems += more
        status = "FAIL" if problems else "ok"
        failures += bool(problems)
        extra = "" if size is None else "  page %.1f KB / budget %s KB (template %.1f KB)" % (
            size, contract_budget(n), len(template.encode("utf-8")) / 1024)
        print("%-16s %s%s" % (n, status, extra))
        for pr in problems:
            print("    - " + pr)

    if args.shots and not args.check:
        shot_problems = screenshots(names)
        for pr in shot_problems:
            print("    - " + pr)
        failures += bool(shot_problems)
        print("Screenshots in %s" % (OUT / "shots"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
