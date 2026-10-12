#!/usr/bin/env python3
"""Nova hook: git history, secrets and attribution, N8 / N10 / N12 (build plan H-5).

Registered in .claude/settings.json as a PreToolUse hook for shell commands
(matcher "Bash|Monitor").

Claude Code contract relied on (https://code.claude.com/docs/en/hooks, checked
2026-10-12): stdin JSON with tool_name, tool_input.command and cwd; exit 2 +
stderr blocks the call and the message goes to Claude; $CLAUDE_PROJECT_DIR is
the project root. Shared policy: context.py.

What it enforces (system/rules/governance.md, system/rules/sync.md):
- N8: blocks force pushes (--force, -f, --force-with-lease, --force-if-includes,
  --mirror, +refspec), `reset --hard` to anything but HEAD, `rebase -i` /
  `--interactive` / `--root`, filter-branch, filter-repo, `replace`,
  `update-ref`, `reflog expire|delete`, `gc --prune`, and `commit --amend` of
  a commit that is already pushed. Sole exception: a valid
  .nova-tmp/purge.lock in a chat (the nova-memory purge procedure).
  Also blocks changing the `origin` remote (it decides the upstream bypass).
- N8: deleting tags (`git tag -d`, push of :refs/tags/...) only under a valid
  update lock or a purge lock in a chat; deleting branches on origin
  (`git push --delete`, `git push origin :branch`, `git branch -d/-D` of a
  branch that exists on origin) only under a purge lock in a chat.
- N9: blocks `gh repo edit --visibility` and non-GET `gh api` calls touching
  collaborators, invitations or visibility.
- N12: `git commit` must carry `Nova-Actor:` and `Nova-Reason:` trailers
  (parsed from -m/--message, -F/--file and heredocs). When the message source
  can't be determined (editor, -C/-c, -F - without a heredoc) the commit is
  allowed with a warning. Routines may not commit as `Nova-Actor: chat`.
- N10: before a commit, scans added lines of the staged diff (plus unstaged
  and untracked files when the same command runs `git add` or `commit -a`)
  for secret patterns and blocks if any are found.
"""
import os
import re
import subprocess
import sys

# --- fail-safe entry: any error, even an import failure, ends in exit 0 or 2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from failsafe import fail_safe
except BaseException as _fe:  # failsafe.py itself is broken: block
    def fail_safe(hook, exc, raw=None, _fe=_fe):
        try:
            sys.stderr.write("Nova guard (%s): hook files are damaged (%s; %s); blocked.\n" % (hook, exc, _fe))
        finally:
            os._exit(2)


def _raw_stdin():
    mod = sys.modules.get("context")
    return getattr(getattr(mod, "STATE", None), "raw", None)


sys.excepthook = lambda _t, _e, _tb: fail_safe("git", _e, _raw_stdin())
try:
    import context as nova  # noqa: E402
    import shell  # noqa: E402
except BaseException as _imp:  # includes SystemExit raised while importing
    fail_safe("git", _imp, _raw_stdin())

