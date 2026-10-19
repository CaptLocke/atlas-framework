#!/usr/bin/env python3
"""Normalize record frontmatter to the field formats in system/schemas/schema.yaml.

Fixes only mechanical, meaning-preserving problems, and only in the keys that
need them (other lines, comments, and the body are left exactly as they are):
- ref:    a bare ID (people/dana-ruiz) becomes "[[people/dana-ruiz]]"; a one-item list becomes the item
- refs, links groups: a single value becomes a list; bare IDs are wrapped; duplicates removed
- list:   a single string becomes a one-item list; duplicates removed
- emails: a single string becomes a list; addresses lowercased and trimmed; duplicates removed
- date:   a datetime in a date-only field keeps its date part
- bool:   "yes"/"true"/"no"/"false" strings become true/false
- int:    a string of digits becomes a number
- enums:  "On Track" / "on-track" become on_track when that is an allowed value
Anything it can't fix safely is left for the validator to report.

Usage (from the repository root):
    python3 system/tools/normalize.py                 # report what would change under user/knowledge/
    python3 system/tools/normalize.py --fix           # apply the fixes
    python3 system/tools/normalize.py --fix FILE...   # only these records (use after writing them)
    python3 system/tools/normalize.py --root DIR ...  # another checkout
Exit code 0 always, unless a file can't be read (2). Standard library plus the vendored YAML parser.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import yaml  # noqa: E402  (vendored)

# A well-formed but impossible value (created: 2026-02-30) raises ValueError, not YAMLError.
YAML_ERRORS = (yaml.YAMLError, ValueError, OverflowError)

ID_RE = re.compile(r"^[a-z]+/[a-z0-9][a-z0-9-]*$")
LINK_RE = re.compile(r"^\[\[\s*([a-z]+/[a-z0-9][a-z0-9-]*)\s*\]\]$")
DT_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})[T ]\d{2}:\d{2}")
# A top-level key: plain (custom-field), double- or single-quoted ("scope").
TOP_KEY_RE = re.compile(r"""^(?:"((?:[^"\\]|\\.)*)"|'((?:[^']|'')*)'|([^\s"'#\-?:][^:#]*?|-[^\s:][^:#]*?))\s*:(?:\s|$)""")


