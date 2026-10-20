#!/usr/bin/env python3
"""Convert routine schedules from the user's time zone to the UTC crons the platform needs.

routines.yaml keeps every schedule in the user's time zone (atlas.yaml: timezone),
but the platform reads a routine's cron as UTC. This converts at the zone's
current UTC offset, so the result is right until the clocks next change; the
offset it used goes in routines.yaml: utc_offset, which every routine run checks
(system/jobs/README.md §Running a routine, step 1).

A local schedule can need more than one UTC cron: "7 8-18 * * 1-5" in
America/Los_Angeles (-0700) runs 15:07-23:07 UTC on Mon-Fri but 0:07 and 1:07 UTC
on Tue-Sat. Each cron printed is one platform routine.

Usage (from the repository root):
    python3 system/tools/cron_utc.py                      # every routine in user/settings/routines.yaml
    python3 system/tools/cron_utc.py "7 20 * * *"         # one schedule
    python3 system/tools/cron_utc.py --tz Europe/Berlin --at 2026-12-01 "7 20 * * *"
    python3 system/tools/cron_utc.py --root DIR           # another checkout
Prints JSON: {"timezone", "utc_offset", "schedules": [...]} for one schedule, or
{"timezone", "utc_offset", "routines": {name: [...]}} for all, plus "errors": {name: why}
for any routine it can't convert (the others still convert; exit 2).
Exit 0 on success, 2 on a schedule it can't convert or a missing time zone.
The offset is the zone's offset now (or at noon on --at), matching `date +%z` in a run.
Standard library plus the vendored YAML parser.
"""
import argparse
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import yaml  # noqa: E402  (vendored)

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # Python < 3.9
    ZoneInfo = None

DAYS = ("sun", "mon", "tue", "wed", "thu", "fri", "sat")
WEEK = 7 * 1440


class CronError(ValueError):
    pass


def expand(field, lo, hi, names=()):
    """The set of values a cron field matches: *, a, a-b, */n, a-b/n, lists."""
    out = set()
    for part in field.lower().split(","):
        rng, _, step = part.partition("/")
        if rng == "*":
            a, b = lo, hi
        elif "-" in rng:
            a, b = (value(x, names) for x in rng.split("-", 1))
        else:
            a = b = value(rng, names)
            if step:
                b = hi
        n = int(step) if step else 1
        if not (lo <= a <= hi and lo <= b <= hi) or a > b or n < 1:
            raise CronError("%r is out of range %d-%d" % (part, lo, hi))
        out.update(range(a, b + 1, n))
    return out


def value(x, names):
    if x in names:
        return names.index(x)
    if not x.isdigit():
        raise CronError("%r is not a number" % x)
    return int(x)


def compress(values, lo, hi):
    """Shortest field text for a set of values: *, ranges of three or more, lists."""
    vs = sorted(values)
    if vs == list(range(lo, hi + 1)):
        return "*"
    parts, i = [], 0
    while i < len(vs):
        j = i
        while j + 1 < len(vs) and vs[j + 1] == vs[j] + 1:
            j += 1
        if j - i >= 2:
            parts.append("%d-%d" % (vs[i], vs[j]))
        else:
            parts.extend(str(v) for v in vs[i:j + 1])
        i = j + 1
    return ",".join(parts)


def zone_of(tz):
    if ZoneInfo is None:
        raise CronError("this Python has no time zone data (needs 3.9 or later)")
    try:
        return ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError):
        try:
            ZoneInfo("America/New_York")
        except ZoneInfoNotFoundError:
            raise CronError("this machine has no time zone data, so %r can't be looked up" % tz)
        raise CronError("unknown time zone %r" % tz)


def offset_minutes(zone, at=None):
    """The zone's offset now, as `date +%z` would print it during a run, or at noon on `at`."""
    if at is None:
        moment = datetime.datetime.now(zone)
    else:
        moment = datetime.datetime.combine(at, datetime.time(12), tzinfo=zone)
    return int(moment.utcoffset().total_seconds() // 60)


def offset_text(minutes):
    """The offset as `date +%z` prints it, e.g. -0700."""
    sign = "-" if minutes < 0 else "+"
    return "%s%02d%02d" % (sign, abs(minutes) // 60, abs(minutes) % 60)


def to_utc(cron, offset):
    """UTC crons that fire at the same instants as the local cron at this offset."""
    fields = cron.split()
    if len(fields) != 5:
        raise CronError("%r is not a 5-field cron expression" % cron)
    minute, hour, dom, month, dow = fields
    if dom != "*" or month != "*":
        raise CronError("%r: only day-of-week schedules can be converted (day of month and month must be *)" % cron)
    mins = expand(minute, 0, 59)
    hours = expand(hour, 0, 23)
    days = {d % 7 for d in expand(dow, 0, 7, DAYS)}
    # Each UTC (hour, minute) and the days it fires on.
    when = {}
    for d in days:
        for h in hours:
            for m in mins:
                t = (d * 1440 + h * 60 + m - offset) % WEEK
                when.setdefault((t % 1440 // 60, t % 60), set()).add(t // 1440)
    # One cron per set of days, then per set of hours sharing those days.
    by_days = {}
    for (h, m), ds in when.items():
        by_days.setdefault(frozenset(ds), {}).setdefault(m, set()).add(h)
    out = []
    for ds, by_min in by_days.items():
        by_hours = {}
        for m, hs in by_min.items():
            by_hours.setdefault(frozenset(hs), set()).add(m)
        for hs, ms in by_hours.items():
            out.append("%s %s * * %s" % (compress(ms, 0, 59), compress(hs, 0, 23), compress(ds, 0, 6)))
    return sorted(out, key=lambda c: (c.split()[4] != "*", c.split()[4], c))


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cron", nargs="?", help="a local cron; default: every routine in routines.yaml")
    ap.add_argument("--tz", help="IANA zone (default: atlas.yaml timezone)")
    ap.add_argument("--at", help="YYYY-MM-DD whose offset to use (default: today)")
    ap.add_argument("--root", default=".", help="repository root")
    a = ap.parse_args(argv)
    try:
        tz = a.tz or load(os.path.join(a.root, "user", "settings", "atlas.yaml")).get("timezone")
        if not tz:
            raise CronError("no time zone: pass --tz or set atlas.yaml: timezone")
        zone = zone_of(tz)
        off = offset_minutes(zone, datetime.date.fromisoformat(a.at) if a.at else None)
        result = {"timezone": tz, "utc_offset": offset_text(off)}
        if a.cron:
            result["schedules"] = to_utc(a.cron, off)
        else:
            routines = load(os.path.join(a.root, "user", "settings", "routines.yaml")).get("routines") or []
            result["routines"], errors = {}, {}
            for r in routines:
                try:
                    result["routines"][r["name"]] = to_utc(r["schedule"], off)
                except CronError as e:
                    errors[r["name"]] = str(e)
            if errors:
                # The rest still convert: one routine Atlas can't convert mustn't block the others.
                result["errors"] = errors
                print(json.dumps(result, indent=2))
                return 2
    except (CronError, OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as e:
        print("cron_utc: %s" % e, file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