# Patterns are assembled from parts so this file never contains a literal
# secret-shaped string (it is committed into every Nova repo).
SECRET_PATTERNS = [
    ("AWS access key ID", r"\b(?:AK" + r"IA|AS" + r"IA)[0-9A-Z]{16}\b"),
    ("AWS secret access key", r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}"),
    ("GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    ("GitHub fine-grained token", r"\bgithub_" + r"pat_[A-Za-z0-9_]{22,}"),
    ("Anthropic API key", r"\bsk-" + r"ant-[A-Za-z0-9_-]{20,}"),
    ("OpenAI API key", r"\bsk-" + r"proj-[A-Za-z0-9_-]{20,}"),
    ("private key", r"-----BEGIN [A-Z0-9 ]*PRIVATE" + r" KEY-----"),
    ("Slack token", r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    ("Google API key", r"\bAI" + r"za[0-9A-Za-z_-]{35}"),
    ("password in URL", r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^/\s:@'\"]+:[^/\s@'\"]+@[^\s/'\"]+"),
]
SECRET_RES = [(n, re.compile(p)) for n, p in SECRET_PATTERNS]
ACTOR_RE = re.compile(r"^(chat|update|setup|routine:[A-Za-z0-9][A-Za-z0-9_-]*)$")
MAX_FILE_BYTES = 2 * 1024 * 1024


def git(args, cwd, timeout=10):
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, errors="replace")
        return r.returncode, r.stdout
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def short_flags(args):
    return "".join(a[1:] for a in args if a.startswith("-") and not a.startswith("--"))


def positional(args):
    return shell.positional(["git"] + args)


# ------------------------------------------------------------------ N8
def rewrite_reason(sub, args, cwd):
    """A string describing the history rewrite, or None."""
    if sub == "push":
        for a in args:
            if a in ("-f", "--force", "--force-with-lease", "--force-if-includes", "--mirror") \
                    or a.startswith("--force-with-lease=") or (re.match(r"^-[a-zA-Z]+$", a) and "f" in a):
                return "force push (%s)" % a
        for p in positional(args):
            if p.startswith("+"):
                return "force push (+refspec %s)" % p
    elif sub == "reset" and "--hard" in args:
        targets = [p for p in positional(args)]
        if targets and targets[0] not in ("HEAD", "@"):
            return "reset --hard %s" % targets[0]
    elif sub == "rebase":
        if any(a in ("-i", "--interactive", "--root") or (re.match(r"^-[a-zA-Z]+$", a) and "i" in a)
               for a in args):
            return "interactive/root rebase"
    elif sub in ("filter-branch", "filter-repo", "replace", "update-ref"):
        return "git %s" % sub
    elif sub == "reflog" and args and args[0] in ("expire", "delete"):
        return "git reflog %s" % args[0]
    elif sub == "gc" and any(a.startswith("--prune") for a in args):
        return "git gc --prune"
    elif sub == "commit" and "--amend" in args and head_is_pushed(cwd):
        return "commit --amend of a commit that is already pushed"
    return None


def ref_deletion(sub, args, cwd):
    """(description, 'tag'|'branch') for commands that delete tags or
    branches that exist on origin, else None."""
    if sub == "tag" and any(a in ("-d", "--delete") or (re.match(r"^-[a-zA-Z]+$", a) and "d" in a)
                            for a in args):
        return "git tag -d (deleting tags)", "tag"
    if sub == "push":
        pos = positional(args)
        refs = pos[1:] if len(pos) > 1 else pos
        deleting = any(a in ("-d", "--delete") for a in args)
        colon = [r for r in refs if r.startswith(":")]
        if deleting or colon:
            targets = colon or refs
            kind = "tag" if targets and all("refs/tags/" in r or "--tags" in args for r in targets) else "branch"
            return "git push deleting %s" % (" ".join(targets) or "refs"), kind
    if sub == "branch":
        deleting = any(a in ("-D", "-d", "--delete") or (re.match(r"^-[a-zA-Z]+$", a) and a[1:].lower().count("d"))
                       for a in args)
        if deleting:
            names = [p for p in positional(args)]
            on_origin = [n for n in names if git(["rev-parse", "--verify", "-q", "refs/remotes/origin/%s" % n],
                                                 cwd)[0] == 0]
            if on_origin:
                return "git branch delete of %s (exists on origin)" % ", ".join(on_origin), "branch"
    return None


def gh_change(argv):
    """Description when a gh command changes repo visibility or collaborators
    (N9), else None."""
    args = argv[1:]
    if len(args) >= 2 and args[0] == "repo" and args[1] == "edit":
        if any(a == "--visibility" or a.startswith("--visibility=") for a in args):
            return "gh repo edit --visibility"
    if args and args[0] == "api":
        text = " ".join(args).lower()
        if "collaborator" in text or "visibility" in text or "/invitations" in text:
            method = shell.option_value(argv, "-X", "--method") or "GET"
            writes = any(a in ("-f", "-F", "--field", "--raw-field", "--input") or
                         a.startswith(("--field=", "--raw-field=", "--input=", "-f", "-F")) for a in args)
            if method.upper() != "GET" or writes:
                return "gh api changing collaborators or visibility"
    return None


def head_is_pushed(cwd):
    rc, _ = git(["rev-parse", "--verify", "-q", "HEAD"], cwd)
    if rc != 0:
        return False
    rc, up = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd)
    if rc == 0 and up.strip():
        rc2, _ = git(["merge-base", "--is-ancestor", "HEAD", "@{u}"], cwd)
        if rc2 == 0:
            return True
    rc, out = git(["branch", "-r", "--contains", "HEAD"], cwd)
    return rc == 0 and bool(out.strip())


def remote_change(sub, args):
    if sub == "remote" and args:
        verb, rest = args[0], positional(args[1:])
        if verb in ("set-url", "rename", "remove", "rm") and rest[:1] == ["origin"]:
            return "git remote %s origin" % verb
        if verb == "add" and rest[:1] == ["origin"]:
            return "git remote add origin"
    if sub == "config" and any(re.match(r"^remote\.origin(\.|$)", a) for a in args):
        destructive = any(a in ("--unset", "--unset-all", "--remove-section", "--rename-section",
                                "--replace-all", "--add") for a in args)
        setting = len(positional(args)) >= 2  # 'git config remote.origin.url <value>'
        if destructive or setting:
            return "changing remote.origin config"
    return None


