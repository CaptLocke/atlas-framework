---
type: schema
name: settings
folder: user/settings/
---
# Schema: settings

All settings are YAML in `user/settings/`. Defaults ship in `system/templates/settings/` and are copied in by `atlas-setup`. `system/tools/validate.py` checks every file against this spec and `schema.yaml`.

**Protected files (N6):** `governance.yaml`, `data-rules.yaml`, `connectors.yaml` change only in a chat, after the user explicitly confirms the change (`system/rules/governance.md`). Hooks block writes to them in routine context.

---

## atlas.yaml
```yaml
user_display_name: Maya Chen
timezone: America/Los_Angeles          # IANA
locale: en-US                          # dates and numbers in output and dashboards
repo: maya-chen/atlas                   # owner/name of this repo
installed_version: 1.0.0               # updated by atlas-update
installed_from_commit: null            # template commit the repo was created from; baseline for drift checks until the first real update
data_version: 1                        # updated by migrations
bootstrap_confirmed: 2                 # Project-instructions version last confirmed current (setup, chat boot check); optional
plan: pro                              # pro | max_5x | max_20x | team | enterprise (user-stated)
attestation:                           # required before any ingestion
  statement: "I confirm I am permitted to store work information from my employer in this private GitHub repository."
  employer: "[[organizations/acme]]"
  role: Product Manager
  recorded_on: 2026-10-12
  atlas_version: 1.0.0
  reconfirm_due: 2027-01-04            # first business day of next (fiscal) quarter
company:                               # the user's employer; filled at setup steps 6–8
  website: https://acme.com
  email_domains: [acme.com, acme.io]   # all domains the company uses; mail from these is internal
  fiscal_year_start_month: 1           # 1–12; default 1 (January). Quarters and the quarterly moments follow it
  fiscal_year_label: end               # end | start: which calendar year names the fiscal year (only matters if start month ≠ 1)
# Self-employed / multiple clients: statement reads "…work information from my business and my clients…", employer: the user's own business.
# Overdue reconfirmation: a known issue reminds the user; ingest continues. Ingest pauses only if the user declines,
# or after a change of employer/role until a new attestation is recorded.
deliverables_folder:                   # where finished files are saved (C13)
  connector: google-drive              # connector name from connectors.yaml, or null (download only)
  path: "Atlas Deliverables"
  folder_id: null                      # connector-specific ID once created/found
drop_folder:
  connector: google-drive              # or null if no cloud drive
  path: "Atlas Drop"
  folder_id: null
  move_supported: true                 # false → Atlas remembers processed file IDs in cursors instead of moving files
first_brief_delivered: 2026-10-13
```

## governance.yaml
Levels: `auto`, `propose`, `approve`, `never` (no other values). Locked classes cannot be changed; validators reject edits to them.
```yaml
autonomy:
  # inside Atlas
  read: auto
  records_write: auto
  merge_supersede: auto          # clear cases follow this; ambiguous always proposed
  archive: auto
  dashboards_refresh: auto
  profile_update: propose
  user_content_edit: propose
  behavior_settings: propose
  extensions_create: propose
  updates_minor: auto            # patch + minor releases
  updates_major: propose
  # outside Atlas
  external_read: auto
  web_research: auto
  drafts_create: auto
  docs_create: auto
  deliverables_save: auto
  drop_folder_housekeeping: auto
  own_items_organize: propose
  docs_edit: propose
  own_calendar_manage: propose
  tasks_manage: propose
  shared_records_update: propose
  # locked
  governance_settings: approve
  send_communication: approve
  share_expose: approve
  destructive: approve           # includes forget and purge
  financial_legal_security: never
overrides:
  - scope: "organizations/acme"  # scope grammar below
    records_write: propose
```
**Override scope grammar:** a record ID (`organizations/acme`, applies to that record and records linked to it), `connector:<name>` (e.g. `connector:outlook`), or `category:<category>` (e.g. `category:crm`). An override may only name non-locked classes and only use the four levels. Most specific scope wins (record > connector > category > global).

## data-rules.yaml
```yaml
categories:                       # handling: ignore | pointer | summary | full
  confidential: pointer
  pii: summary
  phi: pointer
  financial: summary
  legal_privileged: ignore
custom:
  - name: board-materials
    match: "Board decks, board pre-reads, and board minutes"   # plain-language description Claude applies
    handling: summary
exclusions:                       # never read; the ONLY place exclusions are defined
  - "mail: from:*@newsletter.example.com"
  - "messaging: channel:#random"
  - "calendar: series:Personal"
  - "record: people/jane-doe"      # added by 'forget' to stop re-capture
```
**Handling:** `ignore` (do not store anything), `pointer` (a source record noting it exists, no content), `summary` (summary without sensitive details), `full` (store normally).
**Exclusion syntax:** `<category or connector>: <query>` where query is the connector's own search syntax or a simple `field:value` (`from:`, `to:`, `channel:`, `series:`, `folder:`, `label:`); or `record: <id>` to stop capturing a forgotten subject. An import's folder is excluded as `files: folder:<folder_id>` with a `#` comment naming it; the import alone reads it, once (`system/rules/knowledge.md` § Write path).

