"""Atlas hooks: pragmatic shell-command analysis for Bash tool calls.

Used by actions.py (deletes under user/), paths.py (writes to owned and
governance paths) and git.py (git subcommands). Not a hook itself.

What it understands: command separators (; && || | & newlines, subshell
parentheses), leading VAR=value assignments, wrappers (sudo, env, command,
nohup, time, xargs), `bash -c` / `sh -c` / `eval` strings (recursively),
`cd` within one command line, output redirections (> >> >| &> &>> <>), and
heredoc bodies (removed before tokenizing; kept for commit messages).

Known limits (covered by the hook tests on the maintainers branch): variables and command
substitutions are not expanded, globs are reduced to their literal prefix,
and writes made by interpreters (python -c, node -e, perl without -i, awk
with redirection inside its program) are not detected. In routines these
limits don't matter: commands.py allows only commands whose effects this
module can see, and blocks expansions and interpreters outright.
"""
import os
import re
import shlex

SEPARATORS = {";", "&&", "||", "|", "&", "\n", "(", ")", "|&", ";;"}
SEPARATOR_CHARS = set(";&|()\n")


def is_separator(token):
    """True for an operator token that ends a command. shlex groups adjacent
    punctuation, so a blank line arrives as '\n\n' and 'cmd;' + newline as
    ';\n': any token made only of separator characters ends the command."""
    return token in SEPARATORS or (bool(token) and set(token) <= SEPARATOR_CHARS)
REDIRECTS = {">", ">>", ">|", "&>", "&>>", "<>", ">&"}
WRAPPERS = {"sudo", "env", "command", "nohup", "time", "nice", "xargs", "builtin", "exec", "stdbuf", "timeout"}
SHELLS = {"bash", "sh", "zsh", "dash"}
HEREDOC_RE = re.compile(r"<<(?P<dash>-?)[ \t]*(?P<q>['\"]?)(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?P=q)(?P<rest>[^\n]*)\n"
                        r"(?P<body>.*?)\n[ \t]*(?P=name)[ \t]*(?=\n|$)", re.S)


class Segment:
    """One simple command: argv words plus output redirection targets.
    'overwrites' are the redirect targets that truncate (>, >|, &>, <>; not >>),
    'wrappers' the wrapper commands stripped from the front (xargs, env, ...)."""

    def __init__(self, argv, redirects, cwd, overwrites=None, wrappers=None, assigns=None):
        self.argv = argv
        self.redirects = redirects
        self.cwd = cwd
        self.overwrites = overwrites or []
        self.wrappers = wrappers or []
        self.assigns = assigns or []  # NAME=value words before the command

    @property
    def name(self):
        return os.path.basename(self.argv[0]) if self.argv else ""

    def __repr__(self):
        return "Segment(%r, redirects=%r, cwd=%r)" % (self.argv, self.redirects, self.cwd)


def heredoc_bodies(command):
    return [m.group("body") for m in HEREDOC_RE.finditer(command)]


def strip_heredocs(command):
    # keep the whole operator line (commands can follow the delimiter on it: `cat <<EOF | x`),
    # drop the body and terminator
    return HEREDOC_RE.sub(lambda m: "<<" + m.group("dash") + m.group("name") + m.group("rest") + "\n", command)


def tokenize(command):
    """Shell-like tokens; operators are separate tokens. Never raises."""
    text = strip_heredocs(command).replace("\\\n", "")  # backslash-newline joins lines, as in the shell
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


