"""Nova hooks: shared context detection and helpers (build plan H-2).

Imported by actions.py, paths.py and git.py; not registered as a hook itself.

Claude Code hooks contract relied on (https://code.claude.com/docs/en/hooks,
https://code.claude.com/docs/en/tools-reference, checked 2026-10-12):
- PreToolUse command hooks receive one JSON object on stdin with common fields
  (session_id, transcript_path, cwd, permission_mode, hook_event_name) plus
  tool_name, tool_input and tool_use_id.
- Exit code 0 lets the call continue (no JSON = normal permission flow).
  Exit code 2 blocks the call and stderr is fed back to Claude as the reason;
  a JSON "allow" cannot override exit 2. Any other exit code is a NON-blocking
  error, so every hook here catches its own errors and decides explicitly.
- JSON on stdout with hookSpecificOutput.permissionDecision = "ask" asks the
  user instead of deciding.
- $CLAUDE_PROJECT_DIR is the project root (exported to the hook process).
- MCP tools are named mcp__<server>__<tool>; matchers with regex characters are
  unanchored JavaScript regexes ("mcp__.*").

Policy (system/rules/governance.md):
- Routines are identified by a marker: NOVA_CONTEXT=routine (case-insensitive,
  trimmed) means routine; anything else (missing, empty, "chat", other
  values) means chat. Rationale: Claude Code routines run in cloud
  environments that can set the variable reliably, while the chat surfaces
  users work in (Cowork / desktop Project chats) can't. Chats are still
  guarded: every locked action needs a single-use approval record, so
  "unknown = chat" never lets a locked action through unconfirmed.
- Every hook is a no-op in the upstream product repo: origin points to
  system/manifest.yaml: upstream (DEFAULT_UPSTREAM when the manifest is
  missing). A missing manifest does NOT switch the hooks off; owned paths
  then fall back to DEFAULT_OWNED_PATHS.
- Internal errors fail closed in routine context and for locked actions;
  otherwise the call is allowed with a warning on stderr.
"""
import datetime as _dt
import json
import os
import re
import subprocess
import sys

TMP_DIR = ".nova-tmp"
APPROVAL = ".nova-tmp/approval.json"
UPDATE_LOCK = ".nova-tmp/update.lock"
PURGE_LOCK = ".nova-tmp/purge.lock"
GOVERNANCE_FILES = (
    "user/settings/governance.yaml",
    "user/settings/data-rules.yaml",
    "user/settings/connectors.yaml",
)
# Maximum lifetimes (minutes) from system/schemas/formats.md section 2, plus
# one minute of clock slack. A record claiming to live longer is invalid.
MAX_MINUTES = {"approval": 2 + 1, "update": 30 + 1, "purge": 15 + 1}
DEFAULT_UPSTREAM = "CaptLocke/nova"
DEFAULT_OWNED_PATHS = ["CLAUDE.md", "README.md", "LICENSE", "CHANGELOG.md", ".gitignore", "docs/", ".claude/",
                       "system/"]

_CACHE = {}


class State:
    """Per-call state the error handler consults (fail-closed decisions)."""
    hook = "nova"
    context = "routine"
    locked = False      # set once the call is known to be a locked action
    raw = None          # raw stdin text (for failsafe.py)


STATE = State()


# --------------------------------------------------------------- decisions
def block(message):
    sys.stderr.write("Nova guard (%s): %s\n" % (STATE.hook, message))
    sys.stderr.flush()
    sys.exit(2)


def ask(message):
    out = {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "Nova guard (%s): %s" % (STATE.hook, message),
    }}
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()
    sys.exit(0)


def allow(warning=None):
    if warning:
        sys.stderr.write("Nova guard (%s) warning: %s\n" % (STATE.hook, warning))
    sys.exit(0)


# --------------------------------------------------------------- context
def nova_context():
    """'routine' only when NOVA_CONTEXT is 'routine' (case-insensitive,
    trimmed); otherwise 'chat' (routines carry the marker, chats can't)."""
    return "routine" if os.environ.get("NOVA_CONTEXT", "").strip().lower() == "routine" else "chat"


def project_dir(payload):
    d = os.environ.get("CLAUDE_PROJECT_DIR") or (payload or {}).get("cwd") or os.getcwd()
    return os.path.realpath(d)


def session_cwd(payload, proj):
    c = (payload or {}).get("cwd") or proj
    return os.path.realpath(c) if os.path.isdir(c) else proj