def load_schema(root):
    with open(os.path.join(root, "system", "schemas", "schema.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def formats_for(schema, rtype):
    ff = schema.get("field_formats") or {}
    out = dict(ff.get("common") or {})
    out.update(ff.get(rtype) or {})
    return out


def enums_for(schema, rtype):
    out = dict((schema.get("common") or {}).get("enums") or {})
    out.update(((schema.get("types") or {}).get(rtype) or {}).get("enums") or {})
    return out


def as_link(v):
    """A link string for v, or None if v isn't recognisably one ID."""
    if not isinstance(v, str):
        return None
    s = v.strip()
    m = LINK_RE.match(s)
    if m:
        return "[[%s]]" % m.group(1)
    if ID_RE.match(s):
        return "[[%s]]" % s
    return None


def dedupe(items):
    seen, out = set(), []
    for x in items:
        key = json.dumps(x, sort_keys=True, default=str)
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out


def fix_value(kind, v):
    """(new value, changed?) for one field value of the given format."""
    if v is None:
        return v, False
    if kind == "ref":
        if isinstance(v, list) and len(v) == 1:
            v1, _ = fix_value("ref", v[0])
            return (v1, True) if as_link(v1) == v1 else (v, False)
        link = as_link(v)
        return (link, link != v) if link else (v, False)
    if kind == "refs":
        items = v if isinstance(v, list) else [v]
        new = [as_link(x) or x for x in items]
        new = dedupe(new)
        return new, new != v
    if kind == "list":
        items = v if isinstance(v, list) else ([v] if isinstance(v, str) else None)
        if items is None:
            return v, False
        new = dedupe(items)
        return new, new != v
    if kind == "emails":
        items = v if isinstance(v, list) else ([v] if isinstance(v, str) else None)
        if items is None:
            return v, False
        new = dedupe([x.strip().lower() if isinstance(x, str) else x for x in items])
        return new, new != v
    if kind == "date":
        if isinstance(v, datetime.datetime):
            return v.date(), True
        if isinstance(v, str):
            m = DT_PREFIX_RE.match(v.strip())
            if m:
                return datetime.date.fromisoformat(m.group(1)), True
        return v, False
    if kind == "bool":
        if isinstance(v, str) and v.strip().lower() in ("yes", "true", "no", "false"):
            return v.strip().lower() in ("yes", "true"), True
        return v, False
    if kind == "int":
        if isinstance(v, str) and v.strip().isdigit():
            return int(v.strip()), True
        return v, False
    return v, False


def fix_enum(allowed, v):
    if not isinstance(v, str) or v in allowed:
        return v, False
    cand = re.sub(r"[\s\-]+", "_", v.strip().lower())
    return (cand, True) if cand in allowed else (v, False)


def dump_value(v):
    """One-line YAML for v (flow style; strings quoted as JSON, which is valid YAML)."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    if isinstance(v, str):
        plain = yaml.safe_dump(v, default_flow_style=True, allow_unicode=True, width=10 ** 6).strip()
        if plain.endswith("\n..."):
            plain = plain[:-4].strip()
        if plain.endswith("..."):
            plain = plain[:-3].strip()
        return plain if "[[" not in v else json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(dump_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join("%s: %s" % (k, dump_value(x)) for k, x in v.items()) + " }"
    return json.dumps(v, ensure_ascii=False, default=str)


def dump_block(key, v):
    if key == "links" and isinstance(v, dict):
        return ["links:"] + ["  %s: %s" % (g, dump_value(x)) for g, x in v.items()]
    return ["%s: %s" % (key, dump_value(v))]


def split_frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    close = end + 4
    if close < len(text) and text[close] not in "\n\r":
        return None
    return text[4:end + 1], text[close:]


def top_blocks(fm_text):
    """[(key or None, [lines])]: each top-level key with its continuation lines.

    Any unindented line that isn't a comment or a "- " sequence item starts a block of its own,
    so a key this can't name is kept apart rather than glued to the key above it."""
    blocks = []
    for line in fm_text.split("\n"):
        top = line[:1] not in ("", " ", "\t", "#") and not re.match(r"^-(\s|$)", line)
        if top:
            m = TOP_KEY_RE.match(line)
            key = next((g for g in m.groups() if g is not None), None) if m else None
            blocks.append([key.strip() if key else None, [line]])
        elif blocks:
            blocks[-1][1].append(line)
        else:
            blocks.append([None, [line]])
    return blocks


def normalize_text(text, schema, rtype=None):
    """(new text, [change descriptions]). rtype defaults to the frontmatter `type`."""
    parts = split_frontmatter(text)
    if not parts:
        return text, []
    fm_text, rest = parts
    try:
        fm = yaml.safe_load(fm_text) or {}
    except YAML_ERRORS:
        return text, []
    if not isinstance(fm, dict):
        return text, []
    rtype = rtype or fm.get("type")
    formats, enums = formats_for(schema, rtype), enums_for(schema, rtype)
    groups = set((schema.get("common") or {}).get("link_groups") or [])
    fixed, changes = {}, []
    for key, value in fm.items():
        new, changed = value, False
        if key == "links" and isinstance(value, dict):
            new = {}
            for g, items in value.items():
                if g in groups:
                    ni, ch = fix_value("refs", items)
                    new[g] = ni
                    changed = changed or ch
                else:
                    new[g] = items
        elif key in formats:
            new, changed = fix_value(formats[key], value)
        elif key in enums:
            new, changed = fix_enum(enums[key], value)
        if changed:
            fixed[key] = new
            changes.append("%s: %s → %s" % (key, dump_value(value), dump_value(new)))
    if not fixed:
        return text, []
    out = []
    for key, lines in top_blocks(fm_text.rstrip("\n")):
        if key in fixed:
            trailing = []
            while len(lines) > 1 and (not lines[-1].strip() or lines[-1].lstrip().startswith("#")) \
                    and not lines[-1].startswith((" ", "\t")):
                trailing.insert(0, lines.pop())
            comment = ""
            m = re.search(r"\s+#\s.*$", lines[0]) if len(lines) == 1 and "[[" not in lines[0] else None
            if m and not re.search(r"[\"']", lines[0][:m.start()]):
                comment = m.group(0)
            block = dump_block(key, fixed[key])
            block[0] += comment
            out += block + trailing
        else:
            out += lines
    new_fm = "\n".join(out) + "\n"
    try:
        check = yaml.safe_load(new_fm) or {}
    except YAML_ERRORS:
        return text, []
    if check != {**fm, **fixed}:
        return text, []      # never write something that doesn't read back exactly as intended
    return "---\n" + new_fm + "---" + rest, changes


def record_paths(root):
    kdir = os.path.join(root, "user", "knowledge")
    if not os.path.isdir(kdir):
        return []
    out = []
    for folder in sorted(os.listdir(kdir)):
        fpath = os.path.join(kdir, folder)
        if folder.startswith("_") or not os.path.isdir(fpath):
            continue
        out += [os.path.join(fpath, f) for f in sorted(os.listdir(fpath)) if f.endswith(".md")]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")))
    ap.add_argument("--fix", action="store_true", help="write the fixes (default: report only)")
    ap.add_argument("files", nargs="*")
    a = ap.parse_args(argv)
    schema = load_schema(a.root)
    paths = [os.path.abspath(p) for p in a.files] or record_paths(a.root)
    total, rc = 0, 0
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print("ERROR %s: %s" % (p, e))
            rc = 2
            continue
        new, changes = normalize_text(text, schema)
        if not changes:
            continue
        total += 1
        rel = os.path.relpath(p, a.root).replace(os.sep, "/")
        for ch in changes:
            print("%s %s: %s" % ("FIXED" if a.fix else "WOULD FIX", rel, ch))
        if a.fix:
            with open(p, "w", encoding="utf-8") as f:
                f.write(new)
    print("Atlas normalize: %d record(s) %s." % (total, "fixed" if a.fix else "need fixes"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
