"""Atlas hooks: pragmatic shell-command analysis for Bash tool calls.

Used by actions.py (deletes under user/), paths.py (writes to owned and
governance paths) and git.py (git subcommands). Not a hook itself.

What it understands: command separators (; && || | & newlines, subshell
parentheses), leading VAR=value assignments, wrappers (sudo, env, command,
nohup, time, xargs), `bash -c` / `sh -c` / `eval` strings (recursively),
`cd` within one command line, output redirections (> >> >| &> &>> <>), and
heredoc bodies (removed before tokenizing; kept for commit messages).

Known limits (documented in system/tests/README.md): variables and command
substitutions are not expanded, globs are reduced to their literal prefix,
and writes made by interpreters (python -c, node -e, perl without -i, awk
with redirection inside its program) are not detected.
"""
import os
import re
import shlex

SEPARATORS = {";", "&&", "||", "|", "&", "\n", "(", ")", "|&", ";;"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", "<>", ">&"}
WRAPPERS = {"sudo", "env", "command", "nohup", "time", "nice", "xargs", "builtin", "exec", "stdbuf", "timeout"}
SHELLS = {"bash", "sh", "zsh", "dash"}
HEREDOC_RE = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2[^\n]*\n(.*?)\n[ \t]*\3[ \t]*(?=\n|$)", re.S)


class Segment:
    """One simple command: argv words plus output redirection targets."""

    def __init__(self, argv, redirects, cwd):
        self.argv = argv
        self.redirects = redirects
        self.cwd = cwd

    @property
    def name(self):
        return os.path.basename(self.argv[0]) if self.argv else ""

    def __repr__(self):
        return "Segment(%r, redirects=%r, cwd=%r)" % (self.argv, self.redirects, self.cwd)


def heredoc_bodies(command):
    return [m.group(4) for m in HEREDOC_RE.finditer(command)]


def strip_heredocs(command):
    # keep the operator line, drop the body and terminator
    return HEREDOC_RE.sub(lambda m: "<<" + m.group(1) + m.group(3) + "\n", command)


def tokenize(command):
    """Shell-like tokens; operators are separate tokens. Never raises."""
    text = strip_heredocs(command)
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=";&|<>()\n")
        lex.whitespace = " \t\r"
        lex.whitespace_split = True
        lex.commenters = ""
        return list(lex)
    except ValueError:
        # unbalanced quotes etc.: crude fallback that over-reports words
        spaced = re.sub(r"(&&|\|\||[;|&()<>\n])", r" \1 ", text)
        return [t.strip("'\"") for t in spaced.split(" ") if t]


