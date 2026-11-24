#!/usr/bin/env python3
"""Find candidate relationships between records that nothing links yet, for the intelligence sweep.

    python3 -I system/tools/relations.py [--root DIR] [--today YYYY-MM-DD] [--top N] [--out FILE]

Standard library plus the vendored YAML parser; reads only the repo. Prints JSON (or
writes it to --out: in a routine, a file under .atlas-tmp/, which the guard allows).
Reads frontmatter, links and source dates, never a body's text beyond its [[links]],
so it finds where to look, not what is true: `atlas-insights` §A step 3b reads the
candidates' records and decides which, if any, are worth an insight.

Which records: every type `graph.py` draws, read the same way (archived, superseded and
old closed records left out), plus sources for their dates and what they touch. The
user's own person record (`relationship: self`) is never a shared neighbour or an entity.
A source *touches* a record when it links to it or the record lists it in `sources`.

Five lists, each the top N (default 10):

- `buried`: two projects, goals, ideas, risks, questions or decisions with no link
  between them that share at least 2 neighbours (linked records, or sources both cite),
  and no project or goal (pairs already under one project or goal aren't buried).
  Score: each shared neighbour adds 1/ln(1 + its link count), so a hub such as the
  employer counts for little and a niche topic for a lot.
- `together`: two topics, organizations or people (not two people) with no link between
  them, touched by the same source at least 3 times in the last 60 days, in at least half
  of the sources that touch the rarer one.
- `follows`: a topic, organization or person whose sources in the last 180 days are often
  followed, within 14 days, by an outcome on the same work: a commitment slipping (`slipped`, or `done`
  after its `due` date; on the due date), a risk turning `active`, a project going `off_track`, or a decision
  `reversed` (all three dated by `updated`, which any later edit also moves). "The same work" means the source touches the outcome
  or a project or goal it links to. Kept when at least 3 distinct outcomes followed and at
  least half the entity's sources were followed by one. This is a sequence, never a cause.
  Closed records last updated more than 90 days ago aren't read (as in `graph.py`), so a
  done-late commitment counts here only while it is that recent.
- `unowned`: open risks (`potential` or `active`) with no `owner` or no `mitigation`, kept
  when the risk is quiet (neither it nor a source touching it dated in the last 21 days)
  or its `impact` is high and a project it links to has a `target` date (a goal's counts
  only when it is a date) already passed or in the next 28 days, whatever the risk's
  age. High impact first, then the earliest target, then the longest quiet. A risk can
  be unowned on purpose; reading decides.
- `themes`: terms (words of 4+ letters, acronyms, and adjacent pairs of them, never
  across two fields) from the title, aliases and summary of commitments, decisions,
  ideas, risks, questions, projects and events that recur in at least 3 of them, of at
  least 2 types, touched by at least 2 sources whose content may be stored (not
  `retention: pointer`), where no topic's title or aliases hold
  the term itself. Names of people, organizations, projects and goals are left out (a
  project isn't a theme of its own commitments), as are common work words, weekdays,
  months and cadences, and, from 20 records up, terms in more than 15% of them. A
  record counts fully when the term is in its title or aliases and half when only in
  its summary; pairs score half again; a word whose records all carry a listed pair is
  dropped. Reading decides whether a term is a real theme (`topic.md` §Capture guidance).

Sources flagged `suspicious` are left out entirely, including where a record cites them.
"""
import argparse
import json
import math
import os
import sys
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import graph  # noqa: E402
import index  # noqa: E402

WORK = {"project", "goal", "idea", "risk", "question", "decision"}
CONTEXT = {"project", "goal"}
ENTITY = {"topic", "organization", "person"}
TOGETHER_DAYS, FOLLOWS_DAYS, AFTER_DAYS = 60, 180, 14
QUIET_DAYS, AHEAD_DAYS = 21, 28
TOP = 10


def _ids(value):
    out = []
    for v in value if isinstance(value, list) else [value]:
        r = index.ref_id(v)
        if r:
            out.append(r)
    return out


