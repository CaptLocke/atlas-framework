#!/usr/bin/env python3
"""Decide whether the user's slipped commitments call for a cut list, and propose one (ATL-134).

    python3 -I system/tools/cutlist.py [--root DIR] [--today YYYY-MM-DD] [--out FILE]

Standard library plus the vendored YAML parser; reads only the repo's frontmatter and the
questions inbox, never a body's text. Prints JSON (or writes it to --out: in a routine, a
file under .atlas-tmp/, which the guard allows). `atlas-triage` reads it and writes the
question in the user's words; the tool decides which items and which action, so the same
records always give the same list.

Slipped items: commitments with `direction: i_owe`, `status: slipped`, whose `owner` is the
user (`relationship: self`), not archived or superseded.

Due (`due: true`) when there are at least 5 slipped items, no cut list is open, and either
none was asked in the last 7 days or at least 3 more items are slipped than the newest one
listed. A cut list is a questions-inbox entry (live or archived) with a `- **Cut list:**`
line ("6 items"); its `Asked:` date and count are read from there.

Each item gets one action, in this order of rules:
- `keep`: priority high, or priority medium and owed to the user's manager or to someone
  outside the company (relationship customer, prospect, vendor, partner, external, board).
- `hand_off`: not kept, and a person already on the item (in its `links.people`, not the user
  and not the counterparty) is a report, peer or stakeholder: `to` names them, reports first.
- `drop`: priority low and nothing has touched it for 14 days (its `updated` and the dates of
  sources it cites). `notify` is true when it was owed to the manager or outside the company,
  so the list offers a "letting you know" draft.
- `redate`: everything else.
`keep` and `redate` items get a `date`: the next 5 work days (`rhythms.yaml: work_hours.days`,
default Monday to Friday) from tomorrow, at most 2 items a day, kept items first, then by
days late. Items are listed keep, hand_off, redate, drop, then by days late.
"""
import argparse
import json
import os
import re
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import index  # noqa: E402

MIN_SLIPPED, MORE_SINCE, WEEK, QUIET_DAYS, DAYS_AHEAD, PER_DAY = 5, 3, 7, 14, 5, 2
OUTSIDE = {"customer", "prospect", "vendor", "partner", "external", "board"}
COLLEAGUE_ORDER = ["report", "peer", "stakeholder"]
DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
ORDER = {"keep": 0, "hand_off": 1, "redate": 2, "drop": 3}
CUT_RE = re.compile(r"^- \*\*Cut list:\*\* (\d+)", re.M)
ASKED_RE = re.compile(r"^- \*\*Asked:\*\* (\d{4}-\d{2}-\d{2})", re.M)
ENTRY_RE = re.compile(r"(?m)^(?=## Q-)")
HEAD_RE = re.compile(r"^## (Q-\S+) · ([a-z_]+)")


def _id(value):
    return index.ref_id(value) if value else None


def _folder(root, name):
    t = index.types(root).get(name)
    return os.path.join(root, "user", "knowledge", t[0] if t else name + "s")


def _records(root, name):
    d = _folder(root, name)
    out = {}
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if f.endswith(".md"):
            fm = index.read_frontmatter(os.path.join(d, f))
            if fm and fm.get("archived") is not True and not fm.get("superseded_by"):
                out[str(fm.get("id") or "%s/%s" % (os.path.basename(d), f[:-3]))] = fm
    return out


def _source_dates(root):
    out = {}
    for sid, fm in _records(root, "source").items():
        day = index.as_date(fm.get("occurred_on")) or index.as_date(fm.get("captured_on"))
        if day:
            out[sid] = day
    return out


def _work_days(root):
    rh = index.load_yaml(os.path.join(root, "user", "settings", "rhythms.yaml")) or {}
    days = ((rh.get("work_hours") or {}).get("days")) or DAY_NAMES[:5]
    return {DAY_NAMES.index(str(d).lower()[:3]) for d in days if str(d).lower()[:3] in DAY_NAMES} or set(range(5))


