"""Atlas hooks: shared context detection and helpers.

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
- Routines are identified by a marker: ATLAS_CONTEXT=routine (case-insensitive,
  trimmed) means routine. A session whose first prompt was an Atlas routine
  prompt ("Run the Atlas routine ...") is a routine too, even without the
  variable: routine_mark.py (UserPromptSubmit) records it in
  .atlas-tmp/routine-sessions/, which no tool may write or delete. Anything
  else means chat. Rationale: Claude Code routines run in cloud environments
  that can set the variable, while the chat surfaces users work in (Cowork /
  desktop Project chats) can't; the session marker covers a routine attached
  to the wrong environment. Chats are still guarded: every locked action
  needs a single-use approval record.
- In routines the update lock counts only for a signed release at or above
  the installed version (update_lock): a lock file alone proves nothing,
  because the session that wrote it may be following injected content.
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

TMP_DIR = ".atlas-tmp"
MAINTAINER_MARKER = ".atlas-maintainer"
APPROVAL = ".atlas-tmp/approval.json"
UPDATE_LOCK = ".atlas-tmp/update.lock"
PURGE_LOCK = ".atlas-tmp/purge.lock"
ROUTINE_SESSIONS = ".atlas-tmp/routine-sessions"
# Files Claude Code (or git) loads as instructions, servers or hooks when found
# in the repo. Atlas never writes them (H3); the root CLAUDE.md is owned anyway.
AUTOLOAD_NAMES = {"claude.md", "claude.local.md", "agents.md", ".mcp.json", ".gitattributes", ".gitmodules"}
AUTOLOAD_DIRS = {".claude", ".githooks", ".husky"}
# Places outside the repo a routine may write (M4): temp files and the null device.
OUTSIDE_WRITE_OK = ("/tmp/", "/var/tmp/", "/dev/null", "/dev/stdout", "/dev/stderr", "/dev/fd/")
GOVERNANCE_FILES = (
    "user/settings/governance.yaml",
    "user/settings/data-rules.yaml",
    "user/settings/connectors.yaml",
)
# Maximum lifetimes (minutes) from system/schemas/formats.md section 2, plus
# one minute of clock slack. A record claiming to live longer is invalid.
MAX_MINUTES = {"approval": 2 + 1, "update": 30 + 1, "purge": 15 + 1}
DEFAULT_UPSTREAM = "CaptLocke/atlas-framework"
DEFAULT_OWNED_PATHS = ["CLAUDE.md", "README.md", "LICENSE", "CHANGELOG.md", "SECURITY.md", ".gitignore", ".gitattributes",
                       "docs/", ".claude/", "system/"]

_CACHE = {}


class State:
    """Per-call state the error handler consults (fail-closed decisions)."""
    hook = "atlas"
    context = "routine"
    locked = False      # set once the call is known to be a locked action
    raw = None          # raw stdin text (for failsafe.py)


STATE = State()


# --------------------------------------------------------------- decisions
def block(message):
    sys.stderr.write("Atlas guard (%s): %s\n" % (STATE.hook, message))
    sys.stderr.flush()
    sys.exit(2)


def ask(message):
    out = {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "Atlas guard (%s): %s" % (STATE.hook, message),
    }}
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()
    sys.exit(0)


def allow(warning=None):
    if warning:
        sys.stderr.write("Atlas guard (%s) warning: %s\n" % (STATE.hook, warning))
    sys.exit(0)


# --------------------------------------------------------------- context
def atlas_context(payload=None, proj=None):
    """'routine' when ATLAS_CONTEXT is 'routine' (case-insensitive, trimmed) or
    this session started with an Atlas routine prompt; otherwise 'chat'."""
    if os.environ.get("ATLAS_CONTEXT", "").strip().lower() == "routine":
        return "routine"
    if proj and os.path.exists(routine_mark_path(proj, (payload or {}).get("session_id"))):
        return "routine"
    return "chat"


def routine_mark_path(proj, session_id):
    """Marker file for a session that began with a routine prompt ('' when there's no session id)."""
    if not isinstance(session_id, str) or not session_id:
        return ""
    import hashlib
    name = hashlib.sha256(session_id.encode("utf-8", "replace")).hexdigest()[:24]
    return os.path.join(proj, ROUTINE_SESSIONS, name)


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


def upstream_slug(proj):
    """'owner/repo' of the official upstream (manifest 'upstream', else DEFAULT_UPSTREAM)."""
    text = _manifest_text(proj)
    m = re.search(r"^upstream:\s*[\"']?([^\s\"'#]+)", text, re.M) if text else None
    return repo_slug(m.group(1) if m else DEFAULT_UPSTREAM)


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
    # A clone of the upstream (instead of "Use this template") is still guarded: only a
    # maintainer's copy, marked with the git-ignored .atlas-maintainer file, bypasses.
    result = bool(upstream) and os.path.isfile(os.path.join(proj, MAINTAINER_MARKER)) \
        and origin_slug(proj) == repo_slug(upstream)
    _CACHE[key] = result
    return result


def origin_slug(proj):
    """'owner/repo' of the origin remote, or ''."""
    try:
        r = subprocess.run(["git", "-C", proj, "remote", "get-url", "origin"],
                           capture_output=True, text=True, timeout=3)
        return repo_slug(r.stdout) if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


# --------------------------------------------------------------- yaml
def load_yaml(path, proj):
    """safe_load a YAML file with the vendored PyYAML (system/tools/vendor)."""
    with open(path, encoding="utf-8") as f:
        return load_yaml_text(f.read(), proj)


def load_yaml_text(text, proj):
    vendor = os.path.join(proj, "system", "tools", "vendor")
    if os.path.isdir(vendor) and vendor not in sys.path:
        sys.path.insert(0, vendor)
    import yaml  # noqa: E402  (vendored, falls back to an installed PyYAML)
    return yaml.safe_load(text)


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


def _git(proj, args, timeout=10):
    """(returncode, stdout); 1 on any error."""
    try:
        r = subprocess.run(["git", "-C", proj] + args, capture_output=True, text=True,
                           timeout=timeout, errors="replace", stdin=subprocess.DEVNULL)
        return r.returncode, r.stdout
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def in_history(proj, ref):
    """True when 'ref' names a commit that is HEAD or one of its ancestors
    (rollback tags, installed_from_commit): content this repo already had."""
    if not ref or ref.startswith("-"):
        return False
    rc, sha = _git(proj, ["rev-parse", "--verify", "-q", ref + "^{commit}"], timeout=5)
    if rc != 0 or not sha.strip():
        return False
    rc, _ = _git(proj, ["merge-base", "--is-ancestor", sha.strip(), "HEAD"], timeout=5)
    return rc == 0


def release_verified(proj, full_ref):
    """True when refs/atlas-upstream/v<x> is a tag signed by a release key
    (system/tools/release_check.py; fails closed when it can't run)."""
    if not full_ref.startswith("refs/atlas-upstream/"):
        return False
    key = ("verified", proj, full_ref)
    if key not in _CACHE:
        tool = os.path.join(proj, "system", "tools", "release_check.py")
        name = full_ref[len("refs/atlas-upstream/"):]
        try:
            r = subprocess.run([sys.executable, "-I", tool, "verify", full_ref, name], cwd=proj,
                               capture_output=True, timeout=30, stdin=subprocess.DEVNULL)
            _CACHE[key] = r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            _CACHE[key] = False
    return _CACHE[key]


def version_tuple(text):
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", str(text or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def installed_version(proj):
    """Version committed at HEAD (system/VERSION); (0, 0, 0) when there is none."""
    rc, out = _git(proj, ["show", "HEAD:system/VERSION"], timeout=5)
    return version_tuple(out) if rc == 0 and version_tuple(out) else (0, 0, 0)


def update_lock(proj, ctx):
    """(ok, reason, release_ref). In a chat: a valid, unexpired lock (release_ref
    None). In a routine the lock must also name `version_to`, whose release ref
    refs/atlas-upstream/v<version_to> is fetched and signed by a release key,
    at or above the installed version (routines never downgrade)."""
    ok, why = valid_lock(proj, "update")
    if not ok or ctx == "chat":
        return ok, why, None
    data, _ = read_record(proj, UPDATE_LOCK)
    to = version_tuple(data.get("version_to"))
    if to is None:
        return False, "%s has no valid version_to" % UPDATE_LOCK, None
    ref = "refs/atlas-upstream/v%d.%d.%d" % to
    if not release_verified(proj, ref):
        return False, "%s isn't a fetched release signed by Atlas's maker" % ref, None
    if to < installed_version(proj):
        return False, "a routine never installs an older version than the one installed", None
    return True, "", ref


def in_tree(proj, ref, rel):
    """True when path 'rel' (file or folder; '' = root) exists in commit 'ref'."""
    rc, _ = _git(proj, ["cat-file", "-e", "%s:%s" % (ref, rel)], timeout=5)
    return rc == 0


def outside_write_ok(path):
    """May a routine write or delete this absolute path outside the repo? Only temp
    folders' contents and the standard streams (M4)."""
    import tempfile
    raw = os.path.normpath(path)
    if raw in ("/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty") or raw.startswith(("/dev/fd/",
                                                                                          "/proc/self/fd/")):
        return True
    real = os.path.realpath(path)
    for root in ("/tmp", "/var/tmp", tempfile.gettempdir()):
        r = os.path.realpath(root)
        if r not in ("/", "") and real.startswith(r + "/"):
            return True
    return False


def autoload_path(rel):
    """True for a repo path Claude Code or git would load as instructions, a server or a hook (H3).
    The owned .claude/ and root CLAUDE.md are left to the owned-path check."""
    r = rel.rstrip("/")
    if not r or r == ".claude" or r.startswith(".claude/") or r == "CLAUDE.md":
        return False
    parts = r.lower().split("/")
    return parts[-1] in AUTOLOAD_NAMES or any(p in AUTOLOAD_DIRS for p in parts)


def full_ref_name(proj, ref):
    """Full name git resolves 'ref' to ('refs/heads/x' for a branch named
    'refs/atlas-upstream/x'), or '' when it isn't a ref."""
    if not ref or ref.startswith("-"):
        return ""
    rc, out = _git(proj, ["rev-parse", "--symbolic-full-name", ref], timeout=10)
    return out.strip() if rc == 0 else ""


def system_files_changed(proj):
    """(changed, detail). True when tracked owned files differ from HEAD
    (file-mode and line-ending-only changes ignored), when .claude/hooks has
    untracked files (they could shadow a hook module), or when git can't tell
    (fail closed)."""
    owned = [e.rstrip("/") for e in owned_paths(proj)] or [".claude", "system"]
    rc, _ = _git(proj, ["-c", "core.fileMode=false", "diff", "--quiet", "--ignore-cr-at-eol", "HEAD",
                        "--"] + owned, timeout=10)
    if rc not in (0, 1):
        return True, "git could not check the system files"
    if rc == 1:
        return True, "system files differ from the last commit"
    rc, out = _git(proj, ["ls-files", "--others", "--exclude-standard", "--", ".claude/hooks"], timeout=10)
    if rc != 0:
        return True, "git could not check the system files"
    if out.strip():
        return True, "there are unexpected files in .claude/hooks (%s)" % ", ".join(out.split()[:3])
    return False, ""


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
    STATE.context = atlas_context()
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
        STATE.context = atlas_context(payload, proj)
    except Exception:
        STATE.context = "routine"  # can't tell: the stricter rules
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
