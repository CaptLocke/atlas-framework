#!/usr/bin/env python3
"""Atlas hook: locked external actions, N1-N4.

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
  with an unexpired .atlas-tmp/approval.json naming exactly this tool and a
  matching action, which is consumed (deleted) on use.
- Unmapped tools whose names match no pattern: blocked in routines, the user
  is asked in chats ("risky until mapped").
- GitHub tools whose input sets visibility, privacy or a permission are a
  share, whatever their name (N9).
- Data exits (N9): export/import/upload tools are a share unless the
  connector is own_storage; curl/wget that send data are a share; in routines
  WebFetch (matcher "WebFetch") opens only the employer's sites and GitHub.
- GitHub connector writes into this repo: owned paths, protected settings,
  .atlas-tmp/ and .git/ are blocked (N5/N6 for connector side doors).
- Tripwire: a locked action is blocked while tracked files under .claude/ or
  system/ differ from HEAD outside an update (a hook may have been rewritten
  by a command the path guard can't see, such as an interpreter).
- Bash deletes of anything under user/ (rm, rmdir, unlink, shred, git rm,
  git clean -f, find -delete, mv out of user/) are treated as `destructive`
  with tool "Bash". Exempt: user/inbox/drop/ (staging copies removed after
  filing, system/schemas/formats.md section 3) and user/knowledge/_index/
  (regenerable indexes, section 5). Governance files are left to paths.py.
- Routines (1.0.2): shell commands must pass the routine allowlist
  (commands.py), and curl/wget may use only a few known options with every
  address a written-out URL on an allowed host.
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


sys.excepthook = lambda _t, _e, _tb: fail_safe("actions", _e, _raw_stdin())
try:
    import context as atlas  # noqa: E402
    import shell  # noqa: E402
    import commands  # noqa: E402
except BaseException as _imp:  # includes SystemExit raised while importing
    fail_safe("actions", _imp, _raw_stdin())

SEVERITY = {"read": 0, "draft": 1, "write": 2, "send": 3, "share": 4, "delete": 5, "security": 9}
LOCKED_CLASS = {"send": "send_communication", "share": "share_expose", "delete": "destructive"}

# system/connectors/README.md "Risk classification rules" (plus a few
# obvious synonyms). Matched against whole name tokens and simple inflections.
WORDS = {
    "send": ["send", "reply", "forward", "post", "publish", "invite", "respond", "rsvp", "broadcast", "notify",
             "comment", "accept", "decline"],
    "share": ["share", "permission", "grant", "invite", "unshare", "collaborator", "visibility", "gist"],
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
# On GitHub tools only: an input that changes who can see the repo is a share
# (a public repo or a new collaborator exposes everything Atlas keeps).
EXPOSURE_KEYS = ("visibility", "private", "permission")
# Moving content into another service (a design tool, a converter) shares it, unless the
# connector is the user's own storage (connectors.yaml: own_storage: true).
TRANSFER_WORDS = ("export", "import", "upload")
# curl/wget options that send data, and methods other than GET/HEAD
CURL_DATA = ("-d", "--data", "--data-raw", "--data-binary", "--data-urlencode", "--data-ascii", "--json",
             "-F", "--form", "--form-string", "-T", "--upload-file")
WGET_DATA = ("--post-data", "--post-file", "--body-data", "--body-file")
GITHUB_PATH_KEYS = ("path", "file_path", "filepath", "filename", "file")


def inflections(word):
    v = {word, word + "s", word + "es", word + "ed", word + "d", word + "ing", word + "er"}
    if word.endswith("e"):
        v.add(word[:-1] + "ing")
    if word.endswith("y"):
        v.update({word[:-1] + "ies", word[:-1] + "ied"})
    return v


TRANSFER_FORMS = set().union(*(inflections(w) for w in TRANSFER_WORDS))

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


def exposes_repo(server, tool_input):
    """True for a GitHub tool call whose input sets visibility, privacy or a permission."""
    if "github" not in _norm(server) or not isinstance(tool_input, dict):
        return False
    return any(any(k in str(key).lower() for k in EXPOSURE_KEYS) for key in tool_input)


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
        data = atlas.load_yaml(path, proj) or {}
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


def own_storage(tool_name, proj):
    """True when connectors.yaml marks this tool's connector as the user's own storage."""
    path = os.path.join(proj, "user", "settings", "connectors.yaml")
    try:
        conns = (atlas.load_yaml(path, proj) or {}).get("connectors") or []
    except Exception:
        return False
    server, _ = split_tool(tool_name)
    lname = tool_name.lower()
    for c in conns if isinstance(conns, list) else []:
        if not isinstance(c, dict):
            continue
        # the user's own drive: marked own_storage, or a files connector not marked otherwise
        cats = c.get("categories") or []
        if not (c.get("own_storage") is True or (c.get("own_storage") is None and "files" in cats)):
            continue
        extra = c.get("mcp_prefixes")
        prefixes = [str(c.get("mcp_prefix") or "")] + ([str(p) for p in extra] if isinstance(extra, list) else [])
        if any(p and lname.startswith(p.lower()) for p in prefixes) or (
                server and _norm(c.get("connector", "")) == _norm(server)):
            return True
    return False


def _github_target(tool_input, proj):
    """'own' when a GitHub call targets this Atlas repo (or names none), 'other' otherwise."""
    repo = tool_input.get("repo") or tool_input.get("repository") or tool_input.get("repo_name") or ""
    if isinstance(repo, dict):
        repo = repo.get("full_name") or "%s/%s" % (repo.get("owner") or "", repo.get("name") or "")
    owner = tool_input.get("owner") or ""
    own = atlas.origin_slug(proj)
    repo = str(repo).strip().lower()
    if not repo:
        return "own"
    if "/" in repo:
        return "own" if atlas.repo_slug(repo) == own else "other"
    if owner:
        return "own" if atlas.repo_slug("%s/%s" % (owner, repo)) == own else "other"
    return "own" if own.split("/")[-1:] == [repo.removesuffix(".git")] else "other"


def _paths_in(value, out):
    if isinstance(value, dict):
        for k, v in value.items():
            if str(k).lower() in GITHUB_PATH_KEYS and isinstance(v, str):
                out.append(v)
            else:
                _paths_in(v, out)
    elif isinstance(value, list):
        for v in value:
            _paths_in(v, out)
    return out


def github_paths(server, bare, tool_input, proj):
    """Repo paths a GitHub connector call writes in this Atlas repo (N5/N6 via connectors)."""
    if "github" not in _norm(server) or not isinstance(tool_input, dict) or read_only_name(tokens(bare)):
        return []
    if _github_target(tool_input, proj) != "own":
        return []
    return [re.sub(r"^(\./|/)+", "", os.path.normpath(p)) for p in _paths_in(tool_input, []) if p]


def github_extra_risks(server, bare, tool_input, proj):
    """GitHub writes that copy content out (another repo, a fork, a new repo) are shares; forced
    ref updates on this repo rewrite history (N8)."""
    if "github" not in _norm(server) or not isinstance(tool_input, dict):
        return set()
    toks = set(tokens(bare))
    if read_only_name(tokens(bare)):
        return set()
    if "fork" in toks or "forks" in toks or ({"create", "new"} & toks and {"repository", "repo"} & toks):
        return {"share"}
    if _github_target(tool_input, proj) == "other":
        return {"share"}
    if "ref" in toks or "refs" in toks or "branch" in toks:
        if tool_input.get("force") in (True, "true"):
            atlas.STATE.locked = True
            atlas.block("Forcing a ref update on the Atlas repo rewrites history, which Atlas never does (N8).")
    return set()


def check_github_write(tool_name, paths, proj, ctx="chat"):
    owned = atlas.owned_paths(proj)
    bad = [p for p in paths if any(atlas.overlaps(p, e) for e in owned) or p in atlas.GOVERNANCE_FILES
           or p.startswith((".atlas-tmp", ".git/")) or p in (".", ".git") or atlas.autoload_path(p)
           or (ctx != "chat" and p == "user/settings/atlas.yaml")]
    if bad:
        atlas.STATE.locked = True
        atlas.block("%s would write %s in the Atlas repo through GitHub. System files change only through "
                    "atlas-update (N5) and protected settings only in a confirmed chat (N6); connector writes "
                    "to them are never allowed." % (tool_name, ", ".join(sorted(set(bad))[:5])))


SHARED_HOSTS = {"github.io", "githubusercontent.com", "gitlab.io", "netlify.app", "vercel.app", "pages.dev",
                "herokuapp.com", "azurewebsites.net", "cloudfront.net", "appspot.com", "web.app",
                "firebaseapp.com", "blogspot.com", "wordpress.com", "medium.com", "notion.site", "sites.google.com"}


def url_host(url):
    """Host of an http(s) URL ('' when unclear, which is never allowed).

    A backslash or an @ before the path is refused outright: browsers read a backslash as a slash
    and curl doesn't, so github.com\\@other.host is GitHub to one and other.host to the other."""
    u = str(url or "").strip()
    m = re.match(r"^https?://([^/?#]*)", u, re.I)
    if not m or re.search(r"[\\@]", m.group(1)):
        return ""
    host = m.group(1).split(":")[0].lower().rstrip(".")
    return host if re.match(r"^[a-z0-9.-]+$", host) else ""