# ------------------------------------------------------------------ N12
def commit_message(args, cwd, bodies):
    """(message or None, reason-if-None)."""
    parts = []
    source = None
    i = 0
    while i < len(args):
        a = args[i]
        val = None
        if a in ("-m", "--message"):
            val = args[i + 1] if i + 1 < len(args) else ""
            i += 1
        elif a.startswith("--message="):
            val = a.split("=", 1)[1]
        elif re.match(r"^-[a-zA-Z]+$", a) and "m" in a[1:]:
            idx = a.index("m", 1)
            if idx == len(a) - 1:
                val = args[i + 1] if i + 1 < len(args) else ""
                i += 1
            else:
                val = a[idx + 1:]
        elif a in ("-F", "--file") or a.startswith("--file=") or (a.startswith("-F") and len(a) > 2):
            if a in ("-F", "--file"):
                fname = args[i + 1] if i + 1 < len(args) else ""
                i += 1
            elif a.startswith("--file="):
                fname = a.split("=", 1)[1]
            else:
                fname = a[2:]
            if fname == "-":
                if bodies:
                    parts.append("\n".join(bodies))
                    source = "heredoc"
                else:
                    return None, "message read from stdin"
            else:
                path = fname if os.path.isabs(fname) else os.path.join(cwd, fname)
                try:
                    with open(path, encoding="utf-8", errors="replace") as f:
                        parts.append(f.read())
                    source = "file"
                except OSError:
                    return None, "message file %s not readable" % fname
        elif a in ("-C", "-c", "--reuse-message", "--reedit-message") or \
                a.startswith("--reuse-message=") or a.startswith("--reedit-message=") or \
                a.startswith("--fixup") or a.startswith("--squash"):
            return None, "message reused from another commit"
        if val is not None:
            if "$(" in val or "`" in val:
                if bodies:
                    parts.append("\n".join(bodies))
                else:
                    return None, "message built by command substitution"
            else:
                parts.append(val)
            source = source or "-m"
        i += 1
    if not parts:
        if "--amend" in args or "--no-edit" in args:
            return None, "amend keeps the previous message"
        return None, "no -m/-F message (editor)"
    return "\n\n".join(parts), None


def check_trailers(message, ctx):
    actor = re.search(r"(?mi)^Nova-Actor:[ \t]*(.*?)[ \t]*$", message)
    reason = re.search(r"(?mi)^Nova-Reason:[ \t]*(\S.*)$", message)
    missing = [n for n, m in (("Nova-Actor", actor), ("Nova-Reason", reason)) if not m]
    if missing:
        nova.block("commit message is missing the %s trailer%s (N12). End the message with:\n"
                   "  Nova-Actor: chat | routine:<routine-name> | update | setup\n"
                   "  Nova-Reason: <why, one line>\n"
                   "  Nova-Records: <ids or paths, or ->\n(format: system/rules/sync.md)"
                   % (" and ".join(missing), "s" if len(missing) > 1 else ""))
    value = actor.group(1).strip()
    if not ACTOR_RE.match(value):
        nova.block("Nova-Actor %r is not valid; use chat, routine:<routine-name>, update or setup "
                   "(system/rules/sync.md)." % value)
    if ctx != "chat" and value == "chat":
        nova.block("the commit says 'Nova-Actor: chat' but NOVA_CONTEXT is not 'chat' in this session. "
                   "If this IS a chat with the user, the Nova chat environment isn't set up (NOVA_CONTEXT "
                   "missing): tell the user and follow nova-setup's 'Nova chat environment' step to fix it; "
                   "until then, setup work can commit with 'Nova-Actor: setup'. If this is a scheduled "
                   "routine, use 'Nova-Actor: routine:<routine-name>'.")


# ------------------------------------------------------------------ N10
def scan_text(text, label, findings):
    for name, rx in SECRET_RES:
        if rx.search(text):
            findings.append("%s in %s" % (name, label))


def scan_diff(diff, findings):
    current = "?"
    added = {}
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[4:].strip()
            if current.startswith("b/"):
                current = current[2:]
        elif line.startswith("+") and not line.startswith("+++"):
            added.setdefault(current, []).append(line[1:])
    for path, lines in added.items():
        scan_text("\n".join(lines), path, findings)


