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
        self.assertTrue(os.path.exists(self.path(".atlas-tmp/approval.json")))

    def test_routine_marker_is_case_insensitive(self):
        self.approval(SEND, "send_communication")
        for marker in ("ROUTINE", " Routine ", "routine\n"):
            self.assertBlocked(self.run_hook("actions", SEND, {}, context=marker), "routine")
        self.assertTrue(os.path.exists(self.path(".atlas-tmp/approval.json")))

    def test_missing_or_other_context_is_chat(self):
        # missing, empty, 'chat' and other values all mean chat: a locked
        # action still needs (and consumes) an approval record
        for ctx in (None, "", "chat", "Chat-ish", "nightly"):
            r = self.run_hook("actions", SEND, {}, context=ctx)
            self.assertBlocked(r, "approval")
            self.assertNotIn("routine", r.stderr.split("approval")[0])
            self.approval(SEND, "send_communication")
            self.assertAllowed(self.run_hook("actions", SEND, {}, context=ctx))
            self.assertFalse(os.path.exists(self.path(".atlas-tmp/approval.json")))

    def test_security_blocked_without_context(self):
        self.approval("mcp__bank__make_payment", "send_communication")
        self.assertBlocked(self.run_hook("actions", "mcp__bank__make_payment", {}, context=None), "N4")

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
        self.assertFalse(os.path.exists(self.path(".atlas-tmp/approval.json")), "record must be consumed")
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
        self.assertTrue(os.path.exists(self.path(".atlas-tmp/approval.json")))

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
        self.assertFalse(os.path.exists(self.path(".atlas-tmp/approval.json")))

    def test_malformed_connectors_falls_back_to_patterns(self):
        self.connectors("connectors: [unclosed\n")
        self.assertBlocked(self.run_hook("actions", "mcp__outlook__send_message", {}, context="routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__outlook__list_messages", {}, context="routine"))

    def test_garbage_stdin_fails_closed_in_routine(self):
        import subprocess
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.root, ATLAS_CONTEXT="routine")
        r = subprocess.run(["python3", self.path(".claude/hooks/actions.py")], input="not json",
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2)


class UpstreamBypass(HookTestCase):
    origin = "git@github.com:CaptLocke/atlas-framework.git"

    def setUp(self):
        super().setUp()
        self.write(".atlas-maintainer", "")  # the maintainer's own copy

    def test_clone_without_marker_is_guarded(self):
        os.remove(self.path(".atlas-maintainer"))
        self.connectors(CONNECTORS)
        self.assertBlocked(self.run_hook("actions", SEND, {}, context="routine"))
        self.assertBlocked(self.bash("git", "git commit -m 'no trailers'", "routine"))

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
        for url in ("https://github.com/captlocke/atlas-framework", "https://github.com/CaptLocke/atlas-framework.git/",
                    "ssh://git@github.com/CaptLocke/atlas-framework.git",
                    "http://local_proxy@127.0.0.1:41231/git/CaptLocke/atlas-framework"):
            import subprocess
            subprocess.run(["git", "remote", "set-url", "origin", url], cwd=self.root, check=True)
            self.assertAllowed(self.run_hook("actions", SEND, {}, context="routine"))

    def test_similar_name_is_not_upstream(self):
        import subprocess
        for url in ("https://github.com/CaptLocke/atlas-framework-fork", "https://github.com/someone/atlas"):
            subprocess.run(["git", "remote", "set-url", "origin", url], cwd=self.root, check=True)
            self.assertBlocked(self.run_hook("actions", "mcp__x__send_message", {}, context="routine"))


class NoManifest(HookTestCase):
    def test_missing_manifest_still_enforces(self):
        os.remove(self.path("system/manifest.yaml"))
        self.assertBlocked(self.run_hook("actions", "mcp__x__send_message", {}, context="routine"))
        self.assertBlocked(self.run_hook("paths", "Write", {"file_path": self.path("system/kernel.md")},
                                         context="routine"), "owned")

    def test_missing_manifest_upstream_fallback(self):
        import subprocess
        os.remove(self.path("system/manifest.yaml"))
        self.write(".atlas-maintainer", "")
        subprocess.run(["git", "remote", "set-url", "origin", "https://github.com/CaptLocke/atlas-framework.git"],
                       cwd=self.root, check=True)
        self.assertAllowed(self.run_hook("actions", "mcp__x__send_message", {}, context="routine"))


