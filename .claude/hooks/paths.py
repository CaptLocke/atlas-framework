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
- In routines (1.0.2): the update lock counts only for a signed release at or
  above the installed version (context.update_lock), owned paths change only
  from that release's ref, and `git rm` removes only owned files that release
  doesn't have. Writes outside the repo go only to temp folders (M4); paths
  with variables are refused; `company` in user/settings/atlas.yaml (it
  decides which sites routines may reach) can't change (M1), nor can the
  page links in user/settings/dashboards.yaml (they decide which pages
  routines may write to, N9; actions.py handle_artifact); and shell
  redirects can't overwrite existing files under user/ (L2: use Write/Edit).
- In any context: files Claude Code or git load as instructions, servers or
  hooks (CLAUDE.md, CLAUDE.local.md, AGENTS.md, .mcp.json, .gitattributes,
  .gitmodules, .githooks/, nested .claude/) are never written, except the
  owned ones (root CLAUDE.md, .gitattributes) by a signed update under the
  lock, and the routine session markers are never written or deleted (H3, M3).
Bash detection is pragmatic (see shell.py for what is and isn't detected).
"""
import os
import re
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
ATLAS_YAML = "user/settings/atlas.yaml"
EXEMPT_OVERWRITE = ("user/inbox/drop/", "user/knowledge/_index/")


def file_targets(payload):
    ti = payload.get("tool_input") or {}
    out = []
    for key in ("file_path", "notebook_path", "path"):
        v = ti.get(key)
        if isinstance(v, str) and v:
            out.append(v)
    return out


HEAD_SOURCES = ("HEAD", "@")
INDEX_READS = ("--ours", "--theirs", "-m", "--merge", "--conflict", "-p", "--patch")


def git_source(seg):
    """For git checkout/restore/rm segments: 'head' (restore from an explicitly
    named HEAD), 'update:<ref>' (needs the update lock and an allowed ref; ''
    means the index, which is never an allowed source), or 'rm' (git rm, needs
    the update lock). None for any other command."""
    if seg.name != "git":
        return None
    sub, sargs = shell.git_subcommand(seg.argv)
    if sub == "rm":
        return "rm"
    index_read = any(a in INDEX_READS or a.startswith("--conflict=") for a in sargs)
    if sub == "checkout" and "--" in sargs:
        before = shell.positional(["git"] + sargs[:sargs.index("--")])
        ref = before[0] if before else ""
    elif sub == "restore":
        ref = shell.option_value(["git"] + sargs, "-s", "--source") or ""
    else:
        return None
    return "head" if ref in HEAD_SOURCES and not index_read else "update:" + ref


def bash_targets(payload, proj, ctx="chat"):
    """[(word, cwd, 'write'|'overwrite'|'delete', git_source)] of paths a shell command may change.
    'overwrite' is a write that truncates an existing file (>, tee without -a)."""
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return []
    base = atlas.session_cwd(payload, proj)
    out = []
    for seg in shell.segments(command, base):
        writes, deletes = shell.write_targets(seg)
        overwrites = set(seg.overwrites)
        if seg.name == "tee" and not any(a in ("-a", "--append") or re.match(r"^-[a-zA-Z]*a", a)
                                          for a in seg.argv[1:]):
            overwrites |= set(shell.positional(seg.argv))
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
                    if ctx != "chat":
                        atlas.block("This command %ss %s, a path built from a variable or command, which a "
                                    "routine can't check. Write the path out in full." % (
                                        "delete" if kind == "delete" else "write", w))
                    continue
                # a glob with no literal folder ('sys*') may match anything in its folder
                word = (shell.literal_prefix(w) or ".") if shell.has_glob(w) else w
                k = "overwrite" if kind == "write" and w in overwrites else kind
                out.append((word, seg.cwd, k, via))
    return out


def update_source_ok(proj, via, ctx, rel):
    """May this git operation change owned path 'rel' under a valid update lock?
    Returns (ok, lock_reason)."""
    ok, why, release = atlas.update_lock(proj, ctx)
    if not ok:
        return False, why
    if ctx != "chat":
        # routines: only the signed release named by the lock, and git rm only of
        # files that release doesn't have
        if via == "rm":
            return not atlas.in_tree(proj, release, rel), "%s still has %s" % (release, rel or ".")
        ref = via[len("update:"):] if via and via.startswith("update:") else ""
        return bool(ref) and atlas.full_ref_name(proj, ref) == release, \
            "a routine installs system files only from %s, the release named in the update lock" % release
    if via == "rm":
        return True, ""
    ref = via[len("update:"):] if via and via.startswith("update:") else None
    if not ref:
        return False, "the index is never a source for system files"
    full = atlas.full_ref_name(proj, ref)
    if full.startswith("refs/atlas-upstream/"):
        return atlas.release_verified(proj, full), "%s isn't signed by Atlas's maker" % full
    return atlas.in_history(proj, ref), "%s isn't in this repo's history" % ref


def company(text, proj):
    """The 'company' block of an atlas.yaml text (None when absent); raises on bad YAML."""
    data = atlas.load_yaml_text(text, proj) or {}
    return data.get("company") if isinstance(data, dict) else None


def page_links(text, proj):
    """The page URLs in a dashboards.yaml text, and which pages are live; raises on bad YAML."""
    data = atlas.load_yaml_text(text, proj) or {}
    pages = data.get("dashboards") if isinstance(data, dict) else None
    live = sorted(k for k, v in (pages or {}).items() if isinstance(v, dict) and v.get("live")) if isinstance(pages, dict) else []
    return atlas.page_urls(data), live


# Settings a routine may edit except for one part, which decides what routines may reach:
# 'company' sets the sites they open (M1); the page links set the artifacts they write (N9).
FIXED_IN_ROUTINES = {
    ATLAS_YAML: (company, "'company' in user/settings/atlas.yaml decides which sites routines may reach, "
                          "so only a chat with the user changes it."),
    atlas.DASHBOARDS_YAML: (page_links, "The page links and live flags in user/settings/dashboards.yaml decide "
                                        "which pages routines may write to and how, so only a chat changes them."),
}


def fixed_part_change(payload, proj, rel):
    """Why this file-tool edit of a FIXED_IN_ROUTINES file isn't allowed in a routine, or None."""
    part, what = FIXED_IN_ROUTINES[rel]
    path = os.path.join(proj, rel)
    try:
        with open(path, encoding="utf-8") as f:
            before = f.read()
    except OSError:
        before = ""
    ti = payload.get("tool_input") or {}
    tool = payload.get("tool_name")
    after = before
    if tool == "Write":
        after = str(ti.get("content") or "")
    else:
        edits = ti.get("edits") if tool == "MultiEdit" else [ti]
        for e in edits or []:
            old, new = str(e.get("old_string") or ""), str(e.get("new_string") or "")
            if old and old in after:
                after = after.replace(old, new) if e.get("replace_all") else after.replace(old, new, 1)
    try:
        same = part(before, proj) == part(after, proj)
    except Exception:
        return "the new %s isn't valid YAML" % rel
    if not same:
        return "%s Queue the change in user/inbox/approvals.md instead." % what
    return None


def check(rels, tool_name, proj, ctx, payload):
    owned = atlas.owned_paths(proj)
    owned_hits, gov_hits, tmp_hits, git_hits, load_hits, user_overwrites = [], [], [], [], [], []
    owned_why = ""
    for rel, kind, via in rels:
        r = rel.rstrip("/")
        if rel == ".git" or rel.startswith(".git/"):
            git_hits.append(rel)
        if rel == atlas.MAINTAINER_MARKER:
            atlas.block("%s marks the maintainer's own copy of Atlas's source repo and switches the guards off "
                       "there; Atlas never creates, changes or removes it." % rel)
        is_owned = any(atlas.overlaps(rel, e) for e in owned)
        if is_owned:
            if via == "head":
                pass  # restoring committed content never introduces anything new
            elif via is not None:
                ok, why = update_source_ok(proj, via, ctx, rel)
                if not ok:
                    owned_hits.append(rel or ".")
                    owned_why = owned_why or why
            else:
                owned_hits.append(rel or ".")
        marker = r == atlas.ROUTINE_SESSIONS or r.startswith(atlas.ROUTINE_SESSIONS + "/") or (
            kind == "delete" and r and atlas.ROUTINE_SESSIONS.startswith(r + "/"))
        # an owned auto-loaded file (.gitattributes) is left to the owned-path rule above: only a
        # signed update writes it
        if marker or (kind != "delete" and atlas.autoload_path(rel) and not is_owned):
            load_hits.append(rel or ".")
        # a write names the file it changes; a delete of a parent folder also
        # removes the governance files inside it
        if (rel in atlas.GOVERNANCE_FILES) or (kind == "delete" and any(
                atlas.overlaps(rel, g) for g in atlas.GOVERNANCE_FILES)):
            gov_hits.append(rel or ".")
        if kind != "delete" and rel in (atlas.APPROVAL, atlas.PURGE_LOCK):
            tmp_hits.append(rel)
        if ctx != "chat" and rel in FIXED_IN_ROUTINES and kind != "delete":
            # fixed_part_change can replay Write, Edit and MultiEdit only
            why = fixed_part_change(payload, proj, rel) if tool_name in ("Write", "Edit", "MultiEdit") else (
                "Change %s with the Edit tool in a routine." % rel)
            if why:
                atlas.STATE.locked = True
                atlas.block(why)
        if (ctx != "chat" and kind == "overwrite" and rel.startswith("user/") and not rel.startswith(EXEMPT_OVERWRITE)
                and os.path.isfile(os.path.join(proj, rel))):
            user_overwrites.append(rel)

    if git_hits:
        atlas.block("Writing inside .git/ (%s) is not allowed; use git commands, and never change "
                   "the repo's remotes or history (N8)." % ", ".join(sorted(set(git_hits))))

    if load_hits:
        atlas.STATE.locked = True
        atlas.block("%s: Atlas never creates or changes files that Claude Code or git load as instructions, "
                    "servers or hooks (CLAUDE.md, CLAUDE.local.md, AGENTS.md, .mcp.json, .gitattributes, "
                    ".gitmodules, .githooks/, .claude/ folders), and never touches the routine session "
                    "markers in .atlas-tmp/routine-sessions/." % ", ".join(sorted(set(load_hits))[:5]))

    if tmp_hits and ctx != "chat":
        atlas.block("Approval records and purge locks can only be created in a chat with the user "
                   "(%s). In a routine, queue the action in user/inbox/approvals.md instead."
                   % ", ".join(sorted(set(tmp_hits))))

    if owned_hits:
        atlas.STATE.locked = True
        atlas.block("%s %s system-owned (system/manifest.yaml: owned_paths) and never change by editing "
                   "(N5). Only atlas-update changes them, with `git checkout` from a fetched, signed release "
                   "and `git rm`, while .atlas-tmp/update.lock is valid%s. Put user changes in user/ "
                   "(extensions go in user/extensions/ via atlas-extend). If a system file looks broken, "
                   "record it for atlas-health, which can restore it."
                   % (", ".join(sorted(set(owned_hits))[:5]),
                      "is" if len(set(owned_hits)) == 1 else "are",
                      " (here: %s)" % owned_why if owned_why else ""))

    if user_overwrites:
        atlas.block("In a routine the shell doesn't overwrite existing files under user/ (%s): use the Edit or "
                    "Write tool, so every change to a record is a visible edit. Appending with >> is fine."
                    % ", ".join(sorted(set(user_overwrites))[:5]))

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
    rels, outside = [], []
    if tool_name in FILE_TOOLS:
        base = atlas.session_cwd(payload, proj)
        for p in file_targets(payload):
            rel = atlas.rel_to_project(p, base, proj)
            if rel is not None:
                rels.append((rel, "write", None))
            else:
                outside.append(os.path.join(base, os.path.expanduser(p)))
    elif tool_name in ("Bash", "Monitor"):
        for word, cwd, kind, via in bash_targets(payload, proj, ctx):
            rel = atlas.rel_to_project(word, cwd, proj)
            if rel is not None:
                rels.append((rel, kind, via))
            else:
                outside.append(os.path.join(cwd, os.path.expanduser(word)))
    if ctx != "chat":
        bad = [p for p in outside if not atlas.outside_write_ok(p)]
        if bad:
            atlas.STATE.locked = True
            atlas.block("A routine writes only inside the Atlas repo and in temp folders (/tmp), not %s (M4). "
                        "Use a path in the repo or under /tmp." % ", ".join(sorted(set(bad))[:3]))
    if rels:
        check(rels, tool_name, proj, ctx, payload)
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