def scan_for_secrets(cwd, include_worktree):
    findings = []
    rc, diff = git(["diff", "--cached", "--no-color", "--no-ext-diff", "-U0"], cwd, timeout=20)
    if rc == 0:
        scan_diff(diff, findings)
    if include_worktree:
        rc, diff = git(["diff", "--no-color", "--no-ext-diff", "-U0"], cwd, timeout=20)
        if rc == 0:
            scan_diff(diff, findings)
        rc, out = git(["ls-files", "--others", "--exclude-standard", "-z"], cwd, timeout=20)
        if rc == 0:
            for rel in [p for p in out.split("\0") if p][:2000]:
                path = os.path.join(cwd, rel)
                try:
                    if os.path.getsize(path) > MAX_FILE_BYTES:
                        continue
                    with open(path, "rb") as f:
                        data = f.read()
                except OSError:
                    continue
                if b"\0" in data[:8192]:
                    continue
                scan_text(data.decode("utf-8", "replace"), rel, findings)
    return sorted(set(findings))


# ------------------------------------------------------------------ main
def main(payload, proj, ctx):
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not re.search(r"\bgit\b|\bgh\b", command):
        nova.allow()
    base = nova.session_cwd(payload, proj)
    bodies = shell.heredoc_bodies(command)
    purge_ok = None
    staged_by_command = False
    warnings = []
    for seg in shell.segments(command, base):
        if seg.name == "gh":
            change = gh_change(seg.argv)
            if change:
                nova.STATE.locked = True
                nova.block("%s is not allowed: the Nova repo stays private and no collaborators are added "
                           "(N9). If the user wants this, they change it themselves in GitHub." % change)
            continue
        if seg.name != "git":
            continue
        sub, args = shell.git_subcommand(seg.argv)
        cdir = shell.git_dir_option(seg.argv)
        cwd = os.path.normpath(os.path.join(seg.cwd, cdir)) if cdir else seg.cwd
        if sub == "add":
            staged_by_command = True

        identity = remote_change(sub, args)
        if identity:
            nova.STATE.locked = True
            nova.block("%s is not allowed: the origin remote identifies this Nova repo and must not "
                       "change (N8/N9). If the repo moved, tell the user; nova-health can help." % identity)
        deletion = ref_deletion(sub, args, cwd)
        if deletion:
            what, kind = deletion
            ok_update, _ = nova.valid_lock(proj, "update")
            ok_purge, _ = nova.valid_lock(proj, "purge")
            ok_purge = ok_purge and ctx == "chat"
            allowed = (kind == "tag" and (ok_update or ok_purge)) or (kind == "branch" and ok_purge)
            if not allowed:
                nova.STATE.locked = True
                nova.block("%s deletes history references, which Nova never does (N8)%s." % (
                    what, ": tags may only be removed by nova-update (update lock) or a confirmed purge "
                          "(purge lock, chat)" if kind == "tag" else
                    ": only a user-confirmed purge in a chat may delete branches that exist on origin"))
        reason = rewrite_reason(sub, args, cwd)
        if reason:
            if purge_ok is None:
                ok, why = nova.valid_lock(proj, "purge")
                if ok and ctx != "chat":
                    ok, why = False, "a purge lock only counts in a chat (NOVA_CONTEXT=chat)"
                purge_ok, purge_why = ok, why
            if not purge_ok:
                nova.STATE.locked = True
                nova.block("%s rewrites history, which Nova never does (N8). Undo changes with a forward "
                           "revert commit instead (system/rules/sync.md). The only exception is a "
                           "user-confirmed purge through nova-memory in a chat, while "
                           ".nova-tmp/purge.lock is valid (%s)." % (reason, purge_why))

        if sub == "commit":
            message, why = commit_message(args, cwd, bodies)
            if message is None:
                warnings.append("could not read the commit message (%s); make sure it has "
                                "Nova-Actor and Nova-Reason trailers" % why)
            else:
                check_trailers(message, ctx)
            include_wt = staged_by_command or "--" in args or any(
                a in ("-a", "--all", "--include", "-i", "--only", "-o") or
                (re.match(r"^-[a-zA-Z]+$", a) and "a" in a and not a.startswith("-m"))
                for a in args)
            found = scan_for_secrets(cwd, include_wt)
            if found:
                nova.STATE.locked = True
                nova.block("possible secrets in this commit (N10): %s. Remove them from the files "
                           "(store a pointer such as 'password kept in the user's password manager' "
                           "instead), unstage, and commit again. Never commit passwords, tokens or keys."
                           % "; ".join(found[:8]))
    nova.allow("; ".join(warnings) if warnings else None)


if __name__ == "__main__":
    try:
        nova.run("git", main)
    except SystemExit as _exit:
        if _exit.code in (0, 2, None):
            raise
        fail_safe("git", RuntimeError("unexpected exit code %r" % (_exit.code,)), _raw_stdin())
    except BaseException as _err:
        fail_safe("git", _err, _raw_stdin())