def _manifest_text(proj):
    key = ("manifest_text", proj)
    if key not in _CACHE:
        try:
            with open(os.path.join(proj, "system", "manifest.yaml"), encoding="utf-8") as f:
                _CACHE[key] = f.read()
        except OSError:
            _CACHE[key] = None
    return _CACHE[key]


def repo_slug(url):
    """Reduce any git remote URL form to 'owner/repo' (lowercase, no .git).

    Handles https://host/owner/repo(.git), git@host:owner/repo(.git),
    ssh://git@host/owner/repo, and proxy forms such as
    http://proxy@127.0.0.1:1234/git/owner/repo.
    """
    if not url:
        return ""
    u = url.strip().lower().rstrip("/")
    if u.endswith(".git"):
        u = u[:-4]
    u = re.sub(r"^[a-z0-9+.-]+://", "", u)          # scheme
    u = re.sub(r"^[^/@]+@([^/:]+):(?!\d+/)", r"\1/", u)  # scp-like git@host:owner/repo
    parts = [p for p in re.split(r"[/:]", u) if p]
    return "/".join(parts[-2:]) if len(parts) >= 2 else ""


def is_upstream(proj):
    """True when hooks must not enforce anything (maintainers' upstream repo).

    True when origin points to the repo named in manifest 'upstream'
    (DEFAULT_UPSTREAM if the manifest or field is missing). Cached in-process.
    """
    key = ("upstream", proj)
    if key in _CACHE:
        return _CACHE[key]
    text = _manifest_text(proj)
    m = re.search(r"^upstream:\s*[\"']?([^\s\"'#]+)", text, re.M) if text else None
    upstream = (m.group(1) if m else DEFAULT_UPSTREAM).strip().lower()
    result = False
    if upstream:
        try:
            r = subprocess.run(["git", "-C", proj, "remote", "get-url", "origin"],
                               capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                result = repo_slug(r.stdout) == repo_slug(upstream)
        except (OSError, subprocess.SubprocessError):
            result = False
    _CACHE[key] = result
    return result


# --------------------------------------------------------------- yaml
def load_yaml(path, proj):
    """safe_load a YAML file with the vendored PyYAML (system/tools/vendor)."""
    vendor = os.path.join(proj, "system", "tools", "vendor")
    if os.path.isdir(vendor) and vendor not in sys.path:
        sys.path.insert(0, vendor)
    import yaml  # noqa: E402  (vendored, falls back to an installed PyYAML)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def owned_paths(proj):
    key = ("owned", proj)
    if key not in _CACHE:
        mpath = os.path.join(proj, "system", "manifest.yaml")
        if not os.path.exists(mpath):
            _CACHE[key] = list(DEFAULT_OWNED_PATHS)
            return _CACHE[key]
        data = load_yaml(mpath, proj) or {}
        paths = data.get("owned_paths") or []
        if not isinstance(paths, list) or not paths:
            raise ValueError("system/manifest.yaml has no owned_paths list")
        _CACHE[key] = [str(p) for p in paths]
    return _CACHE[key]


# --------------------------------------------------------------- paths
def rel_to_project(path, base, proj):
    """Project-relative POSIX path for 'path' (resolved against base), or None
    when it lies outside the project. '' means the project root itself."""
    if not path:
        return None
    p = os.path.expanduser(path)
    if not os.path.isabs(p):
        p = os.path.join(base, p)
    p = os.path.realpath(p)
    try:
        rel = os.path.relpath(p, proj)
    except ValueError:
        return None
    if rel == ".":
        return ""
    if rel.startswith(".."):
        return None
    return rel.replace(os.sep, "/")


def overlaps(rel, entry):
    """Does project-relative path 'rel' touch manifest entry 'entry'?

    True if rel is inside entry, equals it, or contains it (rel is a parent
    directory, e.g. 'rm -r .' or a glob prefix)."""
    e = entry.rstrip("/")
    r = rel.rstrip("/")
    if r == "":
        return True
    if r == e or r.startswith(e + "/"):
        return True
    if e.startswith(r + "/"):
        return True
    return False


# --------------------------------------------------------------- records
def parse_time(value):
    if not isinstance(value, str) or not value.strip():
        return None
    s = value.strip()
    if s.endswith("Z") or s.endswith("z"):
        s = s[:-1] + "+00:00"
    try:
        t = _dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.astimezone()  # naive = local time
    return t


def read_record(proj, rel):
    path = os.path.join(proj, rel)
    if not os.path.exists(path):
        return None, "%s does not exist" % rel
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        return None, "%s is not valid JSON (%s)" % (rel, e)
    if not isinstance(data, dict):
        return None, "%s is not a JSON object" % rel
    return data, None


def check_expiry(data, kind, rel):
    """(ok, reason) for a record's 'expires' field."""
    exp = parse_time(data.get("expires"))
    if exp is None:
        return False, "%s has no valid 'expires' timestamp (ISO 8601 with offset)" % rel
    now = _dt.datetime.now(_dt.timezone.utc)
    if exp <= now:
        return False, "%s expired at %s" % (rel, data.get("expires"))
    if (exp - now).total_seconds() > MAX_MINUTES[kind] * 60:
        return False, ("%s expires too far in the future (max %d minutes)"
                       % (rel, MAX_MINUTES[kind] - 1))
    return True, ""


def valid_lock(proj, kind):
    """(ok, reason) for update.lock / purge.lock."""
    rel = UPDATE_LOCK if kind == "update" else PURGE_LOCK
    data, err = read_record(proj, rel)
    if data is None:
        return False, err
    return check_expiry(data, kind, rel)


def norm_target(proj, value):
    """Repo-relative POSIX form of a record's 'target' when it is a path."""
    if not isinstance(value, str) or not value.strip():
        return ""
    v = value.strip()
    if os.path.isabs(v):
        rel = rel_to_project(v, proj, proj)
        return rel if rel is not None else v
    v = os.path.normpath(v).replace(os.sep, "/")
    return v[2:] if v.startswith("./") else v


def approval_matches(proj, tool, actions, targets=None):
    """(record, reason). record is the approval dict when it is present,
    unexpired, names exactly this tool and one of the allowed actions, and -
    when 'targets' (repo-relative paths) is given - a target equal to one of
    them."""
    data, err = read_record(proj, APPROVAL)
    if data is None:
        return None, err
    ok, why = check_expiry(data, "approval", APPROVAL)
    if not ok:
        return None, why
    if data.get("tool") != tool:
        return None, "%s is for tool %r, not %r" % (APPROVAL, data.get("tool"), tool)
    if data.get("action") not in actions:
        return None, "%s is for action %r; this call needs %s" % (
            APPROVAL, data.get("action"), " or ".join(sorted(actions)))
    if not str(data.get("user_confirmation", "")).strip():
        return None, "%s has no user_confirmation quote" % APPROVAL
    if targets is not None:
        t = norm_target(proj, data.get("target"))
        if t not in targets:
            return None, "%s target %r does not match the file being changed (%s); set target to the " \
                         "repo-relative path" % (APPROVAL, data.get("target"), ", ".join(sorted(targets)))
    return data, ""


def discard_stale_approval(proj, targets):
    """Delete an approval record whose target is one of 'targets'."""
    data, _ = read_record(proj, APPROVAL)
    if data is not None and norm_target(proj, data.get("target")) in targets:
        try:
            consume_approval(proj)
        except OSError:
            pass


def consume_approval(proj):
    """Delete the approval record (single use). Raises on failure."""
    os.remove(os.path.join(proj, APPROVAL))


# --------------------------------------------------------------- runner
def run(hook_name, handler):
    """Read stdin, apply the upstream bypass, call handler(payload, proj, ctx).

    The handler ends by calling block(), ask() or allow(); returning normally
    means allow."""
    STATE.hook = hook_name
    STATE.context = nova_context()
    try:
        raw = sys.stdin.read()
        STATE.raw = raw
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            raise ValueError("hook input is not a JSON object")
    except Exception as e:  # unreadable input
        payload = None
        input_error = e
    else:
        input_error = None

    proj = project_dir(payload)
    try:
        if is_upstream(proj):
            sys.exit(0)
    except SystemExit:
        raise
    except Exception:
        pass  # cannot tell: keep enforcing

    try:
        if input_error is not None:
            raise input_error
        handler(payload, proj, STATE.context)
    except SystemExit:
        raise
    except Exception as e:
        detail = "%s: %s" % (type(e).__name__, e)
        if STATE.context == "routine" or STATE.locked:
            block("internal error (%s). Blocked to stay safe. Fix the cause (often a "
                  "malformed settings or lock file) or record it as a known issue; "
                  "do not try to work around this guard." % detail)
        allow("internal error (%s); allowed because this is a chat and the call "
              "is not a locked action." % detail)
    sys.exit(0)
