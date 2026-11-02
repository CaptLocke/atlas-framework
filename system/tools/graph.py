#!/usr/bin/env python3
"""Build the Records page's data: every record Atlas keeps, and how they link.

    python3 -I system/tools/graph.py [--root DIR] [--today YYYY-MM-DD] [--max N]

Standard library plus the vendored YAML parser; reads only the repo. Prints JSON
in the shape `system/dashboards/records.contract.md` defines (without `meta`, which
atlas-dashboards adds). Titles and statuses only, never a record's body or summary,
so the page shows nothing the indexes don't already list.

Which records: the types the page draws (person, organization, project, goal,
commitment, event, decision, risk, idea, topic, and question), read the way
`index.py` reads them. Archived and superseded records are left out, and so are
closed ones (a type's closed statuses, `system/schemas/schema.yaml`) not updated in
the last 90 days, and closed questions. Sources, playbooks and user types are never
drawn. Above --max records (default 3000), the most recently updated are kept and
the rest counted in `truncated`.

Links: every [[type/slug]] in a record's frontmatter (except `sources`) or body,
between two records that are both on the page, once per pair.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import index  # noqa: E402  (same folder: one way to read records)

TYPES = ["person", "organization", "project", "goal", "commitment", "event", "decision", "risk", "idea", "topic", "question"]
RECENT_DAYS = 90
MAX_RECORDS = 3000
LINK = re.compile(r"\[\[([a-z][a-z0-9-]*/[a-z0-9][a-z0-9-]*)\]\]")
FRONTMATTER = re.compile(r"^---\s*\n.*?\n---\s*(\n|$)", re.S)


def attention(name, fm, today):
    """('critical' | 'warning' | None, a status word from the page's vocabulary)."""
    st = str(fm.get("status") or "")
    if name == "commitment":
        due = index.as_date(fm.get("due"))
        if st == "slipped":
            return "critical", "Slipped"
        if st == "open" and due and due < today:
            return "critical", "Overdue"
        if st == "open" and due and due == today:
            return "warning", "Due today"
    if name in ("project", "goal"):
        h = str(fm.get("health") or fm.get("assessment") or "")
        if st == "active" and h == "off_track":
            return "critical", "Off track"
        if st == "active" and h == "at_risk":
            return "warning", "At risk"
    if name == "risk":
        if st == "active":
            return "critical", "Critical"
        lv = {"low": 1, "medium": 2, "high": 3}
        if st == "potential" and lv.get(str(fm.get("likelihood")), 1) * lv.get(str(fm.get("impact")), 1) >= 6:
            return "warning", "On edge"
    if name == "decision" and st == "proposed":
        return "warning", "Needs action"
    return None, None


def body_links(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return set()
    return set(LINK.findall(FRONTMATTER.sub("", text, count=1)))


def front_links(fm):
    found = set()

    def walk(v):
        if isinstance(v, str):
            found.update(LINK.findall(v))
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
    for k, v in fm.items():
        if k not in ("sources", "id"):
            walk(v)
    return found


def build(root, today, max_records=MAX_RECORDS):
    tmap = index.types(root)
    keep = []
    for name in TYPES:
        if name not in tmap:
            continue
        folder, closed = tmap[name]
        d = os.path.join(root, "user", "knowledge", folder)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            path = os.path.join(d, f)
            fm = index.read_frontmatter(path)
            if fm is None or fm.get("archived") is True or fm.get("superseded_by"):
                continue
            rid = str(fm.get("id") or "%s/%s" % (folder, f[:-3]))
            st = str(fm.get("status") or "")
            updated = index.as_date(fm.get("updated")) or index.as_date(fm.get("created"))
            if st in closed and (name == "question" or not updated or (today - updated).days > RECENT_DAYS):
                continue
            level, word = attention(name, fm, today)
            rec = {"id": rid, "type": name, "title": index.clean(fm.get("title")) or rid,
                   "status": st or None, "updated": updated.isoformat() if updated else None}
            if level:
                rec["attention"], rec["status_word"] = level, word
            keep.append((rec, front_links(fm) | body_links(path)))
    total = len(keep)
    if total > max_records:
        keep.sort(key=lambda x: (x[0]["updated"] or "", x[0]["id"]), reverse=True)
        keep = keep[:max_records]
    keep.sort(key=lambda x: (TYPES.index(x[0]["type"]), x[0]["title"].lower(), x[0]["id"]))
    pos = {rec["id"]: i for i, (rec, _) in enumerate(keep)}
    pairs = set()
    for i, (rec, refs) in enumerate(keep):
        for r in refs:
            j = pos.get(r)
            if j is not None and j != i:
                pairs.add((min(i, j), max(i, j)))
    return {"records": [rec for rec, _ in keep], "links": [list(p) for p in sorted(pairs)],
            "truncated": total - len(keep)}


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    ap.add_argument("--today", help="YYYY-MM-DD (default: today in atlas.yaml's time zone)")
    ap.add_argument("--max", type=int, default=MAX_RECORDS, help="most records to keep (default %d)" % MAX_RECORDS)
    a = ap.parse_args(argv)
    today = index.as_date(a.today) if a.today else index.local_today(a.root)
    if today is None:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if a.max < 1:
        print("--max must be at least 1", file=sys.stderr)
        return 2
    json.dump(build(a.root, today, a.max), sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