def load(root, today):
    """(records {id: info}, sources {id: date}, touches {source id: set of record ids},
    pointer-only source ids)."""
    tmap = index.types(root)
    recs, sources, touches, flagged, pointer = {}, {}, {}, set(), set()
    src_folder = (tmap.get("source") or ("sources", set()))[0]
    d = os.path.join(root, "user", "knowledge", src_folder)
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            path = os.path.join(d, f)
            fm = index.read_frontmatter(path)
            if fm is None:
                continue
            sid = str(fm.get("id") or "%s/%s" % (src_folder, f[:-3]))
            if str(fm.get("retention") or "") == "pointer":
                pointer.add(sid)
            if "suspicious" in (fm.get("flags") or []):
                flagged.add(sid)
                continue
            day = index.as_date(fm.get("occurred_on")) or index.as_date(fm.get("captured_on"))
            if day:
                sources[sid] = day
            touches[sid] = graph.front_links(fm) | graph.body_links(path)
    for name in graph.TYPES:
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
            if rid in recs:
                continue
            st = str(fm.get("status") or "")
            updated = index.as_date(fm.get("updated")) or index.as_date(fm.get("created"))
            if st in closed and (name == "question" or not updated or (today - updated).days > graph.RECENT_DAYS):
                continue
            recs[rid] = {"type": name, "title": index.clean(fm.get("title")) or rid, "status": st,
                         "health": str(fm.get("health") or fm.get("assessment") or ""),
                         "due": index.as_date(fm.get("due")), "done": index.as_date(fm.get("completed_on")), "updated": updated,
                         "target": index.as_date(fm.get("target")), "impact": str(fm.get("impact") or ""),
                         "missing": [k for k in ("owner", "mitigation") if not fm.get(k)],
                         "self": name == "person" and str(fm.get("relationship") or "") == "self",
                         "fields": [str(fm.get("title") or "")] + [str(x) for x in (fm.get("aliases") or []) if x]
                                   + [str(fm.get("summary") or "")],
                         "names": [str(fm.get("title") or "")] + [str(x) for x in (fm.get("aliases") or []) if x],
                         "links": (graph.front_links(fm) | graph.body_links(path)) - {rid}}
            for sid in _ids(fm.get("sources")):
                touches.setdefault(sid, set()).add(rid)
    touches = {sid: {r for r in rs if r in recs and not recs[r]["self"]}
               for sid, rs in touches.items() if sid not in flagged}
    return recs, sources, touches, pointer


def adjacency(recs, touches):
    adj = {r: set() for r in recs}
    for r, info in recs.items():
        for o in info["links"]:
            if o in recs and o != r:
                adj[r].add(o)
                adj[o].add(r)
    return adj


def buried(recs, adj, touches, top):
    cited = {}
    for sid, rs in touches.items():
        for r in rs:
            cited.setdefault(r, set()).add(sid)
    selfs = {r for r, i in recs.items() if i["self"]}
    hood = {r: (adj[r] - selfs) | cited.get(r, set()) for r in recs if recs[r]["type"] in WORK}
    deg = {r: len(adj[r]) for r in adj}
    deg.update({s: len(rs) for s, rs in touches.items()})
    out, work = [], sorted(hood)
    for i, a in enumerate(work):
        for b in work[i + 1:]:
            if b in adj[a]:
                continue
            shared = hood[a] & hood[b]
            if len(shared) < 2 or any(s in recs and recs[s]["type"] in CONTEXT for s in shared):
                continue
            score = sum(1 / math.log(1 + max(deg.get(s, 1), 1)) for s in shared)
            out.append({"a": a, "b": b, "shared": sorted(shared), "score": round(score, 3)})
    out.sort(key=lambda x: (-x["score"], x["a"], x["b"]))
    return out[:top]


def _entities(recs, rs):
    return {r for r in rs if recs[r]["type"] in ENTITY}


def together(recs, adj, sources, touches, today, top):
    since = today - timedelta(days=TOGETHER_DAYS)
    count, pair = {}, {}
    for sid, rs in touches.items():
        day = sources.get(sid)
        if not day or day < since or day > today:
            continue
        ents = sorted(_entities(recs, rs))
        for e in ents:
            count[e] = count.get(e, 0) + 1
        for i, a in enumerate(ents):
            for b in ents[i + 1:]:
                if recs[a]["type"] == "person" and recs[b]["type"] == "person":
                    continue
                pair.setdefault((a, b), []).append(sid)
    out = []
    for (a, b), sids in pair.items():
        if b in adj[a] or len(sids) < 3:
            continue
        rarer = min(count[a], count[b])
        if len(sids) * 2 < rarer:
            continue
        out.append({"a": a, "b": b, "sources": sorted(sids), "together": len(sids),
                    "of": rarer, "score": round(len(sids) / rarer * math.log(1 + len(sids)), 3)})
    out.sort(key=lambda x: (-x["score"], x["a"], x["b"]))
    return out[:top]


