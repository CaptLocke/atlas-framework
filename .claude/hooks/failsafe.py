"""Atlas hooks: last-resort decision when a hook can't run its normal logic.

Used by the entry point of actions.py, paths.py and git.py when importing
context.py / shell.py fails or anything escapes atlas.run(). Standard library
only and self-contained, so it works even when the other hook modules are
broken. It never exits with a code other than 0 or 2: Claude Code treats any
other exit code as a NON-blocking error (https://code.claude.com/docs/en/hooks),
which would let the call through.

Decision:
1. Upstream product repo (origin = system/manifest.yaml upstream, default
   CaptLocke/atlas-framework): allow (maintainers develop Atlas here).
2. Routine (ATLAS_CONTEXT=routine, case-insensitive, or a session marked by
   routine_mark.py in .atlas-tmp/routine-sessions/): block.
3. Chat (anything else, including missing): allow only clearly harmless calls (MCP tools whose names start with a
   read verb and contain no risky word; file writes under user/ outside the
   governance files; shell commands with no risky word). Block everything else.
"""
import json
import os
import re
import subprocess
import sys

DEFAULT_UPSTREAM = "captlocke/atlas-framework"
RISKY_NAME = re.compile(
    r"(send|reply|repl|forward|post|publish|invite|respond|rsvp|comment|accept|decline|share|permission|grant|"
    r"delete|trash|remove|purge|cancel|destroy|erase|wipe|pay|purchase|charge|sign|password|credential|token|"
    r"secret|buy|transfer|invoice|create|update|edit|move|event)", re.I)
READ_FIRST = re.compile(r"^(?:[a-z0-9]+_)?(get|list|search|read|fetch|find|query|describe|count|show|view)"
                        r"(_|$)", re.I)
RISKY_SHELL = re.compile(
    r"(\brm\b|\bmv\b|\bcp\b|\bgit\b|\bgh\b|>|\btee\b|\bsed\b|\bperl\b|\bunlink\b|\bshred\b|\bfind\b|\bdd\b|"
    r"\btruncate\b|\bunzip\b|\btar\b|\bchmod\b|\bln\b|\bcurl\b|\bwget\b|\bpython|\bnode\b|\bbash\b|\bsh\b|"
    r"\beval\b|system/|\.claude|\.git|governance|data-rules|connectors\.yaml|\.atlas-tmp)")
GOVERNANCE = ("user/settings/governance.yaml", "user/settings/data-rules.yaml", "user/settings/connectors.yaml")


def _slug(url):
    u = (url or "").strip().lower().rstrip("/")
    if u.endswith(".git"):
        u = u[:-4]
    parts = [p for p in re.split(r"[/:]", u) if p]
    return "/".join(parts[-2:]) if len(parts) >= 2 else ""


def _upstream(proj):
    try:
        with open(os.path.join(proj, "system", "manifest.yaml"), encoding="utf-8") as f:
            m = re.search(r"^upstream:\s*[\"']?([^\s\"'#]+)", f.read(), re.M)
        up = m.group(1).lower() if m else DEFAULT_UPSTREAM
    except OSError:
        up = DEFAULT_UPSTREAM
    try:
        r = subprocess.run(["git", "-C", proj, "remote", "get-url", "origin"], capture_output=True,
                           text=True, timeout=3)
        # same rule as context.is_upstream: only the maintainer's marked copy bypasses
        return r.returncode == 0 and _slug(r.stdout) == _slug(up) and \
            os.path.isfile(os.path.join(proj, ".atlas-maintainer"))
    except Exception:
        return False


def _routine(payload, proj):
    if os.environ.get("ATLAS_CONTEXT", "").strip().lower() == "routine":
        return True
    sid = payload.get("session_id")
    if not isinstance(sid, str) or not sid:
        return False
    import hashlib
    name = hashlib.sha256(sid.encode("utf-8", "replace")).hexdigest()[:24]
    return os.path.exists(os.path.join(proj, ".atlas-tmp", "routine-sessions", name))


def _harmless(payload, proj):
    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}
    if tool.startswith("mcp__"):
        m = re.match(r"^mcp__(.+?)__(.+)$", tool)
        bare = m.group(2) if m else tool
        return bool(READ_FIRST.match(bare)) and not RISKY_NAME.search(bare)
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        p = ti.get("file_path") or ti.get("notebook_path") or ""
        if not p:
            return False
        p = os.path.realpath(p if os.path.isabs(p) else os.path.join(proj, p))
        rel = os.path.relpath(p, proj).replace(os.sep, "/")
        return rel.startswith("user/") and rel not in GOVERNANCE
    if tool in ("Bash", "Monitor"):
        cmd = ti.get("command")
        return isinstance(cmd, str) and not RISKY_SHELL.search(cmd)
    return False


def fail_safe(hook, exc, raw=None):
    """Decide and exit (0 or 2). 'raw' is stdin text if already read."""
    try:
        if raw is None:
            try:
                raw = sys.stdin.read()
            except Exception:
                raw = ""
        try:
            payload = json.loads(raw) if raw and raw.strip() else {}
            if not isinstance(payload, dict):
                payload = {}
        except ValueError:
            payload = {}
        proj = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
        if _upstream(proj):
            os._exit(0)
        detail = "%s: %s" % (type(exc).__name__, exc)
        routine = _routine(payload, proj)
        if not routine and _harmless(payload, proj):
            sys.stderr.write("Atlas guard (%s) warning: hook failed (%s); allowed because this is a chat and "
                             "the call looks harmless. Record a known issue for atlas-health.\n" % (hook, detail))
            sys.stderr.flush()
            os._exit(0)
        sys.stderr.write("Atlas guard (%s): the hook could not run (%s), so this call is blocked to stay safe. "
                         "The hook files may be damaged: record a known issue (atlas-health can restore "
                         "system files through atlas-update); do not try to work around the guard.\n"
                         % (hook, detail))
        sys.stderr.flush()
    except BaseException:
        pass
    os._exit(2)
