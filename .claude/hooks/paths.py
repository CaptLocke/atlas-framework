#!/usr/bin/env python3
"""Atlas hook: protected paths, N5 and N6.

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
- N5: owned paths (system/manifest.yaml owned_paths) are never written by
  file tools or ordinary shell commands, in any context. The only changes
  allowed are git's own: restoring from HEAD or the index (any time), and,
  while .atlas-tmp/update.lock is valid, `git checkout <src> -- <path>` from
  a fetched release ref (refs/atlas-upstream/*) or a commit already in this
  repo's history, and `git rm`. That is all atlas-update needs.
- N6: writes to user/settings/{governance,data-rules,connectors}.yaml are
  blocked in routines; in chats they need an approval record with action
  governance_settings for this exact tool whose target is the file's
  repo-relative path, consumed on use. Creating a governance file that does
  not exist yet (atlas-setup copying the defaults) is allowed in any context
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
            sys.stderr.write("Atlas guard (%s): hook files are damaged (%s; %s); blocked.\n" % (hook, exc, _fe))
        finally:
            os._exit(2)


def _raw_stdin():
    mod = sys.modules.get("context")
    return getattr(getattr(mod, "STATE", None), "raw", None)


sys.excepthook = lambda _t, _e, _tb: fail_safe("paths", _e, _raw_stdin())
try:
    import context as atlas  # noqa: E402
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


HEAD_SOURCES = ("", "HEAD", "@")


def git_source(seg):
    """For git checkout/restore/rm segments: 'head' (restore from HEAD or the
    index), 'update:<ref>' (needs the update lock and an allowed ref), or
    'rm' (git rm, needs the update lock). None for any other command."""
    if seg.name != "git":
        return None
    sub, sargs = shell.git_subcommand(seg.argv)
    if sub == "rm":
        return "rm"
    if sub == "checkout" and "--" in sargs:
        before = shell.positional(["git"] + sargs[:sargs.index("--")])
        ref = before[0] if before else ""
        return "head" if ref in HEAD_SOURCES else "update:" + ref
    if sub == "restore":
        ref = shell.option_value(["git"] + sargs, "-s", "--source") or ""
        return "head" if ref in HEAD_SOURCES else "update:" + ref
    return None


def bash_targets(payload, proj):
    """[(word, cwd, 'write'|'delete', git_source)] of paths a shell command may change."""
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return []
    base = atlas.session_cwd(payload, proj)
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
        via = git_source(seg)
        for kind, words in (("write", writes), ("delete", deletes)):
            for w in words:
                if shell.unresolvable(w):
                    continue
                out.append((shell.literal_prefix(w) if shell.has_glob(w) else w, seg.cwd, kind, via))
    return out


def update_source_ok(proj, via):
    """May this git operation change owned paths under a valid update lock?"""
    if via == "rm":
        return True
    ref = via[len("update:"):] if via and via.startswith("update:") else None
    if not ref:
        return False
    if ref.startswith("refs/atlas-upstream/"):
        return True
    return atlas.in_history(proj, ref)


def check(rels, tool_name, proj, ctx):
    owned = atlas.owned_paths(proj)
    owned_hits, gov_hits, tmp_hits, git_hits = [], [], [], []
    update_ok = None
    for rel, kind, via in rels:
        if rel == ".git" or rel.startswith(".git/"):
            git_hits.append(rel)
        if any(atlas.overlaps(rel, e) for e in owned):
            if via == "head":
                pass  # restoring committed content never introduces anything new
            elif via is not None and update_source_ok(proj, via):
                if update_ok is None:
                    update_ok = atlas.valid_lock(proj, "update")
                if not update_ok[0]:
                    owned_hits.append(rel or ".")
            else:
                owned_hits.append(rel or ".")
        # a write names the file it changes; a delete of a parent folder also
        # removes the governance files inside it
        if (rel in atlas.GOVERNANCE_FILES) or (kind == "delete" and any(
                atlas.overlaps(rel, g) for g in atlas.GOVERNANCE_FILES)):
            gov_hits.append(rel or ".")
        if kind == "write" and rel in (atlas.APPROVAL, atlas.PURGE_LOCK):
            tmp_hits.append(rel)

    if git_hits:
        atlas.block("Writing inside .git/ (%s) is not allowed; use git commands, and never change "
                   "the repo's remotes or history (N8)." % ", ".join(sorted(set(git_hits))))

    if tmp_hits and ctx != "chat":
        atlas.block("Approval records and purge locks can only be created in a chat with the user "
                   "(%s). In a routine, queue the action in user/inbox/approvals.md instead."
                   % ", ".join(sorted(set(tmp_hits))))

    if owned_hits:
        atlas.STATE.locked = True
        atlas.block("%s %s system-owned (system/manifest.yaml: owned_paths) and never change by editing "
                   "(N5). Only atlas-update changes them, with `git checkout` from a fetched release and "
                   "`git rm`, while .atlas-tmp/update.lock is valid. Put user changes in user/ (extensions "
                   "go in user/extensions/ via atlas-extend). If a system file looks broken, record it for "
                   "atlas-health, which can restore it."
                   % (", ".join(sorted(set(owned_hits))[:5]),
                      "is" if len(set(owned_hits)) == 1 else "are"))

    if gov_hits:
        files = ", ".join(sorted(set(gov_hits)))
        affected = [g for g in atlas.GOVERNANCE_FILES
                    if any(atlas.overlaps(h if h != "." else "", g) for h in gov_hits)]
        existing = [g for g in affected if os.path.exists(os.path.join(proj, g))]
        if not existing:
            # First creation (atlas-setup copying the defaults) is allowed in any
            # context; never leave a record behind that names these paths.
            atlas.discard_stale_approval(proj, set(affected))
            atlas.allow()
        atlas.STATE.locked = True
        if ctx != "chat":
            atlas.block("%s can only change in a chat, after the user explicitly confirms (N6). This is a "
                       "routine (ATLAS_CONTEXT=routine): queue the proposed change in "
                       "user/inbox/approvals.md instead." % files)
        rec, why = atlas.approval_matches(proj, tool_name, {"governance_settings"}, targets=set(existing))
        if rec is None:
            atlas.block("%s is protected (N6) and needs an approval record: %s. Locked action: state the "
                       "exact change, get the user's explicit yes, then write .atlas-tmp/approval.json with "
                       "action 'governance_settings', tool '%s' and target '%s' (system/schemas/formats.md "
                       "section 2; system/rules/governance.md) and retry."
                       % (files, why, tool_name, existing[0]))
        atlas.consume_approval(proj)
    atlas.allow()


def main(payload, proj, ctx):
    tool_name = payload.get("tool_name") or ""
    rels = []
    if tool_name in FILE_TOOLS:
        base = atlas.session_cwd(payload, proj)
        for p in file_targets(payload):
            rel = atlas.rel_to_project(p, base, proj)
            if rel is not None:
                rels.append((rel, "write", None))
    elif tool_name in ("Bash", "Monitor"):
        for word, cwd, kind, via in bash_targets(payload, proj):
            rel = atlas.rel_to_project(word, cwd, proj)
            if rel is not None:
                rels.append((rel, kind, via))
    if rels:
        check(rels, tool_name, proj, ctx)
    atlas.allow()


if __name__ == "__main__":
    try:
        atlas.run("paths", main)
    except SystemExit as _exit:
        if _exit.code in (0, 2, None):
            raise
        fail_safe("paths", RuntimeError("unexpected exit code %r" % (_exit.code,)), _raw_stdin())
    except BaseException as _err:
        fail_safe("paths", _err, _raw_stdin())
