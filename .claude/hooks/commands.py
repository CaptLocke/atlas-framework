"""Atlas hooks: what a routine's shell may run.

Used by actions.py for Bash/Monitor calls in routines; not a hook itself.

Routines run unattended on content Atlas doesn't control (email, documents,
web pages), so their shell is limited to commands whose effects shell.py can
see. Everything else is blocked, however it is written:
- only the command names in ALLOWED, called by bare name (no paths, so a
  copied binary can't pose as `ls`), plus Atlas's own Python tools;
- no command or process substitution, backticks, arithmetic or brace
  expansion, and no variables except the read-only names in SAFE_VARS; the
  one exception is `$(cat <<'EOF' ... EOF)`, the usual form of a commit message;
- no xargs or sudo, no shells (bash, sh, `bash -c`) and no eval: their
  strings hide expansions from the checks above;
- sed and awk only with programs that can't write files or run commands, and
  find without -exec, -ok or -fprint;
- no links (ln, cp -s/-l): a link could point a write outside the repo.
The paths these commands write or delete are still checked by paths.py (N5,
N6, writes outside the repo) and actions.py (deletes under user/); curl and
wget hosts by actions.py; git and gh by git.py.
"""
import os
import re

import shell

ALLOWED = {
    # reading and text
    "ls", "cat", "head", "tail", "wc", "grep", "egrep", "fgrep", "sort", "uniq", "cut", "tr", "comm", "diff",
    "cmp", "stat", "file", "du", "df", "date", "echo", "printf", "pwd", "basename", "dirname", "realpath",
    "readlink", "true", "false", "test", "[", ":", "sleep", "which", "md5sum", "sha1sum", "sha256sum",
    "column", "nl", "tac", "paste", "join", "fold", "seq", "printenv", "id", "whoami", "hostname", "uname",
    "od", "jq", "base64", "zcat", "sed", "awk", "find",
    # shell state
    "cd", "export", "unset", "set",
    # simple file work (targets checked by paths.py and actions.py)
    "mkdir", "touch", "cp", "mv", "rm", "rmdir", "unlink", "tee", "mktemp",
    # checked by their own rules
    "git", "gh", "curl", "wget", "wget2",
}
SAFE_VARS = {"ATLAS_CONTEXT", "HOME", "PWD", "CLAUDE_PROJECT_DIR", "TZ", "USER", "TMPDIR", "?"}
BLOCKED_WRAPPERS = {"xargs", "sudo", "env", "exec", "builtin"}  # their options can rename or hide the command
# Variables a routine may set for one command (PATH, HOME and the like would change what runs or which
# config git reads).
SAFE_ASSIGN = {"TZ", "LANG", "LC_ALL", "LC_CTYPE", "LC_MESSAGES", "LC_COLLATE", "TERM", "NO_COLOR", "COLUMNS"}
FIND_ACTIONS = {"-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprint0", "-fprintf", "-fls"}
AWK_RISKY = re.compile(r"system|getline|close|fflush|ENVIRON|PROCINFO|@load|@include|[|>]")
HEREDOC_CAT = re.compile(r"\$\(\s*cat\s+<<-?\s*['\"]?[A-Za-z_][A-Za-z0-9_]*['\"]?\s*\)")