## connectors.yaml
Written by `atlas-connectors`. One entry per connector.
```yaml
connectors:
  - connector: outlook                 # name as shown in the connector list
    mcp_prefix: mcp__outlook__         # how tool names appear in sessions (verified at mapping)
    categories: [mail, calendar]
    operations:                        # category.operation → tool (+ notes)
      mail.list_recent: { tool: list_messages, since_param: receivedDateTime, page_param: skip }
      mail.read_item: { tool: get_message }
      mail.search: { tool: search_messages }
      mail.create_draft: { tool: create_draft }
      mail.send: { tool: send_message }
      calendar.list_range: { tool: list_events, range_params: [start, end] }
    tool_risk:                         # every tool exposed, one of: read write draft send share delete security
      list_messages: read
      get_message: read
      search_messages: read
      create_draft: draft
      send_message: send
      delete_message: delete
      list_events: read
    id_format: "opaque string"
    link_format: "https://outlook.office.com/mail/id/{id}"
    limits: "50 items per page"
    available_in_routines: true        # true | false | unknown; routines record evidence in .state/health.yaml (routine_availability), applied here in the next chat
    own_storage: true                  # optional: the user's own file storage (their drive); default true for a `files` connector, false otherwise. Export, import and upload tools on any other connector count as sharing
    covered: { mail: full, calendar: full }   # optional: full | partial per category (partial = some † operations missing)
    mapped_on: 2026-10-12
    tool_fingerprint: 3f9a…            # hash of the tool list; health check re-maps when it changes
```
Operation names per category are defined in `system/connectors/README.md`.

## sources.yaml
Which categories Atlas ingests, how far back, and fallbacks.
```yaml
ingest:
  - category: mail
    connector: outlook
    scope: "inbox and sent; skip folders: Archive/Newsletters"
    lookback_days_initial: 14
  - category: meetings
    connector: zoom
    scope: "all recorded meetings I attended"
fallbacks:                              # categories with no connector
  - category: crm
    method: forward                     # drop | forward | export | manual
    instructions: "Forward deal update emails to yourself with [atlas] in the subject."
```

## rhythms.yaml
```yaml
work_hours: { days: [mon, tue, wed, thu, fri], start: "08:00", end: "18:00" }
moments:
  morning_thoughts: on
  evening_thoughts: on
  daily_brief: on
  weekly_review: on
  status_updates: { enabled: true, audiences: ["[[people/jordan-lee]]"], day: fri }
  goal_progress: on
  user_health_check: on
  system_health_check: on
  automation_review: on
  reset_goals: on
  role_refresh: on
  performance_review: on
triggers:                               # built-ins from system/triggers.md; user triggers too
  new_project: on
  new_key_person: on
  deadline_approaching: { enabled: true, days: 3 }
  key_meeting_upcoming: on
  commitment_overdue: on
  playbook_start: on
  focus_time_needed: on
insights:
  brief_max: 3
  engagement: adaptive                  # adaptive | fixed
  suppressed_kinds: []                  # insight kinds the user turned off, e.g. [idea] ("stop suggesting ideas in the brief")
meetings:                               # which calendar events Atlas shows and preps; optional, every key defaults to include
  all_day: include                      # include | skip: all-day events (holidays, conference days, OOO notices)
  tentative: include                    # include | skip: meetings the user tentatively accepted
  not_responded: include                # include | skip: invitations the user hasn't answered yet
away:                                   # set by atlas-away; null when not away
  start: null                           # YYYY-MM-DD, first day away
  end: null                             # YYYY-MM-DD, LAST day away (inclusive); null while away = away until the user says they're back
  set_on: null
paused: []                              # e.g. [{ job: weekly-review, until: 2026-11-01 }, { moment: evening_thoughts, until: null }]
```

**Meeting filter (`meetings`).** A missing block or key means `include`, so older files behave as before. An event is **shown** unless one of these applies:
- `all_day: skip` and the event is all-day, **except** deadline and milestone events (`kind: deadline | milestone`), which always show under Due.
- `tentative: skip` and the event record's `response` is `tentative`.
- `not_responded: skip` and `response` is `not_responded`.

Events the user organizes (`response: organizer`) and accepted events are always shown; declined events are already skipped at ingestion (`system/connectors/calendar.md`). A skipped event is still recorded in knowledge, so it appears normally once the user accepts it. It is left out of the Daily Brief's Today, Week Ahead's events and meeting hours, meeting prep, and the `key_meeting_upcoming` trigger. Focus suggestions still avoid its time, so Atlas never suggests focus time on top of a meeting the user may attend. Changing the filter is `behavior_settings`.

## routines.yaml
```yaml
profile: lean                           # lean | standard | full | custom (custom = user-edited)
routines:
  - name: nightly-cycle
    schedule: "7 20 * * *"              # cron in atlas.yaml timezone; one schedule per routine
    model: strongest                    # role from system/manifest.yaml models
    routine_id: null                    # platform ID once created
    jobs:
      - ingest
      - triage
      - intelligence
      - { job: email-drafts, when: weekdays }
      - { job: meeting-prep, target: tomorrow }
      - monthly
      - quarterly
      - { job: daily-brief, target: tomorrow }
```
Job entries are a job name or `{ job, when, target, mode }`. Modifiers: `when` (always | weekdays | weekends | sundays), `target` (today | tomorrow), `mode` (full | light; light = new items only, no re-prioritization). Job names are system jobs or registered user jobs.

## dashboards.yaml
```yaml
dashboards:
  daily-brief: { url: null, last_published: null }
  commitments: { url: null, last_published: null }
  projects: { url: null, last_published: null }
  goals: { url: null, last_published: null }
  week-ahead: { url: null, last_published: null }
  people: { url: null, last_published: null }
  decisions-risks: { url: null, last_published: null }
  control-center: { url: null, last_published: null }
  about-you: { url: null, last_published: null }
  atlas-guide: { url: null, last_published: null }
  records: { url: null, last_published: null }
project_pages: {}                       # project ID → url, created on request
# User dashboards from extensions are additional keys named after the extension.
```
`dashboards.yaml` URLs and `last_published` dates are bookkeeping written under `dashboards_refresh` (auto), so routines can update them; choosing which dashboards exist is `behavior_settings`.
