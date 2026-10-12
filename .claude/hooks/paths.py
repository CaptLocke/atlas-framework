#!/usr/bin/env python3
"""Nova hook: protected paths, N5 and N6 (build plan H-4).

Registered in .claude/settings.json as a PreToolUse hook for file tools
(matcher "Write|Edit|MultiEdit|NotebookEdit") and shell commands
(matcher "Bash|Monitor").

Claude Code contract relied on (https://code.claude.com/docs/en/hooks and
https://code.claude.com/docs/en/tools-reference, checked 2026-10-12): stdin
JSON with tool_name / tool_input / cwd; file tools carry the target in
tool_input.file_path (NotebookEdit: notebook_path); Bash carries
tool_input.command; exit 2 + stderr blocks and the message goes to Claude;
$CLAUDE_PROJECT_DIR is the project root. Shared policy: context.py.

What it enforces (system/rules/governance.md, system/schemas/formats.md s2):
- N5: writes to system/manifest.yaml owned_paths only while
  .nova-tmp/update.lock exists and is unexpired (any context).
- N6: writes to user/settings/{governance,data-rules,connectors}.yaml are
  blocked in routines; in chats they need an approval record with action
  governance_settings for this exact tool whose target is the file's
  repo-relative path, consumed on use. Creating a governance file that does
  not exist yet (nova-setup copying the defaults) is allowed in any context
  without a record; a leftover record naming that path is deleted.
- Approval records and purge locks can't be created in routines (they are
  chat-only by definition); nothing writes inside .git/.
Bash detection is pragmatic (see shell.py for what is and isn't detected).
"""
import os
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


sys.excepthook = lambda _t, _e, _tb: fail_safe("paths", _e, _raw_stdin())
try:
    import context as nova  # noqa: E402
    import shell  # noqa: E402
except BaseException as _imp:  # includes SystemExit raised while importing
    fail_safe("paths", _imp, _raw_stdin())

FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def file_targets(payload):
    ti = payload.get("tool_input") or {}
    out = []
    for key in ("file_path", "notebook_path", "path"):
        v = ti.get(key)
        if isinstance(v, str) and v:
            out.append(v)
    return out


def bash_targets(payload, proj):
    """[(word, cwd, 'write'|'delete')] of paths a shell command may change."""
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return []
    base = nova.session_cwd(payload, proj)
    out = []
    for seg in shell.segments(command, base):
        writes, deletes = shell.write_targets(seg)
        sources = shell.copy_sources(seg)
        if sources and writes:
            dest = writes[-1]
            dpath = os.path.join(seg.cwd, os.path.expanduser(dest))
            if dest.endswith("/") or os.path.isdir(dpath):
                writes = writes[:-1] + [os.path.join(dest, os.path.basename(src.rstrip("/")) or src)
                                        for src in sources]
        for kind, words in (("write", writes), ("delete", deletes)):
            for w in words:
                if shell.unresolvable(w):
                    continue
                out.append((shell.literal_prefix(w) if shell.has_glob(w) else w, seg.cwd, kind))
    return out


def check(rels, tool_name, proj, ctx):
    owned = nova.owned_paths(proj)
    owned_hits, gov_hits, tmp_hits, git_hits = [], [], [], []
    for rel, kind in rels:
        if rel == ".git" or rel.startswith(".git/"):
            git_hits.append(rel)
        if any(nova.overlaps(rel, e) for e in owned):
            owned_hits.append(rel or ".")
        # a write names the file it changes; a delete of a parent folder also
        # removes the governance files inside it
        if (rel in nova.GOVERNANCE_FILES) or (kind == "delete" and any(
                nova.overlaps(rel, g) for g in nova.GOVERNANCE_FILES)):
            gov_hits.append(rel or ".")
        if kind == "write" and rel in (nova.APPROVAL, nova.PURGE_LOCK):
            tmp_hits.append(rel)

    if git_hits:
        nova.block("Writing inside .git/ (%s) is not allowed; use git commands, and never change "
                   "the repo's remotes or history (N8)." % ", ".join(sorted(set(git_hits))))

    if tmp_hits and ctx != "chat":
        nova.block("Approval records and purge locks can only be created in a chat with the user "
                   "(%s). In a routine, queue the action in user/inbox/approvals.md instead."
                   % ", ".join(sorted(set(tmp_hits))))

    if owned_hits:
        ok, why = nova.valid_lock(proj, "update")
        if not ok:
            nova.block("%s %s system-owned (system/manifest.yaml: owned_paths) and only change through "
                       "nova-update while .nova-tmp/update.lock is valid (N5): %s. Put user changes in "
                       "user/ (extensions go in user/extensions/ via nova-extend). If a system file looks "
                       "broken, record it for nova-health / nova-update instead of editing it."
                       % (", ".join(sorted(set(owned_hits))[:5]),
                          "is" if len(set(owned_hits)) == 1 else "are", why))

    if gov_hits:
        files = ", ".join(sorted(set(gov_hits)))
        affected = [g for g in nova.GOVERNANCE_FILES
                    if any(nova.overlaps(h if h != "." else "", g) for h in gov_hits)]
        existing = [g for g in affected if os.path.exists(os.path.join(proj, g))]
        if not existing:
            # First creation (nova-setup copying the defaults) is allowed in any
            # context; never leave a record behind that names these paths.
            nova.discard_stale_approval(proj, set(affected))
            nova.allow()
        nova.STATE.locked = True
        if ctx != "chat":
            nova.block("%s can only change in a chat, after the user explicitly confirms (N6). This is a "
                       "routine (NOVA_CONTEXT=routine): queue the proposed change in "
                       "user/inbox/approvals.md instead." % files)
        rec, why = nova.approval_matches(proj, tool_name, {"governance_settings"}, targets=set(existing))
        if rec is None:
            nova.block("%s is protected (N6) and needs an approval record: %s. Locked action: state the "
                       "exact change, get the user's explicit yes, then write .nova-tmp/approval.json with "
                       "action 'governance_settings', tool '%s' and target '%s' (system/schemas/formats.md "
                       "section 2; system/rules/governance.md) and retry."
                       % (files, why, tool_name, existing[0]))
        nova.consume_approval(proj)
    nova.allow()


def main(payload, proj, ctx):
    tool_name = payload.get("tool_name") or ""
    rels = []
    if tool_name in FILE_TOOLS:
        base = nova.session_cwd(payload, proj)
        for p in file_targets(payload):
            rel = nova.rel_to_project(p, base, proj)
            if rel is not None:
                rels.append((rel, "write"))
    elif tool_name in ("Bash", "Monitor"):
        for word, cwd, kind in bash_targets(payload, proj):
            rel = nova.rel_to_project(word, cwd, proj)
            if rel is not None:
                rels.append((rel, kind))
    if rels:
        check(rels, tool_name, proj, ctx)
    nova.allow()


if __name__ == "__main__":
    try:
        nova.run("paths", main)
    except SystemExit as _exit:
        if _exit.code in (0, 2, None):
            raise
        fail_safe("paths", RuntimeError("unexpected exit code %r" % (_exit.code,)), _raw_stdin())
    except BaseException as _err:
        fail_safe("paths", _err, _raw_stdin())
