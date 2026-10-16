#!/usr/bin/env python3
"""Render one Atlas dashboard: embed its data and theme into its template, safely.

    python3 -I system/tools/render.py <template.html> <data.json> <theme.css or -> <out.html>

Standard library only. The data is serialized as compact JSON with <, >, &,
U+2028 and U+2029 escaped, so text from emails or documents can never close the
<script> element it sits in; the theme CSS loses every "<", so it can never
close its <style> element. The template must contain exactly one
{{ATLAS_DATA}} and one {{ATLAS_THEME_CSS}}; nothing else changes. Prints the
page size in KB; exit 1 with a message on any problem
(system/dashboards/README.md, "How a page is rendered").
"""
import json
import os
import re
import sys

DATA_PH = "{{ATLAS_DATA}}"
THEME_PH = "{{ATLAS_THEME_CSS}}"
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


def inject(template, data, theme_css=""):
    if template.count(DATA_PH) != 1:
        raise ValueError("template must contain exactly one %s" % DATA_PH)
    if template.count(THEME_PH) != 1:
        raise ValueError("template must contain exactly one %s" % THEME_PH)
    # one pass, so a placeholder string inside the data is never substituted again
    parts = {DATA_PH: safe_json(data), THEME_PH: safe_css(theme_css)}
    return re.sub(re.escape(DATA_PH) + "|" + re.escape(THEME_PH), lambda m: parts[m.group(0)], template)


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