def outcomes(recs, adj):
    """[(id, kind, date, context ids)]: the outcomes `follows` looks for."""
    out = []
    for r, i in recs.items():
        kind, day = None, None
        late = i["status"] == "slipped" or (i["status"] == "done" and i["done"] and i["due"] and i["done"] > i["due"])
        if i["type"] == "commitment" and late and i["due"]:
            kind, day = "slipped", i["due"]
        elif i["type"] == "risk" and i["status"] == "active":
            kind, day = "risk_active", i["updated"]
        elif i["type"] in CONTEXT and i["status"] == "active" and i["health"] == "off_track":
            kind, day = "off_track", i["updated"]
        elif i["type"] == "decision" and i["status"] == "reversed":
            kind, day = "reversed", i["updated"]
        if kind and day:
            ctx = {r} | {o for o in adj[r] if recs[o]["type"] in CONTEXT}
            out.append((r, kind, day, ctx))
    return out


def follows(recs, adj, sources, touches, today, top):
    since = today - timedelta(days=FOLLOWS_DAYS)
    outs = outcomes(recs, adj)
    seen, hits = {}, {}
    for sid, rs in touches.items():
        day = sources.get(sid)
        if not day or day < since or day > today:
            continue
        after = [o for o in outs if day < o[2] <= day + timedelta(days=AFTER_DAYS) and o[3] & rs]
        for e in _entities(recs, rs):
            seen[e] = seen.get(e, 0) + 1
            for oid, kind, oday, _ in after:
                hits.setdefault((e, kind), {}).setdefault(sid, []).append((oid, oday))
    out = []
    for (e, kind), by_src in hits.items():
        distinct = {oid for v in by_src.values() for oid, _ in v}
        if len(distinct) < 3 or len(by_src) * 2 < seen[e]:
            continue
        inst = [{"source": sid, "on": sources[sid].isoformat(),
                 "then": [{"record": oid, "on": oday.isoformat()} for oid, oday in sorted(set(v))]}
                for sid, v in sorted(by_src.items(), key=lambda kv: sources[kv[0]])]
        out.append({"entity": e, "outcome": kind, "followed": len(by_src), "of": seen[e],
                    "outcomes": len(distinct), "instances": inst,
                    "score": round(len(by_src) / seen[e] * math.log(1 + len(distinct)), 3)})
    out.sort(key=lambda x: (-x["score"], x["entity"], x["outcome"]))
    return out[:top]


def unowned(recs, adj, sources, touches, today, top):
    """Open risks with no owner or no mitigation that are quiet, or high impact with a target close."""
    seen = {}
    for sid, rs in touches.items():
        for r in rs:
            if sid in sources:
                seen[r] = max(seen.get(r, sources[sid]), sources[sid])
    out = []
    for r, info in recs.items():
        if info["type"] != "risk" or info["status"] not in ("potential", "active") or not info["missing"]:
            continue
        last = max(d for d in (info["updated"], seen.get(r)) if d) if (info["updated"] or seen.get(r)) else None
        quiet = (today - last).days if last else None
        ahead = sorted((recs[o]["target"], o) for o in adj[r]       # a passed target first: the most urgent case
                       if recs[o]["type"] in CONTEXT and recs[o]["target"])
        near = ahead[0] if ahead else None
        days = (near[0] - today).days if near else None
        high = info["impact"] == "high"
        if not ((quiet is not None and quiet >= QUIET_DAYS) or (high and days is not None and days <= AHEAD_DAYS)):
            continue
        out.append({"risk": r, "missing": info["missing"], "impact": info["impact"] or None, "quiet_days": quiet,
                    "target": {"record": near[1], "date": near[0].isoformat(), "days": days} if near else None})
    out.sort(key=lambda x: (x["impact"] != "high", x["target"]["days"] if x["target"] else 10 ** 6,
                            -(x["quiet_days"] or 0), x["risk"]))
    return out[:top]


STOP = set("""a an and are as at be been but by can do does done for from get got had has have he her his how i if in
into is it its let me more most my new no not now of on or our out over own per she so some than that the their them
then there these they this those to too up us very was we were what when which who why will with would you your
about after again ago all also any back before being both each few just like many much next only other same should
still such them until via want way week weeks day days today tomorrow yesterday month months year time
send sent sending ask asked check checking confirm draft drafts follow followup review reviews reviewed update updates
updated share shared call calls meeting meetings sync email emails message notes note plan plans planning prep make
made need needs needed work working item items thing things team chat call discuss discussed agree agreed decide
decided set setting start started finish finished expect expects expected report reports status feedback
daily weekly monthly quarterly yearly annual monday tuesday wednesday thursday friday saturday sunday
january february march april june july august september october november december""".split())
CONTENT = {"commitment", "decision", "idea", "risk", "question", "project", "event"}
THEME_MIN_RECORDS, THEME_MIN_SOURCES, THEME_MAX_SHARE = 3, 2, 0.15


