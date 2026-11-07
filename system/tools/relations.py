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

Three lists, each the top N (default 10) by score:

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
  after its `due` date; on the due date), a risk turning `active`, a project or goal going `off_track`, or a decision
  `reversed` (on its `updated` date). "The same work" means the source touches the outcome
  or a project or goal it links to. Kept when at least 3 distinct outcomes followed and at
  least half the entity's sources were followed by one. This is a sequence, never a cause.
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
TOP = 10


def _ids(value):
    out = []
    for v in value if isinstance(value, list) else [value]:
        r = index.ref_id(v)
        if r:
            out.append(r)
    return out


def load(root, today):
    """(records {id: info}, sources {id: date}, touches {source id: set of record ids})."""
    tmap = index.types(root)
    recs, sources, touches = {}, {}, {}
    src_folder = (tmap.get("source") or ("sources", set()))[0]
    d = os.path.join(root, "user", "knowledge", src_folder)
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".md"):
                continue
            path = os.path.join(d, f)
            fm = index.read_frontmatter(path)
            if fm is None or "suspicious" in (fm.get("flags") or []):
                continue
            sid = str(fm.get("id") or "%s/%s" % (src_folder, f[:-3]))
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
                         "self": name == "person" and str(fm.get("relationship") or "") == "self",
                         "links": (graph.front_links(fm) | graph.body_links(path)) - {rid}}
            for sid in _ids(fm.get("sources")):
                touches.setdefault(sid, set()).add(rid)
    for sid in touches:
        touches[sid] = {r for r in touches[sid] if r in recs and not recs[r]["self"]}
    return recs, sources, touches


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


def build(root, today, top=TOP):
    recs, sources, touches = load(root, today)
    adj = adjacency(recs, touches)
    data = {"buried": buried(recs, adj, touches, top),
            "together": together(recs, adj, sources, touches, today, top),
            "follows": follows(recs, adj, sources, touches, today, top)}
    named = set()
    for x in data["buried"] + data["together"]:
        named.update([x["a"], x["b"]])
    for x in data["follows"]:
        named.add(x["entity"])
        named.update(t["record"] for i in x["instances"] for t in i["then"])
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
