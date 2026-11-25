#!/usr/bin/env python3
"""List the figures and dates in a draft and say which the records it cites don't contain (ATL-136).

    python3 -I system/tools/figures.py DRAFT [--root DIR] [--record ID ...]

Standard library plus the vendored YAML parser. Prints JSON:
{"checked": n, "matched": n, "unmatched": [{"figure", "kind", "context"}]}.

Which records: every [[folder/slug]] link in the draft, every --record given, and one hop
further, the sources those records list in `sources`. Their frontmatter and body text are
searched. Nothing outside `user/knowledge/` is read.

What counts as a figure: money ($1,200, €3.5M), percentages (34%, 12.5 percent), numbers
with a decimal point or of 10 and over (2,400; 3.75), and dates (2026-11-24, Nov 24,
24 November, 11/24). Years on their own, and numbers inside a [[link]], are skipped.
A slash date is month/day when it can be, else day/month (24/11); a fraction such as 3/4 reads
as a date. A bare number in the records also matches the same number as a percentage or amount.
Link IDs with ".." are refused, so nothing outside `user/knowledge/` is read. Matching is on a
normal form: digits without separators, money with its unit and multiplier
(3.5M = 3500000), dates as month and day. A figure is matched when the same normal form
appears anywhere in the cited text. The tool doesn't judge whether a figure is right in
context; `atlas-write` looks at the unmatched ones and decides.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import index  # noqa: E402

MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
MON = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
PATTERNS = [
    ("date", re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")),
    ("date", re.compile(r"\b(%s)\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b" % MON, re.I)),
    ("date", re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(%s)\b" % MON, re.I)),
    ("date", re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/\d{2,4})?\b")),
    ("money", re.compile(r"([$€£])\s?(%s)\s?([kmb]n?|thousand|million|billion)?\b" % NUM, re.I)),
    ("percent", re.compile(r"\b(%s)\s?(%%|percent\b)" % NUM, re.I)),
    ("number", re.compile(r"(?<![\w.$€£/-])(%s)(?![\w%%/]|\.\d)" % NUM)),
]
MULT = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mn": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9}
LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def _num(s):
    v = float(s.replace(",", ""))
    return ("%d" % v) if v == int(v) else ("%g" % v)


def figures(text):
    """[(kind, normal form, raw, start)] for every figure in text, links blanked out first."""
    text = LINK_RE.sub(lambda m: " " * len(m.group(0)), text)
    out, taken = [], []
    for kind, rx in PATTERNS:
        for m in rx.finditer(text):
            if any(a <= m.start() < b or a < m.end() <= b for a, b in taken):
                continue
            g = m.groups()
            if kind == "date":
                if g[0].isdigit() and len(g[0]) == 4:
                    norm = "%02d-%02d" % (int(g[1]), int(g[2]))
                elif g[0].isdigit() and g[1].isdigit():
                    a, b = int(g[0]), int(g[1])
                    if 1 <= a <= 12 and 1 <= b <= 31:
                        norm = "%02d-%02d" % (a, b)          # month/day
                    elif 13 <= a <= 31 and 1 <= b <= 12:
                        norm = "%02d-%02d" % (b, a)          # day/month, unambiguous (24/11)
                    else:
                        continue
                elif g[0].isdigit():
                    norm = "%02d-%02d" % (MONTHS[g[1][:3].lower()], int(g[0]))
                else:
                    norm = "%02d-%02d" % (MONTHS[g[0][:3].lower()], int(g[1]))
            elif kind == "money":
                v = float(g[1].replace(",", "")) * MULT.get((g[2] or "").lower(), 1)
                norm = "%s%s" % (g[0], ("%d" % v) if v == int(v) else ("%g" % v))
            elif kind == "percent":
                norm = _num(g[0]) + "%"
            else:
                raw = g[0]
                v = float(raw.replace(",", ""))
                if v < 10 and "." not in raw or (re.fullmatch(r"(19|20)\d\d", raw)):
                    continue
                norm = _num(raw)
            taken.append((m.start(), m.end()))
            out.append((kind, norm, m.group(0), m.start()))
    return sorted(out, key=lambda x: x[3])


def _plain_numbers(text):
    """Every number in the text in normal form, so a cited '3,500,000' matches '$3.5M' and '34' matches '34%'."""
    return {_num(x) for x in re.findall(NUM, LINK_RE.sub(" ", text))}


def cited_text(root, draft, extra):
    ids = [i.strip() for i in LINK_RE.findall(draft)] + list(extra)
    seen, texts, queue = set(), [], list(ids)
    hop = {i: 0 for i in ids}
    while queue:
        rid = queue.pop(0)
        if rid in seen or "/" not in rid or ".." in rid or rid.startswith("/") or "\\" in rid:
            continue
        seen.add(rid)
        path = os.path.join(root, "user", "knowledge", *rid.split("/")) + ".md"
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            texts.append(f.read())
        if hop[rid] == 0:
            fm = index.read_frontmatter(path) or {}
            for s in fm.get("sources") or []:
                sid = index.ref_id(s)
                if sid and sid not in hop:
                    hop[sid] = 1
                    queue.append(sid)
    return "\n".join(texts), len(seen)


def check(root, draft, extra=()):
    cited, n = cited_text(root, draft, extra)
    have = {f[1] for f in figures(cited)} | _plain_numbers(cited)
    out = {"records": n, "checked": 0, "matched": 0, "unmatched": []}
    for kind, norm, raw, at in figures(draft):
        out["checked"] += 1
        bare = norm.lstrip("$€£").rstrip("%")
        if norm in have or (kind in ("money", "percent", "number") and bare in have):
            out["matched"] += 1
        else:
            out["unmatched"].append({"figure": raw.strip(), "kind": kind,
                                     "context": draft[max(0, at - 40):at + len(raw) + 40].replace("\n", " ").strip()})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__.split("\n")[0])
    ap.add_argument("draft")
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    ap.add_argument("--record", action="append", default=[], help="a record ID the draft draws on (repeatable)")
    a = ap.parse_args(argv)
    with open(a.draft, encoding="utf-8") as f:
        draft = f.read()
    sys.stdout.write(json.dumps(check(a.root, draft, a.record), ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
