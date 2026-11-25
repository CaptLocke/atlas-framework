#!/usr/bin/env python3
"""Fingerprint a draft Atlas made, and later say what the user did to it before sending (ATL-136).

    python3 -I system/tools/drafts.py fingerprint FILE
    python3 -I system/tools/drafts.py compare FINGERPRINT_JSON SENT_FILE

Standard library only. Prints JSON. Never stores or prints the text. Quoted replies (lines
starting ">", and everything from an "On … wrote:" or "Original Message" line) and a signature
(from a "-- " line) are dropped first. A fingerprint is the word count, the number of 3-word
runs (lowercased, punctuation dropped), and a sample: the 32 smallest of their hashes, each cut
to 24 bits. A sample of unordered short hashes can't be chained back into the wording, though
a guessed phrase could be confirmed (review H3). `atlas-write` keeps it in
`user/.state/drafts.yaml`; ingest compares it with the sent message when one matches.

compare estimates `kept` (the share of the draft's runs still in the sent text, from the
sample) and `added` (the share of the sent text's runs that weren't in the draft) and gives:
- `unchanged`: kept at least 0.97 and added at most 0.25 (a signature or a name added is fine);
- `light_edit`: kept at least 0.8;
- `heavy_edit`: anything else.
A draft never sent is `discarded`, which the caller decides from its age (14 days), not this tool.
"""
import json
import re
import sys
import zlib

WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
QUOTE_START = re.compile(r"^\s*(on .{0,200} wrote:|-{2,}\s*original message|from: .+)\s*$", re.I)
SAMPLE = 32


def body(text):
    """The new text only: no quoted reply, no signature."""
    out = []
    for line in text.splitlines():
        if line.rstrip() in ("--", "-- ") or QUOTE_START.match(line):
            break
        if not line.lstrip().startswith(">"):
            out.append(line)
    return "\n".join(out)


def runs(text):
    words = WORD_RE.findall(body(text).lower())
    if len(words) < 3:
        return len(words), {" ".join(words)} if words else set()
    return len(words), {" ".join(words[i:i + 3]) for i in range(len(words) - 2)}


def hashes(shingles):
    return sorted({"%06x" % (zlib.crc32(s.encode("utf-8")) & 0xffffff) for s in shingles})


def fingerprint(text):
    n, sh = runs(text)
    hs = hashes(sh)
    return {"words": n, "runs": len(hs), "sample": " ".join(hs[:SAMPLE])}


def compare(fp, sent_text):
    sample = set((fp.get("sample") or "").split())
    n, sh = runs(sent_text)
    sent = set(hashes(sh))
    if not sample:
        return {"outcome": "heavy_edit", "kept": 0.0, "added": 1.0 if sent else 0.0, "words": n}
    kept = len(sample & sent) / len(sample)
    shared = kept * (fp.get("runs") or len(sample))
    added = max(0.0, 1 - shared / len(sent)) if sent else 0.0
    if kept >= 0.97 and added <= 0.25:
        outcome = "unchanged"
    elif kept >= 0.8:
        outcome = "light_edit"
    else:
        outcome = "heavy_edit"
    return {"outcome": outcome, "kept": round(kept, 2), "added": round(added, 2), "words": n,
            "length_change": round((n - fp.get("words", 0)) / fp["words"], 2) if fp.get("words") else None}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) == 2 and a[0] == "fingerprint":
        out = fingerprint(read(a[1]))
    elif len(a) == 3 and a[0] == "compare":
        try:
            fp = json.loads(read(a[1]))
        except ValueError:
            print("FINGERPRINT_JSON must be the JSON fingerprint printed", file=sys.stderr)
            return 2
        out = compare(fp, read(a[2]))
    else:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(out, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
