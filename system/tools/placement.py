#!/usr/bin/env python3
"""Place the day's priorities into its open windows, by rule (atlas-brief §Placement).

    python3 -I system/tools/placement.py <input.json>

Standard library only. Prints the placement as JSON; exits 1 with a message on bad
input. The same calendar and records always give the same placement, so the brief
file and the Today page agree and a rerun changes nothing.

Input:
  {"date": "2026-10-13", "timezone": "America/Los_Angeles",
   "work_hours": {"days": ["mon", ...], "start": "08:00", "end": "18:00"},
   "shortest_window": 30,                         # rhythms.yaml focus.shortest_window; missing = 30
   "events": [{"id", "start", "end", "all_day"}], # the day's meetings and holds, as shown on Today
   "priorities": [{"id", "rank", "title", "effort", "due",       # a commitment line, or
                   "commitments": [{"id", "title", "effort", "due", "status"}]}],   # a project line
   "due_today": [{"id", "title", "effort"}],      # other i_owe commitments due that day
   "now": "10:05"}                                # optional: windows before it are gone

A window is a gap inside work hours between meetings and holds, at least
shortest_window minutes long. Items go in order: priorities by rank, then anything
due today not already placed. A project line takes its most urgent open
commitment. Each item takes its size from `effort` (quick and unsized 30 minutes,
hour 60, half_day 240, day 480) and goes into the earliest window with room left;
one that fits nowhere is "Won't fit", with a date to send at the start of the
day's last window.

Output:
  {"day": {"start": "08:00", "end": "18:00", "work_day": true},
   "windows": [{"start": "11:30", "end": "12:30", "minutes": 60, "items": ["commitments/x", ...], "left": 25}],
   "slots": {"<item id>": {"kind": "window", "start": "11:30", "at": "11:30", "minutes": 30, "sized": true}
                        | {"kind": "wont_fit", "date_at": "16:15", "minutes": 240, "sized": true}
                        | {"kind": "none"}},          # a project with no open commitment, or not a work day
   "open_minutes": 210, "due_today": 3, "due_today_placed": 3}
Slots are keyed by the id the input gave: a priority's own id (the project's, for a project line,
and the commitment it took, too). "start" is the window's start; "at" is where the item begins in it.
"""
import json
import re
import sys
from datetime import datetime

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
SIZE = {"quick": 30, "hour": 60, "half_day": 240, "day": 480}
DEFAULT_SIZE = 30
WINDOWS = (15, 30, 45, 60)
HHMM = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def fail(msg):
    sys.stderr.write("placement: %s\n" % msg)
    sys.exit(1)


def hm(s, what):
    m = HHMM.match(str(s or ""))
    if not m:
        raise ValueError("%s must be HH:MM (got %r)" % (what, s))
    return int(m.group(1)) * 60 + int(m.group(2))