def _cut_lists(root):
    """[(asked date, count, status)] for every cut-list question, live and archived."""
    out = []
    inbox = os.path.join(root, "user", "inbox")
    paths = [os.path.join(inbox, "questions.md")]
    arch = os.path.join(inbox, "archive")
    if os.path.isdir(arch):
        paths += [os.path.join(arch, f) for f in sorted(os.listdir(arch)) if f.endswith("-questions.md")]
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            text = f.read()
        for block in ENTRY_RE.split(text):
            head, cut, asked = HEAD_RE.match(block), CUT_RE.search(block), ASKED_RE.search(block)
            if head and cut:
                out.append((index.as_date(asked.group(1)) if asked else None, int(cut.group(1)), head.group(2)))
    return out


def build(root, today):
    people = _records(root, "person")
    me = next((p for p, fm in people.items() if str(fm.get("relationship") or "") == "self"), None)
    rel = {p: str(fm.get("relationship") or "") for p, fm in people.items()}
    sdates = _source_dates(root)
    slipped = []
    for cid, fm in _records(root, "commitment").items():
        if fm.get("direction") != "i_owe" or fm.get("status") != "slipped":
            continue
        if me and _id(fm.get("owner")) != me:
            continue
        slipped.append((cid, fm))

    lists = _cut_lists(root)
    open_now = any(st == "open" for _, _, st in lists)
    dated = sorted((d, n) for d, n, _ in lists if d)
    last = dated[-1] if dated else None
    n = len(slipped)
    if n < MIN_SLIPPED:
        due, why = False, "fewer than %d slipped" % MIN_SLIPPED
    elif open_now:
        due, why = False, "a cut list is open"
    elif last and (today - last[0]).days < WEEK and n < last[1] + MORE_SINCE:
        due, why = False, "one was asked on %s and fewer than %d more have slipped" % (last[0], MORE_SINCE)
    else:
        due, why = True, "%d slipped" % n

    items = []
    for cid, fm in slipped:
        prio = str(fm.get("priority") or "medium")
        cp = _id(fm.get("counterparty"))
        cp_rel = rel.get(cp, "")
        important = cp_rel == "manager" or cp_rel in OUTSIDE
        due_day = index.as_date(fm.get("due"))
        late = (today - due_day).days if due_day else 0
        touched = [index.as_date(fm.get("updated")) or index.as_date(fm.get("created"))]
        touched += [sdates[s] for s in (_id(x) for x in (fm.get("sources") or [])) if s in sdates]
        quiet = min((today - d).days for d in touched if d) if any(touched) else None
        links = fm.get("links") or {}
        on_it = [p for p in (_id(x) for x in (links.get("people") or [])) if p and p not in (me, cp)]
        helpers = sorted((COLLEAGUE_ORDER.index(rel[p]), p) for p in on_it if rel.get(p) in COLLEAGUE_ORDER)
        item = {"id": cid, "title": index.clean(fm.get("title")) or cid, "priority": prio, "days_late": late,
                "counterparty": cp, "quiet_days": quiet}
        if prio == "high" or (prio == "medium" and important):
            item.update(action="keep", reason="high priority" if prio == "high" else "owed to %s" % (cp_rel or "them"))
        elif helpers:
            item.update(action="hand_off", to=helpers[0][1], reason="%s is already on it" % helpers[0][1])
        elif prio == "low" and quiet is not None and quiet >= QUIET_DAYS:
            item.update(action="drop", notify=important, reason="low priority, nothing on it for %d days" % quiet)
        else:
            item.update(action="redate", reason="still wanted; needs a date that holds")
        items.append(item)
    items.sort(key=lambda x: (ORDER[x["action"]], -x["days_late"], x["id"]))

    work = _work_days(root)
    slots, day = [], today
    while len(slots) < DAYS_AHEAD:
        day += timedelta(days=1)
        if day.weekday() in work:
            slots.append(day)
    k = 0
    for it in items:
        if it["action"] in ("keep", "redate"):
            it["date"] = slots[min(k // PER_DAY, len(slots) - 1)].isoformat()
            k += 1
    return {"slipped": n, "due": due, "why": why, "items": items if due else []}


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    ap.add_argument("--today", help="YYYY-MM-DD (default: today in atlas.yaml's time zone)")
    ap.add_argument("--out", help="write the JSON here instead of printing it")
    a = ap.parse_args(argv)
    today = index.as_date(a.today) if a.today else index.local_today(a.root)
    if today is None:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    text = json.dumps(build(a.root, today), ensure_ascii=False, separators=(",", ":")) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