def _terms(text):
    """Theme terms in a line of text: words of 4+ letters or acronyms (SSO, DPA), and adjacent pairs of them."""
    words = []
    for raw in "".join(ch if ch.isalnum() else " " for ch in text).split():
        w = raw.lower()
        if w in STOP or w.isdigit() or not (len(w) >= 4 or (raw.isupper() and len(raw) >= 2)):
            words.append(None)
            continue
        words.append(w)
    out = {w for w in words if w}
    out.update("%s %s" % (a, b) for a, b in zip(words, words[1:]) if a and b and a != b)
    return out


def themes(recs, touches, top, pointer=frozenset()):
    """Terms that recur across content records and sources with no topic covering them yet."""
    named, covered = set(), set()
    for info in recs.values():
        if info["type"] in ("person", "organization", "project", "goal"):
            for n in info["names"]:
                named.update(_terms(n))
        if info["type"] == "topic":
            for n in info["names"]:
                covered.update(_terms(n))
    srcs = {}
    for sid, rs in touches.items():
        if sid in pointer:   # topic.md counts only content that may be stored (ATL-138)
            continue
        for r in rs:
            srcs.setdefault(r, set()).add(sid)
    content = [r for r, i in recs.items() if i["type"] in CONTENT]
    has, titled = {}, {}
    for r in content:
        f = recs[r]["fields"]
        head = set().union(*(_terms(x) for x in f[:-1])) if f[:-1] else set()
        for t in head | _terms(f[-1]):    # per field, so a pair never spans two of them
            if t not in named and t not in covered:
                has.setdefault(t, set()).add(r)
                if t in head:
                    titled.setdefault(t, set()).add(r)
    cap = max(THEME_MIN_RECORDS, int(len(content) * THEME_MAX_SHARE)) if len(content) >= 20 else len(content)
    out = []
    for t, rs in has.items():
        src = set().union(*(srcs.get(r, set()) for r in rs))
        if (len(rs) < THEME_MIN_RECORDS or len(src) < THEME_MIN_SOURCES or len(rs) > cap
                or len({recs[r]["type"] for r in rs}) < 2):
            continue
        weight = len(titled.get(t, ())) + 0.5 * (len(rs) - len(titled.get(t, ())))   # a title counts more than a summary
        out.append({"term": t, "records": sorted(rs)[:8], "count": len(rs), "sources": len(src),
                    "score": round(weight * math.log(1 + len(src)) * (1.5 if " " in t else 1), 3)})
    out.sort(key=lambda x: (-x["score"], x["term"]))
    kept = []
    for x in out:   # a word whose records all carry a kept pair says nothing the pair doesn't
        if " " not in x["term"] and any(x["term"] in k["term"].split() and k["count"] >= x["count"] for k in kept):
            continue
        kept.append(x)
    return kept[:top]


def build(root, today, top=TOP):
    recs, sources, touches, pointer = load(root, today)
    adj = adjacency(recs, touches)
    data = {"buried": buried(recs, adj, touches, top),
            "together": together(recs, adj, sources, touches, today, top),
            "follows": follows(recs, adj, sources, touches, today, top),
            "unowned": unowned(recs, adj, sources, touches, today, top),
            "themes": themes(recs, touches, top, pointer)}
    named = set()
    for x in data["buried"] + data["together"]:
        named.update([x["a"], x["b"]])
    for x in data["follows"]:
        named.add(x["entity"])
        named.update(t["record"] for i in x["instances"] for t in i["then"])
    for x in data["themes"]:
        named.update(x["records"])
    for x in data["unowned"]:
        named.add(x["risk"])
        if x["target"]:
            named.add(x["target"]["record"])
    data["titles"] = {r: recs[r]["title"] for r in sorted(named)}
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(allow_abbrev=False, description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    ap.add_argument("--today", help="YYYY-MM-DD (default: today in atlas.yaml's time zone)")
    ap.add_argument("--top", type=int, default=TOP, help="most candidates per list (default %d)" % TOP)
    ap.add_argument("--out", help="write the JSON here instead of printing it")
    a = ap.parse_args(argv)
    today = index.as_date(a.today) if a.today else index.local_today(a.root)
    if today is None:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if a.top < 1:
        print("--top must be at least 1", file=sys.stderr)
        return 2
    data = build(a.root, today, a.top)
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
