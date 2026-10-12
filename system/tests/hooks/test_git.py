"""Tests for .claude/hooks/git.py (N8, N10, N12)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_support import HookTestCase, sh  # noqa: E402

TRAILERS = "Nova-Actor: chat\nNova-Reason: test change"


def fake(*parts):
    """Join parts at runtime so this file holds no literal secret-shaped text."""
    return "".join(parts)


class HistoryRewrite(HookTestCase):
    def test_force_push_blocked(self):
        for cmd in ("git push --force origin main", "git push -f", "git push origin +main",
                    "git push --force-with-lease origin HEAD:main", "git push -uf origin main",
                    "git pull --rebase && git push --force-with-lease=main origin main",
                    "git -C . push --mirror"):
            self.assertBlocked(self.bash("git", cmd, "chat"), "N8")

    def test_normal_push_allowed(self):
        self.assertAllowed(self.bash("git", "git pull --rebase && git push origin HEAD:main", "routine"))

    def test_rewrites_blocked(self):
        for cmd in ("git reset --hard HEAD~1", "git reset --hard origin/main", "git rebase -i HEAD~3",
                    "git rebase --interactive main", "git filter-branch --tree-filter x HEAD",
                    "git filter-repo --path user/knowledge/people/dana-ruiz.md --invert-paths",
                    "git reflog expire --expire=now --all", "git gc --prune=now",
                    "git update-ref -d refs/heads/main"):
            self.assertBlocked(self.bash("git", cmd, "chat"), "N8")

    def test_safe_git_allowed(self):
        for cmd in ("git reset --hard", "git reset --hard HEAD", "git status", "git log --oneline -5",
                    "git revert --no-edit HEAD", "git pull --rebase", "git fetch origin",
                    "git rebase --continue", "git diff --cached"):
            self.assertAllowed(self.bash("git", cmd, "routine"))

    def test_amend_after_push_blocked_before_push_allowed(self):
        # simulate a pushed HEAD with a remote-tracking ref
        sh(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], self.root)
        sh(["git", "branch", "--set-upstream-to=origin/main"], self.root)
        cmd = "git commit --amend -m 'x\n\n%s'" % TRAILERS
        self.assertBlocked(self.bash("git", cmd, "chat"), "already pushed")
        self.write("user/work/a.md", "a\n")
        sh(["git", "add", "-A"], self.root)
        sh(["git", "commit", "-q", "-m", "local\n\n" + TRAILERS], self.root)
        self.assertAllowed(self.bash("git", cmd, "chat"))

    def test_purge_lock_exception(self):
        self.purge_lock()
        cmd = "git filter-repo --path user/knowledge/people/dana-ruiz.md --invert-paths --force && git push --force origin main"
        self.assertAllowed(self.bash("git", cmd, "chat"))

    def test_purge_lock_not_valid_in_routine(self):
        self.purge_lock()
        self.assertBlocked(self.bash("git", "git push --force origin main", "routine"), "chat")
        self.assertBlocked(self.bash("git", "git push --force origin main", None))

    def test_expired_purge_lock(self):
        self.purge_lock(minutes=-1)
        self.assertBlocked(self.bash("git", "git push --force origin main", "chat"), "expired")

    def test_origin_change_blocked_even_with_purge_lock(self):
        self.purge_lock()
        for cmd in ("git remote set-url origin https://github.com/CaptLocke/nova",
                    "git remote remove origin", "git config remote.origin.url https://x/y/z"):
            self.assertBlocked(self.bash("git", cmd, "chat"))
        self.assertAllowed(self.bash("git", "git remote get-url origin", "routine"))
        self.assertAllowed(self.bash("git", "git remote add upstream https://github.com/CaptLocke/nova", "routine"))


class CommitTrailers(HookTestCase):
    def setUp(self):
        super().setUp()
        self.write("user/work/note.md", "hello\n")
        sh(["git", "add", "-A"], self.root)

    def test_commit_without_trailers_blocked(self):
        self.assertBlocked(self.bash("git", "git commit -m 'nova(chat): filed note'", "chat"), "Nova-Actor")

    def test_commit_missing_reason_blocked(self):
        cmd = "git commit -m 'nova(chat): x' -m 'Nova-Actor: chat'"
        self.assertBlocked(self.bash("git", cmd, "chat"), "Nova-Reason")

    def test_commit_with_trailers_allowed(self):
        cmd = "git commit -m 'nova(chat): filed note' -m '%s'" % TRAILERS
        self.assertAllowed(self.bash("git", cmd, "chat"))

    def test_heredoc_message(self):
        cmd = ("git add -A && git commit -F - <<'EOF'\nnova(routine): ingest\n\n"
               "Nova-Actor: routine:nightly-cycle\nNova-Reason: nightly ingest\nNova-Records: -\nEOF")
        self.assertAllowed(self.bash("git", cmd, "routine"))
        cmd2 = ("git commit -m \"$(cat <<'EOF'\nnova(chat): x\n\nno trailers here\nEOF\n)\"")
        self.assertBlocked(self.bash("git", cmd2, "chat"))

    def test_message_file(self):
        self.write("msg.txt", "nova(chat): x\n\n%s\n" % TRAILERS)
        self.assertAllowed(self.bash("git", "git commit -F msg.txt", "chat"))
        self.write("msg.txt", "nova(chat): x\n")
        self.assertBlocked(self.bash("git", "git commit --file=msg.txt", "chat"))

    def test_routine_cannot_claim_chat(self):
        cmd = "git commit -m 'x' -m '%s'" % TRAILERS
        self.assertBlocked(self.bash("git", cmd, "routine"), "routine")
        self.assertBlocked(self.bash("git", "git commit -m 'x' -m 'Nova-Actor: robot\nNova-Reason: y'", "chat"),
                           "not valid")

    def test_unknown_message_source_allowed_with_warning(self):
        r = self.bash("git", "git commit", "chat")
        self.assertAllowed(r)
        self.assertIn("could not read the commit message", r.stderr)


class SecretScan(HookTestCase):
    COMMIT = "git commit -m 'nova(chat): x' -m '%s'" % TRAILERS

    def stage(self, text, rel="user/knowledge/people/dana-ruiz.md"):
        self.write(rel, text)
        sh(["git", "add", "-A"], self.root)

    def test_secrets_in_staged_diff_blocked(self):
        samples = [
            fake("AK", "IA", "ABCDEFGHIJKLMNOP"),
            fake("gh", "p_", "a" * 36),
            fake("github_", "pat_", "11ABCDEFG0123456789_abcdefghij"),
            fake("sk-", "ant-", "api03-", "x" * 30),
            fake("-----BEGIN ", "RSA PRIVATE", " KEY-----"),
            fake("xo", "xb-", "1234567890-abcdef"),
            fake("AI", "za", "S" * 35),
            fake("https://maya:", "hunter2", "@db.example.com/x"),
        ]
        for s in samples:
            self.stage("notes\n%s\n" % s)
            self.assertBlocked(self.bash("git", self.COMMIT, "chat"), "N10")
            sh(["git", "reset", "-q"], self.root)

    def test_secret_added_in_same_command_blocked(self):
        self.write("user/work/new.md", "token %s\n" % fake("gh", "o_", "b" * 36))
        self.assertBlocked(self.bash("git", "git add -A && " + self.COMMIT, "routine".replace("routine", "chat")))

    def test_secret_with_commit_all_blocked(self):
        self.write("CLAUDE.md", "x\n%s\n" % fake("sk-", "ant-", "y" * 30))
        self.assertBlocked(self.bash("git", self.COMMIT.replace("commit", "commit -a", 1), "chat"))

    def test_clean_commit_allowed(self):
        self.stage("Dana prefers email. Password kept in the user's password manager.\n"
                   "Link: https://github.com/example-user/nova\n")
        self.assertAllowed(self.bash("git", self.COMMIT, "chat"))

    def test_removed_secret_lines_not_flagged(self):
        self.stage("x %s\n" % fake("AK", "IA", "ABCDEFGHIJKLMNOP"))
        sh(["git", "commit", "-q", "-m", "seed\n\n" + TRAILERS], self.root)
        self.stage("clean\n")
        self.assertAllowed(self.bash("git", self.COMMIT, "chat"))


if __name__ == "__main__":
    unittest.main()
