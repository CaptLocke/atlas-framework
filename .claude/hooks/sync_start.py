#!/usr/bin/env python3
"""Nova hook: pull the latest repo state at session start (SessionStart).

Claude Code contract relied on (https://code.claude.com/docs/en/hooks and
https://code.claude.com/docs/en/hooks-guide, checked 2026-10-12):
- SessionStart fires when a session begins or resumes; input = common fields
  (session_id, transcript_path, cwd, hook_event_name, ...) plus `source`
  (startup | resume | clear | compact | fork), which is also the matcher.
- It cannot block (exit 2 only shows stderr to the user). Context for Claude
  is added through stdout: JSON hookSpecificOutput.additionalContext (used
  here) or plain text.
- $CLAUDE_PROJECT_DIR is the project root.

Behavior (system/rules/sync.md "Session start"):
- No-op in the upstream product repo (same bypass as the other hooks) and
  outside a git repo with an `origin` remote.
- `git fetch origin` then `git pull --rebase --autostash origin main` (about
  20 s budget, never prompts for credentials). A rebase that stops on a
  conflict is aborted so the working tree is left as it was.
- Write check: `git push --dry-run origin HEAD:main` (no effect; it only asks
  the remote whether this session may push). Sessions can come up with a
  read-only attachment; if the dry run is refused, the context tells Claude
  to re-attach the repo with write access before anything else (kernel §2.1).
- Success: additional context "Nova repo synced to origin/main at <sha>".
- Failure (network, auth, conflict, not on main): additional context telling
  Claude to retry the pull before reading or writing Nova files; the reason is
  logged to .nova-tmp/sync.log. Never blocks, never crashes, always exit 0.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FETCH_TIMEOUT = 8
PULL_TIMEOUT = 12
PUSH_CHECK_TIMEOUT = 8


def context(text):
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}


def failure(gs, proj, reason):
    gs.log(proj, "sync_start.failed", reason)
    return context(
        "Nova sync at session start FAILED (%s). Before reading or writing any Nova file, retry: "
        "`git pull --rebase` on main (system/rules/sync.md); resolve conflicts as that rule says. If it "
        "keeps failing, keep working, record a known issue in user/.state/health.yaml, and tell the user in "
        "one line (usually: reconnect GitHub)." % gs.one_line(reason, 200))


def main():
    import gitsync as gs
    payload = gs.read_payload(sys.stdin)
    proj = gs.project_dir(payload)
    if gs.is_upstream(proj) or not gs.is_git_repo(proj) or not gs.has_origin(proj):
        return None
    branch = gs.current_branch(proj)
    if branch != gs.BRANCH:
        return failure(gs, proj, "the repo is on %r, not %s" % (branch or "a detached HEAD", gs.BRANCH))
    if gs.operation_in_progress(proj):
        return failure(gs, proj, "an unfinished %s is in progress" % gs.operation_in_progress(proj))
    rc, _, err = gs.git(proj, ["fetch", "--quiet", "origin"], timeout=FETCH_TIMEOUT)
    if rc != 0:
        return failure(gs, proj, "git fetch failed: %s" % (err.strip() or "exit %d" % rc))
    rc, out, err = gs.git(proj, ["pull", "--rebase", "--autostash", "--quiet", "origin", gs.BRANCH],
                          timeout=PULL_TIMEOUT)
    if rc != 0:
        if gs.operation_in_progress(proj) == "rebase":
            gs.git(proj, ["rebase", "--abort"], timeout=10)
        return failure(gs, proj, "git pull --rebase failed: %s" % ((err or out).strip() or "exit %d" % rc))
    sha = gs.short_sha(proj)
    rc, out, err = gs.git(proj, ["push", "--dry-run", "--quiet", "origin", "HEAD:" + gs.BRANCH],
                          timeout=PUSH_CHECK_TIMEOUT)
    if rc != 0:
        reason = (err or out).strip() or "exit %d" % rc
        gs.log(proj, "sync_start.read_only", reason)
        return context(
            "Nova repo synced to origin/%s at %s, but this session CAN'T PUSH to it (%s). It is probably "
            "attached read-only. Before reading or writing Nova files, re-attach the repository with write "
            "(push) access and clone it again (kernel §2 step 1). If write access is refused, tell the user in "
            "one line: give the Claude GitHub App write access to this repository (GitHub → Settings → "
            "Applications → Claude → Configure), then start a new chat." % (gs.BRANCH, sha, gs.one_line(reason, 160)))
    gs.log(proj, "sync_start.ok", "origin/%s at %s (push ok)" % (gs.BRANCH, sha))
    return context("Nova repo synced to origin/%s at %s; push access confirmed." % (gs.BRANCH, sha))


if __name__ == "__main__":
    try:
        out = main()
        if out:
            import json
            sys.stdout.write(json.dumps(out))
    except BaseException as e:  # never crash, never block
        try:
            import json
            sys.stdout.write(json.dumps(context(
                "Nova sync hook could not run (%s: %s). Pull the repo yourself (`git pull --rebase` on main, "
                "system/rules/sync.md) before reading or writing Nova files." % (type(e).__name__, e))))
        except BaseException:
            pass
    sys.stdout.flush()
    os._exit(0)
