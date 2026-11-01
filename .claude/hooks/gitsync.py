"""Atlas hooks: shared helpers for the sync hooks (sync_start.py, sync_guard.py).

Standard library only. Not registered as a hook itself. Every function here
returns a value instead of raising for ordinary git failures; callers still
wrap everything because these hooks must never crash (system/rules/sync.md).
"""
import datetime as dt
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BRANCH = "main"                                  # system/rules/sync.md: push origin HEAD:main
IGNORED_PREFIXES = (".atlas-tmp/", "user/inbox/drop/")
LOG = ".atlas-tmp/sync.log"
GIT_ENV = {"GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "", "SSH_ASKPASS": "", "GIT_EDITOR": "true",
           "GIT_SEQUENCE_EDITOR": "true", "LC_ALL": "C"}


def project_dir(payload):
    d = os.environ.get("CLAUDE_PROJECT_DIR") or (payload or {}).get("cwd") or os.getcwd()
    return os.path.realpath(d)


def read_payload(stdin):
    try:
        raw = stdin.read()
        data = json.loads(raw) if raw and raw.strip() else {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def is_upstream(proj):
    """Same upstream bypass as the PreToolUse hooks (context.py); falls back
    to failsafe.py's standalone check if context.py can't be imported."""
    import sys
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    try:
        import context
        return context.is_upstream(proj)
    except Exception:
        from failsafe import _upstream
        return _upstream(proj)


def git(proj, args, timeout=10):
    """(returncode, stdout, stderr); returncode 124 on timeout, 127 if git is missing."""
    env = dict(os.environ)
    env.update(GIT_ENV)
    try:
        r = subprocess.run(["git", "-C", proj] + args, capture_output=True, text=True, timeout=timeout,
                           env=env, errors="replace", stdin=subprocess.DEVNULL)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timed out after %ss" % timeout
    except OSError as e:
        return 127, "", str(e)


def is_git_repo(proj):
    rc, out, _ = git(proj, ["rev-parse", "--is-inside-work-tree"], timeout=5)
    return rc == 0 and out.strip() == "true"


def has_origin(proj):
    rc, out, _ = git(proj, ["remote", "get-url", "origin"], timeout=5)
    return rc == 0 and bool(out.strip())


def current_branch(proj):
    rc, out, _ = git(proj, ["symbolic-ref", "--quiet", "--short", "HEAD"], timeout=5)
    return out.strip() if rc == 0 else ""


def short_sha(proj, ref="HEAD"):
    rc, out, _ = git(proj, ["rev-parse", "--short", ref], timeout=5)
    return out.strip() if rc == 0 else "?"


def one_line(text, limit=240):
    t = " ".join((text or "").split())
    return t[:limit] + ("..." if len(t) > limit else "")


def now_iso():
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def log(proj, event, message):
    """Append one line to .atlas-tmp/sync.log (git-ignored). Never raises."""
    try:
        os.makedirs(os.path.join(proj, ".atlas-tmp"), exist_ok=True)
        with open(os.path.join(proj, LOG), "a", encoding="utf-8") as f:
            f.write("%s %s %s\n" % (now_iso(), event, one_line(message, 500)))
    except Exception:
        pass


def unsaved_paths(proj):
    """Paths with uncommitted changes (tracked) or untracked and not
    git-ignored, excluding IGNORED_PREFIXES. None if status failed."""
    rc, out, _ = git(proj, ["status", "--porcelain=v1", "-z", "--untracked-files=all"], timeout=10)
    if rc != 0:
        return None
    entries = out.split("\0")
    paths, i = [], 0
    while i < len(entries):
        e = entries[i]
        i += 1
        if len(e) < 4:
            continue
        code, path = e[:2], e[3:]
        if code[0] in "RC":
            i += 1  # the next entry is the rename/copy source
        if any(path.startswith(p) for p in IGNORED_PREFIXES):
            continue
        paths.append(path)
    return paths


def operation_in_progress(proj):
    """'rebase' / 'merge' / 'cherry-pick' / 'revert' if one is unfinished."""
    rc, out, _ = git(proj, ["rev-parse", "--git-dir"], timeout=5)
    if rc != 0:
        return None
    gdir = out.strip()
    gdir = gdir if os.path.isabs(gdir) else os.path.join(proj, gdir)
    for name, marker in (("rebase", "rebase-merge"), ("rebase", "rebase-apply"), ("merge", "MERGE_HEAD"),
                         ("cherry-pick", "CHERRY_PICK_HEAD"), ("revert", "REVERT_HEAD")):
        if os.path.exists(os.path.join(gdir, marker)):
            return name
    return None


def unpushed_count(proj):
    """Commits on HEAD that origin/main doesn't have (falls back to commits on
    no origin ref when origin/main doesn't exist). None if it can't tell."""
    rc, _, _ = git(proj, ["rev-parse", "--verify", "-q", "HEAD"], timeout=5)
    if rc != 0:
        return 0  # no commits yet
    rc, _, _ = git(proj, ["rev-parse", "--verify", "-q", "refs/remotes/origin/%s" % BRANCH], timeout=5)
    if rc == 0:
        args = ["rev-list", "--count", "origin/%s..HEAD" % BRANCH]
    else:
        args = ["rev-list", "--count", "HEAD", "--not", "--remotes=origin"]
    rc, out, _ = git(proj, args, timeout=10)
    if rc != 0:
        return None
    try:
        return int(out.strip())
    except ValueError:
        return None


def local_today(proj, yaml):
    """Today in the user's time zone (atlas.yaml: timezone), which is the date
    every Atlas record carries; the machine's date is UTC in a routine."""
    try:
        with open(os.path.join(proj, "user", "settings", "atlas.yaml"), encoding="utf-8") as f:
            tz = (yaml.safe_load(f) or {}).get("timezone")
        if tz:
            from zoneinfo import ZoneInfo
            return dt.datetime.now(ZoneInfo(str(tz))).date()
    except Exception:
        pass
    return dt.date.today()


def emit(obj):
    import sys
    sys.stdout.write(json.dumps(obj))
    sys.stdout.flush()


def health_issue(proj, issue_id, summary, fix):
    """Add an open high-severity known issue to user/.state/health.yaml if it
    can be done safely (file exists, parses, result re-parses with the issue).
    Returns True if the issue is now recorded."""
    import sys
    path = os.path.join(proj, "user", ".state", "health.yaml")
    if not os.path.exists(path):
        return False
    vendor = os.path.join(proj, "system", "tools", "vendor")
    if vendor not in sys.path:
        sys.path.insert(0, vendor)
    import yaml
    with open(path, encoding="utf-8") as f:
        text = f.read()
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        return False
    issues = data.get("known_issues")
    if issues is not None and not isinstance(issues, list):
        return False
    for it in issues or []:
        if isinstance(it, dict) and it.get("id") == issue_id and it.get("status", "open") == "open":
            return True
    entry = "  - { id: %s, severity: high, since: %s, summary: %s, fix: %s, status: open }" % (
        issue_id, local_today(proj, yaml).isoformat(), json.dumps(summary), json.dumps(fix))
    lines = text.splitlines()
    idx = next((i for i, l in enumerate(lines) if re.match(r"^known_issues:", l)), None)
    if idx is None:
        new = text.rstrip("\n") + "\nknown_issues:\n" + entry + "\n"
    elif re.match(r"^known_issues:\s*(\[\s*\])?\s*(#.*)?$", lines[idx]):
        lines[idx] = "known_issues:"
        lines.insert(idx + 1, entry)
        new = "\n".join(lines) + "\n"
    else:
        return False  # flow-style list with items: don't risk rewriting it
    check = yaml.safe_load(new)
    if not (isinstance(check, dict) and any(isinstance(i, dict) and i.get("id") == issue_id
                                            for i in check.get("known_issues") or [])):
        return False
    tmp = path + ".atlas-tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new)
    os.replace(tmp, path)
    return True
