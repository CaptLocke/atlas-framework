#!/usr/bin/env python3
"""Nova hook: don't end a turn with changes stranded locally (Stop).

Claude Code contract relied on (https://code.claude.com/docs/en/hooks and
https://code.claude.com/docs/en/hooks-guide, checked 2026-10-12):
- Stop fires when Claude is about to end its turn; input = common fields plus
  `stop_hook_active` (true when Claude is already continuing because a Stop
  hook blocked) and `last_assistant_message`.
- To keep Claude working: exit 0 with JSON {"decision": "block", "reason":
  "..."} (the reason is given to Claude), or exit 2 with stderr. This hook
  uses the JSON form. Claude Code itself overrides a Stop hook after 8
  consecutive blocks; the guide says hooks should check `stop_hook_active`.
- `systemMessage` (universal JSON field) shows a warning to the user.

Behavior (system/rules/sync.md "after each logical change set"):
- No-op in the upstream product repo (same bypass as the other hooks), outside
  a git repo, or without an `origin` remote.
- Blocks the stop when (a) tracked files have uncommitted changes or there are
  untracked, non-ignored files (except .nova-tmp/ and user/inbox/drop/), or an
  unfinished rebase/merge, or (b) HEAD has commits origin/main doesn't (after
  the local `origin/main` tracking ref; no network call).
- Loop safety: when `stop_hook_active` is true, or this would be the 3rd
  consecutive block (counter in .nova-tmp/sync_guard.json, per session), the
  stop is allowed: an open high-severity known issue `sync-push-failing` is
  added to user/.state/health.yaml when that can be done safely, and the user
  sees a one-line warning. A clean stop resets the counter.
- Fails OPEN on any internal error (warning only), so it can never trap the
  user in an endless turn. Always exit 0.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

STATE = ".nova-tmp/sync_guard.json"
MAX_BLOCKS = 2          # the 3rd consecutive block is turned into an allowed stop
FETCH_TIMEOUT = 5
STALE_SECONDS = 3600
REASON = ("Unsaved Nova changes: commit (with Nova-Actor/Nova-Reason trailers) and push to origin main before "
          "finishing (system/rules/sync.md).")
USER_WARNING = ("Nova couldn't save your latest changes to GitHub. They are kept on this session's copy and "
                "will be retried; if this repeats, reconnect GitHub (Settings > Connectors) and ask Nova to "
                "\"save my changes\".")


def load_counter(proj, session):
    try:
        with open(os.path.join(proj, STATE), encoding="utf-8") as f:
            data = json.load(f)
        import time
        if data.get("session") != session or time.time() - float(data.get("at", 0)) > STALE_SECONDS:
            return 0
        return int(data.get("blocks", 0))
    except Exception:
        return 0


def save_counter(proj, session, blocks):
    import time
    try:
        os.makedirs(os.path.join(proj, ".nova-tmp"), exist_ok=True)
        path = os.path.join(proj, STATE)
        if blocks <= 0:
            if os.path.exists(path):
                os.remove(path)
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"session": session, "blocks": blocks, "at": time.time()}, f)
    except Exception:
        pass


def problems(gs, proj):
    """List of human-readable problems, [] when everything is saved."""
    out = []
    op = gs.operation_in_progress(proj)
    if op:
        out.append("an unfinished git %s (finish or abort it)" % op)
    paths = gs.unsaved_paths(proj)
    if paths is None:
        out.append("git status failed")
    elif paths:
        out.append("%d uncommitted file(s): %s%s" % (len(paths), ", ".join(paths[:5]),
                                                     ", ..." if len(paths) > 5 else ""))
    # No network call: commits ahead of the local origin/main tracking ref (updated by every
    # successful push or pull) are unpushed by definition, so the check stays instant.
    n = gs.unpushed_count(proj)
    if n:
        out.append("%d commit(s) not pushed to origin/%s" % (n, gs.BRANCH))
    return out


def give_up(gs, proj, session, found):
    save_counter(proj, session, 0)
    gs.log(proj, "sync_guard.gave_up", "; ".join(found))
    recorded = False
    try:
        recorded = gs.health_issue(
            proj, "sync-push-failing",
            "Latest changes could not be saved to GitHub",
            "Reconnect GitHub (Settings > Connectors), then ask Nova to save changes")
    except Exception:
        recorded = False
    msg = USER_WARNING + ("" if recorded else " (Nova could not record this as a known issue.)")
    return {"systemMessage": msg}


def main():
    import gitsync as gs
    payload = gs.read_payload(sys.stdin)
    proj = gs.project_dir(payload)
    if gs.is_upstream(proj) or not gs.is_git_repo(proj) or not gs.has_origin(proj):
        return None
    session = str(payload.get("session_id") or "")
    found = problems(gs, proj)
    if not found:
        save_counter(proj, session, 0)
        return None
    blocks = load_counter(proj, session)
    if payload.get("stop_hook_active") is True or blocks >= MAX_BLOCKS:
        return give_up(gs, proj, session, found)
    save_counter(proj, session, blocks + 1)
    gs.log(proj, "sync_guard.block", "; ".join(found))
    return {"decision": "block", "reason": "%s Found: %s." % (REASON, "; ".join(found))}


if __name__ == "__main__":
    try:
        out = main()
        if out:
            sys.stdout.write(json.dumps(out))
    except BaseException as e:  # fail open, with a warning
        try:
            sys.stdout.write(json.dumps({"systemMessage": "Nova sync check could not run (%s: %s); make sure "
                                         "your latest changes were saved to GitHub." % (type(e).__name__, e)}))
        except BaseException:
            pass
    sys.stdout.flush()
    os._exit(0)
