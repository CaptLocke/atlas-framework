#!/usr/bin/env python3
"""Cut one dashboard's data into the section documents a live page reads.

    python3 -I system/tools/sections.py <data.json> <out-dir>

Standard library only. <data.json> is the page's data exactly in its contract's
shape (atlas-dashboards, Render step 2). Writes into <out-dir>:
- one file per top-level key, <key>.json = {"data": <value>}: the documents for
  the page database's "sections" collection, doc id = the key ("meta" included);
- live.json = {"meta": {"live": true, ...}}: the only data a live page embeds,
  the fields that don't change between refreshes (render.py takes it as data).
Prints each section's size in KB and fails (exit 1) when one is over the limit
a single database write takes, naming it, so a refresh never half-writes a page
(system/dashboards/README.md, "Live pages"). <out-dir> must be inside .atlas-tmp/
(not its routine-sessions/) or a temp folder, because the tool clears the
.json files it finds there. The sections together must also fit one write.
"""
import json
import os
import re
import sys
import tempfile

SECTION_MAX_KB = 900          # a database batch carries at most 1 MiB, and a refresh is one batch
STATIC_META = ("dashboard", "title", "locale", "atlas_version", "stale_after_hours")
KEY = re.compile(r"^[A-Za-z0-9_-]{1,100}$")


def cut(data):
    """{doc id: document} for every top-level key, plus the embedded live data."""
    if not isinstance(data, dict) or not isinstance(data.get("meta"), dict):
        raise ValueError("the data must be a JSON object with a 'meta' object")
    docs = {}
    for key, value in data.items():
        if not KEY.match(key) or key == "live":
            raise ValueError("section name %r can't be a document id" % key)
        docs[key] = {"data": value}
    meta = data["meta"]
    live = {"meta": dict({k: meta[k] for k in STATIC_META if k in meta}, live=True)}
    return docs, live


def scratch_dir(path):
    """Is this a folder the tool may clear: inside .atlas-tmp/ (of the working directory) or a temp folder?"""
    real = os.path.realpath(path)
    roots = [os.path.join(os.getcwd(), ".atlas-tmp"), "/tmp", "/var/tmp", tempfile.gettempdir()]
    markers = os.path.realpath(os.path.join(os.getcwd(), ".atlas-tmp", "routine-sessions"))
    if real == markers or real.startswith(markers + os.sep):
        return False   # the routine session markers (system/rules/governance.md)
    return any(real.startswith(os.path.realpath(r) + os.sep) for r in roots)


def size_kb(obj):
    return len(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) / 1024


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    data_path, out_dir = argv[1:]
    if not scratch_dir(out_dir):
        print("sections failed: write sections under .atlas-tmp/ or a temp folder, not %s" % out_dir, file=sys.stderr)
        return 1
    try:
        with open(data_path, encoding="utf-8") as f:
            docs, live = cut(json.load(f))
        too_big = [k for k, d in docs.items() if size_kb(d) > SECTION_MAX_KB]
        if too_big:
            raise ValueError("section(s) over %d KB: %s; trim them by the contract's rules"
                             % (SECTION_MAX_KB, ", ".join(sorted(too_big))))
        total = sum(size_kb(d) for d in docs.values())
        if total > SECTION_MAX_KB:
            raise ValueError("the sections come to %.0f KB, over the %d KB one write takes; trim by the contract's "
                             "rules" % (total, SECTION_MAX_KB))
        os.makedirs(out_dir, exist_ok=True)
        for name in os.listdir(out_dir):   # a section dropped from the data mustn't linger
            if name.endswith(".json"):
                os.remove(os.path.join(out_dir, name))
        for key, doc in list(docs.items()) + [("live", live)]:
            with open(os.path.join(out_dir, key + ".json"), "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    except (OSError, ValueError, UnicodeError) as e:
        print("sections failed: %s" % e, file=sys.stderr)
        return 1
    for key in sorted(docs):
        print("%s: %.1f KB" % (key, size_kb(docs[key])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
