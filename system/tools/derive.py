#!/usr/bin/env python3
"""Recompute the person fields that follow from other records.

- last_contact: the newest date the person was seen, from sources that list them in
  `participants` and `held` events that list them in `attendees`. A source's date is
  `occurred_on`, which a thread moves to its newest message as messages are filed
  (`system/schemas/source.md`), else `captured_on`. Filing dates (`captured_on` beside an
  `occurred_on`, `## Updates` lines) are when Atlas read it, not contact. An event's is the
  date of `start`; events the
  user declined or never answered, all-day events and meetings of more than 8 people don't
  count. It only moves forward, and never past today. Sources flagged `suspicious` and
  imported history (`kind: import`) don't count.
- cadence: filled only when empty, from a recurring 1:1 (`kind: one_on_one`, one `series`)
  with at least 3 occurrences, the latest within the last 45 days or still to come:
  `weekly 1:1`, `every 2 weeks 1:1` or `monthly 1:1`, by the typical gap between them.
  A cadence already set is the user's or a source's and is never changed. Declined
  occurrences don't count.

Both are derived, so neither adds an Updates line or changes `updated`. Archived records
are skipped, and so is the user's own record (`relationship: self`). Only these two keys
are rewritten; every other line is left as it is.

Usage (from the repository root). Routines run it through normalize.py, the tool
they're allowed: `python3 system/tools/normalize.py --derive [--fix]`.
    python3 system/tools/derive.py                 # report what would change
    python3 system/tools/derive.py --fix           # apply it
    python3 system/tools/derive.py --today 2026-11-20 ...   # for tests
Today defaults to the user's date in `user/settings/atlas.yaml: timezone`, as the
validator computes it.
Exit code 0 always, unless a file can't be written (2). Standard library plus the vendored YAML parser.
"""
import argparse
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "vendor"))
import yaml  # noqa: E402  (vendored)
from normalize import (YAML_ERRORS, dump_block, record_paths,  # noqa: E402
                       split_frontmatter, top_blocks)

LINK_RE = re.compile(r"\[\[\s*([a-z]+/[a-z0-9][a-z0-9-]*)\s*\]\]")
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
MIN_OCCURRENCES = 3
ALIVE_DAYS = 45
MAX_ATTENDEES = 8
NOT_ATTENDED = ("declined", "not_responded")


def ids(value):
    """IDs named in a ref or list of refs, bare or wiki form."""
    items = value if isinstance(value, list) else [value]
    out = []
    for v in items:
        if not isinstance(v, str):
            continue
        m = LINK_RE.search(v)
        out.append(m.group(1) if m else v.strip())
    return out


