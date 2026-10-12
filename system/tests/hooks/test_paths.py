"""Tests for .claude/hooks/paths.py (N5, N6)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_support import HookTestCase  # noqa: E402


class OwnedPaths(HookTestCase):
    def write_call(self, rel, context="routine", tool="Write"):
        key = "notebook_path" if tool == "NotebookEdit" else "file_path"
        return self.run_hook("paths", tool, {key: self.path(rel), "content": "x"}, context=context)

    def test_owned_write_without_lock_blocked(self):
        for rel in ("system/kernel.md", "system/jobs/ingest.md", ".claude/settings.json",
                    ".claude/hooks/actions.py", "CLAUDE.md", "docs/setup/guide.md", ".gitignore"):
            self.assertBlocked(self.write_call(rel), "update.lock")
        self.assertBlocked(self.write_call("system/kernel.md", context="chat", tool="Edit"))
        self.assertBlocked(self.write_call("system/x.ipynb", tool="NotebookEdit"))

    def test_owned_write_with_lock_allowed(self):
        self.update_lock()
        self.assertAllowed(self.write_call("system/kernel.md"))
        self.assertAllowed(self.write_call(".claude/settings.json", context="chat"))

    def test_expired_or_overlong_lock_blocked(self):
        self.update_lock(minutes=-1)
        self.assertBlocked(self.write_call("system/kernel.md"), "expired")
        self.update_lock(minutes=600)
        self.assertBlocked(self.write_call("system/kernel.md"), "too far")

    def test_relative_path_from_subdir(self):
        r = self.run_hook("paths", "Write", {"file_path": "../system/kernel.md", "content": "x"},
                          context="routine", cwd=self.path("user"))
        self.assertBlocked(r)

    def test_user_paths_allowed(self):
        self.assertAllowed(self.write_call("user/knowledge/people/dana-ruiz.md"))
        self.assertAllowed(self.write_call("user/settings/rhythms.yaml"))
        self.assertAllowed(self.write_call("user/extensions/jobs/deals.md"))
        self.assertAllowed(self.run_hook("paths", "Write", {"file_path": "/tmp/elsewhere.txt"}, "routine"))

    def test_bash_writes_to_owned_paths(self):
        for cmd in ("echo hi > system/kernel.md",
                    "printf x >> CLAUDE.md",
                    "cat notes | tee system/rules/new.md",
                    "sed -i 's/a/b/' system/kernel.md",
                    "mv user/library/x.md system/x.md",
                    "cp /tmp/x .claude/settings.json",
                    "rm -rf system/jobs",
                    "cd system && echo x > kernel.md",
                    "bash -c 'echo x > system/kernel.md'",
                    "unzip -o nova-1.1.0.zip",
                    "git checkout -- system/kernel.md",
                    "touch docs/new.md"):
            self.assertBlocked(self.bash("paths", cmd, "routine"), "owned")

    def test_bash_reads_and_user_writes_allowed(self):
        for cmd in ("cat system/kernel.md", "grep -r foo system/", "cp system/templates/x.yaml user/x.yaml",
                    "echo x > user/work/briefs/2026-10-12.md", "ls -la", "git status",
                    "python3 system/tools/validate.py --all 2>&1 | tail -5",
                    "unzip -o release.zip -d /tmp/nova-release",
                    "echo done >/dev/null 2>&1"):
            self.assertAllowed(self.bash("paths", cmd, "routine"))

    def test_copy_into_directory_resolves_names(self):
        self.assertAllowed(self.bash("paths", "cp /tmp/a.md .", "routine"))
        self.assertBlocked(self.bash("paths", "cp -r /tmp/release/system .", "routine"), "owned")

    def test_broken_manifest_fails_closed_in_routine(self):
        self.write("system/manifest.yaml", "upstream: CaptLocke/nova\nowned_paths: [\n")
        self.assertBlocked(self.write_call("user/work/x.md"), "internal error")
        self.assertAllowed(self.write_call("user/work/x.md", context="chat"))

    def test_bash_owned_with_lock_allowed(self):
        self.update_lock()
        self.assertAllowed(self.bash("paths", "unzip -o nova-1.1.0.zip && cp -r x/system .", "routine"))

    def test_git_internals_blocked(self):
        self.update_lock()
        self.assertBlocked(self.write_call(".git/config"))
        self.assertBlocked(self.bash("paths", "echo x >> .git/config", "chat"))


class GovernanceFiles(HookTestCase):
    def setUp(self):
        super().setUp()
        for f in ("governance", "data-rules", "connectors"):
            self.write("user/settings/%s.yaml" % f, "x: 1\n")

    def gov_write(self, context, name="governance", tool="Edit"):
        return self.run_hook("paths", tool, {"file_path": self.path("user/settings/%s.yaml" % name),
                                             "old_string": "a", "new_string": "b"}, context=context)

    def test_governance_blocked_in_routine(self):
        for name in ("governance", "data-rules", "connectors"):
            self.assertBlocked(self.gov_write("routine", name), "N6")
        self.assertBlocked(self.gov_write(None))
        self.assertBlocked(self.bash("paths", "echo 'send_communication: auto' >> user/settings/governance.yaml",
                                     "routine"))

    def test_governance_via_copy_or_folder_delete(self):
        self.assertBlocked(self.bash("paths", "cp /tmp/governance.yaml user/settings/", "routine"), "N6")
        self.assertBlocked(self.bash("paths", "rm -rf user/settings", "routine"), "N6")
        self.assertAllowed(self.bash("paths", "cp /tmp/rhythms.yaml user/settings/", "routine"))

    def test_governance_blocked_in_routine_even_with_record(self):
        self.approval("Edit", "governance_settings")
        self.assertBlocked(self.gov_write("routine"))

    def test_governance_in_chat_needs_record(self):
        self.assertBlocked(self.gov_write("chat"), "governance_settings")
        self.approval("Edit", "governance_settings")
        self.assertAllowed(self.gov_write("chat"))
        self.assertFalse(os.path.exists(self.path(".nova-tmp/approval.json")))
        self.assertBlocked(self.gov_write("chat"))

    def test_governance_record_wrong_tool_or_action(self):
        self.approval("Write", "governance_settings")
        self.assertBlocked(self.gov_write("chat"))
        self.approval("Edit", "send_communication")
        self.assertBlocked(self.gov_write("chat"))

    def test_first_creation_in_chat_allowed(self):
        os.remove(self.path("user/settings/governance.yaml"))
        self.assertAllowed(self.gov_write("chat", tool="Write"))
        self.assertBlocked(self.gov_write("routine", tool="Write"))

    def test_other_settings_not_protected(self):
        r = self.run_hook("paths", "Write", {"file_path": self.path("user/settings/rhythms.yaml")}, "routine")
        self.assertAllowed(r)


class TransientRecords(HookTestCase):
    def test_routine_cannot_create_approval_or_purge_lock(self):
        for rel in (".nova-tmp/approval.json", ".nova-tmp/purge.lock"):
            r = self.run_hook("paths", "Write", {"file_path": self.path(rel), "content": "{}"}, "routine")
            self.assertBlocked(r, "chat")
        self.assertBlocked(self.bash("paths", "echo '{}' > .nova-tmp/approval.json", None))

    def test_chat_can_create_records_and_routine_update_lock(self):
        r = self.run_hook("paths", "Write", {"file_path": self.path(".nova-tmp/approval.json")}, "chat")
        self.assertAllowed(r)
        r = self.run_hook("paths", "Write", {"file_path": self.path(".nova-tmp/update.lock")}, "routine")
        self.assertAllowed(r)
        self.assertAllowed(self.bash("paths", "mkdir -p .nova-tmp && rm -f .nova-tmp/approval.json", "routine"))


if __name__ == "__main__":
    unittest.main()
