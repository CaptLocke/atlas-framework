"""Tests for system/tools/validate.py (T-2).

Each test builds a temporary repo: a copy of this repo's system/ and .claude/
plus fixture user files from fixtures/good or fixtures/bad, then runs the
validator with --root pointing at it.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
VALIDATE = os.path.join(REPO, "system", "tools", "validate.py")
GOOD = os.path.join(HERE, "fixtures", "good")
BAD = os.path.join(HERE, "fixtures", "bad")


def run_validate(root, *args):
    r = subprocess.run([sys.executable, VALIDATE, "--root", root] + list(args),
                       capture_output=True, text=True, timeout=120)
    return r


class TempRepo(unittest.TestCase):
    fixture = GOOD

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="nova-validatetest-")
        self.root = self.tmp
        ignore = shutil.ignore_patterns("__pycache__", "tests")
        shutil.copytree(os.path.join(REPO, "system"), os.path.join(self.root, "system"), ignore=ignore)
        shutil.copytree(os.path.join(REPO, ".claude"), os.path.join(self.root, ".claude"), ignore=ignore)
        for f in ("CLAUDE.md", "README.md", "LICENSE", "CHANGELOG.md", ".gitignore"):
            if os.path.exists(os.path.join(REPO, f)):
                shutil.copy(os.path.join(REPO, f), os.path.join(self.root, f))
        os.makedirs(os.path.join(self.root, "docs"), exist_ok=True)
        if self.fixture:
            shutil.copytree(os.path.join(self.fixture, "user"), os.path.join(self.root, "user"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def path(self, rel):
        return os.path.join(self.root, rel)

    def read(self, rel):
        with open(self.path(rel), encoding="utf-8") as f:
            return f.read()

    def write(self, rel, text):
        os.makedirs(os.path.dirname(self.path(rel)), exist_ok=True)
        with open(self.path(rel), "w", encoding="utf-8") as f:
            f.write(text)

    def replace(self, rel, old, new):
        text = self.read(rel)
        self.assertIn(old, text, "fixture text to replace not found in %s" % rel)
        self.write(rel, text.replace(old, new, 1))

    def errors(self, r):
        return [l for l in r.stdout.splitlines() if l.startswith("ERROR")]

    def assertError(self, r, path_part, pattern):
        errs = [e for e in self.errors(r) if path_part in e and re.search(pattern, e)]
        self.assertTrue(errs, "expected an ERROR on %s matching %r; got:\n%s" % (path_part, pattern, r.stdout))
        self.assertEqual(r.returncode, 1)


class GoodUserFixture(TempRepo):
    def test_good_user_half_passes(self):
        r = run_validate(self.root, "--user")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(self.errors(r), [])
        self.assertIn("0 error(s)", r.stdout)

    def test_good_paths_mode(self):
        r = run_validate(self.root, self.path("user/knowledge/people/dana-ruiz.md"),
                         self.path("user/settings/governance.yaml"))
        self.assertEqual(r.returncode, 0, r.stdout)


class SeededUserErrors(TempRepo):
    """Mutations of the good fixture; each must be caught."""

    def test_record_id_must_equal_path(self):
        self.replace("user/knowledge/people/dana-ruiz.md", "id: people/dana-ruiz", "id: people/dana")
        self.assertError(run_validate(self.root, "--user"), "dana-ruiz.md", "must equal the path")

    def test_record_broken_link(self):
        self.replace("user/knowledge/projects/enterprise-launch.md", "[[people/maya-chen]]",
                     "[[people/missing-person]]")
        self.assertError(run_validate(self.root, "--user"), "enterprise-launch.md", "does not exist")

    def test_record_bad_enum_and_date(self):
        self.replace("user/knowledge/commitments/send-pricing-feedback.md", "direction: i_owe",
                     "direction: they_owe")
        self.replace("user/knowledge/commitments/send-pricing-feedback.md", "due: 2026-10-15", "due: soon")
        r = run_validate(self.root, "--user")
        self.assertError(r, "send-pricing-feedback.md", "direction 'they_owe'")
        self.assertError(r, "send-pricing-feedback.md", "due must be")

    def test_record_missing_required(self):
        self.replace("user/knowledge/commitments/send-pricing-feedback.md",
                     'counterparty: "[[people/dana-ruiz]]"\n', "")
        self.replace("user/knowledge/organizations/acme.md", "summary: The user's employer.\n", "")
        r = run_validate(self.root, "--user")
        self.assertError(r, "send-pricing-feedback.md", "counterparty")
        self.assertError(r, "acme.md", "summary")

    def test_unknown_folder(self):
        self.write("user/knowledge/widgets/thing.md", "---\nid: widgets/thing\n---\n")
        self.assertError(run_validate(self.root, "--user"), "widgets/thing.md", "not a known type folder")

    def test_governance_locked_class_changed(self):
        self.replace("user/settings/governance.yaml", "send_communication: approve", "send_communication: auto")
        self.assertError(run_validate(self.root, "--user"), "governance.yaml", "locked")

    def test_governance_missing_class(self):
        self.replace("user/settings/governance.yaml", "  web_research: auto\n", "")
        self.assertError(run_validate(self.root, "--user"), "governance.yaml", "web_research.*missing")

    def test_routines_unknown_job(self):
        self.replace("user/settings/routines.yaml", "- triage", "- tidy-desk")
        self.assertError(run_validate(self.root, "--user"), "routines.yaml", "unknown job 'tidy-desk'")

    def test_registry_bad_kind_and_missing_path(self):
        self.replace("user/extensions/registry.yaml", "kind: type", "kind: widget")
        self.replace("user/extensions/registry.yaml", "path: types/deal.md", "path: types/nope.md")
        r = run_validate(self.root, "--user")
        self.assertError(r, "registry.yaml", "kind 'widget'")
        self.assertError(r, "registry.yaml", "does not exist")

    def test_sources_unknown_connector(self):
        self.replace("user/settings/sources.yaml", "connector: outlook", "connector: gmail")
        self.assertError(run_validate(self.root, "--user"), "sources.yaml", "not in connectors.yaml")

    def test_nova_unquoted_version_and_bad_plan(self):
        self.replace("user/settings/nova.yaml", 'installed_version: "1.0.0"', "installed_version: 1.0")
        self.replace("user/settings/nova.yaml", "plan: pro", "plan: platinum")
        r = run_validate(self.root, "--user")
        self.assertError(r, "nova.yaml", "installed_version")
        self.assertError(r, "nova.yaml", "plan must be")

    def test_nova_bad_company(self):
        self.replace("user/settings/nova.yaml", "website: https://acme.com", "website: acme")
        self.replace("user/settings/nova.yaml", "email_domains: [acme.com]", "email_domains: acme.com")
        self.replace("user/settings/nova.yaml", "fiscal_year_start_month: 2", "fiscal_year_start_month: 13")
        self.replace("user/settings/nova.yaml", "fiscal_year_label: end", "fiscal_year_label: middle")
        r = run_validate(self.root, "--user")
        for msg in ("company.website", "company.email_domains", "fiscal_year_start_month", "fiscal_year_label"):
            self.assertError(r, "nova.yaml", msg)

    def test_unparseable_yaml(self):
        self.write("user/settings/sources.yaml", "ingest: [\n")
        self.assertError(run_validate(self.root, "--user"), "sources.yaml", "cannot parse YAML")


class SetupAndLeniency(TempRepo):
    def test_protected_files_required_after_step5(self):
        os.remove(self.path("user/settings/governance.yaml"))
        os.remove(self.path("user/settings/data-rules.yaml"))
        r = run_validate(self.root, "--user")
        self.assertError(r, "user/settings/governance.yaml", "step 5")
        self.assertError(r, "user/settings/data-rules.yaml", "step 5")

    def test_step5_from_setup_state(self):
        os.remove(self.path("user/settings/governance.yaml"))
        self.replace("user/settings/nova.yaml", "attestation:\n", "attestation_pending:\n")
        self.replace("user/settings/nova.yaml", "first_brief_delivered", "attestation: null\nfirst_brief_delivered")
        self.write("user/.state/setup.yaml", "started: 2026-10-12\ncurrent_step: 5\ncompleted: [1, 2, 3, 4]\n")
        r = run_validate(self.root, "--user")
        self.assertNotIn("governance.yaml: missing", r.stdout)
        self.write("user/.state/setup.yaml", "started: 2026-10-12\ncurrent_step: 6\ncompleted: [1, 2, 3, 4, 5]\n")
        self.assertError(run_validate(self.root, "--user"), "user/settings/governance.yaml", "step 5")

    def test_not_required_before_setup(self):
        shutil.rmtree(self.path("user/settings"))
        os.makedirs(self.path("user/settings"))
        r = run_validate(self.root, "--user")
        self.assertNotIn("step 5", r.stdout)

    def test_open_ended_away_and_suppressed_kinds(self):
        self.replace("user/settings/rhythms.yaml", "  start: null", "  start: 2026-10-20")
        self.replace("user/settings/rhythms.yaml", "engagement: adaptive",
                     "engagement: adaptive\n  suppressed_kinds: [quiet_person]")
        r = run_validate(self.root, "--user")
        self.assertEqual(self.errors(r), [], r.stdout)
        self.replace("user/settings/rhythms.yaml", "suppressed_kinds: [quiet_person]", "suppressed_kinds: lots")
        self.assertError(run_validate(self.root, "--user"), "rhythms.yaml", "suppressed_kinds")

    def test_new_relationship_values(self):
        for value in ("prospect", "board"):
            self.replace("user/knowledge/people/dana-ruiz.md", "relationship: customer", "relationship: " + value)
            r = run_validate(self.root, "--user")
            self.assertEqual(self.errors(r), [], r.stdout)
            self.replace("user/knowledge/people/dana-ruiz.md", "relationship: " + value, "relationship: customer")

    def goal(self, slug, rank, status="active"):
        self.write("user/knowledge/goals/%s.md" % slug, "---\nid: goals/%s\ntype: goal\ntitle: %s\nsummary: A goal.\n"
                   "status: %s\ncreated: 2026-10-01\nupdated: 2026-10-01\nrank: %s\n---\nBody.\n" % (slug, slug, status, rank))

    def test_goal_ranks(self):
        self.goal("retention", 1)
        self.goal("launch", 2)
        self.goal("hiring", "null")
        r = run_validate(self.root, "--user")
        self.assertEqual(self.errors(r), [], r.stdout)
        self.goal("launch", 1)
        self.assertError(run_validate(self.root, "--user"), "goals/", "rank 1 is shared")
        self.goal("launch", 0)
        self.assertError(run_validate(self.root, "--user"), "launch.md", "rank must be a whole number")
        self.goal("launch", 2, status="achieved")
        r = run_validate(self.root, "--user")
        self.assertEqual(self.errors(r), [], r.stdout)
        self.assertIn("isn't active", r.stdout)

    def test_meetings_filter(self):
        # absent block is fine (defaults to include); a full block validates; bad values are errors
        self.replace("user/settings/rhythms.yaml", "engagement: adaptive",
                     "engagement: adaptive\nmeetings:\n  all_day: skip\n  tentative: include\n  not_responded: skip")
        r = run_validate(self.root, "--user")
        self.assertEqual(self.errors(r), [], r.stdout)
        self.replace("user/settings/rhythms.yaml", "not_responded: skip", "not_responded: maybe")
        self.assertError(run_validate(self.root, "--user"), "rhythms.yaml", "meetings.not_responded")

    def test_newer_data_version_is_a_warning(self):
        self.replace("user/settings/nova.yaml", "data_version: 1", "data_version: 2")
        r = run_validate(self.root, "--user")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("rollback", r.stdout)

    def test_custom_profile(self):
        self.replace("user/settings/routines.yaml", "profile: lean", "profile: custom")
        r = run_validate(self.root, "--user")
        self.assertEqual(r.returncode, 0, r.stdout)


class BadFixtures(TempRepo):
    fixture = BAD

    def test_bad_fixture_errors(self):
        r = run_validate(self.root, "--user")
        expect = [
            ("jordan-lee.md", "must equal the path"),
            ("jordan-lee.md", "status 'retired'"),
            ("jordan-lee.md", "created must be YYYY-MM-DD"),
            ("jordan-lee.md", "provenance 'guessed'"),
            ("jordan-lee.md", "relationship 'boss'"),
            ("jordan-lee.md", "unknown group 'managers'"),
            ("jordan-lee.md", r"\[\[people/nobody-here\]\] does not exist"),
            ("review-contract.md", "does not match folder"),
            ("review-contract.md", "updated is earlier than created"),
            ("governance.yaml", "level 'sometimes'"),
            ("governance.yaml", "send_communication is locked"),
            ("governance.yaml", "financial_legal_security is locked"),
            ("governance.yaml", "unknown class 'teleport'"),
            ("governance.yaml", "locked class 'destructive' cannot be overridden"),
            ("governance.yaml", "scope 'everything'"),
            ("routines.yaml", "profile must be"),
            ("routines.yaml", "5-field cron"),
            ("routines.yaml", "model must be a role"),
            ("routines.yaml", "unknown job 'make-coffee'"),
            ("routines.yaml", "when='fortnightly'"),
            ("routines.yaml", "unknown modifier 'colour'"),
            ("rhythms.yaml", "work_hours.days"),
            ("rhythms.yaml", "work_hours.start must be a quoted"),
            ("rhythms.yaml", "moments.daily_brief"),
            ("rhythms.yaml", "brief_max"),
            ("rhythms.yaml", "engagement"),
            ("rhythms.yaml", "meetings.all_day must be include or skip"),
            ("rhythms.yaml", "away.end is before"),
            ("rhythms.yaml", "unknown job 'make-coffee'"),
            ("rhythms.yaml", r"paused\[0\].until"),
            ("connectors.yaml", "mcp_prefix"),
            ("connectors.yaml", "unknown category 'fax'"),
            ("connectors.yaml", "risk 'harmless'"),
            ("connectors.yaml", "operation 'mail.teleport'|has no tool_risk tag"),
            ("connectors.yaml", "available_in_routines"),
            ("data-rules.yaml", "handling 'shred'"),
            ("data-rules.yaml", r"custom\[0\] needs name and match"),
            ("data-rules.yaml", r"exclusions\[0\]"),
            ("data-rules.yaml", r"exclusions\[1\]: 'record:'"),
        ]
        for path_part, pattern in expect:
            self.assertError(r, path_part, pattern)

    def test_bad_paths_mode(self):
        r = run_validate(self.root, self.path("user/knowledge/people/jordan-lee.md"))
        self.assertError(r, "jordan-lee.md", "must equal the path")


class SeededSystemErrors(TempRepo):
    fixture = None

    def system_errors(self):
        return run_validate(self.root, "--system")

    def test_version_mismatch(self):
        self.write("system/VERSION", "9.9.9\n")
        self.assertError(self.system_errors(), "system/VERSION", "does not match")

    def test_owned_path_missing(self):
        os.remove(self.path("CHANGELOG.md"))
        self.assertError(self.system_errors(), "manifest.yaml", "CHANGELOG.md does not exist")

    def test_manifest_fields(self):
        self.replace("system/manifest.yaml", "upstream: CaptLocke/nova", "upstream: not a repo")
        self.replace("system/manifest.yaml", "data_version: 1", "data_version: one")
        r = self.system_errors()
        self.assertError(r, "manifest.yaml", "upstream must be")
        self.assertError(r, "manifest.yaml", "data_version must be")

    def test_job_missing_section_and_bad_model(self):
        jobs = [f for f in os.listdir(self.path("system/jobs")) if f.endswith(".md") and f != "README.md"]
        if not jobs:
            self.skipTest("no job files yet")
        rel = "system/jobs/" + jobs[0]
        text = self.read(rel)
        text = re.sub(r"(?m)^## Early exit[ \t]*$", "## Leaving early", text)
        text = re.sub(r"(?m)^model: \w+", "model: huge", text, count=1)
        self.write(rel, text)
        r = self.system_errors()
        self.assertError(r, jobs[0], "Early exit")
        self.assertError(r, jobs[0], "model must be")

    def test_missing_job_when_others_exist(self):
        self.write("system/jobs/ingest.md", "---\ntype: job\nname: ingest\nmodel: fast\nskills: []\n---\n")
        for j in ("triage.md",):
            if os.path.exists(self.path("system/jobs/" + j)):
                os.remove(self.path("system/jobs/" + j))
        self.assertError(self.system_errors(), "system/jobs/triage.md", "expected job is missing")

    def test_skill_name_mismatch_and_missing_description(self):
        self.write(".claude/skills/nova-recall/SKILL.md", "---\nname: nova-remember\n---\n# x\n")
        r = self.system_errors()
        self.assertError(r, "nova-recall/SKILL.md", "must equal the folder name")
        self.assertError(r, "nova-recall/SKILL.md", "description is required")

    def test_skill_frontmatter_invalid_yaml(self):
        self.write(".claude/skills/nova-recall/SKILL.md",
                   "---\nname: nova-recall\ndescription: Find things: answers and more\n---\n# x\n")
        self.assertError(self.system_errors(), "nova-recall/SKILL.md", "not valid YAML")

    def test_settings_template_checked(self):
        self.replace("system/templates/settings/governance.yaml", "destructive: approve", "destructive: auto")
        self.assertError(self.system_errors(), "templates/settings/governance.yaml", "locked")

    def test_profile_unknown_job(self):
        self.replace("system/routine-profiles/lean.yaml", "- ingest", "- ingest-everything")
        self.assertError(self.system_errors(), "lean.yaml", "unknown job")

    def test_migration_versions(self):
        self.write("system/migrations/0002-broken.md",
                   "---\ntype: migration\nid: \"0002\"\nfrom_data_version: 1\nto_data_version: 3\n"
                   "additive: yes-ish\nneeds_user_input: false\n---\n")
        r = self.system_errors()
        self.assertError(r, "0002-broken.md", "to_data_version must be")
        self.assertError(r, "0002-broken.md", "additive")


class CurrentRepo(unittest.TestCase):
    """The repository itself must validate (system half; user half is empty)."""

    def test_repo_validates(self):
        r = subprocess.run([sys.executable, VALIDATE, "--all"], capture_output=True, text=True, cwd=REPO,
                           timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
