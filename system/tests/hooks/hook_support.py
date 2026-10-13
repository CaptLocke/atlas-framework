"""Shared helpers for Atlas hook tests: build a throwaway Atlas repo and run a
hook script against it exactly as Claude Code would (JSON on stdin, env vars).

Fake secrets used in tests are assembled at runtime so no file in the repo
contains a literal secret-shaped string (the git hook would flag it).
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HOOKS = os.path.join(REPO, ".claude", "hooks")
USER_ORIGIN = "https://github.com/example-user/atlas.git"


def iso(minutes):
    t = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes)
    return t.isoformat(timespec="seconds")


def sh(args, cwd, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("%s failed: %s" % (args, r.stderr))
    return r


class HookTestCase(unittest.TestCase):
    """Each test gets a fresh git repo that looks like a user's Atlas repo."""

    origin = USER_ORIGIN

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="atlas-hooktest-")
        self.root = os.path.realpath(self.tmp)
        shutil.copytree(HOOKS, os.path.join(self.root, ".claude", "hooks"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(os.path.join(REPO, "system", "tools", "vendor"),
                        os.path.join(self.root, "system", "tools", "vendor"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(os.path.join(REPO, "system", "manifest.yaml"),
                    os.path.join(self.root, "system", "manifest.yaml"))
        for d in ("user/settings", "user/knowledge/people", "user/inbox/drop",
                  "user/knowledge/_index", "docs"):
            os.makedirs(os.path.join(self.root, d), exist_ok=True)
        self.write("user/knowledge/people/dana-ruiz.md", "---\nid: people/dana-ruiz\n---\n")
        self.write(".gitignore", ".atlas-tmp/\n__pycache__/\n")
        for f in ("CLAUDE.md", "README.md", "LICENSE", "CHANGELOG.md"):
            self.write(f, "x\n")
        sh(["git", "init", "-q", "-b", "main"], self.root)
        sh(["git", "config", "user.email", "test@example.com"], self.root)
        sh(["git", "config", "user.name", "Atlas Test"], self.root)
        sh(["git", "config", "commit.gpgsign", "false"], self.root)
        if self.origin:
            sh(["git", "remote", "add", "origin", self.origin], self.root)
        sh(["git", "add", "-A"], self.root)
        sh(["git", "commit", "-q", "-m", "init\n\nAtlas-Actor: setup\nAtlas-Reason: test"], self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- files
    def path(self, rel):
        return os.path.join(self.root, rel)

    def write(self, rel, text):
        p = self.path(rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)

    def write_json(self, rel, data):
        self.write(rel, json.dumps(data))

    def approval(self, tool, action, minutes=2, target="test target", **extra):
        rec = {"action": action, "tool": tool, "target": target,
               "user_confirmation": "yes, do it", "created": iso(0), "expires": iso(minutes)}
        rec.update(extra)
        self.write_json(".atlas-tmp/approval.json", rec)

    def update_lock(self, minutes=30):
        self.write_json(".atlas-tmp/update.lock", {"by": "atlas-update", "version_from": "1.0.0",
                                                  "version_to": "1.1.0", "created": iso(0),
                                                  "expires": iso(minutes)})

    def purge_lock(self, minutes=15):
        self.write_json(".atlas-tmp/purge.lock", {"by": "atlas-memory",
                                                 "targets": ["user/knowledge/people/dana-ruiz.md"],
                                                 "user_confirmation": "yes, permanently erase",
                                                 "created": iso(0), "expires": iso(minutes)})

    def connectors(self, text):
        self.write("user/settings/connectors.yaml", text)

    # -- running hooks
    def run_hook(self, hook, tool_name, tool_input, context="chat", cwd=None):
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = self.root
        env.pop("ATLAS_CONTEXT", None)
        if context is not None:
            env["ATLAS_CONTEXT"] = context
        payload = {"session_id": "test", "transcript_path": "/dev/null",
                   "cwd": cwd or self.root, "permission_mode": "default",
                   "hook_event_name": "PreToolUse", "tool_name": tool_name,
                   "tool_input": tool_input, "tool_use_id": "toolu_test"}
        r = subprocess.run(["python3", os.path.join(self.root, ".claude", "hooks", hook + ".py")],
                           input=json.dumps(payload), capture_output=True, text=True, env=env,
                           cwd=self.root, timeout=60)
        return r

    def run_event(self, hook, event, extra=None, context="chat"):
        """Run a non-tool hook (SessionStart, Stop) with its event payload."""
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = self.root
        env.pop("ATLAS_CONTEXT", None)
        if context is not None:
            env["ATLAS_CONTEXT"] = context
        payload = {"session_id": "test", "transcript_path": "/dev/null", "cwd": self.root,
                   "permission_mode": "default", "hook_event_name": event}
        payload.update(extra or {})
        return subprocess.run(["python3", os.path.join(self.root, ".claude", "hooks", hook + ".py")],
                              input=json.dumps(payload), capture_output=True, text=True, env=env,
                              cwd=self.root, timeout=90)

    def bash(self, hook, command, context="chat", cwd=None):
        return self.run_hook(hook, "Bash", {"command": command, "description": "test"}, context, cwd)

    # -- assertions
    def assertBlocked(self, r, contains=None):
        self.assertEqual(r.returncode, 2, "expected block (exit 2); got %s\nstdout=%s\nstderr=%s"
                         % (r.returncode, r.stdout, r.stderr))
        if contains:
            self.assertIn(contains, r.stderr)

    def assertAllowed(self, r):
        self.assertEqual(r.returncode, 0, "expected allow; got %s\nstderr=%s" % (r.returncode, r.stderr))
        self.assertNotIn('"deny"', r.stdout)
        self.assertNotIn('"ask"', r.stdout)

    def assertAsked(self, r):
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")
