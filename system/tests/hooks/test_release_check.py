"""Tests for system/tools/release_check.py: SSH signatures on release tags."""
import base64
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_support import REPO, sh  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "system", "tools"))
import release_check as rc  # noqa: E402

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except ImportError:  # pragma: no cover
    Ed25519PrivateKey = None


def s(b):
    return len(b).to_bytes(4, "big") + b


class Key:
    def __init__(self):
        self.k = Ed25519PrivateKey.generate()
        raw = self.k.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.blob = s(b"ssh-ed25519") + s(raw)
        self.b64 = base64.b64encode(self.blob).decode()

    def sign(self, message, namespace=b"git", hash_alg=b"sha512"):
        h = hashlib.new(hash_alg.decode(), message).digest()
        signed = b"SSHSIG" + s(namespace) + s(b"") + s(hash_alg) + s(h)
        sig = s(b"ssh-ed25519") + s(self.k.sign(signed))
        blob = b"SSHSIG" + (1).to_bytes(4, "big") + s(self.blob) + s(namespace) + s(b"") + s(hash_alg) + s(sig)
        b64 = base64.b64encode(blob).decode()
        lines = [b64[i:i + 70] for i in range(0, len(b64), 70)]
        return "-----BEGIN SSH SIGNATURE-----\n%s\n-----END SSH SIGNATURE-----\n" % "\n".join(lines)


@unittest.skipIf(Ed25519PrivateKey is None, "needs the cryptography package to make test signatures")
class ReleaseCheck(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="atlas-relcheck-")
        sh(["git", "init", "-q", "-b", "main"], self.root)
        sh(["git", "-c", "user.email=t@e", "-c", "user.name=T", "-c", "commit.gpgsign=false",
            "commit", "-q", "--allow-empty", "-m", "release"], self.root)
        self.commit = sh(["git", "rev-parse", "HEAD"], self.root).stdout.strip()
        self.key = Key()

    def tag(self, name, ref=None, key=None, body_name=None, mutate=None, **kw):
        payload = ("object %s\ntype commit\ntag %s\ntagger T <t@e> 0 +0000\n\nAtlas %s\n"
                   % (self.commit, body_name or name, name)).encode()
        sig = (key or self.key).sign(payload, **kw)
        if mutate:
            payload = mutate(payload)
        r = subprocess.run(["git", "hash-object", "-t", "tag", "-w", "--stdin", "--literally"], cwd=self.root,
                           input=payload + sig.encode(), capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        ref = ref or "refs/atlas-upstream/" + name
        sh(["git", "update-ref", ref, r.stdout.decode().strip()], self.root)
        return ref

    def check(self, ref, name, signers=None):
        return rc.verify_tag(self.root, ref, name, signers or (self.key.b64,))

    def test_signed_tag_verifies(self):
        self.assertEqual(self.check(self.tag("v1.1.0"), "v1.1.0"), self.commit)
        self.assertEqual(self.check(self.tag("v1.1.1", hash_alg=b"sha256"), "v1.1.1"), self.commit)

    def test_backup_key_verifies(self):
        backup = Key()
        ref = self.tag("v1.2.0", key=backup)
        self.assertEqual(self.check(ref, "v1.2.0", (self.key.b64, backup.b64)), self.commit)

    def test_refusals(self):
        other = Key()
        cases = {
            "untrusted key": (self.tag("v2.0.0", key=other), "v2.0.0"),
            "other namespace": (self.tag("v2.0.1", namespace=b"file"), "v2.0.1"),
            "edited after signing": (self.tag("v2.0.2", mutate=lambda p: p.replace(b"Atlas", b"Atlaz")), "v2.0.2"),
            "renamed": (self.tag("v2.0.3", ref="refs/atlas-upstream/v9.0.0"), "v9.0.0"),
            "not a release name": (self.tag("v2.0.4"), "main"),
        }
        sh(["git", "update-ref", "refs/atlas-upstream/v2.0.5", self.commit], self.root)
        cases["not a tag"] = ("refs/atlas-upstream/v2.0.5", "v2.0.5")
        for label, (ref, name) in cases.items():
            with self.subTest(label):
                with self.assertRaises(rc.CheckFailed):
                    self.check(ref, name)

    def test_cli_uses_built_in_keys(self):
        ref = self.tag("v3.0.0")  # signed by a test key, not a release key
        r = subprocess.run([sys.executable, "-I", os.path.join(REPO, "system", "tools", "release_check.py"),
                            "verify", ref, "v3.0.0"], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("trusted Atlas release key", r.stderr)


class Ed25519(unittest.TestCase):
    def test_rfc8032_vector(self):
        # RFC 8032 section 7.1, TEST 2
        pk = bytes.fromhex("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c")
        sig = bytes.fromhex("92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
                            "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00")
        self.assertTrue(rc.ed25519_verify(pk, b"\x72", sig))
        self.assertFalse(rc.ed25519_verify(pk, b"\x73", sig))


if __name__ == "__main__":
    unittest.main()
