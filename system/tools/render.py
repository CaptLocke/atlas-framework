#!/usr/bin/env python3
"""Render one Atlas dashboard: embed its data and theme into its template, safely.

    python3 -I system/tools/render.py <template.html> <data.json> <theme.css or -> <out.html>

Standard library only. The data is serialized as compact JSON with <, >, &,
U+2028 and U+2029 escaped, so text from emails or documents can never close the
<script> element it sits in; the theme CSS loses every "<", so it can never
close its <style> element. The template must contain exactly one
{{ATLAS_DATA}} and one {{ATLAS_THEME_CSS}}, and at most one each of
{{ATLAS_BASE_CSS}} and {{ATLAS_BASE_JS}}, which are filled with the shared
system/dashboards/_base.css and _base.js (always Atlas's own copies, whatever
template is rendered); the base CSS also carries the Atlas fonts from
system/dashboards/fonts/, embedded as data: URIs, since a page loads nothing
from outside. Nothing else changes. Prints the page size in KB; exit
1 with a message on any problem (system/dashboards/README.md, "How a page is
rendered").
"""
import base64
import json
import os
import re
import sys

DATA_PH = "{{ATLAS_DATA}}"
THEME_PH = "{{ATLAS_THEME_CSS}}"
BASE_CSS_PH = "{{ATLAS_BASE_CSS}}"
BASE_JS_PH = "{{ATLAS_BASE_JS}}"
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboards")
ESCAPES = (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"), (" ", "\\u2028"), (" ", "\\u2029"))


def safe_json(data):
    """JSON that can sit inside <script type="application/json"> safely."""
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    for ch, esc in ESCAPES:
        text = text.replace(ch, esc)
    return text


def safe_css(css):
    """Theme CSS holds only declarations; without "<" it can never close the style element."""
    return (css or "").replace("<", "")


FONTS = (  # (family, file, weight range): the Atlas design system's two faces, Latin subset (OFL; licences beside them)
    ("Newsreader", "newsreader-latin.woff2", "400 600"),
    ("Inter", "inter-latin.woff2", "400 600"),
)


def fonts_css():
    """@font-face rules with the fonts inlined, so a page loads nothing from outside."""
    out = []
    for family, name, weight in FONTS:
        path = os.path.join(BASE_DIR, "fonts", name)
        if not os.path.exists(path):
            continue  # the fallback stacks in _base.css still apply
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        out.append('@font-face{font-family:"%s";font-style:normal;font-weight:%s;font-display:swap;'
                   'src:url(data:font/woff2;base64,%s) format("woff2")}' % (family, weight, b64))
    return "\n".join(out) + ("\n" if out else "")


def base_file(name):
    with open(os.path.join(BASE_DIR, name), encoding="utf-8") as f:
        text = f.read().rstrip() + "\n"
    return fonts_css() + text if name == "_base.css" else text


def inject(template, data, theme_css=""):
    if template.count(DATA_PH) != 1:
        raise ValueError("template must contain exactly one %s" % DATA_PH)
    if template.count(THEME_PH) != 1:
        raise ValueError("template must contain exactly one %s" % THEME_PH)
    parts = {DATA_PH: safe_json(data), THEME_PH: safe_css(theme_css)}
    for ph, name in ((BASE_CSS_PH, "_base.css"), (BASE_JS_PH, "_base.js")):
        n = template.count(ph)
        if n > 1:
            raise ValueError("template must contain at most one %s" % ph)
        if n:
            parts[ph] = "\n" + base_file(name)
    # one pass, so a placeholder string inside the data or the base files is never substituted again
    return re.sub("|".join(re.escape(k) for k in parts), lambda m: parts[m.group(0)], template)


def main(argv):
    if len(argv) != 5:
        print(__doc__, file=sys.stderr)
        return 2
    template_path, data_path, theme_path, out_path = argv[1:]
    try:
        with open(template_path, encoding="utf-8") as f:
            template = f.read()
        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)
        theme = ""
        if theme_path != "-":
            with open(theme_path, encoding="utf-8") as f:
                theme = f.read()
        page = inject(template, data, theme)
        tmp = out_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(page)
        os.replace(tmp, out_path)
    except (OSError, ValueError, UnicodeError) as e:
        print("render failed: %s" % e, file=sys.stderr)
        return 1
    print("%s: %.1f KB" % (out_path, len(page.encode("utf-8")) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
