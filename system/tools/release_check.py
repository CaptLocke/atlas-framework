#!/usr/bin/env python3
"""Atlas release check: verify that a release tag was signed by Atlas's maker,
and restore Atlas's system files from it.

Standard library only (no ssh-keygen needed). Two uses:

  python3 -I system/tools/release_check.py verify <ref> <tag>
      atlas-update, before taking any file from a fetched release. Exit 0 and
      print the release commit when <ref> is an annotated tag named <tag>,
      signed by a key in SIGNERS; exit 1 otherwise.

  python3 -I /opt/atlas/release_check.py
      The first step of every Atlas routine (its prompt says so). The "Atlas
      routine" environment's setup script writes this file to /opt/atlas, outside
      the repo, so a chat can't change it (atlas-setup reference/automations.md
      §3). It fetches the installed version's tag from UPSTREAM, verifies it,
      and puts the system-owned files back to that release (committing and
      pushing the repair), so the routine runs the released hooks even if a chat
      changed them. Prints one status line, writes .atlas-tmp/release-check.json,
      and always exits 0.

Signatures are git's SSH signatures (ssh-keygen -Y sign, namespace "git") made
with Ed25519 keys. Replacing a key is a release, signed by a key users already
trust, that changes SIGNERS; users then paste the new setup script.
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import time

UPSTREAM = "CaptLocke/atlas-framework"
SIGNERS = (  # ssh-ed25519 public keys: main, then offline backup
    "AAAAC3NzaC1lZDI1NTE5AAAAIP5zeqZrVr4K4Im8koRm5jkuyjjYciof5oxbAGEFUArK",
    "AAAAC3NzaC1lZDI1NTE5AAAAIF8Eax3RKJZebfTKRZP2zsU/BKc5aBvsFL99/Ul5i/0b",
)
MIN_VERSION = (1, 0, 1)  # the routine check never restores a release older than this (raise it on re-paste)
TAG_NAME = re.compile(r"^v\d+\.\d+\.\d+(-rc\.\d+)?$")
STATUS_FILE = ".atlas-tmp/release-check.json"
UPSTREAM_URL = None  # tests only; the real check always fetches github.com/UPSTREAM


class CheckFailed(Exception):
    pass


# --------------------------------------------------------- Ed25519 (RFC 8032)
_P = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _P - 2, _P) % _P
_I = pow(2, (_P - 1) // 4, _P)


def _add(a, b):
    x1, y1, z1, t1 = a
    x2, y2, z2, t2 = b
    A = (y1 - x1) * (y2 - x2) % _P
    B = (y1 + x1) * (y2 + x2) % _P
    C = 2 * t1 * t2 * _D % _P
    Dz = 2 * z1 * z2 % _P
    E, F, G, H = B - A, Dz - C, Dz + C, B + A
    return (E * F % _P, G * H % _P, F * G % _P, E * H % _P)


def _mul(s, p):
    q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            q = _add(q, p)
        p = _add(p, p)
        s >>= 1
    return q


def _equal(a, b):
    return ((a[0] * b[2] - b[0] * a[2]) % _P == 0) and ((a[1] * b[2] - b[1] * a[2]) % _P == 0)


def _decode(s):
    if len(s) != 32:
        return None
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    if y >= _P:
        return None
    x2 = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P) % _P
    if x2 == 0:
        if sign:
            return None
        x = 0
    else:
        x = pow(x2, (_P + 3) // 8, _P)
        if (x * x - x2) % _P != 0:
            x = x * _I % _P
        if (x * x - x2) % _P != 0:
            return None
        if (x & 1) != sign:
            x = _P - x
    return (x, y, 1, x * y % _P)


_GY = 4 * pow(5, _P - 2, _P) % _P
_G = _decode(_GY.to_bytes(32, "little"))


def ed25519_verify(public, message, signature):
    if len(public) != 32 or len(signature) != 64:
        return False
    A = _decode(public)
    R = _decode(signature[:32])
    if A is None or R is None:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= _L:
        return False
    h = int.from_bytes(hashlib.sha512(signature[:32] + public + message).digest(), "little") % _L
    return _equal(_mul(s, _G), _add(R, _mul(h, A)))


# ------------------------------------------------------------ SSH signatures
def _string(buf, i):
    if i + 4 > len(buf):
        raise CheckFailed("signature is truncated")
    n = int.from_bytes(buf[i:i + 4], "big")
    if i + 4 + n > len(buf):
        raise CheckFailed("signature is truncated")
    return buf[i + 4:i + 4 + n], i + 4 + n


def _ssh_string(b):
    return len(b).to_bytes(4, "big") + b


def _ed25519_key(blob):
    kind, i = _string(blob, 0)
    key, i = _string(blob, i)
    if kind != b"ssh-ed25519" or len(key) != 32 or i != len(blob):
        raise CheckFailed("signature is not an Ed25519 signature")
    return key


def verify_sshsig(armored, message, signers, namespace=b"git"):
    """Raise CheckFailed unless 'armored' is a valid SSH signature of
    'message' in 'namespace' by one of 'signers' (base64 key blobs)."""
    m = re.search(r"-----BEGIN SSH SIGNATURE-----\s*(.*?)\s*-----END SSH SIGNATURE-----", armored, re.S)
    if not m:
        raise CheckFailed("no SSH signature")
    try:
        blob = base64.b64decode("".join(m.group(1).split()), validate=True)
    except ValueError:
        raise CheckFailed("signature is not valid base64")
    if blob[:6] != b"SSHSIG" or int.from_bytes(blob[6:10], "big") != 1:
        raise CheckFailed("not an SSHSIG version 1 signature")
    pub_blob, i = _string(blob, 10)
    ns, i = _string(blob, i)
    reserved, i = _string(blob, i)
    hash_alg, i = _string(blob, i)
    sig_blob, i = _string(blob, i)
    if i != len(blob):
        raise CheckFailed("signature has trailing data")
    if ns != namespace:
        raise CheckFailed("signature namespace is %r, not %r" % (ns, namespace))
    trusted = set()
    for s in signers:
        try:
            trusted.add(base64.b64decode(s))
        except ValueError:
            continue
    if pub_blob not in trusted:
        raise CheckFailed("signed by a key that isn't a trusted Atlas release key")
    if hash_alg == b"sha512":
        digest = hashlib.sha512(message).digest()
    elif hash_alg == b"sha256":
        digest = hashlib.sha256(message).digest()
    else:
        raise CheckFailed("unsupported hash %r" % hash_alg)
    kind, j = _string(sig_blob, 0)
    raw, j = _string(sig_blob, j)
    if kind != b"ssh-ed25519" or j != len(sig_blob):
        raise CheckFailed("signature is not an Ed25519 signature")
    signed = (b"SSHSIG" + _ssh_string(ns) + _ssh_string(reserved) + _ssh_string(hash_alg)
              + _ssh_string(digest))
    if not ed25519_verify(_ed25519_key(pub_blob), signed, raw):
        raise CheckFailed("signature does not match")


# ------------------------------------------------------------------ git tags
def _git(repo, args, check=True, timeout=120):
    r = subprocess.run(["git", "--literal-pathspecs", "-C", repo] + args, capture_output=True, timeout=timeout,
                       stdin=subprocess.DEVNULL)
    if check and r.returncode != 0:
        raise CheckFailed("git %s failed: %s" % (args[0], r.stderr.decode("utf-8", "replace").strip()[:200]))
    return r


def verify_tag(repo, ref, name, signers=None):
    """Commit id the signed annotated tag 'ref' (named 'name') points to."""
    signers = SIGNERS if signers is None else signers
    if not TAG_NAME.match(name or ""):
        raise CheckFailed("%r is not an Atlas release tag name" % name)
    kind = _git(repo, ["cat-file", "-t", ref]).stdout.decode().strip()
    if kind != "tag":
        raise CheckFailed("%s is not an annotated (signed) tag" % ref)
    raw = _git(repo, ["cat-file", "tag", ref]).stdout
    at = raw.rfind(b"\n-----BEGIN SSH SIGNATURE-----")
    if at < 0:
        raise CheckFailed("%s is not signed" % name)
    at += 1
    payload, armored = raw[:at], raw[at:].decode("ascii", "replace")
    head = payload.split(b"\n\n", 1)[0].decode("utf-8", "replace").split("\n")
    pairs = [line.split(" ", 1) for line in head if " " in line]
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise CheckFailed("tag object has repeated headers")
    if fields.get("type") != "commit" or fields.get("tag") != name:
        raise CheckFailed("tag object is for %r (%s), not release %s" % (fields.get("tag"), fields.get("type"), name))
    verify_sshsig(armored, payload, signers)
    commit = fields.get("object", "")
    if not re.match(r"^[0-9a-f]{40}([0-9a-f]{24})?$", commit):
        raise CheckFailed("tag object id is malformed")
    return commit


# ---------------------------------------------------- routine setup (restore)
SAFE_PATH = re.compile(r"^(\.claude|\.gitignore|[A-Za-z0-9_][A-Za-z0-9._-]*)(/[A-Za-z0-9_][A-Za-z0-9._-]*)*$")


def _owned_paths(text):
    """owned_paths from a (signed) manifest: plain relative names only, never user/ or .git."""
    out, inside = [], False
    for line in (text or "").splitlines():
        if re.match(r"^owned_paths:\s*$", line):
            inside = True
            continue
        if inside:
            m = re.match(r"^\s+-\s+[\"']?([^\"'#\s]+)", line)
            if m:
                out.append(m.group(1).rstrip("/"))
            elif line.strip() and not line.startswith((" ", "\t")):
                break
    return [p for p in out if SAFE_PATH.match(p) and p.split("/")[0] not in ("user", ".git")]


def _find_repo():
    for c in (os.environ.get("CLAUDE_PROJECT_DIR"), os.getcwd()):
        if c and os.path.isfile(os.path.join(c, "system", "manifest.yaml")):
            return c
    for root in ("/workspace", os.path.expanduser("~")):
        try:
            for name in sorted(os.listdir(root)):
                c = os.path.join(root, name)
                if os.path.isfile(os.path.join(c, "system", "manifest.yaml")):
                    return c
        except OSError:
            continue
    return None


def _version(v):
    return tuple(int(x) for x in v.split("."))


def _installed_version(repo):
    """installed_version from atlas.yaml; None when Atlas isn't set up (no atlas.yaml).
    Raises CheckFailed when the file exists but the version is missing or malformed."""
    try:
        with open(os.path.join(repo, "user", "settings", "atlas.yaml"), encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return None
    m = re.search(r"^installed_version:[ \t]*[\"']?(\d+\.\d+\.\d+)[\"']?[ \t]*(#.*)?$", text, re.M)
    if not m:
        raise CheckFailed("installed_version in user/settings/atlas.yaml is missing or not a release number")
    if _version(m.group(1)) < MIN_VERSION:
        raise CheckFailed("installed_version %s is older than this check allows (%s)"
                          % (m.group(1), ".".join(map(str, MIN_VERSION))))
    return m.group(1)


def restore(repo):
    """(status, detail). status: clean | restored | restored-settings | skipped. Raises CheckFailed."""
    version = _installed_version(repo)
    if not version:
        return "skipped", "Atlas isn't set up in this repo yet (no user/settings/atlas.yaml)"
    tag = "v" + version
    ref = "refs/atlas-upstream/" + tag
    url = UPSTREAM_URL or "https://github.com/%s.git" % UPSTREAM
    _git(repo, ["fetch", "--quiet", "--depth=1", "--no-tags", url, "+refs/tags/%s:%s" % (tag, ref)])
    commit = verify_tag(repo, ref, tag)
    # only the signed release decides what is system-owned (a chat can edit HEAD's manifest)
    owned = _owned_paths(_git(repo, ["show", commit + ":system/manifest.yaml"]).stdout.decode("utf-8", "replace"))
    if not owned:
        raise CheckFailed("release %s lists no owned paths" % tag)
    _git(repo, ["reset", "-q"])  # start from an empty index: commit only what this check restores
    for p in owned:
        now = set(_git(repo, ["ls-files", "-z", "--", p]).stdout.decode("utf-8", "replace").split("\0")) - {""}
        rel = set(_git(repo, ["ls-tree", "-r", "-z", "--name-only", commit, "--", p]).stdout
                  .decode("utf-8", "replace").split("\0")) - {""}
        extra = sorted(now - rel)
        if extra:
            _git(repo, ["rm", "-q", "-f", "--"] + extra)
        if rel:
            _git(repo, ["checkout", commit, "--", p])
    # untracked or ignored files (a planted module or .pyc) can shadow hook code
    _git(repo, ["clean", "-q", "-f", "-d", "-x", "--", ".claude/hooks"], check=False)
    if _git(repo, ["diff", "--cached", "--quiet", "HEAD"], check=False).returncode == 0:
        return "clean", "system files match signed %s" % tag
    # hook registrations are read when the session starts: a changed settings file only counts next run
    settings_changed = _git(repo, ["diff", "--cached", "--quiet", "HEAD", "--", ".claude/settings.json"],
                            check=False).returncode != 0
    msg = ("atlas(release-check): restore system files to signed %s\n\nAtlas-Actor: release-check\n"
           "Atlas-Reason: system files differed from the signed release before a routine\n"
           "Atlas-Records: -\n" % tag)
    _git(repo, ["-c", "user.name=Atlas", "-c", "user.email=atlas@users.noreply.github.com",
                "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", msg])
    pushed = _git(repo, ["push", "--quiet", "origin", "HEAD:main"], check=False).returncode == 0
    return ("restored-settings" if settings_changed else "restored"), "system files restored to signed %s%s%s" % (
        tag, "; .claude/settings.json had been changed, so this run's hook list may be the changed one"
        if settings_changed else "", "" if pushed else " (commit not pushed yet; push it with this run's changes)")


def run_check():
    repo = _find_repo()
    if not repo:
        print("Atlas release check: no Atlas repo found; nothing checked")
        return
    try:
        status, detail = restore(repo)
    except (CheckFailed, OSError, subprocess.SubprocessError) as e:
        status, detail = "failed", str(e)
    record = {"status": status, "detail": detail, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    try:
        os.makedirs(os.path.join(repo, ".atlas-tmp"), exist_ok=True)
        with open(os.path.join(repo, STATUS_FILE), "w", encoding="utf-8") as f:
            json.dump(record, f)
    except OSError:
        pass
    print("Atlas release check: %s: %s" % (status, detail))


def main(argv):
    if len(argv) == 4 and argv[1] == "verify":
        try:
            print(verify_tag(os.getcwd(), argv[2], argv[3]))
            return 0
        except (CheckFailed, OSError, subprocess.SubprocessError) as e:
            print("release check failed: %s" % e, file=sys.stderr)
            return 1
    if len(argv) <= 1:
        try:
            run_check()
        except Exception as e:  # never stop the routine here; the kernel reads the status
            print("Atlas release check: failed: %s" % e)
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