def _strip_prefix(argv):
    """Drop VAR=value assignments and wrapper commands from the front."""
    i = 0
    while i < len(argv):
        w = argv[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            i += 1
            continue
        base = os.path.basename(w)
        if base in WRAPPERS:
            i += 1
            # skip wrapper options and their simple values (e.g. timeout 10, env -u X)
            while i < len(argv) and (argv[i].startswith("-") or re.match(r"^\d+[smhd]?$", argv[i])):
                i += 1
            continue
        break
    return argv[i:]


def segments(command, cwd, _depth=0):
    """Split a command line into Segments, tracking `cd` and recursing into
    `bash -c` strings and `eval`."""
    tokens = tokenize(command)
    out = []
    cur, redirects = [], []
    cur_cwd = cwd
    i = 0

    def flush():
        nonlocal cur, redirects, cur_cwd
        argv = _strip_prefix(cur)
        if argv:
            name = os.path.basename(argv[0])
            if name == "cd":
                target = argv[1] if len(argv) > 1 else os.path.expanduser("~")
                if not re.search(r"[$`*?]", target):
                    t = os.path.expanduser(target)
                    cur_cwd = os.path.normpath(os.path.join(cur_cwd, t))
            elif name in SHELLS and "-c" in argv[1:] and _depth < 3:
                idx = argv.index("-c")
                if idx + 1 < len(argv):
                    out.extend(segments(argv[idx + 1], cur_cwd, _depth + 1))
            elif name == "eval" and len(argv) > 1 and _depth < 3:
                out.extend(segments(" ".join(argv[1:]), cur_cwd, _depth + 1))
            else:
                out.append(Segment(argv, redirects, cur_cwd))
        elif redirects:
            out.append(Segment([], redirects, cur_cwd))
        cur, redirects = [], []

    while i < len(tokens):
        t = tokens[i]
        if t in SEPARATORS:
            flush()
        elif t in REDIRECTS or re.match(r"^[<>&|]+$", t) and ">" in t:
            target = tokens[i + 1] if i + 1 < len(tokens) else ""
            # '>&1', '2>&-' style fd duplication is not a file write
            if t in (">&",) and re.match(r"^(\d+|-)$", target):
                i += 2
                continue
            if cur and re.match(r"^\d+$", cur[-1]):
                cur.pop()  # the fd number in '2>file'
            if target and target not in SEPARATORS:
                redirects.append(target)
                i += 2
                continue
        elif t.startswith("<"):
            # input redirection / heredoc operator: skip its word
            i += 2
            continue
        else:
            cur.append(t)
        i += 1
    flush()
    return out


def has_glob(word):
    return bool(re.search(r"[*?\[]", word))


def literal_prefix(word):
    """For 'system/*.md' return 'system/'; for '*' return ''."""
    m = re.search(r"[*?\[]", word)
    if not m:
        return word
    pre = word[:m.start()]
    return pre[: pre.rfind("/") + 1] if "/" in pre else ""


def unresolvable(word):
    return "$" in word or "`" in word


def positional(argv, value_opts=()):
    """Non-option words after argv[0]; honors '--'. value_opts consume the
    next word (e.g. '-t' for cp)."""
    out, i, opts_done = [], 1, False
    while i < len(argv):
        w = argv[i]
        if not opts_done and w == "--":
            opts_done = True
        elif not opts_done and w.startswith("-") and w != "-":
            if w in value_opts:
                i += 1
        else:
            out.append(w)
        i += 1
    return out


def option_value(argv, short, long=None):
    """Value for -x VALUE / -xVALUE / --long=VALUE / --long VALUE."""
    for i, w in enumerate(argv):
        if w == short or (long and w == long):
            return argv[i + 1] if i + 1 < len(argv) else None
        if long and w.startswith(long + "="):
            return w.split("=", 1)[1]
        if short and len(short) == 2 and w.startswith(short) and len(w) > 2 and not w.startswith("--"):
            return w[2:]
    return None


def write_targets(seg):
    """Paths a segment may create, overwrite, move or delete.

    Returns (writes, deletes): lists of words (possibly relative / globbed)."""
    writes = list(seg.redirects)
    deletes = []
    argv = seg.argv
    if not argv:
        return writes, deletes
    name = seg.name
    args = positional(argv)

    if name == "tee":
        writes += args
    elif name in ("sed", "perl", "ruby"):
        if any(a == "-i" or a.startswith("-i") or a.startswith("--in-place") or
               (re.match(r"^-[a-zA-Z]*i", a) and not a.startswith("--")) for a in argv[1:]):
            # first positional is the script for sed unless -e/-f given
            script_given = any(a in ("-e", "-f") or a.startswith("--expression") for a in argv[1:])
            files = args if script_given else args[1:]
            writes += files
    elif name in ("cp", "install", "rsync", "ln", "link"):
        t = option_value(argv, "-t", "--target-directory")
        if t:
            writes.append(t)
        else:
            pos = positional(argv, value_opts=("-t", "-S", "--suffix", "-m", "-o", "-g"))
            if len(pos) >= 2:
                writes.append(pos[-1])
    elif name == "mv":
        t = option_value(argv, "-t", "--target-directory")
        pos = positional(argv, value_opts=("-t", "-S", "--suffix"))
        if t:
            writes.append(t)
            deletes += pos
        elif len(pos) >= 2:
            writes.append(pos[-1])
            deletes += pos[:-1]
    elif name in ("rm", "unlink", "rmdir", "shred", "srm"):
        deletes += args
    elif name in ("touch", "mkdir", "truncate", "chmod", "chown", "chgrp", "setfacl"):
        pos = args
        if name in ("chmod", "chown", "chgrp") and pos:
            pos = pos[1:]
        if name == "truncate":
            pos = positional(argv, value_opts=("-s", "--size", "-r", "--reference"))
        writes += pos
    elif name == "dd":
        writes += [a[3:] for a in argv[1:] if a.startswith("of=")]
    elif name == "find":
        if "-delete" in argv or any(a in ("-exec", "-execdir") and j + 1 < len(argv) and
                                    os.path.basename(argv[j + 1]) in ("rm", "shred", "unlink")
                                    for j, a in enumerate(argv)):
            roots = []
            for a in argv[1:]:
                if a.startswith("-") or a in ("(", "!"):
                    break
                roots.append(a)
            deletes += roots or ["."]
    elif name == "unzip":
        d = option_value(argv, "-d")
        writes.append(d if d else ".")
    elif name == "tar":
        if any(re.match(r"^-?[a-zA-Z]*x", a) for a in argv[1:2]) or "--extract" in argv or "-x" in argv:
            d = option_value(argv, "-C", "--directory")
            writes.append(d if d else ".")
    elif name == "git" and len(argv) > 1:
        sub, sargs = git_subcommand(argv)
        if sub == "rm":
            deletes += [a for a in positional(["git"] + sargs)]
        elif sub == "mv":
            pos = positional(["git"] + sargs)
            if len(pos) >= 2:
                writes.append(pos[-1])
                deletes += pos[:-1]
        elif sub in ("checkout", "restore"):
            if "--" in sargs:
                writes += sargs[sargs.index("--") + 1:]
            elif sub == "restore":
                writes += positional(["git"] + sargs, value_opts=("-s", "--source"))
        elif sub == "clean" and any(re.match(r"^-[a-zA-Z]*f", a) or a == "--force" for a in sargs):
            pos = positional(["git"] + sargs, value_opts=("-e", "--exclude"))
            deletes += pos or ["."]
    return writes, deletes


def copy_sources(seg):
    """Source words of cp/mv/install/ln/rsync/git mv (to expand a directory
    destination into dest/<basename>), or [] for other commands."""
    argv = seg.argv
    name = seg.name
    if name == "git":
        sub, sargs = git_subcommand(argv)
        if sub != "mv":
            return []
        argv, name = ["git"] + sargs, "mv"
    if name not in ("cp", "mv", "install", "ln", "link", "rsync"):
        return []
    if option_value(argv, "-t", "--target-directory"):
        return positional(argv, value_opts=("-t", "-S", "--suffix", "-m", "-o", "-g"))
    pos = positional(argv, value_opts=("-t", "-S", "--suffix", "-m", "-o", "-g"))
    return pos[:-1] if len(pos) >= 2 else []


GIT_GLOBAL_VALUE_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def git_subcommand(argv):
    """('push', [args...]) for ['git', '-C', 'x', 'push', ...]."""
    i = 1
    while i < len(argv):
        w = argv[i]
        if w in GIT_GLOBAL_VALUE_OPTS:
            i += 2
            continue
        if w.startswith("-"):
            i += 1
            continue
        return w, argv[i + 1:]
    return "", []


def git_dir_option(argv):
    """The -C directory of a git invocation, if any."""
    i = 1
    while i < len(argv):
        if argv[i] == "-C" and i + 1 < len(argv):
            return argv[i + 1]
        if not argv[i].startswith("-"):
            break
        i += 2 if argv[i] in GIT_GLOBAL_VALUE_OPTS else 1
    return None
