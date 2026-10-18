#!/usr/bin/env python3
"""Atlas validator.

Usage:
  python3 system/tools/validate.py [--system | --user | --all] [--root DIR] [paths...]

  --system   system half: manifest, VERSION, schemas, rules, skills, jobs,
             routine profiles, dashboard contracts, migrations, templates
  --user     user half: settings, knowledge records, extensions registry
  --all      both (the default when no paths are given)
  paths      validate only these files (dispatched by location)

Prints a human-readable report and exits 1 if any ERROR was found, else 0.
Missing folders/components are warnings while a component folder is still
empty; once a folder has files, every expected component must exist.

Sources of truth: system/schemas/schema.yaml (fields, enums, kinds),
system/schemas/settings.md (settings files), system/schemas/formats.md
(registry, manifest), system/guide/authoring.md (skill/job/migration/
dashboard outlines). Standard library plus vendored PyYAML
(system/tools/vendor/).
"""
import argparse
import datetime as dt
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import yaml  # noqa: E402  (vendored)

SKILLS = ["atlas-recall", "atlas-capture", "atlas-brief", "atlas-triage", "atlas-insights", "atlas-memory",
          "atlas-thoughts", "atlas-review", "atlas-status-update", "atlas-prep", "atlas-write", "atlas-setup",
          "atlas-settings", "atlas-extend", "atlas-health", "atlas-update", "atlas-dashboards", "atlas-away",
          "atlas-connectors", "atlas-report-issue"]
JOBS = ["ingest", "triage", "intelligence", "email-drafts", "meeting-prep", "daily-brief", "weekly-review",
        "status-updates", "monthly", "quarterly", "maintenance", "update-check"]
DASHBOARDS = ["daily-brief", "commitments", "projects", "goals", "week-ahead", "people", "decisions-risks",
              "control-center", "about-you", "atlas-guide", "records"]
ON_DEMAND_DASHBOARDS = ["project-page"]
JOB_SECTIONS = ["Purpose", "Runs when", "Away and paused", "Readiness check", "Inputs", "Steps",
                "Outputs", "Early exit", "Guardrails", "Run report"]
SKILL_SECTIONS = ["Purpose", "When to use", "Inputs", "Procedure", "Outputs", "Guardrails", "Done when"]
AUTONOMY_CLASSES = [
    "read", "records_write", "merge_supersede", "archive", "dashboards_refresh", "profile_update",
    "user_content_edit", "behavior_settings", "extensions_create", "updates_minor", "updates_major",
    "external_read", "web_research", "drafts_create", "docs_create", "deliverables_save",
    "drop_folder_housekeeping", "own_items_organize", "docs_edit", "own_calendar_manage", "tasks_manage",
    "shared_records_update", "governance_settings", "send_communication", "share_expose", "destructive",
    "financial_legal_security"]
BUILTIN_TRIGGERS = ["new_project", "new_key_person", "deadline_approaching", "key_meeting_upcoming",
                    "commitment_overdue", "playbook_start", "focus_time_needed"]
MOMENTS = ["morning_thoughts", "evening_thoughts", "daily_brief", "weekly_review", "status_updates",
           "goal_progress", "user_health_check", "system_health_check", "automation_review", "reset_goals",
           "role_refresh", "performance_review"]
PLANS = ["pro", "max_5x", "max_20x", "team", "enterprise"]
PROFILES = ["lean", "standard", "full", "custom"]
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
MEETING_FILTERS = ["all_day", "tentative", "not_responded"]
FALLBACK_METHODS = ["drop", "forward", "export", "manual"]
SETTINGS_FILES = ["atlas.yaml", "governance.yaml", "data-rules.yaml", "connectors.yaml", "sources.yaml",
                  "rhythms.yaml", "routines.yaml", "dashboards.yaml"]
# date-valued fields per record type (null allowed); "dt" also allows datetimes
DATE_FIELDS = {
    "project": {"start": "d", "target": "d"},
    "commitment": {"due": "d", "completed_on": "d"},
    "decision": {"decided_on": "d", "revisit_on": "d"},
    "event": {"start": "dt", "end": "dt"},
    "question": {"asked_on": "d", "answered_on": "d"},
    "person": {"last_contact": "d"},
    "playbook": {"last_used": "d"},
    "source": {"captured_on": "d", "occurred_on": "dt"},
}
WIKI_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CRON_FIELD_RE = re.compile(r"^[\d*,/\-A-Za-z]+$")


class Report:
    def __init__(self, root):
        self.root = root
        self.errors, self.warnings = [], []
        self.checked = set()

    def rel(self, path):
        try:
            return os.path.relpath(path, self.root).replace(os.sep, "/")
        except ValueError:
            return path

    def error(self, path, msg):
        self.errors.append((self.rel(path), msg))

    def warn(self, path, msg):
        self.warnings.append((self.rel(path), msg))

    def saw(self, path):
        self.checked.add(self.rel(path))


# ---------------------------------------------------------------- helpers
def load_yaml(path, rep):
    rep.saw(path)
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f), True
    except (OSError, yaml.YAMLError) as e:
        rep.error(path, "cannot parse YAML: %s" % str(e).replace("\n", " "))
        return None, False


def read_frontmatter(path, rep):
    """(frontmatter dict or None, body text)."""
    rep.saw(path)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        rep.error(path, "cannot read: %s" % e)
        return None, ""
    if not text.startswith("---"):
        rep.error(path, "missing YAML frontmatter (file must start with '---')")
        return None, text
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(\r?\n|$)", text, re.S)
    if not m:
        rep.error(path, "frontmatter is not closed with '---'")
        return None, text
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        rep.error(path, "frontmatter is not valid YAML: %s" % str(e).replace("\n", " "))
        return None, text[m.end():]
    if not isinstance(fm, dict):
        rep.error(path, "frontmatter must be a YAML mapping")
        return None, text[m.end():]
    return fm, text[m.end():]


def enum_misses(value, allowed):
    """Values not in 'allowed'. A list field (e.g. a source's flags) is checked entry by entry."""
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    return [v for v in values if v not in allowed]


def is_date(v):
    if isinstance(v, dt.date) and not isinstance(v, dt.datetime):
        return True
    return isinstance(v, str) and bool(DATE_RE.match(v)) and _real_date(v)


def _real_date(s):
    try:
        dt.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def is_datetime(v):
    if isinstance(v, dt.datetime):
        return True
    return isinstance(v, str) and bool(DATETIME_RE.match(v))


def headings(body):
    return {h.strip().lower() for h in re.findall(r"^##[ \t]+(.+?)[ \t]*#*$", body, re.M)}


def wiki_links(value):
    """All [[target]] strings inside a YAML value (recursively)."""
    out = []
    if isinstance(value, str):
        out += [t.strip() for t in WIKI_RE.findall(value)]
    elif isinstance(value, dict):
        for v in value.values():
            out += wiki_links(v)
    elif isinstance(value, list):
        for v in value:
            out += wiki_links(v)
    return out


def listdir(path):
    try:
        return sorted(os.listdir(path))
    except OSError:
        return []