def to_date(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    if isinstance(v, str):
        m = DATE_RE.match(v.strip())
        if m:
            try:
                return datetime.date.fromisoformat(m.group(1))
            except ValueError:
                return None
    return None


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None, None
    parts = split_frontmatter(text)
    if not parts:
        return text, None
    try:
        fm = yaml.safe_load(parts[0]) or {}
    except YAML_ERRORS:
        return text, None
    return text, fm if isinstance(fm, dict) else None


def source_date(fm, today):
    """When the source's newest item happened, not after today."""
    d = to_date(fm.get("occurred_on")) or to_date(fm.get("captured_on"))
    return d if d and d <= today else None


def local_today(root):
    try:
        with open(os.path.join(root, "user", "settings", "atlas.yaml"), encoding="utf-8") as f:
            tz = (yaml.safe_load(f) or {}).get("timezone")
        if tz:
            from zoneinfo import ZoneInfo
            return datetime.datetime.now(ZoneInfo(str(tz))).date()
    except Exception:
        pass
    return datetime.date.today()


def cadence_for(dates, today):
    """A cadence label from a 1:1 series' occurrence dates, or None."""
    days = sorted(set(dates))
    if len(days) < MIN_OCCURRENCES or (today - days[-1]).days > ALIVE_DAYS:
        return None
    gaps = sorted((b - a).days for a, b in zip(days, days[1:]))
    gap = gaps[len(gaps) // 2]
    if 5 <= gap <= 9:
        return "weekly 1:1"
    if 12 <= gap <= 16:
        return "every 2 weeks 1:1"
    if 26 <= gap <= 35:
        return "monthly 1:1"
    return None


def derive(root, today):
    """{path: (text, fm, {key: new value})} for people whose fields would change."""
    people, seen, series = {}, {}, {}
    for path in record_paths(root):
        text, fm = load(path)
        if not fm:
            continue
        rtype, rid = fm.get("type"), fm.get("id")
        if rtype == "person":
            people[rid] = (path, text, fm)
        elif rtype == "source" and "suspicious" not in (fm.get("flags") or []) and fm.get("kind") != "import":
            d = source_date(fm, today)
            if d:
                for pid in ids(fm.get("participants") or []):
                    seen[pid] = max(seen.get(pid, d), d)
        elif rtype == "event" and fm.get("status") != "cancelled":
            d = to_date(fm.get("start"))
            if not d:
                continue
            attendees = ids(fm.get("attendees") or [])
            if fm.get("response") in NOT_ATTENDED or fm.get("all_day") is True:
                continue
            if fm.get("status") == "held" and d <= today and len(attendees) <= MAX_ATTENDEES:
                for pid in attendees:
                    seen[pid] = max(seen.get(pid, d), d)
            if fm.get("kind") == "one_on_one" and fm.get("series"):
                for pid in attendees:
                    series.setdefault((pid, str(fm["series"])), []).append(d)
    changes = {}
    for pid, (path, text, fm) in people.items():
        if fm.get("archived") is True or fm.get("relationship") == "self":
            continue
        new = {}
        current = to_date(fm.get("last_contact"))
        if pid in seen and (current is None or seen[pid] > current):
            new["last_contact"] = seen[pid]
        if not fm.get("cadence"):
            found = [cadence_for(ds, today) for (p, _), ds in series.items() if p == pid]
            found = [c for c in found if c]
            if found:
                order = ["weekly 1:1", "every 2 weeks 1:1", "monthly 1:1"]
                new["cadence"] = min(found, key=order.index)
        if new:
            changes[path] = (text, fm, new)
    return changes


def rewrite(text, fm, new):
    """The record with only `new`'s keys set, or None if it wouldn't read back exactly."""
    fm_text, rest = split_frontmatter(text)
    out, done = [], set()
    for key, lines in top_blocks(fm_text.rstrip("\n")):
        if key in new:
            out += dump_block(key, new[key])
            done.add(key)
        else:
            out += lines
    for key in new:
        if key not in done:
            out += dump_block(key, new[key])
    new_fm = "\n".join(out) + "\n"
    try:
        check = yaml.safe_load(new_fm) or {}
    except YAML_ERRORS:
        return None
    if check != {**fm, **new}:
        return None
    return "---\n" + new_fm + "---" + rest


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    ap.add_argument("--fix", action="store_true", help="write the changes (default: report only)")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today)")
    a = ap.parse_args(argv)
    try:
        today = datetime.date.fromisoformat(a.today) if a.today else local_today(a.root)
    except ValueError:
        print("ERROR --today must be YYYY-MM-DD (got %r)" % a.today)
        return 2
    rc = 0
    for path, (text, fm, new) in sorted(derive(a.root, today).items()):
        rel = os.path.relpath(path, a.root).replace(os.sep, "/")
        for key, v in new.items():
            print("%s %s: %s %s → %s" % ("SET" if a.fix else "WOULD SET", rel, key,
                                         fm.get(key) or "(empty)", v))
        if not a.fix:
            continue
        out = rewrite(text, fm, new)
        if out is None:
            print("SKIPPED %s: would not read back cleanly" % rel)
            continue
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(out)
        except OSError as e:
            print("ERROR %s: %s" % (rel, e))
            rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
