#!/usr/bin/env python3
"""Flag personal or work details still left in an issue report draft.

    python3 -I system/tools/redact_check.py <report.txt>

Run by atlas-report-issue after redaction and before the user sees the draft.
Standard library only. It flags, it never edits: each output line names one
leftover (line number, kind, the text found). Exit 1 when there is anything to
resolve, 0 when the report looks clean, 2 when it couldn't check (no report,
or no Atlas repo around this script).

What it looks for:
- email addresses, phone numbers, and IP addresses (Atlas's support address is fine);
- links, with or without https://, except to Atlas's own public repo;
- names, aliases and slugs of the user's people, organizations, projects, topics and
  commitments (user/knowledge/_index/people.md, organizations.md, projects.md,
  topics.md, commitments.md, archive.md), the user's own
  name, their employer's website and email domains (user/settings/atlas.yaml),
  and the repo's owner/name. A first or last name on its own counts only when
  capitalized, and never when it's a common English word.
Placeholders such as [PERSON-1] are ignored, and common product names (Gmail,
Slack, Google Drive...) are never flagged on their own.
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRODUCTS = {"google", "gmail", "google calendar", "google drive", "microsoft", "outlook", "teams", "onedrive",
            "sharepoint", "slack", "notion", "zoom", "github", "anthropic", "claude", "atlas", "cowork",
            "dropbox", "salesforce", "hubspot", "asana", "jira", "linear", "box", "apple", "icloud"}
COMMON = set("""will may mark grace page rose june april august bill bob art chase hope joy faith grant
lane park hall king young green brown white black gray grey long short ward rich frank dean drew miles
sky summer autumn winter spring dawn eve jean ray roy max ben sam pat chris kim lee rob ed al day
none null daily brief week goals people records project projects commitments decisions risks""".split())
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w.:-])(?:\+\d[\d ().-]{6,}\d|\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}"
                   # unseparated: a national number from 0 (07700900123), or a North American one
                   # (2125550123); a run starting with 1 is left alone, since timestamps look like that
                   r"|0\d{9,10}|[2-9]\d{2}[2-9]\d{6})(?![\w-])")
IP = re.compile(r"(?<![\w.])\d{1,3}(?:\.\d{1,3}){3}(?![\w.])")
URL = re.compile(r"\b(?:https?://[^\s)\]>\"']+|(?:[a-z0-9-]+\.)+[a-z]{2,}/[^\s)\]>\"']*)", re.I)
PLACEHOLDER = re.compile(r"\[[A-Z]+(?:-\d+)?\]")


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def manifest_values(repo):
    text = _read(os.path.join(repo, "system", "manifest.yaml")) or ""
    up = re.search(r"^upstream:\s*[\"']?([^\s\"'#]+)", text, re.M)
    mail = re.search(r"^support_email:\s*[\"']?([^\s\"'#]+)", text, re.M)
    return ((up.group(1) if up else "CaptLocke/atlas-framework").lower(),
            (mail.group(1) if mail else "atlas.framework.support@gmail.com").lower())


def terms(repo, warnings):
    """{term: (kind, whole)}: whole terms match in any case; name parts only capitalized."""
    found = {}

    def add(term, kind, part=False):
        t = re.sub(r"\s+", " ", str(term or "")).strip().strip("'\"")
        low = t.lower()
        if len(low) < 3 or low in PRODUCTS or low in ("none", "-", "[]", "n/a") or EMAIL.fullmatch(t):
            return
        if part and (low in COMMON or not t[:1].isupper()):
            return
        key = t if part else low
        found.setdefault(key, (kind, not part))

    idx = os.path.join(repo, "user", "knowledge", "_index")
    for name, kind in (("people.md", "person"), ("organizations.md", "organization"), ("projects.md", "project"),
                       ("topics.md", "topic"), ("commitments.md", "commitment"), ("archive.md", "record")):
        text = _read(os.path.join(idx, name))
        if text is None:
            if name in ("people.md", "organizations.md"):
                warnings.append("%s not found; names from it weren't checked" % name)
            continue
        for line in text.splitlines():
            m = re.match(r"^- \[\[([^\]]+)\]\]\s*\|\s*([^|]+)\|(.*)$", line)
            if not m:
                continue
            slug, title, rest = m.groups()
            add(slug.split("/")[-1], kind)
            add(title, kind)
            al = re.search(r"aliases:\s*([^|]*)", rest)
            for a in (al.group(1).split(",") if al else []):
                add(a, kind)
            parts = title.split()
            if kind == "person" and len(parts) > 1:
                add(parts[0], kind, part=True)
                add(parts[-1], kind, part=True)
    settings = _read(os.path.join(repo, "user", "settings", "atlas.yaml"))
    if settings is None:
        warnings.append("user/settings/atlas.yaml not found; the user's name and employer domains weren't checked")
        settings = ""
    m = re.search(r"^user_display_name:\s*[\"']?([^\"'#\n]+)", settings, re.M)
    if m:
        add(m.group(1), "user's name")
        for p in m.group(1).split():
            add(p, "user's name", part=True)
    in_list = False
    for line in settings.splitlines():
        value = None
        if re.match(r"^\s*(website|email_domains):", line):
            value = line.split(":", 1)[1]
            in_list = not value.strip()          # email_domains written as a block list follows
        elif in_list and re.match(r"^\s*-\s", line):
            value = line.split("-", 1)[1]
        else:
            in_list = False
        for d in re.findall(r"([a-z0-9-]+(?:\.[a-z0-9-]+)+)", value or "", re.I):
            add(re.sub(r"^www\.", "", d), "employer domain")
    try:
        url = subprocess.run(["git", "-C", repo, "remote", "get-url", "origin"], capture_output=True,
                             text=True, timeout=5).stdout.strip()
        slug = "/".join(re.split(r"[/:]", re.sub(r"\.git$", "", url))[-2:])
        if slug and slug.lower() != manifest_values(repo)[0]:
            add(slug, "repo")
            add(slug.split("/")[0], "repo owner")
    except (OSError, subprocess.SubprocessError):
        pass
    return found


def _is_upstream_link(link, upstream):
    m = re.match(r"^(?:https?://)?([^/?#]+)(/[^?#]*)?", link, re.I)
    return bool(m) and m.group(1).lower() in ("github.com", "www.github.com") and \
        re.match(r"^/%s(?:\.git)?(?:[/?#]|$)" % re.escape(upstream), (m.group(2) or "").lower()) is not None


def check(text, found, upstream, support):
    flags = []
    whole = [t for t, (k, w) in found.items() if w]
    parts = [t for t, (k, w) in found.items() if not w]
    edge = r"(?<![A-Za-z0-9])(%s)(?![A-Za-z0-9])"
    rx_whole = re.compile(edge % "|".join(map(re.escape, sorted(whole, key=len, reverse=True))), re.I) if whole else None
    rx_part = re.compile(edge % "|".join(map(re.escape, sorted(parts, key=len, reverse=True)))) if parts else None
    for n, raw in enumerate(text.splitlines(), 1):
        line = PLACEHOLDER.sub(" ", raw)
        for m in EMAIL.finditer(line):
            if m.group(0).lower() != support:
                flags.append((n, "email", m.group(0)))
        no_mail = EMAIL.sub(" ", line)
        for m in URL.finditer(no_mail):
            link = m.group(0).rstrip(".,;:")
            if not _is_upstream_link(link, upstream):
                flags.append((n, "link", link))
        for m in IP.finditer(line):
            flags.append((n, "IP address", m.group(0)))
        for m in PHONE.finditer(line):
            flags.append((n, "phone number", m.group(0)))
        taken = []
        for rx, ci in ((rx_whole, True), (rx_part, False)):
            if not rx:
                continue
            for m in rx.finditer(line):
                if any(a <= m.start() < b for a, b in taken):
                    continue
                taken.append((m.start(), m.end()))
                key = m.group(1).lower() if ci else m.group(1)
                kind = found.get(key, ("name", True))[0]
                flags.append((n, kind, m.group(1)))
    return flags


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    text = _read(argv[1])
    if text is None:
        print("can't read %s; nothing was checked" % argv[1], file=sys.stderr)
        return 2
    if not os.path.isfile(os.path.join(REPO, "system", "manifest.yaml")):
        print("no Atlas repo around %s; nothing was checked" % __file__, file=sys.stderr)
        return 2
    warnings = []
    upstream, support = manifest_values(REPO)
    flags = check(text, terms(REPO, warnings), upstream, support)
    for w in warnings:
        print("warning: " + w)
    for n, kind, found in flags:
        print("line %d: %s: %s" % (n, kind, found))
    if not flags:
        print("no personal or work details found")
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
