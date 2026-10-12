#!/usr/bin/env python3
"""Nova hook: locked external actions, N1-N4 (build plan H-3).

Registered in .claude/settings.json as a PreToolUse hook for MCP tools
(matcher "mcp__.*") and shell commands (matcher "Bash|Monitor").

Claude Code contract relied on (https://code.claude.com/docs/en/hooks, checked
2026-10-12): stdin JSON with tool_name / tool_input; exit 2 + stderr blocks and
the message goes to Claude; JSON permissionDecision "ask" asks the user;
MCP tool names are mcp__<server>__<tool>; $CLAUDE_PROJECT_DIR is the project
root. Details and the shared policy are in context.py.

What it enforces (system/rules/governance.md):
- Risk of an MCP tool = its tag in user/settings/connectors.yaml (matched by
  mcp_prefix + tool name) PLUS always-on name patterns
  (system/connectors/README.md); the riskiest wins, so a wrong tag can't
  loosen a guard.
- security (financial/legal/security, N4): always blocked.
- send / share / delete (N1-N3): blocked in routines; in chats allowed only
  with an unexpired .nova-tmp/approval.json naming exactly this tool and a
  matching action, which is consumed (deleted) on use.
- Unmapped tools whose names match no pattern: blocked in routines, the user
  is asked in chats ("risky until mapped").
- Bash deletes of anything under user/ (rm, rmdir, unlink, shred, git rm,
  git clean -f, find -delete, mv out of user/) are treated as `destructive`
  with tool "Bash". Exempt: user/inbox/drop/ (staging copies removed after
  filing, system/schemas/formats.md section 3) and user/knowledge/_index/
  (regenerable indexes, section 5). Governance files are left to paths.py.
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
            sys.stderr.write("Nova guard (%s): hook files are damaged (%s; %s); blocked.\n" % (hook, exc, _fe))
        finally:
            os._exit(2)


def _raw_stdin():
    mod = sys.modules.get("context")
    return getattr(getattr(mod, "STATE", None), "raw", None)


sys.excepthook = lambda _t, _e, _tb: fail_safe("actions", _e, _raw_stdin())
try:
    import context as nova  # noqa: E402
    import shell  # noqa: E402
except BaseException as _imp:  # includes SystemExit raised while importing
    fail_safe("actions", _imp, _raw_stdin())

SEVERITY = {"read": 0, "draft": 1, "write": 2, "send": 3, "share": 4, "delete": 5, "security": 9}
LOCKED_CLASS = {"send": "send_communication", "share": "share_expose", "delete": "destructive"}

# system/connectors/README.md "Risk classification rules" (plus a few
# obvious synonyms). Matched against whole name tokens and simple inflections.
WORDS = {
    "send": ["send", "reply", "forward", "post", "publish", "invite", "respond", "rsvp", "broadcast", "notify",
             "comment", "accept", "decline"],
    "share": ["share", "permission", "grant", "invite", "unshare"],
    "delete": ["delete", "trash", "remove", "purge", "destroy", "erase", "wipe", "cancel"],
    "security": ["pay", "purchase", "charge", "sign", "password", "credential", "token", "2fa", "mfa",
                 "buy", "checkout", "otp", "secret", "apikey"],
    "write": ["create", "update", "edit", "move", "label", "set", "add", "modify", "rename", "upload",
              "write", "insert", "patch", "put", "mark", "apply", "assign", "complete", "copy", "tag"],
    "draft": ["draft"],
    "read": ["get", "list", "search", "read", "fetch", "query", "find", "view", "show", "describe",
             "lookup", "count", "retrieve", "browse", "inspect", "preview", "download", "export", "check",
             "summarize", "status", "info"],
}
IRREGULAR = {"sent": "send", "replies": "reply", "paid": "pay", "bought": "buy", "removal": "remove",
             "deletion": "delete", "permissions": "permission", "credentials": "credential",
             "tokens": "token", "signature": "sign", "esign": "sign", "esignature": "sign",
             "cancelled": "cancel", "canceled": "cancel", "cancellation": "cancel"}

# Leading read verbs: a name that starts with one of these (after any vendor
# prefix such as "slack_") only reads, unless a later word is an unambiguous
# action verb. Then send/share/delete *nouns* ("replies", "posts", "shared",
# "permissions") don't make it risky: get_thread_replies, list_shared_drives.
READ_VERBS = {"get", "list", "search", "read", "fetch", "find", "query", "describe", "count", "show", "view",
              "lookup", "retrieve", "browse", "inspect", "preview", "check"}
# Unambiguous action verbs (base form only; "reply", "post", "share",
# "comment", "invite" are also nouns and are excluded on purpose).
ACTION_VERBS = {"send", "forward", "publish", "respond", "grant", "delete", "trash", "remove", "purge",
                "destroy", "erase", "wipe", "create", "update", "edit", "move", "set", "add", "modify", "rename",
                "upload", "write", "insert", "patch", "put", "mark", "apply", "assign", "cancel", "accept",
                "decline", "rsvp", "unshare", "archive", "make", "new", "reschedule", "pay", "purchase",
                "charge", "sign", "buy", "transfer"}
CREATE_VERBS = {"create", "new", "add", "insert", "make", "compose", "write", "start"}
MESSAGE_NOUNS = {"message", "messages", "msg", "msgs", "post", "posts", "reply", "replies", "comment",
                 "comments", "chat", "chats", "thread", "threads", "mail", "email", "emails"}
EVENT_NOUNS = {"event", "events", "meeting", "meetings", "appointment", "appointments", "invite", "invites",
               "invitation", "invitations"}
EVENT_WRITE_VERBS = {"create", "update", "edit", "modify", "move", "patch", "put", "add", "insert", "reschedule",
                     "set", "quick", "new", "make", "change"}
ATTENDEE_KEYS = ("attendee", "invitee", "guest", "participant")


def inflections(word):
    v = {word, word + "s", word + "es", word + "ed", word + "d", word + "ing", word + "er"}
    if word.endswith("e"):
        v.add(word[:-1] + "ing")
    if word.endswith("y"):
        v.update({word[:-1] + "ies", word[:-1] + "ied"})
    return v


TOKEN_RISK = {}
for _risk, _words in WORDS.items():
    for _w in _words:
        for _f in inflections(_w):
            TOKEN_RISK.setdefault(_f, set()).add(_risk)
for _f, _w in IRREGULAR.items():
    for _risk, _words in WORDS.items():
        if _w in _words:
            TOKEN_RISK.setdefault(_f, set()).add(_risk)


def split_tool(tool_name):
    """('outlook', 'send_message') for 'mcp__outlook__send_message'."""
    m = re.match(r"^mcp__(.+?)__(.+)$", tool_name)
    return (m.group(1), m.group(2)) if m else ("", tool_name)


def tokens(name):
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return [t for t in re.split(r"[^A-Za-z0-9]+", name.lower()) if t]


# Money nouns: an action when the name doesn't start with a read verb
# ("make_payment" -> security, "list_payments" -> read).
FINANCIAL_NOUNS = set()
for _w in ("payment", "payout", "transfer", "wire", "refund", "invoice", "subscription"):
    FINANCIAL_NOUNS |= inflections(_w)


def read_only_name(toks):
    """True when the first verb in the name is a read verb and no later word
    is an unambiguous action verb."""
    for i, t in enumerate(toks):
        if t in READ_VERBS:
            return not any(x in ACTION_VERBS for x in toks[i + 1:])
        if t in ACTION_VERBS:
            return False
    return False


def name_risks(bare):
    """(risks, event_write): risk kinds from the name, and whether it writes a
    calendar event (a send unless tagged write and sent without attendees)."""
    toks = tokens(bare)
    risks = set()
    for t in toks:
        risks |= TOKEN_RISK.get(t, set())
    reading = read_only_name(toks)
    if reading:
        risks -= {"send", "share", "delete", "write", "draft"}
    if not reading and any(t in FINANCIAL_NOUNS for t in toks):
        risks.add("security")
    if "archive" in toks and "permanently" in toks:
        risks.add("delete")
    # creating a message/post/reply/comment publishes it: chat_message_create
    if not reading and any(t in CREATE_VERBS for t in toks) and any(t in MESSAGE_NOUNS for t in toks):
        risks.add("send")
    # Drafting a reply/forward is a draft, not a send ("create_reply_draft"),
    # unless the name also says send/post/publish ("send_draft").
    if "draft" in risks:
        explicit_send = any(t in inflections("send") | inflections("post") | inflections("publish") | {"sent"}
                            for t in toks)
        if not explicit_send:
            risks.discard("send")
    event_write = (not reading and any(t in EVENT_NOUNS for t in toks)
                   and any(t in EVENT_WRITE_VERBS for t in toks) and "delete" not in risks)
    return risks, event_write


def has_attendees(tool_input):
    if not isinstance(tool_input, dict):
        return False
    for k, v in tool_input.items():
        if any(a in str(k).lower() for a in ATTENDEE_KEYS) and v not in (None, "", [], {}):
            return True
    return False


def _norm(name):
    return re.sub(r"[\s_-]+", "", str(name)).lower()


def lookup_tag(tool_name, proj):
    """(tag or None, mapped: bool, warning or None) from connectors.yaml.

    Matches mcp_prefix / mcp_prefixes case-insensitively (chats and routines
    may expose a connector under different prefixes), then falls back to the
    MCP server name compared with the connector name (case, '-', '_' and
    spaces ignored). Tool names in tool_risk are compared case-insensitively."""
    path = os.path.join(proj, "user", "settings", "connectors.yaml")
    if not os.path.exists(path):
        return None, False, None
    try:
        data = nova.load_yaml(path, proj) or {}
        conns = data.get("connectors") or []
    except Exception as e:  # malformed: fall back to name patterns, treat unmapped
        return None, False, "user/settings/connectors.yaml could not be read (%s)" % e
    server, bare = split_tool(tool_name)
    lname = tool_name.lower()
    for c in conns if isinstance(conns, list) else []:
        if not isinstance(c, dict):
            continue
        risks = c.get("tool_risk") or {}
        if not isinstance(risks, dict):
            continue
        lrisks = {str(k).lower(): v for k, v in risks.items()}
        prefixes = []
        if c.get("mcp_prefix"):
            prefixes.append(str(c["mcp_prefix"]))
        extra = c.get("mcp_prefixes")
        if isinstance(extra, list):
            prefixes += [str(p) for p in extra if p]
        elif isinstance(extra, str) and extra:
            prefixes.append(extra)
        candidates = [lname]
        for p in prefixes:
            if lname.startswith(p.lower()):
                candidates.append(lname[len(p):])
        if server and _norm(c.get("connector", "")) == _norm(server):
            candidates.append(bare.lower())
        for cand in candidates:
            if cand in lrisks:
                return str(lrisks[cand]).strip().lower(), True, None
    return None, False, None


def guard_locked(tool_name, risks, proj, ctx, what):
    """risks: the locked kinds this call falls under (send/share/delete).
    An approval for any one of their classes authorizes the call."""
    nova.STATE.locked = True
    classes = {LOCKED_CLASS[r] for r in risks}
    cls = LOCKED_CLASS[max(risks, key=lambda r: SEVERITY[r])]
    if ctx != "chat":
        nova.block(
            "%s is a locked action (%s) and this is a routine (NOVA_CONTEXT=routine). "
            "Routines never send, share or delete. Prepare a draft if useful and queue the action "
            "in user/inbox/approvals.md for the user (system/rules/governance.md)." % (what, cls))
    rec, why = nova.approval_matches(proj, tool_name, classes)
    if rec is None:
        nova.block(
            "%s is a locked action (%s) and needs an approval record: %s. "
            "Locked action: show the user exactly what will happen, wait for an explicit yes, then write "
            ".nova-tmp/approval.json with action '%s' and tool '%s' (format: system/schemas/formats.md "
            "section 2; procedure: system/rules/governance.md) and retry. Never write a record without a "
            "real confirmation." % (what, cls, why, cls, tool_name))
    nova.consume_approval(proj)
    nova.allow()


def handle_mcp(payload, proj, ctx):
    tool_name = payload.get("tool_name") or ""
    server, bare = split_tool(tool_name)
    risks, event_write = name_risks(bare)
    tag, mapped, warning = lookup_tag(tool_name, proj)
    if tag:
        risks.add(tag if tag in SEVERITY else "delete")  # unknown tag value: treat as risky
    if event_write:
        # creating/changing an event with attendees sends invitations; only a
        # tool tagged 'write' called without attendees manages the own calendar
        if not (tag == "write" and not has_attendees(payload.get("tool_input"))):
            risks.add("send")
    if "security" in risks:
        nova.STATE.locked = True
        nova.block(
            "%s looks like a financial, legal or security action (payments, purchases, signing, "
            "credentials, account security). Nova never does these, in any context (N4). Tell the user "
            "and offer to prepare what they need to do it themselves." % tool_name)
    locked = [r for r in risks if r in LOCKED_CLASS]
    if locked:
        guard_locked(tool_name, locked, proj, ctx, "Calling %s" % tool_name)
    if not risks and not mapped and not read_only_name(tokens(bare)):
        msg = ("%s is not mapped in user/settings/connectors.yaml and its name doesn't show what it does, "
               "so it is treated as risky until mapped (run nova-connectors in a chat)." % tool_name)
        if warning:
            msg += " Note: " + warning
        if ctx != "chat":
            nova.block(msg)
        nova.ask(msg)
    nova.allow(warning)


EXEMPT_DELETE = ("user/inbox/drop/", "user/knowledge/_index/")


def handle_bash(payload, proj, ctx):
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        nova.allow()
    base = nova.session_cwd(payload, proj)
    hits = []
    for seg in shell.segments(command, base):
        writes, deletes = shell.write_targets(seg)
        if seg.name == "mv" or (seg.name == "git" and shell.git_subcommand(seg.argv)[0] == "mv"):
            # moving within user/ is a rename, not a delete
            dest = writes[-1] if writes else ""
            drel = nova.rel_to_project(shell.literal_prefix(dest), seg.cwd, proj) if dest else None
            if drel is not None and drel.startswith("user/"):
                deletes = []
        for word in deletes:
            if shell.unresolvable(word):
                continue
            rel = nova.rel_to_project(shell.literal_prefix(word) if shell.has_glob(word) else word, seg.cwd, proj)
            if rel is None or not nova.overlaps(rel, "user/"):
                continue
            r = rel.rstrip("/") + ("/" if os.path.isdir(os.path.join(proj, rel)) else "")
            if any(r.startswith(e) for e in EXEMPT_DELETE):
                continue
            if rel in nova.GOVERNANCE_FILES:
                continue  # paths.py guards governance files (governance_settings)
            hits.append(rel or ".")
    if hits:
        guard_locked("Bash", ["delete"], proj, ctx,
                     "Deleting %s" % ", ".join(sorted(set(hits))[:5]))
    nova.allow()


def main(payload, proj, ctx):
    tool_name = payload.get("tool_name") or ""
    if tool_name.startswith("mcp__"):
        handle_mcp(payload, proj, ctx)
    elif tool_name in ("Bash", "Monitor"):
        handle_bash(payload, proj, ctx)
    nova.allow()


if __name__ == "__main__":
    try:
        nova.run("actions", main)
    except SystemExit as _exit:
        if _exit.code in (0, 2, None):
            raise
        fail_safe("actions", RuntimeError("unexpected exit code %r" % (_exit.code,)), _raw_stdin())
    except BaseException as _err:
        fail_safe("actions", _err, _raw_stdin())