def expansion_problem(command):
    """Why the command line uses shell expansion a routine may not, or None."""
    for m in shell.HEREDOC_RE.finditer(command):
        if not m.group("q") and re.search(r"\$\(|`", m.group("body")):
            return "a command substitution inside a heredoc"
    text = shell.strip_heredocs(command)
    i, n, sq, dq = 0, len(text), False, False
    while i < n:
        c = text[i]
        if sq:
            sq = c != "'"
        elif c == "\\":
            i += 2
            continue
        elif c == "'" and not dq:
            sq = True
        elif c == '"':
            dq = not dq
        elif c == "`":
            return "backticks (command substitution)"
        elif c in "<>" and text[i + 1:i + 2] == "(" and not dq:
            return "process substitution %s(...)" % c
        elif c == "{" and not dq:
            end = re.match(r"\{[^\s{}]*\}", text[i:])
            if end and ("," in end.group(0) or ".." in end.group(0)):
                return "brace expansion %s" % end.group(0)
        elif c == "$":
            nxt = text[i + 1:i + 2]
            if nxt == "(":
                m = HEREDOC_CAT.match(text, i)
                if m:
                    i = m.end()
                    continue
                return "command substitution $(...)" if text[i + 2:i + 3] != "(" else "arithmetic $((...))"
            if nxt == "'" and not dq:
                sq = True  # $'...' quoting: a literal string
                i += 2
                continue
            name = None
            if nxt == "{":
                m = re.match(r"\$\{([A-Za-z_][A-Za-z0-9_]*|\?)\}", text[i:])
                name = m.group(1) if m else text[i:i + 12] + "..."
            else:
                m = re.match(r"\$([A-Za-z_][A-Za-z0-9_]*|[?@*#!$0-9-])", text[i:])
                name = m.group(1) if m else None
            if name is not None and name not in SAFE_VARS:
                return "the variable $%s (routines expand only %s)" % (
                    name, ", ".join("$" + v for v in sorted(SAFE_VARS)))
        i += 1
    return None


def _skip_sed_address(s, i):
    n = len(s)
    for _ in range(2):
        if i < n and s[i].isdigit():
            while i < n and (s[i].isdigit() or s[i] == "~"):
                i += 1
        elif i < n and s[i] == "$":
            i += 1
        elif i < n and s[i] in "/\\":
            d = "/" if s[i] == "/" else (s[i + 1] if i + 1 < n else "/")
            i += 1 if s[i] == "/" else 2
            while i < n and s[i] != d:
                i += 2 if s[i] == "\\" else 1
            i += 1
            while i < n and s[i] in "IM":
                i += 1
        if i < n and s[i] in ",+~":
            i += 1
            continue
        break
    return i


def sed_script_ok(s):
    """False when a sed program could run a command (e, s///e) or write a file (w, W, s///w)."""
    i, n = 0, len(s)
    while i < n:
        while i < n and s[i] in " \t\n;":
            i += 1
        if i >= n:
            break
        i = _skip_sed_address(s, i)
        while i < n and s[i] in " \t!":
            i += 1
        if i >= n:
            break
        c = s[i]
        if c in "{}":
            i += 1
            continue
        if c in "ewW":
            return False
        if c in "sy":
            d = s[i + 1] if i + 1 < n else ""
            if not d or d in "\\\n":
                return False
            j, parts = i + 2, 0
            while j < n and parts < 2:
                if s[j] == "\\":
                    j += 2
                    continue
                if s[j] == d:
                    parts += 1
                j += 1
            k = j
            while k < n and s[k] not in ";\n}":
                k += 1
            if c == "s" and re.search(r"[ewW]", s[j:k]):
                return False
            i = k
            continue
        # any other command: a/i/c text and r/R file names run to the end of the
        # line; the rest (p d q b t : = l n N g G h H x z D P F Q T) to ; or newline
        i += 1
        if c in "aicrR":
            while i < n and s[i] != "\n":
                i += 1
        else:
            while i < n and s[i] not in ";\n}":
                i += 1
    return True


def sed_problem(argv):
    scripts, i, files_opt = [], 1, False
    while i < len(argv):
        a = argv[i]
        if a in ("-e", "--expression"):
            scripts.append(argv[i + 1] if i + 1 < len(argv) else "")
            i += 2
            continue
        if a.startswith("--expression="):
            scripts.append(a.split("=", 1)[1])
        elif a in ("-f", "--file") or a.startswith("--file=") or re.match(r"^-[a-zA-Z]*f", a):
            files_opt = True
        i += 1
    if files_opt:
        return "sed -f (a script file)"
    if not scripts:
        pos = shell.positional(argv, value_opts=("-l", "--line-length"))
        scripts = pos[:1]
    if any(not sed_script_ok(s) for s in scripts):
        return "a sed program that runs commands or writes files (e, w, s///e, s///w)"
    return None