def _strip_prefix(argv, wrappers=None, assigns=None):
    """Drop VAR=value assignments and wrapper commands from the front
    (appended to 'assigns' and 'wrappers' when given)."""
    i = 0
    while i < len(argv):
        w = argv[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            if assigns is not None:
                assigns.append(w)
            i += 1
            continue
        base = os.path.basename(w)
        if base in WRAPPERS:
            if wrappers is not None:
                wrappers.append(base)
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
    cur, redirects, overwrites = [], [], []
    cur_cwd = cwd
    i = 0

    def flush():
        nonlocal cur, redirects, overwrites, cur_cwd
        wrappers, assigns = [], []
        argv = _strip_prefix(cur, wrappers, assigns)
        if argv:
            name = os.path.basename(argv[0])
            if name == "cd":
                target = argv[1] if len(argv) > 1 else os.path.expanduser("~")
                if not re.search(r"[$`*?]", target):
                    t = os.path.expanduser(target)
                    cur_cwd = os.path.normpath(os.path.join(cur_cwd, t))
            elif name in SHELLS and "-c" in argv[1:] and _depth < 3:
                idx = argv.index("-c")
                # the shell itself is kept too, so a caller can refuse shells outright
                out.append(Segment(argv[:idx + 1], redirects, cur_cwd, overwrites, wrappers))
                if idx + 1 < len(argv):
                    out.extend(segments(argv[idx + 1], cur_cwd, _depth + 1))
            elif name == "eval" and len(argv) > 1 and _depth < 3:
                out.append(Segment(["eval"], redirects, cur_cwd, overwrites, wrappers))
                out.extend(segments(" ".join(argv[1:]), cur_cwd, _depth + 1))
            else:
                out.append(Segment(argv, redirects, cur_cwd, overwrites, wrappers, assigns))
        elif redirects or assigns:
            out.append(Segment([], redirects, cur_cwd, overwrites, wrappers, assigns))
        cur, redirects, overwrites = [], [], []

    while i < len(tokens):
        t = tokens[i]
        if is_separator(t):
            flush()
        elif t in REDIRECTS or re.match(r"^[<>&|]+$", t) and ">" in t:
            target = tokens[i + 1] if i + 1 < len(tokens) else ""
            # '>&1', '2>&-' style fd duplication is not a file write
            if t in (">&",) and re.match(r"^(\d+|-)$", target):
                i += 2
                continue
            if cur and re.match(r"^\d+$", cur[-1]):
                cur.pop()  # the fd number in '2>file'
            if target and not is_separator(target):
                redirects.append(target)
                if ">>" not in t:
                    overwrites.append(target)
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
            script_given = any(a in ("-e", "-f") or a.startswith(("--expression", "--file")) for a in argv[1:])
            pos = positional(argv, value_opts=("-e", "--expression", "-f", "--file", "-l", "--line-length"))
            files = pos if script_given else pos[1:]
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
    elif name in ("curl", "wget", "wget2"):
        writes += download_targets(argv)
    elif name == "sort":
        o = option_value(argv, "-o", "--output")
        if o:
            writes.append(o)
    elif name == "uniq":
        pos = positional(argv, value_opts=("-f", "-s", "-w", "--skip-fields", "--skip-chars", "--check-chars"))
        if len(pos) >= 2:
            writes.append(pos[1])
    elif name == "mktemp":
        # no template: the system temp folder; -t: under $TMPDIR; -p DIR: in DIR
        d = option_value(argv, "-p", "--tmpdir")
        pos = positional(argv, value_opts=("-p", "--suffix"))
        if d:
            writes.append(d)
        elif pos and "-t" not in argv:
            writes.append(pos[0])
    elif PYTHON_RE.match(name):
        writes += python_writes(argv, seg.cwd)
    elif name == "tar":
        if any(re.match(r"^-?[a-zA-Z]*x", a) for a in argv[1:2]) or "--extract" in argv or "-x" in argv:
            d = option_value(argv, "-C", "--directory")
            writes.append(d if d else ".")
    elif name == "git" and len(argv) > 1:
        sub, sargs = git_subcommand(argv)
        listed = pathspec_file(sargs, seg.cwd)
        out_file = option_value(["git"] + sargs, "-o" if sub == "format-patch" else None, "--output") \
            if sub in ("diff", "log", "show", "format-patch", "diff-tree", "range-diff") else None
        if out_file:
            writes.append(out_file)
        if sub == "rm":
            deletes += [a for a in positional(["git"] + sargs,
                                              value_opts=("--pathspec-from-file",))] + listed
        elif sub == "mv":
            pos = positional(["git"] + sargs)
            if len(pos) >= 2:
                writes.append(pos[-1])
                deletes += pos[:-1]
        elif sub in ("checkout", "restore"):
            writes += listed
            if "--" in sargs:
                writes += sargs[sargs.index("--") + 1:]
            elif sub == "restore":
                writes += positional(["git"] + sargs, value_opts=("-s", "--source", "--pathspec-from-file"))
        elif sub == "clean" and any(re.match(r"^-[a-zA-Z]*f", a) or a == "--force" for a in sargs):
            pos = positional(["git"] + sargs, value_opts=("-e", "--exclude"))
            deletes += pos or ["."]
    return writes, deletes


PYTHON_RE = re.compile(r"^python(3(\.\d+)?)?$")
PYTHON_FLAGS = {"-I", "-B", "-u", "-E", "-s"}
# Atlas's own tools (system/tools/), the only scripts routines may run.
ATLAS_TOOLS = ("validate.py", "normalize.py", "render.py", "release_check.py", "redact_check.py", "index.py")


def python_parts(argv):
    """(flags, script, module, args) for a python command line. script and
    module are None when absent; flags are the interpreter options before them.
    flags may contain anything (e.g. '-c'): callers decide what is allowed."""
    i, flags = 1, []
    while i < len(argv) and argv[i].startswith("-") and argv[i] != "-":
        if argv[i] in ("-m", "-c"):
            if argv[i] == "-m" and i + 1 < len(argv):
                return flags, None, argv[i + 1], argv[i + 2:]
            flags.append(argv[i])
            return flags, None, None, argv[i + 1:]
        flags.append(argv[i])
        i += 1
    if i < len(argv):
        return flags, argv[i], None, argv[i + 1:]
    return flags, None, None, []


def python_writes(argv, cwd):
    """Files Atlas's tools write: render.py's output, normalize.py --fix
    (its files, or its --root), index.py (the index folder, unless --check),
    and `python3 -m zipfile -e <zip> <dir>`."""
    _, script, module, args = python_parts(argv)
    tool = os.path.basename(script) if script else ""
    if tool == "render.py" and len(args) >= 4:
        return [args[3]]
    if tool == "normalize.py" and "--fix" in args:
        root = option_value(["x"] + args, None, "--root")
        files = positional(["x"] + args, value_opts=("--root",))
        return files + ([root] if root else []) or ["user/knowledge"]
    if tool == "index.py" and "--check" not in args:
        root = option_value(["x"] + args, None, "--root")
        return [os.path.join(root or ".", "user", "knowledge", "_index")]
    if module == "zipfile" and args[:1] in (["-e"], ["--extract"]) and len(args) >= 3:
        return [args[-1]]
    return []


def short_value(argv, letter):
    """Value of a one-letter option, also inside a bundle: -o F, -oF, -sSLo F, -qO-."""
    for i, w in enumerate(argv[1:], 1):
        if w.startswith("-") and not w.startswith("--") and len(w) > 1:
            idx = w.find(letter, 1)
            if idx > 0 and (idx == 1 or w[1:idx].isalpha()):
                rest = w[idx + 1:]
                return rest if rest else (argv[i + 1] if i + 1 < len(argv) else None)
    return None


def download_targets(argv):
    """Files curl/wget write: -o/--output, wget -O/-P, and the URL's own file
    name for curl -O / --remote-name and plain wget."""
    name = os.path.basename(argv[0])
    out = []
    urls = [a for a in argv[1:] if re.match(r"^[a-z][a-z0-9+.-]*://", a, re.I)]

    def url_file(u):
        path = re.sub(r"^[a-z][a-z0-9+.-]*://[^/]*", "", u, flags=re.I).split("?")[0].split("#")[0]
        return os.path.basename(path) or "index.html"

    if name == "curl":
        o = short_value(argv, "o") or option_value(argv, None, "--output")
        if o and o != "-":
            out.append(o)
        if any(a in ("--remote-name", "--remote-name-all") or re.match(r"^-[a-zA-Z]*O", a) for a in argv[1:]):
            out += [url_file(u) for u in urls]
        return out
    o = short_value(argv, "O") or option_value(argv, None, "--output-document")
    p = short_value(argv, "P") or option_value(argv, None, "--directory-prefix")
    if o and o != "-":
        out.append(o)
    elif not o:
        out += [os.path.join(p or "", url_file(u)) for u in urls] or ([p] if p else [])
    return out


def pathspec_file(sargs, cwd):
    """Paths listed in a git --pathspec-from-file file. A list that can't be
    read (stdin, missing file) counts as the whole repo: fail closed."""
    f = option_value(["git"] + sargs, None, "--pathspec-from-file")
    if f is None:
        return []
    if f == "-":
        return ["."]
    try:
        with open(os.path.join(cwd, os.path.expanduser(f)), encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return ["."]
    sep = "\0" if "--pathspec-file-nul" in sargs else "\n"
    return [p.strip() for p in text.split(sep) if p.strip()] or []


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