def allowed_hosts(proj):
    """github.com plus the employer's website and email domains (each a real domain, not a shared host)."""
    allowed = {"github.com", "raw.githubusercontent.com"}
    try:
        data = atlas.load_yaml(os.path.join(proj, "user", "settings", "atlas.yaml"), proj) or {}
        company = data.get("company") or {}
        site = url_host("https://" + re.sub(r"^[a-z]+://", "", str(company.get("website") or ""), flags=re.I))
        domains = company.get("email_domains") or []
        domains = [domains] if isinstance(domains, str) else list(domains)
        for d in [site] + [str(x) for x in domains]:
            d = d.lower().strip().lstrip(".")
            d = d[4:] if d.startswith("www.") else d
            if re.match(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$", d) and d not in SHARED_HOSTS \
                    and not any(d.endswith("." + h) for h in SHARED_HOSTS):
                allowed.add(d)
    except Exception:
        pass
    return allowed


def host_allowed(host, proj):
    return bool(host) and any(host == d or host.endswith("." + d) for d in allowed_hosts(proj))


def block_host(what, host):
    atlas.STATE.locked = True
    atlas.block("%s %s from a routine is not allowed: routines reach only the employer's own sites and "
                "GitHub, because a link can carry data out. Use web search results instead, or note the link "
                "in the run report for the next chat." % (what, host or "that address"))


def handle_webfetch(payload, proj, ctx):
    """Routines open only the employer's own sites and GitHub: a link can carry data out."""
    if ctx == "chat":
        atlas.allow()
    host = url_host((payload.get("tool_input") or {}).get("url"))
    if host_allowed(host, proj):
        atlas.allow()
    block_host("Opening", host)


def guard_locked(tool_name, risks, proj, ctx, what):
    """risks: the locked kinds this call falls under (send/share/delete).
    An approval for any one of their classes authorizes the call."""
    atlas.STATE.locked = True
    classes = {LOCKED_CLASS[r] for r in risks}
    cls = LOCKED_CLASS[max(risks, key=lambda r: SEVERITY[r])]
    changed, detail = atlas.system_files_changed(proj)
    if changed and not atlas.valid_lock(proj, "update")[0]:
        atlas.block(
            "%s is a locked action (%s), and %s, outside an update. Locked actions "
            "stay blocked until the system files are restored: tell the user, and offer atlas-health's "
            "\"restore system files\" (git checkout HEAD -- followed by the owned paths)." % (what, cls, detail))
    if ctx != "chat":
        atlas.block(
            "%s is a locked action (%s) and this is a routine (ATLAS_CONTEXT=routine). "
            "Routines never send, share or delete. Prepare a draft if useful and queue the action "
            "in user/inbox/approvals.md for the user (system/rules/governance.md)." % (what, cls))
    rec, why = atlas.approval_matches(proj, tool_name, classes)
    if rec is None:
        atlas.block(
            "%s is a locked action (%s) and needs an approval record: %s. "
            "Locked action: show the user exactly what will happen, wait for an explicit yes, then write "
            ".atlas-tmp/approval.json with action '%s' and tool '%s' (format: system/schemas/formats.md "
            "section 2; procedure: system/rules/governance.md) and retry. Never write a record without a "
            "real confirmation." % (what, cls, why, cls, tool_name))
    atlas.consume_approval(proj)
    atlas.allow()


def handle_mcp(payload, proj, ctx):
    tool_name = payload.get("tool_name") or ""
    server, bare = split_tool(tool_name)
    risks, event_write = name_risks(bare)
    tag, mapped, warning = lookup_tag(tool_name, proj)
    if tag:
        risks.add(tag if tag in SEVERITY else "delete")  # unknown tag value: treat as risky
    if exposes_repo(server, payload.get("tool_input")):
        risks.add("share")
    if (TRANSFER_FORMS & set(tokens(bare)) and not READ_VERBS & set(tokens(bare))
            and not own_storage(tool_name, proj)):
        risks.add("share")
    risks |= github_extra_risks(server, bare, payload.get("tool_input"), proj)
    gh_paths = github_paths(server, bare, payload.get("tool_input"), proj)
    if gh_paths:
        check_github_write(tool_name, gh_paths, proj, ctx)
    if event_write:
        # creating/changing an event with attendees sends invitations; only a
        # tool tagged 'write' called without attendees manages the own calendar
        if not (tag == "write" and not has_attendees(payload.get("tool_input"))):
            risks.add("send")
    if "security" in risks:
        atlas.STATE.locked = True
        atlas.block(
            "%s looks like a financial, legal or security action (payments, purchases, signing, "
            "credentials, account security). Atlas never does these, in any context (N4). Tell the user "
            "and offer to prepare what they need to do it themselves." % tool_name)
    locked = [r for r in risks if r in LOCKED_CLASS]
    if locked:
        guard_locked(tool_name, locked, proj, ctx, "Calling %s" % tool_name)
    if not risks and not mapped and not read_only_name(tokens(bare)):
        msg = ("%s is not mapped in user/settings/connectors.yaml and its name doesn't show what it does, "
               "so it is treated as risky until mapped (run atlas-connectors in a chat)." % tool_name)
        if warning:
            msg += " Note: " + warning
        if ctx != "chat":
            atlas.block(msg)
        atlas.ask(msg)
    atlas.allow(warning)


EXEMPT_DELETE = ("user/inbox/drop/", "user/knowledge/_index/")


def uploads(seg):
    """True when a curl/wget call sends data (a body, a form, a file, a non-GET method) or reads
    its options from a config file or script (-K, wget -e/--execute)."""
    args = seg.argv[1:]
    curl = seg.name == "curl"
    for i, a in enumerate(args):
        opt = a.split("=", 1)[0]
        nxt = args[i + 1] if i + 1 < len(args) else ""
        if curl:
            if opt in CURL_DATA or opt in ("-K", "--config"):
                return True
            if opt == "--request":
                if (a.split("=", 1)[1] if "=" in a else nxt).upper() not in ("GET", "HEAD"):
                    return True
            elif re.match(r"^-[A-Za-z]", a) and not a.startswith("--"):
                letters = a[1:]
                for j, ch in enumerate(letters):
                    if ch in "dFTK":
                        return True
                    if ch == "X":
                        method = letters[j + 1:] or nxt
                        if method.upper() not in ("GET", "HEAD"):
                            return True
                        break
        else:
            if opt in WGET_DATA or opt in ("-e", "--execute", "-i", "--input-file"):
                return True
            if opt == "--method" and (a.split("=", 1)[1] if "=" in a else nxt).upper() not in ("GET", "HEAD"):
                return True
    return False


# Routines: the only curl/wget options allowed (anything else, such as a proxy, a config file,
# --resolve or an upload, is refused). Short flags may be bundled (-fsSL); the letters in
# *_VALUE_LETTERS take a value (-o FILE, -qO-).
CURL_FLAG_LETTERS = set("sSLfIiv#gO")
CURL_VALUE_LETTERS = set("oHAmwre")
CURL_VALUE_OPTS = {"--output", "--header", "--user-agent", "--max-time", "--connect-timeout", "--write-out",
                   "--range", "--retry", "--referer", "--url"}
CURL_LONG_FLAGS = {"--silent", "--show-error", "--location", "--fail", "--fail-with-body", "--head", "--include",
                   "--compressed", "--remote-name", "--verbose", "--globoff"}
WGET_FLAG_LETTERS = set("qSv")
WGET_VALUE_LETTERS = set("OTtPU")
WGET_VALUE_OPTS = {"--output-document", "--timeout", "--tries", "--max-redirect", "--directory-prefix",
                   "--user-agent"}
WGET_LONG_FLAGS = {"--quiet", "--spider", "--no-verbose", "-nv", "--server-response"}


def download_problem(seg, proj):
    """Why this curl/wget call isn't allowed in a routine, or None (C1)."""
    curl = seg.name == "curl"
    letters, value_letters = (CURL_FLAG_LETTERS, CURL_VALUE_LETTERS) if curl else \
        (WGET_FLAG_LETTERS, WGET_VALUE_LETTERS)
    value_opts, long_flags = (CURL_VALUE_OPTS, CURL_LONG_FLAGS) if curl else (WGET_VALUE_OPTS, WGET_LONG_FLAGS)
    args, urls, i = seg.argv[1:], [], 0
    while i < len(args):
        a = args[i]
        opt = a.split("=", 1)[0]
        if opt in ("-X", "--request", "--method") or (a.startswith("-X") and len(a) > 2):
            method = a[2:] if a.startswith("-X") and len(a) > 2 else (
                a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else ""))
            if method.upper() not in ("GET", "HEAD"):
                return "%s %s %s" % (seg.name, opt, method)
            i += 1 if "=" not in a and not (a.startswith("-X") and len(a) > 2) else 0
        elif a.startswith("--"):
            if opt in value_opts:
                if "=" not in a:
                    i += 1
                if opt == "--url":
                    urls.append(a.split("=", 1)[1] if "=" in a else (args[i] if i < len(args) else ""))
            elif a not in long_flags:
                return "%s option %s" % (seg.name, a)
        elif a in long_flags:
            pass
        elif a.startswith("-") and len(a) > 1:
            for j, ch in enumerate(a[1:]):
                if ch in value_letters:
                    if j == len(a) - 2:
                        i += 1  # the value is the next word
                    break
                if ch not in letters:
                    return "%s option -%s" % (seg.name, ch)
        else:
            urls.append(a)
        i += 1
    if not urls:
        return "%s without a written-out address" % seg.name
    for u in urls:
        if not re.match(r"^https?://", u, re.I):
            return "%s %s (write the address out in full, starting with https://)" % (seg.name, u[:60])
        if not host_allowed(url_host(u), proj):
            block_host("Reaching", url_host(u) or u[:60])
    return None


