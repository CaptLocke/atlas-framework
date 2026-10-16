#!/usr/bin/env python3
"""Flag personal or work details still left in an issue report draft.

    python3 -I system/tools/redact_check.py <report.txt>

Run by atlas-report-issue after redaction and before the user sees the draft.
Standard library only. It flags, it never edits: each line of output names one
leftover (line number, kind, the text found), and the exit code is 1 when there
is anything to resolve, 0 when the report looks clean.

What it looks for:
- email addresses and phone numbers (Atlas's support address is fine);
- links, except to Atlas's own public repo;
- names, aliases and slugs of the user's people and organizations
  (user/knowledge/_index/people.md, organizations.md), the user's own name, and
  their employer's website and email domains (user/settings/atlas.yaml);
- the user's repo owner/name (git remote origin).
Placeholders such as [PERSON-1] or [EMAIL-1] are ignored. Common product names
(Gmail, Slack, Google Drive...) are never flagged on their own.
"""
import os
import re
import subprocess
import sys

UPSTREAM = "captlocke/atlas-framework"
SUPPORT = "atlas.framework.support@gmail.com"
PRODUCTS = {"google", "gmail", "google calendar", "google drive", "microsoft", "outlook", "teams", "onedrive",
            "sharepoint", "slack", "notion", "zoom", "github", "anthropic", "claude", "atlas", "cowork",
            "dropbox", "salesforce", "hubspot", "asana", "jira", "linear", "box", "apple", "icloud"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w-])\+?\d[\d ().-]{7,}\d(?![\w-])")
URL = re.compile(r"\b(?:https?://|www\.)[^\s)\]>\"']+", re.I)
PLACEHOLDER = re.compile(r"\[[A-Z]+(?:-\d+)?\]")


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def terms(repo):
    """{lowercased term: kind} to look for, from the user's indexes and settings."""
    found = {}

    def add(term, kind):
        t = re.sub(r"\s+", " ", str(term or "")).strip().strip("'\"").lower()
        if len(t) >= 3 and t not in PRODUCTS and not EMAIL.fullmatch(t):
            found.setdefault(t, kind)

    idx = os.path.join(repo, "user", "knowledge", "_index")
    for name, kind in (("people.md", "person"), ("organizations.md", "organization")):
        for line in _read(os.path.join(idx, name)).splitlines():
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
                add(parts[0], kind)   # first name on its own
                add(parts[-1], kind)  # surname on its own
    settings = _read(os.path.join(repo, "user", "settings", "atlas.yaml"))
    m = re.search(r"^user_display_name:\s*[\"']?([^\"'#\n]+)", settings, re.M)
    if m:
        add(m.group(1), "user's name")
        for p in m.group(1).split():
            add(p, "user's name")
    for line in settings.splitlines():
        if re.match(r"^\s*(website|email_domains):", line):
            for d in re.findall(r"([a-z0-9-]+(?:\.[a-z0-9-]+)+)", line.split(":", 1)[1], re.I):
                add(re.sub(r"^www\.", "", d), "employer domain")
    try:
        url = subprocess.run(["git", "-C", repo, "remote", "get-url", "origin"], capture_output=True,
                             text=True, timeout=5).stdout.strip()
        slug = "/".join(re.split(r"[/:]", re.sub(r"\.git$", "", url))[-2:])
        if slug.lower() != UPSTREAM:
            add(slug, "repo")
            add(slug.split("/")[0], "repo owner")
    except (OSError, subprocess.SubprocessError):
        pass
    return found


def check(text, found):
    flags = []
    patterns = [(t, k, re.compile(r"(?<![\w-])%s(?![\w-])" % re.escape(t), re.I))
                for t, k in sorted(found.items(), key=lambda x: -len(x[0]))]
    for n, raw in enumerate(text.splitlines(), 1):
        line = PLACEHOLDER.sub(" ", raw)
        for m in EMAIL.finditer(line):
            if m.group(0).lower() != SUPPORT:
                flags.append((n, "email", m.group(0)))
        for m in URL.finditer(line):
            if UPSTREAM not in m.group(0).lower():
                flags.append((n, "link", m.group(0).rstrip(".,;:")))
        for m in PHONE.finditer(line):
            if len(re.sub(r"\D", "", m.group(0))) >= 9 and not re.match(r"^\d{4}-\d{2}-\d{2}", m.group(0)):
                flags.append((n, "phone number", m.group(0)))
        taken = []
        for t, kind, rx in patterns:
            for m in rx.finditer(line):
                if any(a <= m.start() < b for a, b in taken):
                    continue
                taken.append((m.start(), m.end()))
                flags.append((n, kind, m.group(0)))
    return flags


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    text = _read(argv[1])
    repo = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    flags = check(text, terms(repo))
    for n, kind, found in flags:
        print("line %d: %s: %s" % (n, kind, found))
    if not flags:
        print("no personal or work details found")
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