def awk_problem(argv):
    if any(a in ("-f", "--file", "-i", "--include", "-l", "--load", "-E", "--exec") or
           a.startswith(("--file=", "--include=", "--load=", "--exec=")) for a in argv[1:]):
        return "awk with a program file or extension"
    pos = shell.positional(argv, value_opts=("-F", "-v", "--field-separator", "--assign"))
    if pos and AWK_RISKY.search(pos[0]):
        return ("an awk program that could run commands or write files (it uses system, getline, a pipe or "
                "'>'); for comparisons use grep or sort, or read the file with the Read tool")
    return None


def python_problem(seg, proj):
    flags, script, module, args = shell.python_parts(seg.argv)
    if any(f not in shell.PYTHON_FLAGS for f in flags):
        return "python %s" % " ".join(f for f in flags if f not in shell.PYTHON_FLAGS)
    if module is not None:
        if module == "zipfile" and args[:1] in (["-e"], ["--extract"], ["-l"], ["--list"], ["-t"], ["--test"]):
            return None
        return "python -m %s" % module
    if script is None:
        return "python reading a program from stdin"
    path = os.path.realpath(os.path.join(seg.cwd, os.path.expanduser(script)))
    tools = os.path.realpath(os.path.join(proj, "system", "tools"))
    if os.path.dirname(path) == tools and os.path.basename(path) in shell.ATLAS_TOOLS:
        return None
    return "python running %s (routines run only Atlas's tools in system/tools/)" % script


def segment_problem(seg, proj):
    """Why one simple command isn't allowed in a routine, or None."""
    names = [a.split("=", 1)[0] for a in seg.assigns]
    if seg.argv and seg.name in ("export", "readonly"):
        names += [a.split("=", 1)[0] for a in seg.argv[1:] if "=" in a]
    bad = [n for n in names if n not in SAFE_ASSIGN]
    if bad:
        return "setting the variable %s (routines set only %s)" % (bad[0], ", ".join(sorted(SAFE_ASSIGN)))
    if not seg.argv:
        return None
    blocked = [w for w in seg.wrappers if w in BLOCKED_WRAPPERS]
    if blocked:
        return "%s (it runs commands the guard can't see)" % blocked[0]
    word = seg.argv[0]
    if "/" in word:
        return "running %s by path (call commands by name)" % word
    name = seg.name
    if shell.PYTHON_RE.match(name):
        return python_problem(seg, proj)
    if name not in ALLOWED:
        return "%s isn't one of the commands routines may run" % name
    if name == "sed":
        return sed_problem(seg.argv)
    if name == "awk":
        return awk_problem(seg.argv)
    if name == "find":
        hit = [a for a in seg.argv[1:] if a in FIND_ACTIONS]
        if hit:
            return "find %s" % hit[0]
    if name == "cp" and any(a in ("-s", "-l", "--symbolic-link", "--link") or
                            re.match(r"^-[a-zA-Z]*[sl]", a) and not a.startswith("--") for a in seg.argv[1:]):
        return "cp making links"
    if name == "sort" and any(a.startswith("--compress-program") for a in seg.argv[1:]):
        return "sort --compress-program (it runs a program)"
    if name == "cd" and any("$" in a for a in seg.argv[1:]):
        return "cd to a variable"
    return None


def problem(command, cwd, proj):
    """Why a routine may not run this command line, or None."""
    why = expansion_problem(command)
    if why:
        return why
    for seg in shell.segments(command, cwd):
        why = segment_problem(seg, proj)
        if why:
            return why
    return None
