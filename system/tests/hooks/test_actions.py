"""Tests for .claude/hooks/actions.py (N1-N4)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hook_support import HookTestCase  # noqa: E402

CONNECTORS = """\
connectors:
  - connector: outlook
    mcp_prefix: mcp__outlook__
    categories: [mail]
    operations:
      mail.list_recent: { tool: list_messages }
      mail.send: { tool: dispatch_mail }
    tool_risk:
      list_messages: read
      get_message: read
      dispatch_mail: send
      create_draft: draft
      approve_invoice: security
      list_reply_templates: read
"""

SEND = "mcp__outlook__dispatch_mail"


class ActionsRoutine(HookTestCase):
    def setUp(self):
        super().setUp()
        self.connectors(CONNECTORS)

    def test_send_blocked_in_routine(self):
        self.assertBlocked(self.run_hook("actions", SEND, {"to": "x"}, context="routine"),
                           "routine")

    def test_send_blocked_in_routine_even_with_record(self):
        self.approval(SEND, "send_communication")
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="routine"))
        self.assertTrue(os.path.exists(self.path(".nova-tmp/approval.json")))

    def test_missing_context_is_routine(self):
        self.approval(SEND, "send_communication")
        self.assertBlocked(self.run_hook("actions", SEND, {}, context=None), "routine")

    def test_unknown_context_value_is_routine(self):
        self.approval(SEND, "send_communication")
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="Chat-ish"))

    def test_read_allowed_in_routine(self):
        self.assertAllowed(self.run_hook("actions", "mcp__outlook__list_messages", {}, context="routine"))

    def test_draft_allowed_in_routine(self):
        self.assertAllowed(self.run_hook("actions", "mcp__outlook__create_draft", {}, context="routine"))

    def test_name_pattern_applies_to_unmapped_tool(self):
        self.assertBlocked(self.run_hook("actions", "mcp__slack__post_message", {}, context="routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__drive__trashFile", {}, context="routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__drive__share_file", {}, context="routine"))

    def test_name_pattern_overrides_wrong_tag(self):
        self.connectors(CONNECTORS + "      delete_message: read\n")
        self.assertBlocked(self.run_hook("actions", "mcp__outlook__delete_message", {}, context="routine"))

    def test_reply_draft_is_a_draft(self):
        self.assertAllowed(self.run_hook("actions", "mcp__mail__create_reply_draft", {}, context="routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__mail__send_draft", {}, context="routine"))

    def test_unmapped_ambiguous_tool_blocked_in_routine(self):
        self.assertBlocked(self.run_hook("actions", "mcp__crm__frobnicate", {}, context="routine"),
                           "not mapped")

    def test_bash_rm_under_user_blocked_in_routine(self):
        self.assertBlocked(self.bash("actions", "rm user/knowledge/people/dana-ruiz.md", "routine"))
        self.assertBlocked(self.bash("actions", "git rm -q user/knowledge/people/dana-ruiz.md", "routine"))
        self.assertBlocked(self.bash("actions", "cd user && rm -rf knowledge", "routine"))
        self.assertBlocked(self.bash("actions", "find user/knowledge -name '*.md' -delete", "routine"))
        self.assertBlocked(self.bash("actions", "rm -rf ./*", "routine"))

    def test_bash_allowed_deletes(self):
        self.assertAllowed(self.bash("actions", "rm -f user/inbox/drop/notes.pdf", "routine"))
        self.assertAllowed(self.bash("actions", "rm -f user/knowledge/_index/people.md", "routine"))
        self.assertAllowed(self.bash("actions", "rm -f /tmp/scratch.txt && ls user", "routine"))
        self.assertAllowed(self.bash("actions", "mv user/inbox/drop/a.pdf user/library/a.pdf", "routine"))
        self.assertAllowed(self.bash("actions", "echo rm user/x", "routine"))


class ActionsChat(HookTestCase):
    def setUp(self):
        super().setUp()
        self.connectors(CONNECTORS)

    def test_send_in_chat_without_record_blocked(self):
        r = self.run_hook("actions", SEND, {}, context="chat")
        self.assertBlocked(r, "approval")
        self.assertIn("system/rules/governance.md", r.stderr)

    def test_send_in_chat_with_record_allowed_once(self):
        self.approval(SEND, "send_communication")
        self.assertAllowed(self.run_hook("actions", SEND, {}, context="chat"))
        self.assertFalse(os.path.exists(self.path(".nova-tmp/approval.json")), "record must be consumed")
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="chat"))

    def test_expired_record_blocked(self):
        self.approval(SEND, "send_communication", minutes=-1)
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="chat"), "expired")

    def test_record_lasting_too_long_blocked(self):
        self.approval(SEND, "send_communication", minutes=60)
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="chat"), "too far")

    def test_record_for_other_tool_blocked(self):
        self.approval("mcp__outlook__other_tool", "send_communication")
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="chat"), "not")
        self.assertTrue(os.path.exists(self.path(".nova-tmp/approval.json")))

    def test_record_for_wrong_action_blocked(self):
        self.approval(SEND, "destructive")
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="chat"))

    def test_record_without_confirmation_blocked(self):
        self.approval(SEND, "send_communication", user_confirmation="")
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="chat"))

    def test_security_tool_always_blocked(self):
        self.approval("mcp__outlook__approve_invoice", "send_communication")
        self.assertBlocked(self.run_hook("actions", "mcp__outlook__approve_invoice", {}, context="chat"), "N4")
        self.assertBlocked(self.run_hook("actions", "mcp__outlook__approve_invoice", {}, context="routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__bank__make_payment", {}, context="chat"))
        self.assertBlocked(self.run_hook("actions", "mcp__vault__get_password", {}, context="chat"))

    def test_design_is_not_sign(self):
        self.assertAllowed(self.run_hook("actions", "mcp__adobe__search_design", {}, context="routine"))

    def test_unmapped_ambiguous_tool_asks_in_chat(self):
        self.assertAsked(self.run_hook("actions", "mcp__crm__frobnicate", {}, context="chat"))

    def test_bash_rm_in_chat_needs_record(self):
        cmd = "rm user/knowledge/people/dana-ruiz.md"
        self.assertBlocked(self.bash("actions", cmd, "chat"))
        self.approval("Bash", "destructive")
        self.assertAllowed(self.bash("actions", cmd, "chat"))
        self.assertFalse(os.path.exists(self.path(".nova-tmp/approval.json")))

    def test_malformed_connectors_falls_back_to_patterns(self):
        self.connectors("connectors: [unclosed\n")
        self.assertBlocked(self.run_hook("actions", "mcp__outlook__send_message", {}, context="routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__outlook__list_messages", {}, context="routine"))

    def test_garbage_stdin_fails_closed_in_routine(self):
        import subprocess
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.root, NOVA_CONTEXT="routine")
        r = subprocess.run(["python3", self.path(".claude/hooks/actions.py")], input="not json",
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2)


class UpstreamBypass(HookTestCase):
    origin = "git@github.com:CaptLocke/nova.git"

    def test_everything_allowed_in_upstream_repo(self):
        self.connectors(CONNECTORS)
        self.assertAllowed(self.run_hook("actions", SEND, {}, context="routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__bank__make_payment", {}, context=None))
        self.assertAllowed(self.bash("actions", "rm -rf user", None))
        self.assertAllowed(self.run_hook("paths", "Write", {"file_path": self.path("system/kernel.md"),
                                                             "content": "x"}, context="routine"))
        self.assertAllowed(self.bash("git", "git push --force origin main", "routine"))
        self.assertAllowed(self.bash("git", "git commit -m 'no trailers'", "routine"))

    def test_https_and_proxy_forms(self):
        for url in ("https://github.com/captlocke/nova", "https://github.com/CaptLocke/nova.git/",
                    "ssh://git@github.com/CaptLocke/nova.git",
                    "http://local_proxy@127.0.0.1:41231/git/CaptLocke/nova"):
            import subprocess
            subprocess.run(["git", "remote", "set-url", "origin", url], cwd=self.root, check=True)
            self.assertAllowed(self.run_hook("actions", SEND, {}, context="routine"))

    def test_similar_name_is_not_upstream(self):
        import subprocess
        for url in ("https://github.com/CaptLocke/nova-fork", "https://github.com/someone/nova"):
            subprocess.run(["git", "remote", "set-url", "origin", url], cwd=self.root, check=True)
            self.assertBlocked(self.run_hook("actions", "mcp__x__send_message", {}, context="routine"))


class NoManifest(HookTestCase):
    def test_missing_manifest_is_noop(self):
        os.remove(self.path("system/manifest.yaml"))
        self.assertAllowed(self.run_hook("actions", "mcp__x__send_message", {}, context="routine"))


if __name__ == "__main__":
    unittest.main()
