#!/usr/bin/env python3
"""Phase 0, Check A: does this chat surface show a hook's "ask" prompt?

Asks for confirmation only for a shell command containing the word
"confirmprobe"; every other command runs normally. It also records the
session's permission mode in /tmp/hook-probe.log, so you can see it even
if no prompt appears.
"""
import json
import sys

try:
    payload = json.loads(sys.stdin.read() or "{}")
except ValueError:
    sys.exit(0)

command = (payload.get("tool_input") or {}).get("command") or ""
mode = payload.get("permission_mode", "unknown")
with open("/tmp/hook-probe.log", "a", encoding="utf-8") as log:
    log.write("permission_mode=%s command=%r\n" % (mode, command[:80]))

if "confirmprobe" in command:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "Hook probe: allow the test command? (permission mode: %s)" % mode,
    }}))
sys.exit(0)