def fmt(m):
    return "%02d:%02d" % (m // 60, m % 60)


def local_minutes(iso, tz, date):
    """Minutes since the day's midnight in the user's time zone, clipped to the day."""
    dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if dt.tzinfo is not None and tz:
        try:
            from zoneinfo import ZoneInfo
            dt = dt.astimezone(ZoneInfo(tz))
        except Exception:
            pass   # keep the offset the time was written with (the user's own)
    day = dt.date().isoformat()
    if day < date:
        return 0
    if day > date:
        return 24 * 60
    return dt.hour * 60 + dt.minute


def urgency(c):
    """Most urgent first: slipped, then earliest due, then no date."""
    return (0 if c.get("status") == "slipped" else 1, c.get("due") or "9999-99-99", str(c.get("title") or ""))


def place(inp):
    date = str(inp.get("date") or "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise ValueError("date must be YYYY-MM-DD")
    tz = inp.get("timezone")
    wh = inp.get("work_hours") or {}
    start, end = hm(wh.get("start"), "work_hours.start"), hm(wh.get("end"), "work_hours.end")
    if end <= start:
        raise ValueError("work_hours.end must be after work_hours.start")
    shortest = inp.get("shortest_window", 30)
    if shortest not in WINDOWS:
        raise ValueError("shortest_window must be one of %s" % ", ".join(map(str, WINDOWS)))
    weekday = DAYS[datetime.fromisoformat(date).weekday()]
    work_day = weekday in (wh.get("days") or DAYS[:5])

    # The items, in order: priorities by rank, then anything else due today.
    items, seen = [], set()
    for p in sorted(inp.get("priorities") or [], key=lambda p: (p.get("rank") is None, p.get("rank") or 0)):
        pid = p.get("id")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        if "commitments" in p:   # a project line: its most urgent open commitment
            open_ = [c for c in p.get("commitments") or [] if c.get("status", "open") in ("open", "slipped")]
            if not open_:
                items.append({"key": pid, "minutes": None})
                continue
            c = sorted(open_, key=urgency)[0]
            seen.add(c.get("id"))
            items.append({"key": pid, "also": c.get("id"), "minutes": SIZE.get(c.get("effort"), DEFAULT_SIZE), "sized": c.get("effort") in SIZE})
            continue
        effort = p.get("effort")
        items.append({"key": pid, "minutes": SIZE.get(effort, DEFAULT_SIZE), "sized": effort in SIZE})
    due_ids = []
    for c in inp.get("due_today") or []:
        due_ids.append(c.get("id"))
        if c.get("id") and c["id"] not in seen:
            seen.add(c["id"])
            items.append({"key": c["id"], "minutes": SIZE.get(c.get("effort"), DEFAULT_SIZE), "sized": c.get("effort") in SIZE})

    out = {"day": {"start": fmt(start), "end": fmt(end), "work_day": work_day}, "windows": [], "slots": {},
           "open_minutes": 0, "due_today": len([i for i in due_ids if i]), "due_today_placed": 0}
    if not work_day:
        for it in items:
            out["slots"][it["key"]] = {"kind": "none"}
        return out

    # Busy time inside work hours, merged; the gaps between are the windows.
    busy = []
    for e in inp.get("events") or []:
        if e.get("all_day") or not e.get("start") or not e.get("end"):
            continue
        s, f = local_minutes(e["start"], tz, date), local_minutes(e["end"], tz, date)
        s, f = max(s, start), min(f, end)
        if f > s:
            busy.append([s, f])
    busy.sort()
    merged = []
    for b in busy:
        if merged and b[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b[1])
        else:
            merged.append(b)
    floor = start
    if inp.get("now"):
        floor = max(start, hm(inp["now"], "now"))
    gaps, t = [], start
    for s, f in merged + [[end, end]]:
        g0 = max(t, floor)
        if s - g0 >= shortest:
            gaps.append([g0, s])
        t = max(t, f)
    windows = [{"start": g[0], "end": g[1], "left": g[1] - g[0], "items": []} for g in gaps]

    for it in items:
        place_one(it, windows, out)
        if it.get("also"):
            out["slots"][it["also"]] = out["slots"][it["key"]]
    out["windows"] = [{"start": fmt(w["start"]), "end": fmt(w["end"]), "minutes": w["end"] - w["start"],
                       "items": w["items"], "left": w["left"]} for w in windows]
    out["open_minutes"] = sum(w["end"] - w["start"] for w in windows)
    out["due_today_placed"] = len([i for i in due_ids if i and out["slots"].get(i, {}).get("kind") == "window"])
    return out


def place_one(it, windows, out):
    """Earliest window with room; else won't fit, with a date to send in the last window."""
    if it["minutes"] is None:
        out["slots"][it["key"]] = {"kind": "none"}
        return
    w = next((w for w in windows if w["left"] >= it["minutes"]), None)
    if w:
        at = w["end"] - w["left"]
        w["left"] -= it["minutes"]
        w["items"].append(it["key"])
        out["slots"][it["key"]] = {"kind": "window", "start": fmt(w["start"]), "at": fmt(at), "minutes": it["minutes"], "sized": it["sized"]}
    else:
        last = windows[-1]["start"] if windows else None
        out["slots"][it["key"]] = {"kind": "wont_fit", "date_at": fmt(last) if last is not None else None,
                                  "minutes": it["minutes"], "sized": it["sized"]}


def main(argv):
    if len(argv) != 2:
        fail("usage: placement.py <input.json>")
    try:
        with open(argv[1], encoding="utf-8") as f:
            inp = json.load(f)
        if not isinstance(inp, dict):
            raise ValueError("the input must be a JSON object")
        json.dump(place(inp), sys.stdout, indent=1)
        sys.stdout.write("\n")
    except (OSError, ValueError) as e:
        fail(str(e))


if __name__ == "__main__":
    main(sys.argv)