def handle_bash(payload, proj, ctx):
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not command.strip():
        atlas.allow()
    base = atlas.session_cwd(payload, proj)
    if ctx != "chat":
        why = commands.problem(command, base, proj)
        if why:
            atlas.STATE.locked = True
            atlas.block("Routines run only plain commands the safety checks can follow, and this uses %s. "
                        "Do this step another way (one plain command, Atlas's tools in system/tools/, or the "
                        "Read/Write/Edit tools), or note it in the run report for the next chat "
                        "(system/rules/governance.md)." % why)
    hits = []
    for seg in shell.segments(command, base):
        if seg.name in ("curl", "wget", "wget2"):
            if uploads(seg):
                guard_locked("Bash", ["share"], proj, ctx, "Sending data with %s" % seg.name)
            if ctx != "chat":
                why = download_problem(seg, proj)
                if why:
                    atlas.STATE.locked = True
                    atlas.block("In a routine, curl and wget fetch only written-out https:// addresses on the "
                                "employer's sites and GitHub, with a few plain options; this call uses %s."
                                % why)
        writes, deletes = shell.write_targets(seg)
        if seg.name == "mv" or (seg.name == "git" and shell.git_subcommand(seg.argv)[0] == "mv"):
            # moving within user/ is a rename, not a delete
            dest = writes[-1] if writes else ""
            drel = atlas.rel_to_project(shell.literal_prefix(dest), seg.cwd, proj) if dest else None
            if drel is not None and drel.startswith("user/"):
                deletes = []
        for word in deletes:
            if shell.unresolvable(word):
                continue
            rel = atlas.rel_to_project(shell.literal_prefix(word) if shell.has_glob(word) else word, seg.cwd, proj)
            if rel is None or not atlas.overlaps(rel, "user/"):
                continue
            r = rel.rstrip("/") + ("/" if os.path.isdir(os.path.join(proj, rel)) else "")
            if any(r.startswith(e) for e in EXEMPT_DELETE):
                continue
            if rel in atlas.GOVERNANCE_FILES:
                continue  # paths.py guards governance files (governance_settings)
            hits.append(rel or ".")
    if hits:
        guard_locked("Bash", ["delete"], proj, ctx,
                     "Deleting %s" % ", ".join(sorted(set(hits))[:5]))
    atlas.allow()


def main(payload, proj, ctx):
    tool_name = payload.get("tool_name") or ""
    if tool_name.startswith("mcp__"):
        handle_mcp(payload, proj, ctx)
    elif tool_name in ("Bash", "Monitor"):
        handle_bash(payload, proj, ctx)
    elif tool_name == "WebFetch":
        handle_webfetch(payload, proj, ctx)
    atlas.allow()


if __name__ == "__main__":
    try:
        atlas.run("actions", main)
    except SystemExit as _exit:
        if _exit.code in (0, 2, None):
            raise
        fail_safe("actions", RuntimeError("unexpected exit code %r" % (_exit.code,)), _raw_stdin())
    except BaseException as _err:
        fail_safe("actions", _err, _raw_stdin())
