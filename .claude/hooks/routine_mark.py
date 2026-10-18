#!/usr/bin/env python3
"""Atlas hook: mark a session that starts as an Atlas routine (UserPromptSubmit).

Claude Code contract relied on (https://code.claude.com/docs/en/hooks): a
UserPromptSubmit command hook gets the common fields (session_id, cwd, ...)
plus `prompt`; exit 0 with no output lets the prompt through unchanged.

Routines are meant to run in the "Atlas routine" environment, which sets
ATLAS_CONTEXT=routine. If a routine is attached to another environment, the
variable is missing and the other hooks would treat the session as a chat.
So when a prompt asks to "Run the Atlas routine ...", this hook records the
session in .atlas-tmp/routine-sessions/ (context.routine_mark_path), and the
other hooks apply routine rules for the rest of the session. No tool may
write or delete those markers (paths.py). The prompt itself is only that one
phrase: the run checks ATLAS_CONTEXT and raises `routine-env-missing` at step 0
of system/jobs/README.md section Running a routine (kernel section 6).

Never blocks and never fails the prompt: any error just leaves no marker.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROUTINE_PROMPT = re.compile(r"\brun the atlas routine\b", re.I)


def main():
    import json
    import context as atlas
    payload = json.loads(sys.stdin.read() or "{}")
    if not isinstance(payload, dict) or not ROUTINE_PROMPT.search(str(payload.get("prompt") or "")):
        return
    proj = atlas.project_dir(payload)
    if atlas.is_upstream(proj):
        return
    path = atlas.routine_mark_path(proj, payload.get("session_id"))
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("routine session (no ATLAS_CONTEXT=routine needed)\n")


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        pass
    os._exit(0)
