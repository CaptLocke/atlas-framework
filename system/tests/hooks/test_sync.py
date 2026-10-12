"""Tests for .claude/hooks/sync_start.py (SessionStart) and sync_guard.py (Stop)."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_support import HookTestCase, sh  # noqa: E402

TRAILERS = "Nova-Actor: chat\nNova-Reason: test"


class SyncCase(HookTestCase):
    """A user repo whose origin is a local bare repo with main pushed."""

    origin = None

    def setUp(self):
        super().setUp()
        self.outside = tempfile.mkdtemp(prefix="nova-remote-")   # outside the work tree
        self.addCleanup(shutil.rmtree, self.outside, True)
        self.remote = os.path.join(self.outside, "remote.git")
        sh(["git", "init", "-q", "--bare", "-b", "main", self.remote], self.outside)
        sh(["git", "remote", "add", "origin", self.remote], self.root)
        sh(["git", "push", "-q", "-u", "origin", "main"], self.root)

    def other_clone_commit(self, rel="user/work/from-elsewhere.md"):
        other = os.path.join(self.outside, "other")
        if not os.path.exists(other):
            sh(["git", "clone", "-q", self.remote, other], self.outside)
            sh(["git", "config", "user.email", "o@example.com"], other)
            sh(["git", "config", "user.name", "Other"], other)
        target = os.path.join(other, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w") as f:
            f.write("from another session\n")
        sh(["git", "add", "-A"], other)
        sh(["git", "commit", "-q", "-m", "remote change\n\n" + TRAILERS], other)
        sh(["git", "push", "-q", "origin", "main"], other)
        return sh(["git", "rev-parse", "--short", "HEAD"], other).stdout.strip()

    def start(self, context="chat"):
        r = self.run_event("sync_start", "SessionStart", {"source": "startup"}, context)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"] if r.stdout.strip() else ""

    def stop(self, active=False, session="test"):
        r = self.run_event("sync_guard", "Stop", {"stop_hook_active": active, "session_id": session})
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout) if r.stdout.strip() else {}

    def commit_local(self, rel="user/work/local.md"):
        self.write(rel, "local\n")
        sh(["git", "add", "-A"], self.root)
        sh(["git", "commit", "-q", "-m", "local\n\n" + TRAILERS], self.root)


class SessionStart(SyncCase):
    def test_pulls_new_remote_commits(self):
        sha = self.other_clone_commit()
        ctx = self.start()
        self.assertIn("synced to origin/main at %s" % sha, ctx)
        self.assertTrue(os.path.exists(self.path("user/work/from-elsewhere.md")))

    def test_pull_keeps_local_uncommitted_work(self):
        self.other_clone_commit()
        self.write("user/work/draft.md", "work in progress\n")
        self.write("CLAUDE.md", "edited locally\n")
        self.assertIn("synced", self.start())
        self.assertTrue(os.path.exists(self.path("user/work/from-elsewhere.md")))
        with open(self.path("CLAUDE.md")) as f:
            self.assertEqual(f.read(), "edited locally\n")

    def test_unreachable_remote_does_not_crash(self):
        sh(["git", "remote", "set-url", "origin", os.path.join(self.outside, "missing.git")], self.root)
        ctx = self.start()
        self.assertIn("FAILED", ctx)
        self.assertIn("git pull --rebase", ctx)
        with open(self.path(".nova-tmp/sync.log")) as f:
            self.assertIn("sync_start.failed", f.read())

    def test_conflict_is_aborted_and_reported(self):
        self.other_clone_commit("user/work/same.md")
        self.commit_local("user/work/same.md")
        ctx = self.start()
        self.assertIn("FAILED", ctx)
        self.assertFalse(os.path.exists(self.path(".git/rebase-merge")))
        self.assertFalse(os.path.exists(self.path(".git/rebase-apply")))

    def test_not_on_main(self):
        sh(["git", "checkout", "-q", "-b", "claude/x"], self.root)
        self.assertIn("not main", self.start())

    def test_broken_helper_module_does_not_crash(self):
        self.write(".claude/hooks/gitsync.py", "raise ImportError('simulated damage')\n")
        ctx = self.start()
        self.assertIn("could not run", ctx)
        r = self.run_event("sync_guard", "Stop", {"stop_hook_active": False})
        self.assertEqual(r.returncode, 0)
        self.assertIn("systemMessage", r.stdout)
        self.assertNotIn('"block"', r.stdout)


class StopGuard(SyncCase):
    def test_clean_state_allows(self):
        self.assertEqual(self.stop(), {})

    def test_uncommitted_tracked_change_blocks(self):
        self.write("user/knowledge/people/dana-ruiz.md", "changed\n")
        out = self.stop()
        self.assertEqual(out.get("decision"), "block")
        self.assertIn("Unsaved Nova changes", out["reason"])
        self.assertIn("Nova-Actor/Nova-Reason", out["reason"])
        self.assertIn("dana-ruiz.md", out["reason"])

    def test_untracked_file_blocks(self):
        self.write("user/work/new.md", "x\n")
        self.assertEqual(self.stop().get("decision"), "block")

    def test_unpushed_commit_blocks(self):
        self.commit_local()
        out = self.stop()
        self.assertEqual(out.get("decision"), "block")
        self.assertIn("1 commit(s) not pushed", out["reason"])
        sh(["git", "push", "-q", "origin", "main"], self.root)
        self.assertEqual(self.stop(), {})

    def test_ignored_paths_do_not_block(self):
        self.write(".nova-tmp/approval.json", "{}")
        self.write("user/inbox/drop/upload.pdf", "x")
        self.write("cache/__pycache__/x.pyc", "x")
        self.assertEqual(self.stop(), {})

    def test_stop_hook_active_allows_and_records_issue(self):
        self.write("user/.state/health.yaml", "last_user_check: null\nknown_issues: []\n")
        sh(["git", "add", "-A"], self.root)
        sh(["git", "commit", "-q", "-m", "state\n\n" + TRAILERS], self.root)
        sh(["git", "push", "-q", "origin", "main"], self.root)
        self.write("user/work/new.md", "x\n")
        out = self.stop(active=True)
        self.assertNotIn("decision", out)
        self.assertIn("couldn't save your latest changes to GitHub", out["systemMessage"])
        self.assertIn("reconnect GitHub", out["systemMessage"])
        with open(self.path("user/.state/health.yaml")) as f:
            text = f.read()
        self.assertIn("id: sync-push-failing", text)
        self.assertIn("severity: high", text)
        # recorded once only
        self.stop(active=True)
        with open(self.path("user/.state/health.yaml")) as f:
            self.assertEqual(f.read().count("sync-push-failing"), 1)

    def test_third_consecutive_block_allows(self):
        self.write("user/work/new.md", "x\n")
        self.assertEqual(self.stop().get("decision"), "block")
        self.assertEqual(self.stop().get("decision"), "block")
        out = self.stop()
        self.assertNotIn("decision", out)
        self.assertIn("systemMessage", out)
        self.assertIn("could not record", out["systemMessage"])  # no health.yaml yet: warning only
        self.assertFalse(os.path.exists(self.path("user/.state/health.yaml")))
        # the counter restarts after giving up and after a clean stop
        self.assertEqual(self.stop().get("decision"), "block")
        os.remove(self.path("user/work/new.md"))
        self.assertEqual(self.stop(), {})
        self.assertFalse(os.path.exists(self.path(".nova-tmp/sync_guard.json")))

    def test_counter_is_per_session(self):
        self.write("user/work/new.md", "x\n")
        self.stop(session="a")
        self.stop(session="a")
        self.assertEqual(self.stop(session="b").get("decision"), "block")

    def test_unsafe_health_file_left_alone(self):
        original = "known_issues: [{ id: other, severity: low, status: open }]\n"
        self.write("user/.state/health.yaml", original)
        out = self.stop(active=True)
        self.assertIn("could not record", out["systemMessage"])
        with open(self.path("user/.state/health.yaml")) as f:
            self.assertEqual(f.read(), original)

    def test_unfinished_rebase_blocks(self):
        self.other_clone_commit("user/work/same.md")
        self.commit_local("user/work/same.md")
        sh(["git", "fetch", "-q", "origin"], self.root)
        subprocess.run(["git", "rebase", "origin/main"], cwd=self.root, capture_output=True)
        out = self.stop()
        self.assertEqual(out.get("decision"), "block")
        self.assertIn("rebase", out["reason"])


class SyncUpstreamBypass(SyncCase):
    def test_upstream_repo_is_untouched(self):
        sh(["git", "remote", "set-url", "origin", "https://github.com/CaptLocke/nova.git"], self.root)
        self.write("user/work/new.md", "x\n")
        self.commit_local()
        r = self.run_event("sync_start", "SessionStart", {"source": "startup"})
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        r = self.run_event("sync_guard", "Stop", {"stop_hook_active": False})
        self.assertEqual((r.returncode, r.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
