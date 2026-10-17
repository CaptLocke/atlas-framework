#!/usr/bin/env python3
"""Atlas hook: git history, secrets and attribution, N8 / N10 / N12.

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
  .atlas-tmp/purge.lock in a chat (the atlas-memory purge procedure).
  Also blocks changing the `origin` remote (it decides the upstream bypass).
- N5: `git fetch`/`git pull` only from origin or the official upstream
  (system/manifest.yaml: upstream), and only the upstream may fill
  refs/atlas-upstream/* (the release refs atlas-update installs from). A
  commit that touches owned paths needs a valid update lock and
  `Atlas-Actor: update`.
- N8: deleting tags (`git tag -d`, push of :refs/tags/...) only under a valid
  update lock or a purge lock in a chat; deleting branches on origin
  (`git push --delete`, `git push origin :branch`, `git branch -d/-D` of a
  branch that exists on origin) only under a purge lock in a chat.
- N9: `gh` only reads (repo/pr/issue/release/run view and list, auth status,
  GET `gh api` without fields), in any context: Atlas never changes GitHub
  through it, so it can't make the repo public or copy content out (C4/H1).
- `git config` writes only user.name/email and a few display settings, and
  `git -c` takes only those keys; --exec-path, --git-dir, --work-tree,
  --namespace and --config-env are refused, as are `rebase --exec` and
  `grep -O` (each could run a command outside the guards; H2).
- Routines (1.0.2) use a short list of git subcommands, can't move HEAD or
  the working tree to any commit but HEAD and origin/main (checkout/switch
  only `main`, branches only at HEAD, merge/rebase only origin/*, pull only
  from origin without refspecs), revert only commits that don't touch owned
  paths, and commit owned paths only when they match, file for file, the
  signed release named in the update lock (C3). `git reset --hard
  origin/main` is allowed under a valid update lock (undoing a failed update
  before it is pushed).
- N12: `git commit` must carry `Atlas-Actor:` and `Atlas-Reason:` trailers
  (parsed from -m/--message, -F/--file and heredocs). When the message source
  can't be determined (editor, -C/-c, -F - without a heredoc) the commit is
  allowed with a warning. Routines may not commit as `Atlas-Actor: chat`.
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
            sys.stderr.write("Atlas guard (%s): hook files are damaged (%s; %s); blocked.\n" % (hook, exc, _fe))
        finally:
            os._exit(2)


def _raw_stdin():
    mod = sys.modules.get("context")
    return getattr(getattr(mod, "STATE", None), "raw", None)


sys.excepthook = lambda _t, _e, _tb: fail_safe("git", _e, _raw_stdin())
try:
    import context as atlas  # noqa: E402
    import shell  # noqa: E402
except BaseException as _imp:  # includes SystemExit raised while importing
    fail_safe("git", _imp, _raw_stdin())

# Patterns are assembled from parts so this file never contains a literal
# secret-shaped string (it is committed into every Atlas repo).
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
    elif sub == "reset" and any(a in ("--hard", "--keep", "--merge") for a in args):
        targets = [p for p in positional(args)]
        if targets and targets[0] not in ("HEAD", "@") and "--" not in args[:args.index(targets[0])]:
            mode = [a for a in args if a in ("--hard", "--keep", "--merge")][0]
            return "reset %s %s" % (mode, targets[0])
    elif sub == "rebase":
        if any(a in ("-i", "--interactive", "--root", "-x", "--exec") or a.startswith(("--exec=", "--rebase-merges"))
               or (re.match(r"^-[a-zA-Z]+$", a) and ("i" in a or "x" in a)) for a in args):
            return "interactive, root or --exec rebase"
    elif sub == "branch" and any(a in ("-f", "--force", "-M", "-C") or
                                 (re.match(r"^-[a-zA-Z]+$", a) and re.search(r"[fMC]", a)) for a in args):
        return "git branch -f/-M/-C (moving or overwriting a branch)"
    elif sub == "checkout" and any(a == "-B" or (re.match(r"^-[a-zA-Z]+$", a) and "B" in a) for a in args):
        return "git checkout -B (resetting a branch)"
    elif sub == "switch" and any(a in ("-C", "--force-create") or a.startswith("--force-create=") for a in args):
        return "git switch -C (resetting a branch)"
    elif sub == "update-ref":
        pos = positional(args)
        if args[:1] == ["-d"] and pos and pos[0].startswith("refs/atlas-upstream/") and len(pos) <= 2:
            return None  # dropping a fetched release ref (atlas-update, after a failed signature check)
        return "git update-ref"
    elif sub in ("filter-branch", "filter-repo", "replace"):
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
    if sub == "push" and "--prune" in args:
        return "git push --prune (deletes branches on origin)", "branch"
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


GH_READS = {("auth", "status"), ("repo", "view"), ("repo", "list"), ("pr", "list"), ("pr", "view"),
            ("pr", "status"), ("pr", "diff"), ("pr", "checks"), ("issue", "list"), ("issue", "view"),
            ("issue", "status"), ("release", "list"), ("release", "view"), ("run", "list"), ("run", "view"),
            ("gist", "list"), ("gist", "view")}


def gh_change(argv):
    """Description when a gh command does anything but read (N9: Atlas never changes GitHub through gh),
    else None."""
    args = list(argv[1:])
    while args and args[0].startswith("-"):  # global flags: --repo x, -R x, --hostname x
        if args[0] in ("--version", "--help", "-h"):
            return None
        args = args[2:] if args[0] in ("-R", "--repo", "--hostname") else args[1:]
    if not args or args[0] in ("version", "help"):
        return None
    if args[0] == "api":
        method = (shell.option_value(argv, "-X", "--method") or "GET").upper()
        fields = any(a in ("-f", "-F", "--field", "--raw-field", "--input") or
                     a.startswith(("--field=", "--raw-field=", "--input=", "--method=", "-f", "-F"))
                     and not a.startswith("--method=GET") for a in args)
        if method != "GET" or fields:
            return "gh api with %s" % ("method " + method if method != "GET" else "fields (a write)")
        return None
    if tuple(args[:2]) in GH_READS:
        return None
    return "gh %s" % " ".join(args[:2])


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
        setting = len(shell.positional(["git"] + args, value_opts=CONFIG_VALUE_OPTS)) >= 2
        if destructive or setting:
            return "changing remote.origin config"
    return None


def push_problem(sub, args, cwd):
    """git push goes only to origin, and origin's push URLs (pushurl, pushInsteadOf applied) must
    still be this repo (N9: nothing leaves except to the user's own repo)."""
    if sub != "push":
        return None
    if any(a.split("=", 1)[0] in ("--repo", "--receive-pack", "--exec") for a in args):
        return "git push with --repo/--receive-pack/--exec"
    pos = shell.positional(["git"] + args, value_opts=("-o", "--push-option"))
    if pos and pos[0] != "origin":
        return "git push to %r" % pos[0]
    rc, fetch_url = git(["remote", "get-url", "origin"], cwd)
    rc2, push_urls = git(["remote", "get-url", "--push", "--all", "origin"], cwd)
    if rc != 0 or rc2 != 0:
        return "git push without a readable origin"
    if any(u != fetch_url.strip() for u in push_urls.split()):
        return "git push to a redirected push URL"
    return None


# ------------------------------------------------------------------ N5
FETCH_VALUE_OPTS = ("--depth", "--deepen", "--shallow-since", "--shallow-exclude", "-j", "--jobs",
                    "--negotiation-tip", "--upload-pack", "-o", "--server-option", "--refmap",
                    "-s", "--strategy", "-X", "--strategy-option")


FETCH_SPREAD_OPTS = ("--all", "--multiple", "--refmap")
GITHUB_URL = re.compile(r"^(https://github\.com/|ssh://git@github\.com/|git@github\.com:)", re.I)


def fetch_problem(sub, args, proj):
    """Why this fetch/pull isn't allowed, or None."""
    upstream = atlas.upstream_slug(proj)

    def official(url):
        return bool(upstream) and bool(GITHUB_URL.match(url)) and atlas.repo_slug(url) == upstream

    if sub == "remote" and args[:1] == ["update"]:
        return "git remote update: Atlas fetches from one named source at a time"
    if sub == "remote" and args[:1] == ["add"]:
        rest = positional(args[1:])
        if not (len(rest) >= 2 and official(rest[1])):
            return "git remote add: Atlas only uses its own repo (origin) and the official upstream"
        return None
    if sub not in ("fetch", "pull"):
        return None
    spread = [a for a in args if a.split("=", 1)[0] in FETCH_SPREAD_OPTS]
    if spread:
        return "git %s %s: Atlas fetches from one named source at a time" % (sub, spread[0])
    pos = shell.positional(["git"] + args, value_opts=FETCH_VALUE_OPTS)
    repo = pos[0] if pos else "origin"
    refspecs = pos[1:]
    from_upstream = official(repo)
    if repo != "origin" and not from_upstream:
        return ("git %s from %r: Atlas only fetches from its own repo (origin) or the official upstream "
                "(https://github.com/%s)" % (sub, repo, upstream))
    if not from_upstream and any("atlas-upstream" in r.lower() for r in refspecs):
        return "only the official upstream (%s) may fill refs/atlas-upstream/* (release refs)" % upstream
    return None


REDIRECT_KEY = re.compile(r"^(url\.|remote\.|branch\.[^=]*\.(remote|merge|pushremote)\b)", re.I)


CONFIG_VALUE_OPTS = ("-f", "--file", "--blob", "--type", "--default", "--comment")


def config_redirect(sub, args, argv):
    """Config that would make fetches read from somewhere else: 'git -c url.X.insteadOf=..',
    'git config url.*', 'git branch -u'. Returns a description or None."""
    i = 1
    while i < len(argv) and argv[i] != sub:
        if argv[i] == "-c" and i + 1 < len(argv) and REDIRECT_KEY.match(argv[i + 1]):
            return "git -c %s" % argv[i + 1].split("=", 1)[0]
        i += 1
    if sub == "config":
        pos = shell.positional(["git"] + args, value_opts=CONFIG_VALUE_OPTS)
        keys = [a for a in pos[:1] if REDIRECT_KEY.match(a)]
        writes = len(pos) >= 2 or any(a in ("--add", "--replace-all") for a in args)
        if keys and writes:
            return "git config %s" % keys[0]
    if sub == "branch" and any(a in ("-u", "--set-upstream-to") or a.startswith("--set-upstream-to=")
                               for a in args):
        return "git branch --set-upstream-to"
    return None


CONFIG_SAFE_KEY = re.compile(r"^(user\.(name|email)|pull\.rebase|rebase\.autostash|core\.(quotepath|filemode|autocrlf)"
                             r"|color\.[a-z.]+|advice\.[a-z]+|init\.defaultbranch)$", re.I)
CONFIG_WRITE_FLAGS = ("--unset", "--unset-all", "--add", "--replace-all", "--rename-section", "--remove-section",
                      "-e", "--edit")
BLOCKED_GLOBAL_OPTS = ("--exec-path", "--git-dir", "--work-tree", "--namespace", "--config-env", "--super-prefix")


def config_problem(sub, args, argv):
    """git -c / config writes beyond a few safe keys, and global options that relocate git (H2)."""
    i = 1
    while i < len(argv) and argv[i] != sub:
        a = argv[i]
        if a.split("=", 1)[0] in BLOCKED_GLOBAL_OPTS:
            return "git %s" % a.split("=", 1)[0]
        if a == "-c" and i + 1 < len(argv):
            key = argv[i + 1].split("=", 1)[0]
            if not CONFIG_SAFE_KEY.match(key):
                return "git -c %s" % key
            i += 2
            continue
        i += 1
    if sub in ("fetch", "pull", "ls-remote", "clone", "archive") and any(
            a.startswith("--upload-pack") or (sub in ("clone", "ls-remote") and a == "-u") for a in args):
        return "git %s --upload-pack (it runs a program)" % sub
    if sub == "grep" and any(a in ("-O", "--open-files-in-pager") or a.startswith(("-O", "--open-files-in-pager="))
                             for a in args):
        return "git grep -O (it runs a program)"
    if sub != "config":
        return None
    pos = shell.positional(["git"] + args, value_opts=CONFIG_VALUE_OPTS)
    if pos[:1] in (["get"], ["list"]):
        return None
    if pos[:1] in (["set"], ["unset"], ["rename-section"], ["remove-section"], ["edit"]):
        key, writes = (pos[1] if len(pos) > 1 else ""), True
    else:
        key = pos[0] if pos else ""
        writes = len(pos) >= 2 or any(a in CONFIG_WRITE_FLAGS for a in args)
    if not writes:
        return None
    if any(a in ("-f", "--file", "--blob") or a.startswith(("--file=", "--blob=")) for a in args):
        return "git config writing another file"
    if not CONFIG_SAFE_KEY.match(key):
        return "git config %s (Atlas sets only user.name, user.email and display settings)" % (key or "--edit")
    return None


ROUTINE_SUBS = {"status", "diff", "log", "show", "ls-files", "ls-tree", "ls-remote", "rev-parse", "rev-list", "add",
                "commit", "pull", "push", "fetch", "tag", "checkout", "switch", "rm", "mv", "restore", "grep",
                "blame", "cat-file", "merge-base", "branch", "remote", "config", "rebase", "reset", "stash",
                "describe", "shortlog", "for-each-ref", "count-objects", "show-ref", "diff-tree", "name-rev",
                "check-ignore", "revert", "update-ref", "merge", "version", "help", "reflog", "whatchanged"}
# origin's main only: other branches on origin could have been pushed by this same session
ORIGIN_REF = re.compile(r"^(origin/main|refs/remotes/origin/main|origin/HEAD|@\{u\}|@\{upstream\})$")
PUSH_REFSPEC = re.compile(r"^(HEAD|main|HEAD:main|HEAD:refs/heads/main|main:main|refs/heads/main|"
                          r"(refs/tags/)?pre-update-[0-9][0-9A-Za-z.-]*)$")
HEAD_REFS = ("HEAD", "@")
RELEASE_REFSPEC = re.compile(r"^refs/tags/(v\d+\.\d+\.\d+(-[A-Za-z0-9.]+)?):refs/atlas-upstream/\1$")
PULL_FLAGS = {"--rebase", "--rebase=true", "--no-rebase", "--ff-only", "--ff", "--autostash", "--no-autostash",
              "-q", "--quiet", "-v", "--verbose", "--no-edit", "-r"}
FETCH_FLAGS = {"--no-tags", "--tags", "-q", "--quiet", "-v", "--verbose", "--prune", "-p", "--dry-run",
               "--unshallow"}
FETCH_VALUE_FLAGS = ("--depth", "--deepen", "--shallow-since")
REBASE_FLAGS = {"--continue", "--abort", "--skip", "--quit", "--autostash", "--no-autostash", "-q", "--quiet"}
LS_REMOTE_FLAGS = {"--tags", "--refs", "--heads", "--branches", "-t", "-h", "-b", "-q", "--quiet", "--symref",
                   "--exit-code"}


def _flags_outside(args, allowed, value_flags=()):
    for a in args:
        if a.startswith("-") and a not in allowed and a.split("=", 1)[0] not in value_flags:
            return a
    return None


def routine_problem(sub, args, cwd, proj):
    """Why a routine may not run this git command, or None. Routines never move HEAD or the working tree
    to an older commit, so system files can't be swapped for an earlier release's (C3)."""
    if not sub:
        return None
    if sub not in ROUTINE_SUBS:
        return "git %s" % sub
    pos = positional(args)
    if sub == "checkout":
        if "--" in args or any(a.startswith("--pathspec-from-file") for a in args):
            return None  # paths: checked by the paths hook
        if "-b" in args:
            return None if pos[1:2] in ([], ["HEAD"], ["main"]) else "git checkout -b at %s" % pos[1]
        return None if pos == ["main"] else (
            "git checkout %s (routines use `git checkout main` or `git checkout -- <path>`)" % " ".join(args))
    if sub == "switch":
        if any(a in ("-c", "--create") for a in args):
            return None if pos[1:2] in ([], ["HEAD"], ["main"]) else "git switch -c at %s" % pos[1]
        return None if pos in ([], ["main"]) else "git switch %s (routines switch only to main)" % " ".join(args)
    if sub == "branch":
        if any(a in ("-d", "-D", "--delete", "-m", "--move", "-c", "--copy", "-l", "--list", "-a", "--all", "-r",
                     "--remotes", "-v", "-vv", "--show-current") or a.startswith(("--contains", "--merged",
                                                                                  "--no-merged", "--points-at",
                                                                                  "--sort", "--format"))
               for a in args):
            return None
        return None if len(pos) < 2 or pos[1] in HEAD_REFS else "git branch at %s" % pos[1]
    if sub == "merge":
        if "--allow-unrelated-histories" in args:
            return "git merge --allow-unrelated-histories"
        refs = shell.positional(["git"] + args, value_opts=("-m", "--message", "-s", "--strategy", "-X",
                                                            "--strategy-option", "-F", "--file"))
        bad = [r for r in refs if not ORIGIN_REF.match(r)]
        return "git merge %s (routines merge only origin/...)" % bad[0] if bad else None
    if sub == "rebase":
        flag = _flags_outside(args, REBASE_FLAGS)
        if flag:
            return "git rebase %s" % flag
        bad = [r for r in pos if not ORIGIN_REF.match(r)]
        return "git rebase onto %s (routines rebase only onto origin/...)" % bad[0] if bad or len(pos) > 1 else None
    if sub == "pull":
        flag = _flags_outside(args, PULL_FLAGS)
        if flag:
            return "git pull %s" % flag
        return None if pos in ([], ["origin"], ["origin", "main"]) else (
            "git pull %s (routines pull only from origin main)" % " ".join(pos))
    if sub == "fetch":
        flag = _flags_outside(args, FETCH_FLAGS, FETCH_VALUE_FLAGS)
        if flag:
            return "git fetch %s" % flag
        pos = shell.positional(["git"] + args, value_opts=FETCH_VALUE_FLAGS)
        repo, refspecs = (pos[0] if pos else "origin"), pos[1:]
        if repo == "origin":
            return None if refspecs in ([], ["main"]) else "git fetch origin %s" % " ".join(refspecs)
        if fetch_problem(sub, args, proj):
            return None  # not an allowed source: fetch_problem refuses it with its own reason
        bad = [r for r in refspecs if not RELEASE_REFSPEC.match(r)]
        if bad or not refspecs:
            return "git fetch %s %s (from the upstream, fetch only refs/tags/vX.Y.Z:refs/atlas-upstream/vX.Y.Z)" \
                % (repo[:60], (bad or [""])[0])
        return None
    if sub == "ls-remote":
        flag = _flags_outside(args, LS_REMOTE_FLAGS, ("--sort",))
        if flag:
            return "git ls-remote %s" % flag
        return None  # the repo is checked by fetch_problem
    if sub == "push":
        if "--all" in args or "--tags" in args:
            return "git push %s" % ("--all" if "--all" in args else "--tags")
        refs = shell.positional(["git"] + args, value_opts=("-o", "--push-option"))[1:]
        bad = [r for r in refs if not PUSH_REFSPEC.match(r)]
        return "git push origin %s (routines push only main and pre-update tags)" % bad[0] if bad else None
    if sub == "tag" and any(a in ("-f", "--force") for a in args):
        return "git tag -f (moving a tag)"
    if sub == "remote":
        return None if not args or args[0] in ("-v", "--verbose", "get-url", "show", "add") else \
            "git remote %s" % args[0]  # add: fetch_problem allows only the official upstream
    if sub == "reset":
        cut = args.index("--") if "--" in args else len(args)
        targets = positional(args[:cut])
        if targets and targets[0] not in HEAD_REFS and not ORIGIN_REF.match(targets[0]):
            return "git reset to %s (routines reset only to HEAD or origin/main)" % targets[0]
        return None
    if sub == "revert":
        if any(a in ("--continue", "--abort", "--quit", "--skip") for a in args):
            return None
        owned = atlas.owned_paths(proj)
        for c in shell.positional(["git"] + args, value_opts=("-m", "--mainline", "-X", "--strategy-option",
                                                               "--strategy")):
            rc, out = git(["diff-tree", "--no-commit-id", "--name-only", "-r", "-m", c], cwd)
            if rc != 0:
                return "git revert %s (can't tell what it changes)" % c
            if any(atlas.overlaps(f, e) for f in out.split() for e in owned):
                return "git revert %s (it changes system files, which only atlas-update changes)" % c
    return None


def ls_remote_problem(sub, args, proj):
    """git ls-remote only asks origin or the official upstream (a URL can carry data out)."""
    if sub != "ls-remote":
        return None
    pos = shell.positional(["git"] + args, value_opts=("--sort", "--upload-pack"))
    if any(a.startswith(("--upload-pack", "-u")) for a in args):
        return "git ls-remote --upload-pack"
    if not pos or pos[0] == "origin":
        return None
    upstream = atlas.upstream_slug(proj)
    if GITHUB_URL.match(pos[0]) and atlas.repo_slug(pos[0]) == upstream:
        return None
    return "git ls-remote %s: Atlas asks only its own repo (origin) and the official upstream" % pos[0][:60]


def release_mismatch(proj, cwd, release, include_worktree):
    """In a routine, owned paths may be committed only as the signed release has them, file for file
    (C3). Returns a description of the difference, or None."""
    owned = [e.rstrip("/") for e in atlas.owned_paths(proj)]
    rc, text = git(["show", "%s:system/manifest.yaml" % release], cwd)
    try:
        rel_owned = (atlas.load_yaml_text(text, proj) or {}).get("owned_paths") if rc == 0 else None
    except Exception:
        rel_owned = None
    if not isinstance(rel_owned, list):
        return "%s has no readable owned_paths" % release
    paths = sorted(set(owned) | {str(e).rstrip("/") for e in rel_owned})
    checks = [["diff", "--cached", "--quiet", release, "--"] + paths]
    if include_worktree:
        checks.append(["diff", "--quiet", release, "--"] + paths)
    for args in checks:
        rc, _ = git(args, cwd, timeout=20)
        if rc != 0:
            return "system files differ from %s (a routine commits them only exactly as released)" % release
    if include_worktree:
        rc, out = git(["ls-files", "--others", "--exclude-standard", "--"] + paths, cwd, timeout=20)
        if rc != 0 or out.strip():
            return "there are new files under system paths that %s doesn't have" % release
    return None


def lock_reset(sub, args, proj, ctx):
    """`git reset --hard origin/main` while a valid update lock exists: undoing a failed update."""
    if sub != "reset" or "--hard" not in args:
        return False
    targets = positional(args)
    return bool(targets) and bool(ORIGIN_REF.match(targets[0])) and atlas.update_lock(proj, ctx)[0]


def committed_paths(cwd, include_worktree):
    """Repo-relative paths this commit would include, or None if git can't tell."""
    rc, out = git(["diff", "--cached", "--name-only", "-z"], cwd, timeout=20)
    if rc != 0:
        return None
    paths = set(p for p in out.split("\0") if p)
    if include_worktree:
        for args in (["diff", "--name-only", "-z"], ["ls-files", "--others", "--exclude-standard", "-z"]):
            rc, out = git(args, cwd, timeout=20)
            if rc != 0:
                return None
            paths.update(p for p in out.split("\0") if p)
    return paths


def owned_commit_problem(proj, cwd, include_worktree, message, ctx="chat"):
    """Why this commit may not touch owned paths, or None."""
    paths = committed_paths(cwd, include_worktree)
    if paths is None:
        return "git could not list the files in this commit"
    owned = atlas.owned_paths(proj)
    hits = sorted(p for p in paths if any(atlas.overlaps(p, e) for e in owned))
    if not hits:
        return None
    ok, why, release = atlas.update_lock(proj, ctx)
    actor = re.search(r"(?mi)^Atlas-Actor:[ \t]*(\S+)", message or "")
    if ok and actor and actor.group(1) == "update":
        return release_mismatch(proj, cwd, release, include_worktree) if release else None
    return ("this commit changes system-owned files (%s), which only atlas-update may commit, with "
            "'Atlas-Actor: update' while .atlas-tmp/update.lock is valid (%s)"
            % (", ".join(hits[:5]), why if not ok else "the commit isn't marked Atlas-Actor: update"))


COMMIT_VALUE_OPTS = ("-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c", "--reedit-message",
                     "--author", "--date", "-t", "--template", "--fixup", "--squash", "--cleanup",
                     "--trailer")


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
    actor = re.search(r"(?mi)^Atlas-Actor:[ \t]*(.*?)[ \t]*$", message)
    reason = re.search(r"(?mi)^Atlas-Reason:[ \t]*(\S.*)$", message)
    missing = [n for n, m in (("Atlas-Actor", actor), ("Atlas-Reason", reason)) if not m]
    if missing:
        atlas.block("commit message is missing the %s trailer%s (N12). End the message with:\n"
                   "  Atlas-Actor: chat | routine:<routine-name> | update | setup\n"
                   "  Atlas-Reason: <why, one line>\n"
                   "  Atlas-Records: <ids or paths, or ->\n(format: system/rules/sync.md)"
                   % (" and ".join(missing), "s" if len(missing) > 1 else ""))
    value = actor.group(1).strip()
    if not ACTOR_RE.match(value):
        atlas.block("Atlas-Actor %r is not valid; use chat, routine:<routine-name>, update or setup "
                   "(system/rules/sync.md)." % value)
    if ctx != "chat" and value == "chat":
        atlas.block("this session is marked as a routine (ATLAS_CONTEXT=routine), so it cannot commit as "
                   "'Atlas-Actor: chat'. Use 'Atlas-Actor: routine:<routine-name>' with the name of the "
                   "routine being run (system/rules/sync.md).")


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
        atlas.allow()
    base = atlas.session_cwd(payload, proj)
    bodies = shell.heredoc_bodies(command)
    purge_ok = None
    staged_by_command = False
    warnings = []
    if re.search(r"(^|[\s;&|(])(export\s+)?GIT_[A-Z_]+=", command):
        atlas.STATE.locked = True
        atlas.block("Setting GIT_* variables (config, directories, transport) is not allowed: they can redirect "
                    "where git reads or pushes (N8/N9).")
    for seg in shell.segments(command, base):
        if seg.name == "gh":
            change = gh_change(seg.argv)
            if change:
                atlas.STATE.locked = True
                atlas.block("%s is not allowed: Atlas only reads GitHub through gh, so the repo stays private "
                           "and nothing is copied out (N9). If the user wants a change on GitHub, they make it "
                           "themselves." % change)
            continue
        if seg.name != "git":
            continue
        sub, args = shell.git_subcommand(seg.argv)
        cdir = shell.git_dir_option(seg.argv)
        cwd = os.path.normpath(os.path.join(seg.cwd, os.path.expanduser(cdir))) if cdir else seg.cwd
        if ctx != "chat" and atlas.rel_to_project(cwd, cwd, proj) is None:
            atlas.STATE.locked = True
            atlas.block("In a routine git runs only in the Atlas repo, not in %s." % cwd)
        if sub == "add":
            staged_by_command = True

        identity = remote_change(sub, args)
        if identity:
            atlas.STATE.locked = True
            atlas.block("%s is not allowed: the origin remote identifies this Atlas repo and must not "
                       "change (N8/N9). If the repo moved, tell the user; atlas-health can help." % identity)
        deletion = ref_deletion(sub, args, cwd)
        if deletion:
            what, kind = deletion
            ok_update, _ = atlas.valid_lock(proj, "update")
            ok_purge, _ = atlas.valid_lock(proj, "purge")
            ok_purge = ok_purge and ctx == "chat"
            allowed = (kind == "tag" and (ok_update or ok_purge)) or (kind == "branch" and ok_purge)
            if not allowed:
                atlas.STATE.locked = True
                atlas.block("%s deletes history references, which Atlas never does (N8)%s." % (
                    what, ": tags may only be removed by atlas-update (update lock) or a confirmed purge "
                          "(purge lock, chat)" if kind == "tag" else
                    ": only a user-confirmed purge in a chat may delete branches that exist on origin"))
        push_why = push_problem(sub, args, cwd)
        if push_why:
            atlas.STATE.locked = True
            atlas.block("%s is not allowed: Atlas pushes only to its own repo (origin), so nothing it keeps "
                        "can be copied elsewhere (N9)." % push_why)
        redirect = config_redirect(sub, args, seg.argv)
        fetch_why = fetch_problem(sub, args, proj) or (redirect and (
            "%s would change where git fetches from or pushes to, which Atlas never does" % redirect))
        if fetch_why:
            atlas.STATE.locked = True
            atlas.block("%s (N5)." % fetch_why)
        cfg = config_problem(sub, args, seg.argv)
        if cfg:
            atlas.STATE.locked = True
            atlas.block("%s isn't allowed: it could make git run a program or read and write somewhere "
                        "else, outside the safety checks." % cfg)
        lsr = ls_remote_problem(sub, args, proj)
        if lsr:
            atlas.STATE.locked = True
            atlas.block("%s (N9)." % lsr)
        if ctx != "chat":
            why = routine_problem(sub, args, cwd, proj)
            if why:
                atlas.STATE.locked = True
                atlas.block("In a routine, git keeps to Atlas's own steps (sync, commit, push, and updates "
                            "from signed releases); %s isn't one of them. Do this step another way or leave it "
                            "for a chat (system/rules/sync.md)." % why)
        reason = rewrite_reason(sub, args, cwd)
        if reason and lock_reset(sub, args, proj, ctx):
            reason = None  # undoing a failed update before it is pushed (atlas-update)
        if reason:
            if purge_ok is None:
                ok, why = atlas.valid_lock(proj, "purge")
                if ok and ctx != "chat":
                    ok, why = False, "a purge lock never counts in a routine (ATLAS_CONTEXT=routine)"
                purge_ok, purge_why = ok, why
            if not purge_ok:
                atlas.STATE.locked = True
                atlas.block("%s rewrites history, which Atlas never does (N8). Undo changes with a forward "
                           "revert commit instead (system/rules/sync.md). The only exception is a "
                           "user-confirmed purge through atlas-memory in a chat, while "
                           ".atlas-tmp/purge.lock is valid (%s)." % (reason, purge_why))

        if sub == "commit":
            message, why = commit_message(args, cwd, bodies)
            if message is None:
                warnings.append("could not read the commit message (%s); make sure it has "
                                "Atlas-Actor and Atlas-Reason trailers" % why)
            else:
                check_trailers(message, ctx)
            include_wt = staged_by_command or "--" in args or bool(
                shell.positional(["git"] + args, value_opts=COMMIT_VALUE_OPTS)) or any(
                a.startswith("--pathspec-from-file") for a in args) or any(
                a in ("-a", "--all", "--include", "-i", "--only", "-o") or
                (re.match(r"^-[a-zA-Z]+$", a) and "a" in a and not a.startswith("-m"))
                for a in args)
            owned_why = owned_commit_problem(proj, cwd, include_wt, message, ctx)
            if owned_why:
                atlas.STATE.locked = True
                atlas.block("%s (N5). If a system file needs fixing, record it for atlas-health, which "
                           "restores system files from the release." % owned_why)
            found = scan_for_secrets(cwd, include_wt)
            if found:
                atlas.STATE.locked = True
                atlas.block("possible secrets in this commit (N10): %s. Remove them from the files "
                           "(store a pointer such as 'password kept in the user's password manager' "
                           "instead), unstage, and commit again. Never commit passwords, tokens or keys."
                           % "; ".join(found[:8]))
    atlas.allow("; ".join(warnings) if warnings else None)


if __name__ == "__main__":
    try:
        atlas.run("git", main)
    except SystemExit as _exit:
        if _exit.code in (0, 2, None):
            raise
        fail_safe("git", RuntimeError("unexpected exit code %r" % (_exit.code,)), _raw_stdin())
    except BaseException as _err:
        fail_safe("git", _err, _raw_stdin())