class Ctx:
    """Repo-wide facts the checks share."""

    def __init__(self, root, rep):
        self.root = root
        self.rep = rep
        self.schema = None
        self.manifest = None
        self._registry = None

    def p(self, *parts):
        return os.path.join(self.root, *parts)

    def load_schema(self):
        if self.schema is None:
            path = self.p("system", "schemas", "schema.yaml")
            data = None
            if os.path.exists(path):
                data, _ = load_yaml(path, self.rep)
            else:
                self.rep.error(path, "missing (needed for all record checks)")
            self.schema = data if isinstance(data, dict) else {}
        return self.schema

    def load_manifest(self):
        if self.manifest is None:
            path = self.p("system", "manifest.yaml")
            data = None
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    try:
                        data = yaml.safe_load(f)
                    except yaml.YAMLError:
                        data = None
            self.manifest = data if isinstance(data, dict) else {}
        return self.manifest

    def registry(self):
        if self._registry is None:
            path = self.p("user", "extensions", "registry.yaml")
            entries = []
            if os.path.exists(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    entries = [e for e in (data.get("extensions") or []) if isinstance(e, dict)]
                except (OSError, yaml.YAMLError, AttributeError):
                    entries = []
            self._registry = entries
        return self._registry

    def registered(self, kind):
        return [str(e.get("name")) for e in self.registry() if e.get("kind") == kind and e.get("name")]

    def job_names(self):
        files = [f[:-3] for f in listdir(self.p("system", "jobs")) if f.endswith(".md") and f != "README.md"]
        names = set(files) if files else set(JOBS)
        return names | set(self.registered("job"))

    def user_types(self):
        """{folder: type name} for registered user types."""
        out = {}
        for e in self.registry():
            if e.get("kind") != "type" or not e.get("path"):
                continue
            path = self.p("user", "extensions", str(e["path"]))
            if not os.path.exists(path):
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
                fm = yaml.safe_load(m.group(1)) if m else {}
            except (OSError, yaml.YAMLError):
                fm = {}
            folder = str((fm or {}).get("folder", "")).strip("/").split("/")[-1]
            if folder:
                out[folder] = str((fm or {}).get("name") or e.get("name"))
        return out

    def record_exists(self, target):
        target = target.strip().strip("/")
        if target.endswith(".md"):
            target = target[:-3]
        return os.path.exists(self.p("user", "knowledge", *target.split("/")) + ".md")


# ================================================================ system
def check_manifest(c):
    rep = c.rep
    path = c.p("system", "manifest.yaml")
    if not os.path.exists(path):
        rep.error(path, "missing")
        return
    data, ok = load_yaml(path, rep)
    if not ok:
        return
    if not isinstance(data, dict):
        rep.error(path, "must be a YAML mapping")
        return
    for key in ("name", "version", "data_version", "min_plan", "support_email", "upstream", "owned_paths",
                "models", "profiles"):
        if key not in data:
            rep.error(path, "missing field '%s'" % key)
    if "version" in data and not (isinstance(data["version"], str) and SEMVER_RE.match(data["version"])):
        rep.error(path, "version must be a quoted-or-plain semver string like 1.0.0")
    if "data_version" in data and not (isinstance(data["data_version"], int) and data["data_version"] >= 1):
        rep.error(path, "data_version must be a positive integer")
    if data.get("min_plan") is not None and data.get("min_plan") not in PLANS:
        rep.error(path, "min_plan must be one of %s" % ", ".join(PLANS))
    if data.get("support_email") is None and "support_email" in data:
        rep.warn(path, "support_email is null (atlas-report-issue has nowhere to send reports)")
    kv, bv = data.get("kernel_version"), data.get("bootstrap_version")
    for key, val, rel, pattern in (("kernel_version", kv, ("system", "kernel.md"), r"atlas-kernel-(\d+)"),
                                   ("bootstrap_version", bv, ("system", "templates", "bootstrap-stub.md"),
                                    r"Atlas bootstrap (\d+)")):
        if val is None:
            rep.error(path, "missing field '%s'" % key)
            continue
        fp = c.p(*rel)
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                found = re.findall(pattern, f.read())
            if not found or any(int(x) != val for x in found):
                rep.error(fp, "%s marker must be %s (system/manifest.yaml: %s); found %s"
                          % (key.split("_")[0], val, key, ", ".join(found) or "none"))
    up = data.get("upstream")
    if up is not None and not (isinstance(up, str) and re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", up)):
        rep.error(path, "upstream must be 'owner/repo'")
    owned = data.get("owned_paths")
    if owned is not None:
        if not isinstance(owned, list) or not owned:
            rep.error(path, "owned_paths must be a non-empty list")
        else:
            for p in owned:
                if not isinstance(p, str) or p.startswith("/") or ".." in p.split("/"):
                    rep.error(path, "owned_paths entry %r must be a relative path" % (p,))
                    continue
                if p.startswith("user"):
                    rep.error(path, "owned_paths must never include user/ (%s)" % p)
                if not os.path.exists(c.p(*p.rstrip("/").split("/"))):
                    rep.error(path, "owned path %s does not exist" % p)
                elif p.endswith("/") != os.path.isdir(c.p(*p.rstrip("/").split("/"))):
                    rep.error(path, "owned path %s: folders end with '/', files don't" % p)
            for must in ("system/", ".claude/"):
                if must not in owned:
                    rep.error(path, "owned_paths must include %s" % must)
    models = data.get("models")
    if models is not None:
        if not isinstance(models, dict) or not {"fast", "strongest"} <= set(models):
            rep.error(path, "models must define 'fast' and 'strongest'")
    profiles = data.get("profiles")
    if profiles is not None:
        if not isinstance(profiles, list) or not profiles:
            rep.error(path, "profiles must be a non-empty list")
        else:
            pdir = c.p("system", "routine-profiles")
            have = [f for f in listdir(pdir) if f.endswith(".yaml")]
            for prof in profiles:
                if prof not in PROFILES:
                    rep.error(path, "unknown profile %r" % prof)
                if not os.path.exists(os.path.join(pdir, "%s.yaml" % prof)):
                    (rep.error if have else rep.warn)(path, "profile file system/routine-profiles/%s.yaml "
                                                      "missing" % prof)

    vpath = c.p("system", "VERSION")
    if not os.path.exists(vpath):
        rep.error(vpath, "missing")
    else:
        rep.saw(vpath)
        with open(vpath, encoding="utf-8") as f:
            v = f.read().strip()
        if v != str(data.get("version")):
            rep.error(vpath, "VERSION (%s) does not match system/manifest.yaml version (%s)"
                      % (v, data.get("version")))


def check_schema_files(c):
    rep = c.rep
    schema = c.load_schema()
    if not schema:
        return
    for key in ("common", "types", "autonomy_levels", "locked_classes", "registry_kinds", "tool_risk",
                "connector_categories", "routine_modifiers", "data_rule_handling"):
        if key not in schema:
            rep.error(c.p("system", "schemas", "schema.yaml"), "missing section '%s'" % key)
    for tname, t in (schema.get("types") or {}).items():
        md = c.p("system", "schemas", "%s.md" % tname)
        if not os.path.exists(md):
            rep.error(md, "schema doc for type '%s' missing" % tname)
        if not isinstance(t, dict) or "folder" not in t or "status" not in (t.get("enums") or {}):
            rep.error(c.p("system", "schemas", "schema.yaml"), "type '%s' needs folder and a status enum" % tname)
    for f in listdir(c.p("system", "schemas")):
        if f.endswith(".md"):
            fm, _ = read_frontmatter(c.p("system", "schemas", f), rep)
            if fm is not None and fm.get("type") != "schema":
                rep.error(c.p("system", "schemas", f), "frontmatter type must be 'schema'")


def check_rules(c):
    rdir = c.p("system", "rules")
    files = [f for f in listdir(rdir) if f.endswith(".md")]
    if not files:
        c.rep.warn(rdir, "no rules found")
    for f in files:
        path = os.path.join(rdir, f)
        fm, body = read_frontmatter(path, c.rep)
        if fm is None:
            continue
        if fm.get("type") != "rule":
            c.rep.error(path, "frontmatter type must be 'rule'")
        if fm.get("name") != f[:-3]:
            c.rep.error(path, "frontmatter name must be '%s'" % f[:-3])


def check_skill(c, path, name=None):
    rep = c.rep
    name = name or os.path.basename(os.path.dirname(path))
    fm, body = read_frontmatter(path, rep)
    if fm is None:
        return
    if fm.get("name") != name:
        rep.error(path, "frontmatter name %r must equal the folder name %r" % (fm.get("name"), name))
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        rep.error(path, "frontmatter description is required")
    elif len(desc) > 1024:
        rep.warn(path, "description is longer than 1024 characters")
    have = headings(body)
    missing = [s for s in SKILL_SECTIONS if s.lower() not in have]
    if missing:
        rep.warn(path, "missing outline sections: %s (system/guide/authoring.md)" % ", ".join(missing))
    lines = body.count("\n")
    if lines > 300:
        rep.warn(path, "SKILL.md is %d lines (target under ~250; move detail to reference/)" % lines)


def check_skills(c):
    sdir = c.p(".claude", "skills")
    dirs = [d for d in listdir(sdir) if os.path.isdir(os.path.join(sdir, d))]
    for d in dirs:
        sk = os.path.join(sdir, d, "SKILL.md")
        if not os.path.exists(sk):
            c.rep.error(os.path.join(sdir, d), "skill folder has no SKILL.md")
        else:
            check_skill(c, sk, d)
    for s in SKILLS:
        if s not in dirs:
            (c.rep.error if dirs else c.rep.warn)(os.path.join(sdir, s), "expected skill is missing")


def check_job(c, path, user=False):
    rep = c.rep
    stem = os.path.basename(path)[:-3]
    fm, body = read_frontmatter(path, rep)
    if fm is None:
        return
    if fm.get("type") != "job":
        rep.error(path, "frontmatter type must be 'job'")
    if fm.get("name") != stem:
        rep.error(path, "frontmatter name %r must equal the file name %r" % (fm.get("name"), stem))
    if fm.get("model") not in ("fast", "strongest"):
        rep.error(path, "frontmatter model must be 'fast' or 'strongest'")
    skills = fm.get("skills")
    if not isinstance(skills, list):
        rep.error(path, "frontmatter skills must be a list")
    else:
        sdir = c.p(".claude", "skills")
        user_skills = set(c.registered("skill"))
        for s in skills:
            if not os.path.exists(os.path.join(sdir, str(s), "SKILL.md")) and s not in user_skills:
                (rep.error if listdir(sdir) else rep.warn)(path, "skill %r not found" % s)
    have = headings(body)
    missing = [s for s in JOB_SECTIONS if s.lower() not in have]
    if missing:
        rep.error(path, "missing required sections: %s (system/guide/authoring.md)" % ", ".join(missing))
    lines = body.count("\n")
    if lines > 150:
        rep.warn(path, "job spec is %d lines (target under ~120)" % lines)


def check_jobs(c):
    jdir = c.p("system", "jobs")
    files = [f for f in listdir(jdir) if f.endswith(".md") and f != "README.md"]
    for f in files:
        check_job(c, os.path.join(jdir, f))
    for j in JOBS:
        if "%s.md" % j not in files:
            (c.rep.error if files else c.rep.warn)(os.path.join(jdir, j + ".md"), "expected job is missing")


def check_dashboards(c):
    ddir = c.p("system", "dashboards")
    contracts = [f for f in listdir(ddir) if f.endswith(".contract.md")]
    jobs = c.job_names()
    for f in contracts:
        path = os.path.join(ddir, f)
        name = f[:-len(".contract.md")]
        fm, body = read_frontmatter(path, c.rep)
        if fm is None:
            continue
        if fm.get("type") != "dashboard-contract":
            c.rep.error(path, "frontmatter type must be 'dashboard-contract'")
        if fm.get("name") != name:
            c.rep.error(path, "frontmatter name must be %r" % name)
        tpl = fm.get("template")
        if not tpl or not os.path.exists(os.path.join(ddir, str(tpl))):
            c.rep.error(path, "template %r not found in system/dashboards/" % tpl)
        if not isinstance(fm.get("size_budget_kb"), int):
            c.rep.error(path, "size_budget_kb must be an integer")
        sah = fm.get("stale_after_hours")
        if sah is not None and (isinstance(sah, bool) or not isinstance(sah, int) or sah < 1):
            c.rep.error(path, "stale_after_hours must be a whole number of hours (omit it for pages that never go stale)")
        rb = fm.get("republished_by")
        if not isinstance(rb, list):
            c.rep.error(path, "republished_by must be a list")
        else:
            for j in rb:
                if j not in jobs and not str(j).startswith("atlas-"):
                    c.rep.warn(path, "republished_by names unknown job %r" % j)
        missing = [s for s in ("Purpose", "Data", "Sources", "Rendering notes")
                   if not any(h.startswith(s.lower()) for h in headings(body))]
        if missing:
            c.rep.warn(path, "missing outline sections: %s" % ", ".join(missing))
    for d in DASHBOARDS + ON_DEMAND_DASHBOARDS:
        if "%s.contract.md" % d not in contracts:
            (c.rep.error if contracts else c.rep.warn)(os.path.join(ddir, d + ".contract.md"),
                                                       "expected dashboard contract is missing")


def check_migrations(c):
    mdir = c.p("system", "migrations")
    files = [f for f in listdir(mdir) if f.endswith(".md") and f != "README.md"]
    manifest = c.load_manifest()
    top = 0
    for f in files:
        path = os.path.join(mdir, f)
        m = re.match(r"^(\d{4})-[a-z0-9-]+\.md$", f)
        if not m:
            c.rep.error(path, "migration files are named NNNN-<slug>.md")
        fm, body = read_frontmatter(path, c.rep)
        if fm is None:
            continue
        if fm.get("type") != "migration":
            c.rep.error(path, "frontmatter type must be 'migration'")
        if m and str(fm.get("id")).zfill(4) != m.group(1):
            c.rep.error(path, "frontmatter id must be %s" % m.group(1))
        fr, to = fm.get("from_data_version"), fm.get("to_data_version")
        if not isinstance(fr, int) or not isinstance(to, int) or to != fr + 1:
            c.rep.error(path, "to_data_version must be from_data_version + 1 (integers)")
        else:
            top = max(top, to)
        for k in ("additive", "needs_user_input"):
            if not isinstance(fm.get(k), bool):
                c.rep.error(path, "%s must be true or false" % k)
        missing = [s for s in ("Purpose", "Affected paths", "Transformation", "Validation",
                               "Questions for the user", "Reverse step") if s.lower() not in headings(body)]
        if missing:
            c.rep.warn(path, "missing outline sections: %s" % ", ".join(missing))
    if files and isinstance(manifest.get("data_version"), int) and top != manifest["data_version"]:
        c.rep.error(mdir, "latest migration reaches data_version %d but the manifest says %s"
                    % (top, manifest["data_version"]))


def check_templates(c):
    tdir = c.p("system", "templates", "settings")
    files = [f for f in listdir(tdir) if f.endswith(".yaml")]
    if not files:
        c.rep.warn(tdir, "no settings templates found")
    for f in files:
        check_settings_file(c, os.path.join(tdir, f), template=True)
    for f in SETTINGS_FILES:
        if files and f not in files:
            c.rep.error(os.path.join(tdir, f), "settings template is missing")
    reg = c.p("system", "templates", "extensions", "registry.yaml")
    if os.path.exists(reg):
        check_registry(c, reg)


def check_profiles(c):
    pdir = c.p("system", "routine-profiles")
    for f in [f for f in listdir(pdir) if f.endswith(".yaml")]:
        path = os.path.join(pdir, f)
        data, ok = load_yaml(path, c.rep)
        if ok:
            check_routines(c, path, data, template=False)
            if isinstance(data, dict) and data.get("profile") != f[:-5]:
                c.rep.error(path, "profile must be %r" % f[:-5])


CHANGELOG_SUBSECTIONS = ("what's new", "action needed", "under the hood")


def check_changelog(c):
    """CHANGELOG.md has a section for system/VERSION and only the three known ### headings
    (release checklist: docs/maintainers/releasing.md, kept in the maintainer's private repo)."""
    path = c.p("CHANGELOG.md")
    if not os.path.exists(path):
        return  # reported by check_manifest (owned path missing)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    versions = [m.group(1) for m in re.finditer(r"^## +(\S+)", text, re.M)]
    vpath = c.p("system", "VERSION")
    if os.path.exists(vpath):
        with open(vpath, encoding="utf-8") as f:
            ver = f.read().strip()
        if ver and ver not in versions:
            c.rep.error(path, "no '## %s' section for system/VERSION (see the release checklist, kept in "
                              "the maintainer's private repo)" % ver)
    for m in re.finditer(r"^### +(.+?)\s*$", text, re.M):
        if m.group(1).strip().lower() not in CHANGELOG_SUBSECTIONS:
            c.rep.error(path, "unknown heading '### %s' (use What's new, Action needed, or Under the hood)"
                        % m.group(1).strip())


def check_system(c):
    check_manifest(c)
    check_changelog(c)
    check_schema_files(c)
    check_rules(c)
    check_skills(c)
    check_jobs(c)
    check_profiles(c)
    check_dashboards(c)
    check_migrations(c)
    check_templates(c)
    for hook in ("context.py", "actions.py", "paths.py", "git.py", "shell.py"):
        if not os.path.exists(c.p(".claude", "hooks", hook)):
            c.rep.error(c.p(".claude", "hooks", hook), "hook script missing")
    if not os.path.exists(c.p(".claude", "settings.json")):
        c.rep.error(c.p(".claude", "settings.json"), "missing (hooks are not registered)")


# ================================================================ settings
def need(rep, path, data, key, template, kind=None):
    """Check a required key; returns the value (or None)."""
    if not isinstance(data, dict) or key not in data:
        rep.error(path, "missing '%s'" % key)
        return None
    v = data[key]
    if v is None and not template:
        rep.error(path, "'%s' must be set" % key)
    return v


def check_level(rep, path, where, value, levels):
    if value not in levels:
        rep.error(path, "%s: level %r is not one of %s" % (where, value, ", ".join(levels)))


def check_governance(c, path, data, template):
    rep, schema = c.rep, c.load_schema()
    levels = schema.get("autonomy_levels") or ["auto", "propose", "approve", "never"]
    locked = schema.get("locked_classes") or {}
    auto = need(rep, path, data, "autonomy", template)
    if isinstance(auto, dict):
        for k, v in auto.items():
            if k not in AUTONOMY_CLASSES:
                rep.error(path, "autonomy: unknown class %r" % k)
                continue
            check_level(rep, path, "autonomy.%s" % k, v, levels)
        for k in AUTONOMY_CLASSES:
            if k not in auto:
                rep.error(path, "autonomy: class %r is missing" % k)
        for k, v in locked.items():
            if k in auto and auto[k] != v:
                rep.error(path, "autonomy.%s is locked at %r and cannot be changed" % (k, v))
    elif auto is not None:
        rep.error(path, "autonomy must be a mapping")
    overrides = data.get("overrides") if isinstance(data, dict) else None
    if overrides is None:
        return
    if not isinstance(overrides, list):
        rep.error(path, "overrides must be a list")
        return
    cats = schema.get("connector_categories") or []
    for i, o in enumerate(overrides):
        where = "overrides[%d]" % i
        if not isinstance(o, dict):
            rep.error(path, "%s must be a mapping" % where)
            continue
        scope = o.get("scope")
        if not isinstance(scope, str):
            rep.error(path, "%s: scope is required" % where)
        elif scope.startswith("connector:"):
            if not scope[len("connector:"):].strip():
                rep.error(path, "%s: connector scope needs a name" % where)
        elif scope.startswith("category:"):
            if scope[len("category:"):].strip() not in cats:
                rep.error(path, "%s: unknown category in %r" % (where, scope))
        elif re.match((schema.get("common") or {}).get("id_pattern", r"^[a-z]+/[a-z0-9][a-z0-9-]*$"), scope):
            if not template and not c.record_exists(scope):
                rep.warn(path, "%s: record %s does not exist" % (where, scope))
        else:
            rep.error(path, "%s: scope %r must be a record ID, connector:<name> or category:<category>"
                      % (where, scope))
        keys = [k for k in o if k != "scope"]
        if not keys:
            rep.error(path, "%s names no class" % where)
        for k in keys:
            if k in locked:
                rep.error(path, "%s: locked class %r cannot be overridden" % (where, k))
            elif k not in AUTONOMY_CLASSES:
                rep.error(path, "%s: unknown class %r" % (where, k))
            else:
                check_level(rep, path, "%s.%s" % (where, k), o[k], levels)


def check_data_rules(c, path, data, template):
    rep, schema = c.rep, c.load_schema()
    handling = schema.get("data_rule_handling") or ["ignore", "pointer", "summary", "full"]
    cats = need(rep, path, data, "categories", template)
    if isinstance(cats, dict):
        for k, v in cats.items():
            if v not in handling:
                rep.error(path, "categories.%s: handling %r is not one of %s" % (k, v, ", ".join(handling)))
    elif cats is not None:
        rep.error(path, "categories must be a mapping")
    custom = (data or {}).get("custom") or []
    if not isinstance(custom, list):
        rep.error(path, "custom must be a list")
        custom = []
    for i, cu in enumerate(custom):
        if not isinstance(cu, dict) or not cu.get("name") or not cu.get("match"):
            rep.error(path, "custom[%d] needs name and match" % i)
        elif cu.get("handling") not in handling:
            rep.error(path, "custom[%d]: handling %r invalid" % (i, cu.get("handling")))
    excl = (data or {}).get("exclusions") or []
    if not isinstance(excl, list):
        rep.error(path, "exclusions must be a list")
        excl = []
    for i, e in enumerate(excl):
        if not isinstance(e, str) or not re.match(r"^[A-Za-z0-9_.-]+:\s*\S", e):
            rep.error(path, "exclusions[%d] must look like '<category or connector>: <query>' or "
                      "'record: <id>'" % i)
        elif e.startswith("record:") and not re.match(r"^record:\s*[a-z]+/[a-z0-9][a-z0-9-]*$", e):
            rep.error(path, "exclusions[%d]: 'record:' needs a record ID" % i)


def check_connectors(c, path, data, template):
    rep, schema = c.rep, c.load_schema()
    cats = schema.get("connector_categories") or []
    risks = schema.get("tool_risk") or []
    conns = need(rep, path, data, "connectors", template=True)
    if conns is None:
        return
    if not isinstance(conns, list):
        rep.error(path, "connectors must be a list")
        return
    seen = set()
    for i, cn in enumerate(conns):
        where = "connectors[%d]" % i
        if not isinstance(cn, dict):
            rep.error(path, "%s must be a mapping" % where)
            continue
        name = cn.get("connector")
        if not name:
            rep.error(path, "%s: connector name is required" % where)
        elif name in seen:
            rep.error(path, "%s: duplicate connector %r" % (where, name))
        seen.add(name)
        where = "connector %s" % name
        prefix = cn.get("mcp_prefix")
        if not isinstance(prefix, str) or not re.match(r"^mcp__.+__$", prefix):
            rep.error(path, "%s: mcp_prefix must look like 'mcp__<server>__'" % where)
        ccats = cn.get("categories") or []
        if not isinstance(ccats, list) or not ccats:
            rep.error(path, "%s: categories must be a non-empty list" % where)
            ccats = []
        for cat in ccats:
            if cat not in cats:
                rep.error(path, "%s: unknown category %r" % (where, cat))
        tr = cn.get("tool_risk")
        if not isinstance(tr, dict) or not tr:
            rep.error(path, "%s: tool_risk must tag every tool" % where)
            tr = {}
        for tool, r in tr.items():
            if r not in risks:
                rep.error(path, "%s: tool %s has risk %r (one of %s)" % (where, tool, r, ", ".join(risks)))
        ops = cn.get("operations") or {}
        if not isinstance(ops, dict):
            rep.error(path, "%s: operations must be a mapping" % where)
            ops = {}
        for op, spec in ops.items():
            m = re.match(r"^([a-z]+)\.([a-z_]+)$", str(op))
            if not m or m.group(1) not in cats:
                rep.error(path, "%s: operation %r must be '<category>.<operation>'" % (where, op))
            elif m.group(1) not in ccats:
                rep.warn(path, "%s: operation %s is outside the connector's categories" % (where, op))
            tool = spec.get("tool") if isinstance(spec, dict) else None
            if not tool:
                rep.error(path, "%s: operation %s needs a tool" % (where, op))
            elif tool not in tr:
                rep.error(path, "%s: tool %s (operation %s) has no tool_risk tag" % (where, tool, op))
        air = cn.get("available_in_routines", "unknown")
        if air not in (True, False, "unknown"):
            rep.error(path, "%s: available_in_routines must be true, false or unknown" % where)
        if cn.get("own_storage", False) not in (True, False):
            rep.error(path, "%s: own_storage must be true or false" % where)
        if cn.get("mapped_on") is not None and not is_date(cn.get("mapped_on")):
            rep.error(path, "%s: mapped_on must be YYYY-MM-DD" % where)


def check_sources(c, path, data, template):
    rep, schema = c.rep, c.load_schema()
    cats = schema.get("connector_categories") or []
    connectors = _connector_names(c)
    for key in ("ingest", "fallbacks"):
        items = (data or {}).get(key)
        if items is None:
            if key == "ingest":
                rep.error(path, "missing 'ingest'")
            continue
        if not isinstance(items, list):
            rep.error(path, "%s must be a list" % key)
            continue
        for i, it in enumerate(items):
            where = "%s[%d]" % (key, i)
            if not isinstance(it, dict):
                rep.error(path, "%s must be a mapping" % where)
                continue
            if it.get("category") not in cats:
                rep.error(path, "%s: unknown category %r" % (where, it.get("category")))
            if key == "ingest":
                cn = it.get("connector")
                if not cn:
                    rep.error(path, "%s: connector is required" % where)
                elif connectors is not None and cn not in connectors:
                    rep.error(path, "%s: connector %r is not in connectors.yaml" % (where, cn))
                lb = it.get("lookback_days_initial")
                if lb is not None and not (isinstance(lb, int) and lb >= 0):
                    rep.error(path, "%s: lookback_days_initial must be a whole number" % where)
            else:
                if it.get("method") not in FALLBACK_METHODS:
                    rep.error(path, "%s: method must be one of %s" % (where, ", ".join(FALLBACK_METHODS)))


def _connector_names(c):
    path = c.p("user", "settings", "connectors.yaml")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return {cn.get("connector") for cn in (data.get("connectors") or []) if isinstance(cn, dict)}
    except (OSError, yaml.YAMLError, AttributeError):
        return None


def _on(v):
    return isinstance(v, bool) or (isinstance(v, dict) and isinstance(v.get("enabled", v.get("on", v.get(True))), bool))


def check_rhythms(c, path, data, template):
    rep = c.rep
    if not isinstance(data, dict):
        rep.error(path, "must be a YAML mapping")
        return
    wh = need(rep, path, data, "work_hours", template)
    if isinstance(wh, dict):
        days = wh.get("days")
        if not isinstance(days, list) or not days or any(d not in DAYS for d in days):
            rep.error(path, "work_hours.days must list days from %s" % ", ".join(DAYS))
        for k in ("start", "end"):
            v = wh.get(k)
            if not (isinstance(v, str) and re.match(r"^([01]\d|2[0-3]):[0-5]\d$", v)):
                rep.error(path, "work_hours.%s must be a quoted \"HH:MM\" time (got %r)" % (k, v))
    moments = need(rep, path, data, "moments", template)
    if isinstance(moments, dict):
        for k, v in moments.items():
            if k not in MOMENTS:
                rep.warn(path, "moments: unknown moment %r" % k)
            if not _on(v):
                rep.error(path, "moments.%s must be on/off or a mapping with 'on'" % k)
    triggers = data.get("triggers")
    if isinstance(triggers, dict):
        known = set(BUILTIN_TRIGGERS) | set(c.registered("trigger"))
        for k, v in triggers.items():
            if k not in known:
                rep.warn(path, "triggers: %r is not a built-in or registered trigger" % k)
            if not _on(v):
                rep.error(path, "triggers.%s must be on/off or a mapping with 'on'" % k)
            if isinstance(v, dict) and "days" in v and not (isinstance(v["days"], int) and v["days"] > 0):
                rep.error(path, "triggers.%s.days must be a positive whole number" % k)
    elif triggers is not None:
        rep.error(path, "triggers must be a mapping")
    ins = data.get("insights")
    if isinstance(ins, dict):
        if "brief_max" in ins and not (isinstance(ins["brief_max"], int) and ins["brief_max"] >= 0):
            rep.error(path, "insights.brief_max must be a whole number")
        if "engagement" in ins and ins["engagement"] not in ("adaptive", "fixed"):
            rep.error(path, "insights.engagement must be adaptive or fixed")
        sk = ins.get("suppressed_kinds")
        if sk is not None and not (isinstance(sk, list) and all(isinstance(x, str) for x in sk)):
            rep.error(path, "insights.suppressed_kinds must be a list of insight kinds")
        for k in ins:
            if k not in ("brief_max", "engagement", "suppressed_kinds"):
                rep.warn(path, "insights: unknown key %r" % k)
    meetings = data.get("meetings")
    if isinstance(meetings, dict):
        for k, v in meetings.items():
            if k not in MEETING_FILTERS:
                rep.warn(path, "meetings: unknown key %r (known: %s)" % (k, ", ".join(MEETING_FILTERS)))
            elif v not in ("include", "skip"):
                rep.error(path, "meetings.%s must be include or skip (got %r)" % (k, v))
    elif meetings is not None:
        rep.error(path, "meetings must be a mapping (all_day, tentative, not_responded)")
    away = data.get("away")
    if away is not None:
        if not isinstance(away, dict):
            rep.error(path, "away must be a mapping (start, end, set_on)")
        else:
            for k in ("start", "end", "set_on"):
                v = away.get(k)
                if v is not None and not is_date(v):
                    rep.error(path, "away.%s must be YYYY-MM-DD or null" % k)
            s, e = away.get("start"), away.get("end")
            # end: null while start is set means open-ended away (until the user is back)
            if e is not None and s is None:
                rep.error(path, "away.end is set but away.start is null")
            if is_date(s) and is_date(e) and str(e) < str(s):
                rep.error(path, "away.end is before away.start")
    paused = data.get("paused") or []
    if not isinstance(paused, list):
        rep.error(path, "paused must be a list")
        paused = []
    jobs = c.job_names()
    for i, p in enumerate(paused):
        if not isinstance(p, dict) or not (p.get("job") or p.get("moment")):
            rep.error(path, "paused[%d] needs job or moment" % i)
            continue
        if p.get("job") and p["job"] not in jobs:
            rep.error(path, "paused[%d]: unknown job %r" % (i, p["job"]))
        if p.get("moment") and p["moment"] not in MOMENTS:
            rep.warn(path, "paused[%d]: unknown moment %r" % (i, p["moment"]))
        if p.get("until") is not None and not is_date(p.get("until")):
            rep.error(path, "paused[%d].until must be YYYY-MM-DD or null" % i)


def check_routines(c, path, data, template):
    rep, schema = c.rep, c.load_schema()
    if not isinstance(data, dict):
        rep.error(path, "must be a YAML mapping")
        return
    prof = data.get("profile")
    if prof is None and not template or prof is not None and prof not in PROFILES:
        rep.error(path, "profile must be one of %s" % ", ".join(PROFILES))
    routines = data.get("routines")
    if not isinstance(routines, list):
        rep.error(path, "routines must be a list")
        return
    mods = schema.get("routine_modifiers") or {}
    roles = set((c.load_manifest().get("models") or {}).keys()) or {"fast", "strongest"}
    jobs = c.job_names()
    names = set()
    for i, r in enumerate(routines):
        where = "routines[%d]" % i
        if not isinstance(r, dict):
            rep.error(path, "%s must be a mapping" % where)
            continue
        name = r.get("name")
        if not isinstance(name, str) or not SLUG_RE.match(name):
            rep.error(path, "%s: name must be a lowercase slug" % where)
        elif name in names:
            rep.error(path, "%s: duplicate routine name %r" % (where, name))
        names.add(name)
        where = "routine %s" % name
        sched = r.get("schedule")
        fields = sched.split() if isinstance(sched, str) else []
        if len(fields) != 5 or not all(CRON_FIELD_RE.match(f) for f in fields):
            rep.error(path, "%s: schedule must be a 5-field cron expression (got %r)" % (where, sched))
        if r.get("model") not in roles:
            rep.error(path, "%s: model must be a role from system/manifest.yaml models (%s)"
                      % (where, ", ".join(sorted(roles))))
        js = r.get("jobs")
        if not isinstance(js, list) or not js:
            rep.error(path, "%s: jobs must be a non-empty list" % where)
            continue
        for j in js:
            if isinstance(j, str):
                jn = j
            elif isinstance(j, dict):
                jn = j.get("job")
                for k, v in j.items():
                    if k == "job":
                        continue
                    if k not in mods:
                        rep.error(path, "%s: job %s has unknown modifier %r" % (where, jn, k))
                    elif v not in mods[k]:
                        rep.error(path, "%s: job %s modifier %s=%r (one of %s)"
                                  % (where, jn, k, v, ", ".join(mods[k])))
            else:
                rep.error(path, "%s: job entries are a name or {job, when, target, mode}" % where)
                continue
            if jn not in jobs:
                rep.error(path, "%s: unknown job %r (not in system/jobs or registered)" % (where, jn))


def check_dashboards_settings(c, path, data, template):
    rep = c.rep
    ds = need(rep, path, data, "dashboards", template)
    if isinstance(ds, dict):
        known = set(DASHBOARDS) | set(c.registered("dashboard"))
        for k, v in ds.items():
            if k not in known:
                rep.error(path, "dashboards: unknown dashboard %r" % k)
            if not isinstance(v, dict) or "url" not in v:
                rep.error(path, "dashboards.%s must have url and last_published" % k)
        for k in DASHBOARDS:
            if k not in ds:
                rep.warn(path, "dashboards: %s is missing" % k)
    pp = (data or {}).get("project_pages")
    if pp is not None and not isinstance(pp, dict):
        rep.error(path, "project_pages must be a mapping of project ID to url")


def check_atlas(c, path, data, template):
    rep = c.rep
    if not isinstance(data, dict):
        rep.error(path, "must be a YAML mapping")
        return
    for k in ("user_display_name", "timezone", "repo", "installed_version", "data_version", "plan"):
        need(rep, path, data, k, template)
    tz = data.get("timezone")
    if tz is not None and not (isinstance(tz, str) and (re.match(r"^[A-Za-z_]+(/[A-Za-z0-9_+-]+)+$", tz)
                                                        or tz == "UTC")):
        rep.error(path, "timezone must be an IANA name like America/Los_Angeles")
    repo = data.get("repo")
    if repo is not None and not (isinstance(repo, str) and re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", repo)):
        rep.error(path, "repo must be 'owner/name'")
    iv = data.get("installed_version")
    if iv is not None and not (isinstance(iv, str) and SEMVER_RE.match(iv)):
        rep.error(path, "installed_version must be a semver string (quote it, e.g. \"1.0.0\")")
    dv = data.get("data_version")
    if dv is not None and not (isinstance(dv, int) and dv >= 0):
        rep.error(path, "data_version must be a whole number")
    mdv = c.load_manifest().get("data_version")
    if isinstance(dv, int) and isinstance(mdv, int) and not template:
        if dv > mdv:
            rep.warn(path, "data_version %d is newer than this release expects (%d); usual after a rollback "
                           "(atlas-update handles it)" % (dv, mdv))
        elif dv < mdv:
            rep.warn(path, "data_version %d is older than this release expects (%d); migrations are pending"
                     % (dv, mdv))
    if data.get("plan") is not None and data.get("plan") not in PLANS:
        rep.error(path, "plan must be one of %s" % ", ".join(PLANS))
    bc = data.get("bootstrap_confirmed")
    if bc is not None:
        if isinstance(bc, bool) or not isinstance(bc, int) or bc < 0:
            rep.error(path, "bootstrap_confirmed must be a whole number (the Atlas bootstrap version)")
        elif not template:
            mbv = c.load_manifest().get("bootstrap_version")
            if isinstance(mbv, int) and bc < mbv:
                rep.warn(path, "Project instructions confirmed for bootstrap %d, this release uses %d: an "
                               "'action' question asks the user to update them" % (bc, mbv))
    comp = data.get("company")
    if comp is not None:
        if not isinstance(comp, dict):
            rep.error(path, "company must be a mapping (website, email_domains, fiscal_year_start_month, fiscal_year_label)")
        else:
            web = comp.get("website")
            if web is not None and not (isinstance(web, str) and re.match(r"^https?://[^\s/]+\.[^\s]+$", web)):
                rep.error(path, "company.website must be a URL like https://acme.com")
            doms = comp.get("email_domains")
            if doms is not None:
                if not isinstance(doms, list):
                    rep.error(path, "company.email_domains must be a list, e.g. [acme.com]")
                else:
                    for d in doms:
                        if not (isinstance(d, str) and re.match(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$", d)):
                            rep.error(path, "company.email_domains: %r is not a domain like acme.com" % (d,))
            fm = comp.get("fiscal_year_start_month")
            if fm is not None and not (isinstance(fm, int) and not isinstance(fm, bool) and 1 <= fm <= 12):
                rep.error(path, "company.fiscal_year_start_month must be a whole number from 1 to 12")
            fl = comp.get("fiscal_year_label")
            if fl is not None and fl not in ("end", "start"):
                rep.error(path, "company.fiscal_year_label must be end or start")
    att = data.get("attestation") if "attestation" in data else None
    if "attestation" not in data:
        rep.error(path, "missing 'attestation' (null until recorded)")
    elif att is not None:
        if not isinstance(att, dict):
            rep.error(path, "attestation must be a mapping")
        else:
            for k in ("statement", "employer", "role", "recorded_on", "atlas_version", "reconfirm_due"):
                if not att.get(k):
                    rep.error(path, "attestation.%s is required" % k)
            for k in ("recorded_on", "reconfirm_due"):
                if att.get(k) and not is_date(att[k]):
                    rep.error(path, "attestation.%s must be YYYY-MM-DD" % k)
    for k in ("deliverables_folder", "drop_folder"):
        v = need(rep, path, data, k, template=True)
        if v is not None and not (isinstance(v, dict) and {"connector", "path"} <= set(v)):
            rep.error(path, "%s needs connector and path" % k)
    fb = data.get("first_brief_delivered")
    if fb is not None and not is_date(fb):
        rep.error(path, "first_brief_delivered must be YYYY-MM-DD or null")


SETTINGS_CHECKS = {
    "atlas.yaml": check_atlas,
    "governance.yaml": check_governance,
    "data-rules.yaml": check_data_rules,
    "connectors.yaml": check_connectors,
    "sources.yaml": check_sources,
    "rhythms.yaml": check_rhythms,
    "routines.yaml": check_routines,
    "dashboards.yaml": check_dashboards_settings,
}


def check_settings_file(c, path, template=False):
    name = os.path.basename(path)
    fn = SETTINGS_CHECKS.get(name)
    if fn is None:
        c.rep.warn(path, "unknown settings file (not in system/schemas/settings.md)")
        return
    data, ok = load_yaml(path, c.rep)
    if not ok:
        return
    if data is None:
        data = {}
    if not isinstance(data, dict):
        c.rep.error(path, "must be a YAML mapping")
        return
    fn(c, path, data, template)


# ================================================================ user
def check_registry(c, path):
    rep, schema = c.rep, c.load_schema()
    kinds = schema.get("registry_kinds") or []
    data, ok = load_yaml(path, rep)
    if not ok:
        return
    entries = (data or {}).get("extensions") if isinstance(data, dict) else None
    if entries is None:
        if not isinstance(data, dict) or "extensions" not in data:
            rep.error(path, "missing 'extensions' list")
        return
    if not isinstance(entries, list):
        rep.error(path, "extensions must be a list")
        return
    seen = set()
    is_template = "templates" in path.replace(os.sep, "/")
    for i, e in enumerate(entries):
        where = "extensions[%d]" % i
        if not isinstance(e, dict):
            rep.error(path, "%s must be a mapping" % where)
            continue
        name = e.get("name")
        if not isinstance(name, str) or not re.match(r"^[a-z0-9][a-z0-9_-]*$", name):
            rep.error(path, "%s: name must be a lowercase slug" % where)
        key = (e.get("kind"), name)
        if key in seen:
            rep.error(path, "%s: duplicate %s %r" % (where, e.get("kind"), name))
        seen.add(key)
        if e.get("kind") not in kinds:
            rep.error(path, "%s: kind %r is not one of %s" % (where, e.get("kind"), ", ".join(kinds)))
        p = e.get("path")
        if e.get("kind") == "routine":
            # Routines live in user/settings/routines.yaml, so their entries have path: null (formats.md §8).
            if p is not None:
                rep.error(path, "%s: a routine entry has path: null (the routine lives in user/settings/routines.yaml)" % where)
        elif not isinstance(p, str) or not p:
            rep.error(path, "%s: path is required" % where)
        elif p.startswith("/") or ".." in p.split("/"):
            rep.error(path, "%s: path must be relative to user/extensions/" % where)
        elif not is_template and not os.path.exists(c.p("user", "extensions", *p.split("/"))):
            rep.error(path, "%s: user/extensions/%s does not exist" % (where, p))
        if not isinstance(e.get("requires_atlas"), str) or not e.get("requires_atlas"):
            rep.error(path, "%s: requires_atlas range is required (e.g. \">=1.0\")" % where)
        if not is_date(e.get("created")):
            rep.error(path, "%s: created must be YYYY-MM-DD" % where)
        ov = e.get("overrides")
        if ov is not None and not isinstance(ov, str):
            rep.error(path, "%s: overrides must be a component name or null" % where)
        if not e.get("description"):
            rep.warn(path, "%s: description is empty" % where)


def check_record(c, path):
    rep, schema = c.rep, c.load_schema()
    common = schema.get("common") or {}
    types = schema.get("types") or {}
    kdir = c.p("user", "knowledge")
    rel = os.path.relpath(path, kdir).replace(os.sep, "/")
    parts = rel.split("/")
    if len(parts) != 2 or not rel.endswith(".md"):
        rep.error(path, "records live at user/knowledge/<folder>/<slug>.md")
        return
    folder, slug = parts[0], parts[1][:-3]
    folder_type = {t.get("folder"): name for name, t in types.items() if isinstance(t, dict)}
    utypes = c.user_types()
    if folder in folder_type:
        expected, tdef = folder_type[folder], types[folder_type[folder]]
    elif folder in utypes:
        expected, tdef = utypes[folder], None
    else:
        rep.error(path, "folder %r is not a known type folder or registered user type" % folder)
        return
    fm, body = read_frontmatter(path, rep)
    if fm is None:
        return
    for k in common.get("required") or []:
        if k not in fm or fm[k] in (None, "") and k != "summary":
            rep.error(path, "required field '%s' is missing or empty" % k)
    if fm.get("summary") in (None, ""):
        if "summary" in fm:
            rep.error(path, "summary must not be empty")
    if fm.get("type") is not None and fm.get("type") != expected:
        rep.error(path, "type %r does not match folder %s/ (expected %r)" % (fm.get("type"), folder, expected))
    want_id = "%s/%s" % (folder, slug)
    if fm.get("id") is not None and fm.get("id") != want_id:
        rep.error(path, "id %r must equal the path %r" % (fm.get("id"), want_id))
    if not re.match(common.get("id_pattern", r"^[a-z]+/[a-z0-9][a-z0-9-]*$"), want_id):
        rep.error(path, "file name must be a lowercase ASCII slug (words joined by '-')")
    for k in common.get("date_fields") or ["created", "updated"]:
        if fm.get(k) is not None and not is_date(fm[k]):
            rep.error(path, "%s must be YYYY-MM-DD (got %r)" % (k, fm[k]))
    if is_date(fm.get("created")) and is_date(fm.get("updated")) and str(fm["updated"]) < str(fm["created"]):
        rep.error(path, "updated is earlier than created")
    for k, allowed in (common.get("enums") or {}).items():
        for bad in enum_misses(fm.get(k), allowed):
            rep.error(path, "%s %r is not one of %s" % (k, bad, ", ".join(allowed)))
    if fm.get("archived") is not None and not isinstance(fm["archived"], bool):
        rep.error(path, "archived must be true or false")
    if tdef is not None:
        for k in tdef.get("required") or []:
            if k not in fm:
                rep.error(path, "required field '%s' is missing (use null if unknown)" % k)
        for k, allowed in (tdef.get("enums") or {}).items():
            for bad in enum_misses(fm.get(k), allowed):
                rep.error(path, "%s %r is not one of %s" % (k, bad, ", ".join(allowed)))
        if expected == "event" and fm.get("all_day") is not None and not isinstance(fm["all_day"], bool):
            rep.error(path, "all_day must be true or false")
        if expected == "source" and fm.get("compacted_on") is not None:
            if fm.get("retention") not in ("summary", "pointer"):
                rep.error(path, "a compacted source must have retention summary or pointer")
            if not re.match(r"^[0-9a-f]{7,40}$", str(fm.get("full_text_commit") or "")):
                rep.error(path, "a compacted source needs full_text_commit (the commit holding the full body)")
        if expected == "source" and fm.get("kind") == "import" and not fm.get("import_id"):
            rep.error(path, "an import source needs import_id (the import's id), so undo can find it")
        if expected == "goal" and fm.get("rank") is not None:
            rk = fm["rank"]
            if isinstance(rk, bool) or not isinstance(rk, int) or rk < 1:
                rep.error(path, "rank must be a whole number from 1 (most important), or null")
            elif fm.get("status") != "active":
                rep.warn(path, "rank is set on a goal that isn't active; clear it and renumber the active goals")
        check_field_formats(c, path, fm, expected)
        for k, kind in DATE_FIELDS.get(expected, {}).items():
            v = fm.get(k)
            if v is None:
                continue
            if not (is_date(v) or (kind == "dt" and is_datetime(v))):
                rep.error(path, "%s must be YYYY-MM-DD%s (got %r)" % (k, " or an ISO datetime" if kind == "dt"
                                                                       else "", v))
        known = set(common.get("required") or []) | set(common.get("optional") or []) | \
            set(tdef.get("fields") or []) | set(tdef.get("required") or [])
        extra = [k for k in fm if k not in known]
        if extra:
            rep.warn(path, "fields not in the %s schema: %s" % (expected, ", ".join(sorted(map(str, extra)))))
    links = fm.get("links")
    if links is not None:
        if not isinstance(links, dict):
            rep.error(path, "links must be a mapping of link group to list")
        else:
            for g, v in links.items():
                if g not in (common.get("link_groups") or []):
                    rep.error(path, "links: unknown group %r" % g)
                if not isinstance(v, list):
                    rep.error(path, "links.%s must be a list" % g)
                    continue
                for item in v:
                    if not (isinstance(item, str) and WIKI_RE.search(item)):
                        rep.error(path, "links.%s: %r must be a [[folder/slug]] link" % (g, item))
    for k in ("sources", "aliases"):
        if fm.get(k) is not None and not isinstance(fm[k], list):
            rep.error(path, "%s must be a list" % k)
    for target in sorted(set(wiki_links(fm))):
        if not c.record_exists(target):
            rep.error(path, "link target [[%s]] does not exist" % target)
    for target in sorted(set(t.strip() for t in WIKI_RE.findall(body))):
        if not c.record_exists(target):
            rep.warn(path, "body link [[%s]] does not exist" % target)


LINK_ONLY_RE = re.compile(r"^\[\[[a-z]+/[a-z0-9][a-z0-9-]*\]\]$")
EMAIL_RE = re.compile(r"^[^@\sA-Z]+@[^@\sA-Z]+\.[^@\sA-Z]+$")
FIX_HINT = " (system/tools/normalize.py --fix can fix this)"


STEP_WHEN_RE = re.compile(r"^[+-]\d+d$")


def steps_problem(v):
    """None if v is a valid playbook steps list (system/schemas/playbook.md), else a description."""
    if not isinstance(v, list):
        return "must be a list of steps"
    for i, s in enumerate(v):
        if isinstance(s, str):
            continue
        if not isinstance(s, dict) or not isinstance(s.get("step"), str):
            return "item %d must be text or a mapping with 'step'" % (i + 1)
        extra = set(s) - {"step", "when", "draft", "to"}
        if extra:
            return "item %d has unknown keys %s" % (i + 1, ", ".join(sorted(extra)))
        if s.get("when") is not None and not STEP_WHEN_RE.match(str(s["when"])):
            return "item %d: when must look like -30d or +2d" % (i + 1)
        if s.get("draft") is not None and s["draft"] not in ("email", "message"):
            return "item %d: draft must be email or message" % (i + 1)
    return None


def check_field_formats(c, path, fm, rtype):
    """Enforce schema.yaml field_formats (ref, refs, list, emails, bool, int, date, dt) and lowercase enums."""
    rep, schema = c.rep, c.load_schema()
    ff = schema.get("field_formats") or {}
    formats = dict(ff.get("common") or {})
    formats.update(ff.get(rtype) or {})
    for k, kind in formats.items():
        v = fm.get(k)
        if v is None:
            continue
        bad = None
        if kind == "ref" and not (isinstance(v, str) and LINK_ONLY_RE.match(v)):
            bad = "must be one [[folder/slug]] link"
        elif kind == "refs" and not (isinstance(v, list) and all(isinstance(x, str) and LINK_ONLY_RE.match(x) for x in v)):
            bad = "must be a list of [[folder/slug]] links"
        elif kind == "list" and not isinstance(v, list):
            bad = "must be a list"
        elif kind == "emails" and not (isinstance(v, list) and all(isinstance(x, str) and EMAIL_RE.match(x) for x in v)):
            bad = "must be a list of lowercase email addresses"
        elif kind == "bool" and not isinstance(v, bool):
            bad = "must be true or false"
        elif kind == "int" and (isinstance(v, bool) or not isinstance(v, int)):
            bad = "must be a whole number"
        elif kind == "date" and not is_date(v):
            bad = "must be YYYY-MM-DD"
        elif kind == "dt" and not (is_date(v) or is_datetime(v)):
            bad = "must be YYYY-MM-DD or an ISO datetime"
        elif kind == "steps":
            bad = steps_problem(v)
        if bad:
            rep.error(path, "%s %s (got %r)%s" % (k, bad, v, FIX_HINT))
    if isinstance(fm.get("aliases"), list) and len(fm["aliases"]) != len(set(map(str, fm["aliases"]))):
        rep.warn(path, "aliases has duplicates" + FIX_HINT)


def setup_step5_done(c):
    """True once setup step 5 is complete: user/.state/setup.yaml lists 5 as
    completed, or atlas.yaml has an attestation recorded."""
    sp = c.p("user", ".state", "setup.yaml")
    if os.path.exists(sp):
        try:
            with open(sp, encoding="utf-8") as f:
                st = yaml.safe_load(f) or {}
            if 5 in (st.get("completed") or []) or "5" in [str(x) for x in (st.get("completed") or [])]:
                return True
        except (OSError, yaml.YAMLError, AttributeError):
            pass
    np = c.p("user", "settings", "atlas.yaml")
    if os.path.exists(np):
        try:
            with open(np, encoding="utf-8") as f:
                nv = yaml.safe_load(f) or {}
            return bool(isinstance(nv, dict) and nv.get("attestation"))
        except (OSError, yaml.YAMLError):
            return False
    return False


IMPORT_STATUS = ["planned", "sampling", "running", "complete", "undone"]
IMPORT_ROUTES = ["drive", "attachment", "computer"]


def check_import(c, path):
    """user/.state/import.yaml (formats.md §1), present only once an import exists."""
    rep = c.rep
    data, ok = load_yaml(path, rep)
    if not ok:
        return
    if not isinstance(data, dict):
        rep.error(path, "must be a YAML mapping")
        return
    for k in ("id", "status", "source_system", "started"):
        if data.get(k) is None:
            rep.error(path, "missing field '%s'" % k)
    if data.get("route") is None and data.get("status") not in (None, "planned"):
        rep.error(path, "missing field 'route' (chosen before any note is read)")
    if data.get("status") is not None and data.get("status") not in IMPORT_STATUS:
        rep.error(path, "status must be one of %s" % ", ".join(IMPORT_STATUS))
    if data.get("route") is not None and data.get("route") not in IMPORT_ROUTES:
        rep.error(path, "route must be one of %s" % ", ".join(IMPORT_ROUTES))
    if data.get("route") == "drive" and not (isinstance(data.get("folder"), dict) and data["folder"].get("folder_id")):
        rep.error(path, "the drive route needs folder.folder_id (the import folder is tracked by ID)")
    for k in ("started", "completed"):
        if data.get(k) is not None and not is_date(data.get(k)):
            rep.error(path, "%s must be YYYY-MM-DD" % k)
    if data.get("status") == "complete" and data.get("completed") is None:
        rep.error(path, "a complete import needs completed (the date it finished)")
    lw = data.get("live_window_days")
    if lw is not None and (isinstance(lw, bool) or not isinstance(lw, int) or lw < 0):
        rep.error(path, "live_window_days must be a whole number of days")
    counts = data.get("counts")
    if counts is not None:
        if not isinstance(counts, dict) or any(isinstance(v, bool) or not isinstance(v, int) or v < 0
                                               for v in counts.values()):
            rep.error(path, "counts must map names to whole numbers")
        elif isinstance(counts.get("total"), int) and isinstance(counts.get("processed"), int) \
                and counts["processed"] > counts["total"]:
            rep.error(path, "counts.processed is larger than counts.total")
    for k in ("exclude", "processed", "previous"):
        if data.get(k) is not None and not isinstance(data.get(k), list):
            rep.error(path, "%s must be a list" % k)
    sk = data.get("skipped")
    if sk is not None and not (isinstance(sk, list) and all(isinstance(e, dict) and e.get("path") and e.get("why")
                                                              for e in sk)):
        rep.error(path, "skipped must be a list of { path, why }")


def check_user(c):
    rep = c.rep
    sdir = c.p("user", "settings")
    present = [f for f in listdir(sdir) if f.endswith(".yaml")]
    if not os.path.exists(os.path.join(sdir, "atlas.yaml")):
        rep.warn(sdir, "user/settings/atlas.yaml not found: Atlas is not set up yet (settings checks skipped "
                       "for missing files)")
    for f in present:
        check_settings_file(c, os.path.join(sdir, f))
    if setup_step5_done(c):
        for f in ("governance.yaml", "data-rules.yaml"):
            if f not in present:
                rep.error(os.path.join(sdir, f), "missing: setup step 5 is complete (attestation recorded), so "
                                                 "this protected settings file must exist (copy it from "
                                                 "system/templates/settings/)")
    reg = c.p("user", "extensions", "registry.yaml")
    if os.path.exists(reg):
        check_registry(c, reg)
    nm = c.p("user", ".state", "import.yaml")
    if os.path.exists(nm):
        check_import(c, nm)
    kdir = c.p("user", "knowledge")
    for folder in listdir(kdir):
        fpath = os.path.join(kdir, folder)
        if folder.startswith("_") or not os.path.isdir(fpath):
            continue
        for f in listdir(fpath):
            if f.endswith(".md"):
                check_record(c, os.path.join(fpath, f))
            elif not f.startswith("."):
                rep.warn(os.path.join(fpath, f), "non-markdown file in a knowledge folder")
    check_goal_ranks(c)
    check_hot(c)
    tdir = c.p("user", "work", "templates")
    for f in listdir(tdir):
        if f.endswith(".md"):
            check_template(c, os.path.join(tdir, f))
    idir = c.p("user", "inbox")
    for f in listdir(idir):
        if f in INBOX_STATUSES:
            check_inbox(c, os.path.join(idir, f))
    for f in listdir(os.path.join(idir, "archive")):
        if f.endswith(".md"):
            check_inbox(c, os.path.join(idir, "archive", f))


INBOX_STATUSES = {
    "approvals.md": ["pending", "approved", "rejected", "executed", "expired"],
    "insights.md": ["new", "seen", "acted", "dismissed", "expired"],
    "questions.md": ["open", "answered", "dismissed"],
}
INBOX_OPEN = {"pending", "approved", "new", "seen", "open"}
ENTRY_RE = re.compile(r"^## ([AIQ]-\d{4}-\d{2}-\d{2}-\d+) · ([a-z_]+)", re.M)


def check_inbox(c, path):
    """Inbox and inbox-archive files: valid statuses, a counts block that matches (formats.md §3)."""
    rep = c.rep
    base = os.path.basename(path)
    m = re.match(r"^\d{4}-\d{2}-(approvals|insights|questions)\.md$", base)
    name = m.group(1) + ".md" if m else base
    allowed = INBOX_STATUSES.get(name)
    if not allowed:
        rep.warn(path, "unexpected file in the inbox archive (expected YYYY-MM-<approvals|insights|questions>.md)")
        return
    fm, body = read_frontmatter(path, rep)
    if fm is None:
        return
    actual = dict((s, 0) for s in allowed)
    for eid, status in ENTRY_RE.findall(body or ""):
        if status not in allowed:
            rep.error(path, "%s: status %r is not one of %s" % (eid, status, ", ".join(allowed)))
            continue
        actual[status] += 1
        if m and status in INBOX_OPEN:
            rep.error(path, "%s is still %s; only resolved entries belong in the archive" % (eid, status))
    counts = fm.get("counts")
    if counts is None:
        rep.warn(path, "no counts block (formats.md §3); maintenance adds it")
    elif not isinstance(counts, dict):
        rep.error(path, "counts must be a mapping of status to number")
    else:
        wrong = ["%s %s (file has %d)" % (s, counts.get(s, 0), n) for s, n in actual.items() if (counts.get(s) or 0) != n]
        if wrong:
            rep.error(path, "counts don't match the entries: " + ", ".join(wrong))


HOT_MAX = 75
HOT_NEVER = ("sources/", "people/", "organizations/")
INDEX_LINE_RE = re.compile(r"^- \[\[([a-z]+/[a-z0-9][a-z0-9-]*)\]\]")


TEMPLATE_KINDS = ["email", "message", "doc", "deck", "sheet"]


def check_template(c, path):
    """user/work/templates/<slug>.md (formats.md §7, Deliverable templates)."""
    rep = c.rep
    fm, body = read_frontmatter(path, rep)
    if fm is None:
        return
    slug = os.path.basename(path)[:-3]
    if fm.get("type") != "template":
        rep.error(path, "frontmatter type must be 'template'")
    if fm.get("name") != slug:
        rep.error(path, "name must equal the file name (%s)" % slug)
    if fm.get("status") not in ("draft", "active", "retired"):
        rep.error(path, "status must be draft, active, or retired")
    if fm.get("kind") not in TEMPLATE_KINDS:
        rep.error(path, "kind must be one of %s" % ", ".join(TEMPLATE_KINDS))
    for k in ("title", "used_for"):
        if not fm.get(k):
            rep.error(path, "missing '%s'" % k)
    for k in ("audience", "examples"):
        v = fm.get(k)
        if v is not None and not (isinstance(v, list) and all(isinstance(x, str) and LINK_ONLY_RE.match(x) for x in v)):
            rep.error(path, "%s must be a list of [[folder/slug]] links" % k)
    for target in sorted(set(wiki_links({"a": fm.get("audience"), "e": fm.get("examples")}))):
        if not c.record_exists(target):
            rep.error(path, "link target [[%s]] does not exist" % target)
    if "## Structure" not in (body or ""):
        rep.error(path, "needs a ## Structure section")


def check_hot(c):
    """user/knowledge/_index/hot.md stays small and live (formats.md §5)."""
    path = c.p("user", "knowledge", "_index", "hot.md")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if INDEX_LINE_RE.match(l)]
    if len(lines) > HOT_MAX:
        c.rep.error(path, "%d record lines; the hot index holds at most %d (formats.md §5)" % (len(lines), HOT_MAX))
    closed = c.load_schema().get("closed_statuses") or {}
    folder_type = {t.get("folder"): n for n, t in (c.load_schema().get("types") or {}).items() if isinstance(t, dict)}
    for l in lines:
        rid = INDEX_LINE_RE.match(l).group(1)
        if rid.startswith(HOT_NEVER):
            c.rep.error(path, "[[%s]]: sources, people, and organizations never go in hot.md" % rid)
            continue
        fields = [x.strip() for x in l.split("|")]
        status = fields[3] if len(fields) > 3 else None
        rtype = folder_type.get(rid.split("/")[0])
        if rtype and status in (closed.get(rtype) or []):
            c.rep.error(path, "[[%s]] is %s; closed records never go in hot.md" % (rid, status))


def check_goal_ranks(c):
    """Active goals' ranks must be unique (system/schemas/goal.md, Ranking)."""
    gdir = c.p("user", "knowledge", "goals")
    seen = {}
    for f in listdir(gdir):
        if not f.endswith(".md"):
            continue
        path = os.path.join(gdir, f)
        fm, _ = read_frontmatter(path, Report(c.root))
        if not isinstance(fm, dict) or fm.get("status") != "active":
            continue
        rk = fm.get("rank")
        if isinstance(rk, int) and not isinstance(rk, bool) and rk >= 1:
            seen.setdefault(rk, []).append(path)
    for rk, paths in sorted(seen.items()):
        if len(paths) > 1:
            for p in paths:
                c.rep.error(p, "rank %d is shared by %d active goals; ranks must be unique" % (rk, len(paths)))


# ================================================================ dispatch
def check_path(c, path):
    rel = c.rep.rel(os.path.abspath(path))
    p = os.path.abspath(path)
    if not os.path.exists(p):
        c.rep.error(p, "file not found")
        return
    if rel.startswith("user/knowledge/") and rel.endswith(".md") and "/_" not in rel:
        check_record(c, p)
    elif re.match(r"^user/work/templates/[^/]+\.md$", rel):
        check_template(c, p)
    elif re.match(r"^user/inbox/(archive/)?[^/]+\.md$", rel):
        check_inbox(c, p)
    elif rel.startswith("user/settings/") and rel.endswith(".yaml"):
        check_settings_file(c, p)
    elif rel.startswith("system/templates/settings/") and rel.endswith(".yaml"):
        check_settings_file(c, p, template=True)
    elif rel.endswith("extensions/registry.yaml"):
        check_registry(c, p)
    elif re.match(r"^\.claude/skills/[^/]+/SKILL\.md$", rel):
        check_skill(c, p)
    elif re.match(r"^system/jobs/[^/]+\.md$", rel) and not rel.endswith("README.md"):
        check_job(c, p)
    elif re.match(r"^user/extensions/jobs/[^/]+\.md$", rel):
        check_job(c, p, user=True)
    elif re.match(r"^system/routine-profiles/[^/]+\.yaml$", rel):
        data, ok = load_yaml(p, c.rep)
        if ok:
            check_routines(c, p, data, template=False)
    elif rel in ("system/manifest.yaml", "system/VERSION"):
        check_manifest(c)
        check_changelog(c)
    elif rel == "CHANGELOG.md":
        check_changelog(c)
    elif rel == "user/.state/import.yaml":
        check_import(c, p)
    elif rel.startswith("system/dashboards/") or rel.startswith("system/migrations/"):
        (check_dashboards if "dashboards" in rel else check_migrations)(c)
    elif rel.startswith("system/rules/"):
        check_rules(c)
    else:
        c.rep.warn(p, "no validator for this path")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate Atlas system and user files.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--system", action="store_true", help="validate the system half")
    g.add_argument("--user", action="store_true", help="validate the user half")
    g.add_argument("--all", action="store_true", help="validate both (default)")
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..")),
                    help="repository root (default: the repo containing this script)")
    ap.add_argument("--quiet", action="store_true", help="print errors only")
    ap.add_argument("paths", nargs="*", help="specific files to validate")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    rep = Report(root)
    c = Ctx(root, rep)
    scope = []
    if args.paths:
        for p in args.paths:
            check_path(c, p if os.path.isabs(p) else os.path.join(os.getcwd(), p))
        scope.append("%d path(s)" % len(args.paths))
    if args.system or args.all or not (args.user or args.paths):
        check_system(c)
        scope.append("system")
    if args.user or args.all or not (args.system or args.paths):
        check_user(c)
        scope.append("user")

    print("Atlas validate: %s (%s)" % (", ".join(scope), root))
    for path, msg in rep.errors:
        print("ERROR  %s: %s" % (path, msg))
    if not args.quiet:
        for path, msg in rep.warnings:
            print("WARN   %s: %s" % (path, msg))
    print("Summary: %d error(s), %d warning(s), %d file(s) checked"
          % (len(rep.errors), len(rep.warnings), len(rep.checked)))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