class ReadNouns(HookTestCase):
    """Read tools whose names contain send/share/delete nouns are reads."""

    def test_read_verbs_with_risky_nouns(self):
        for name in ("mcp__slack__slack_get_thread_replies", "mcp__slack__list_channel_posts",
                     "mcp__drive__list_shared_drives", "mcp__drive__get_file_permissions",
                     "mcp__mail__list_sent_messages", "mcp__docs__list_comments",
                     "mcp__mail__search_deleted_items", "mcp__cal__list_events"):
            self.assertAllowed(self.run_hook("actions", name, {}, context="routine"))

    def test_read_verb_with_later_action_verb_is_risky(self):
        for name in ("mcp__mail__get_and_send_report", "mcp__drive__list_then_delete_files",
                     "mcp__drive__find_and_remove_duplicates"):
            self.assertBlocked(self.run_hook("actions", name, {}, context="routine"))

    def test_security_nouns_still_apply_to_reads(self):
        self.assertBlocked(self.run_hook("actions", "mcp__vault__get_password", {}, context="chat"), "N4")
        self.assertAllowed(self.run_hook("actions", "mcp__bank__list_payments", {}, context="routine"))


class ConnectorPrefixes(HookTestCase):
    def test_mixed_case_prefix_and_tool(self):
        self.connectors("connectors:\n  - connector: Outlook\n    mcp_prefix: mcp__Outlook__\n"
                        "    categories: [mail]\n    tool_risk:\n      Do_Thing: send\n      Frob: read\n")
        self.assertBlocked(self.run_hook("actions", "mcp__outlook__do_thing", {}, context="routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__OUTLOOK__frob", {}, context="routine"))

    def test_prefix_list_chat_and_routine(self):
        self.connectors("connectors:\n  - connector: gmail\n    mcp_prefixes: [mcp__claude_ai_Gmail__, "
                        "mcp__gmail-routine__]\n    categories: [mail]\n    tool_risk:\n"
                        "      frobnicate: send\n      zap: read\n")
        self.assertBlocked(self.run_hook("actions", "mcp__claude_ai_Gmail__frobnicate", {}, "routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__gmail-routine__frobnicate", {}, "routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__gmail-routine__zap", {}, "routine"))

    def test_server_name_fallback(self):
        self.connectors("connectors:\n  - connector: google-drive\n    mcp_prefix: mcp__gdrive__\n"
                        "    categories: [files]\n    tool_risk:\n      frobnicate: share\n      zap: read\n")
        self.assertBlocked(self.run_hook("actions", "mcp__Google_Drive__frobnicate", {}, "routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__Google_Drive__zap", {}, "routine"))


class MissedSends(HookTestCase):
    def test_comment_accept_decline_cancel(self):
        for name in ("mcp__docs__add_comment", "mcp__docs__comment_on_file", "mcp__cal__accept_invitation",
                     "mcp__cal__decline_event", "mcp__cal__rsvp", "mcp__cal__respond_to_event",
                     "mcp__cal__cancel_meeting"):
            self.assertBlocked(self.run_hook("actions", name, {}, context="routine"))

    def test_message_create_forms(self):
        for name in ("mcp__teams__chat_message_create", "mcp__teams__message_create",
                     "mcp__slack__create_message", "mcp__forum__create_post", "mcp__mail__create_reply",
                     "mcp__slack__chatPostMessage"):
            self.assertBlocked(self.run_hook("actions", name, {}, context="routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__mail__create_reply_draft", {}, context="routine"))

    def test_event_writes(self):
        self.assertBlocked(self.run_hook("actions", "mcp__cal__create_event", {"title": "Focus"}, "routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__cal__update_event", {"attendees": ["a"]}, "routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__cal__quick_add_event", {}, "routine"))
        self.connectors("connectors:\n  - connector: cal\n    mcp_prefix: mcp__cal__\n"
                        "    categories: [calendar]\n    tool_risk:\n      create_event: write\n"
                        "      update_event: write\n")
        self.assertAllowed(self.run_hook("actions", "mcp__cal__create_event", {"title": "Focus"}, "routine"))
        self.assertAllowed(self.run_hook("actions", "mcp__cal__create_event", {"attendees": []}, "routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__cal__create_event",
                                         {"title": "Sync", "attendees": ["dana@acme.example"]}, "routine"))
        self.assertBlocked(self.run_hook("actions", "mcp__cal__update_event",
                                         {"guestEmails": ["dana@acme.example"]}, "routine"))


class ImportFailure(HookTestCase):
    """A broken hook module must never let a call through by crashing."""

    def break_module(self, name):
        self.write(".claude/hooks/%s.py" % name, "raise ImportError('simulated damage')\n")

    def test_broken_shell_module(self):
        self.break_module("shell")
        for hook in ("actions", "paths", "git"):
            r = self.bash(hook, "ls", "routine")
            self.assertBlocked(r, "could not run")
        self.assertBlocked(self.run_hook("actions", "mcp__mail__send_message", {}, "chat"))
        self.assertBlocked(self.bash("git", "git push --force", "chat"))
        self.assertBlocked(self.run_hook("paths", "Write", {"file_path": self.path("system/k.md")}, "chat"))
        # clearly harmless calls in a chat are allowed with a warning
        r = self.run_hook("actions", "mcp__mail__list_messages", {}, "chat")
        self.assertAllowed(r)
        self.assertIn("warning", r.stderr)
        self.assertAllowed(self.run_hook("paths", "Write", {"file_path": self.path("user/work/a.md")}, "chat"))
        self.assertAllowed(self.bash("git", "ls -la", "chat"))

    def test_broken_module_missing_context_is_chat(self):
        self.break_module("shell")
        self.write("user/settings/governance.yaml", "x: 1\n")
        # harmless calls allowed with a warning
        self.assertAllowed(self.run_hook("actions", "mcp__mail__list_messages", {}, None))
        self.assertAllowed(self.run_hook("paths", "Write", {"file_path": self.path("user/work/a.md")}, None))
        # anything that looks locked is blocked
        for r in (self.run_hook("actions", "mcp__mail__send_message", {}, None),
                  self.run_hook("actions", "mcp__drive__share_file", {}, ""),
                  self.run_hook("actions", "mcp__bank__make_payment", {}, None),
                  self.run_hook("paths", "Write", {"file_path": self.path("user/settings/governance.yaml")}, None),
                  self.run_hook("paths", "Write", {"file_path": self.path("system/kernel.md")}, None),
                  self.bash("actions", "rm -rf user/knowledge", None),
                  self.bash("git", "git push --force origin main", None)):
            self.assertBlocked(r, "could not run")
        # routine marker blocks even harmless calls
        self.assertBlocked(self.run_hook("actions", "mcp__mail__list_messages", {}, "ROUTINE"))

    def test_broken_context_and_failsafe(self):
        self.break_module("context")
        self.assertBlocked(self.run_hook("actions", "mcp__mail__list_messages", {}, "routine"))
        self.break_module("failsafe")
        r = self.run_hook("actions", "mcp__mail__list_messages", {}, "chat")
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_broken_modules_in_upstream_repo_allow(self):
        import subprocess
        self.break_module("context")
        subprocess.run(["git", "remote", "set-url", "origin", "git@github.com:CaptLocke/atlas-framework.git"],
                       cwd=self.root, check=True)
        # 1.0.2: like the hooks themselves, the fail-safe bypasses only the maintainer's marked copy
        self.assertBlocked(self.run_hook("actions", "mcp__mail__send_message", {}, "routine"))
        self.write(".atlas-maintainer", "")
        self.assertAllowed(self.run_hook("actions", "mcp__mail__send_message", {}, "routine"))

    def test_exit_codes_only_0_or_2(self):
        self.write(".claude/hooks/shell.py", "import sys\nsys.exit(3)\n")
        r = self.bash("paths", "ls", "chat")
        self.assertIn(r.returncode, (0, 2))


if __name__ == "__main__":
    unittest.main()
