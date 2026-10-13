---
type: schema
name: formats
---
# File formats: state, inbox, logs, indexes, journal, outputs, extensions

Exact formats for every non-record file Nova reads or writes. Skills, jobs, hooks, validators, and dashboards rely on these.

---

## 1. State (`user/.state/`)
Committed to the repo (they're part of the user's history), written only by Nova.

### cursors.yaml
```yaml
cursors:
  mail:outlook: { last_seen: "2026-10-12T20:07:00-07:00", last_id: "AAMk…" }
  calendar:outlook: { synced_through: "2026-10-26" }
  meetings:zoom: { last_seen: "2026-10-12T17:30:00-07:00" }
  files:google-drive:drop: { last_seen: "2026-10-12T20:07:00-07:00" }
  journal: { last_processed: "2026-10-12" }
```
Key = `<category>:<connector>[:<scope>]`. Advance a cursor only after the items before it are fully filed and committed.

### jobs.yaml
```yaml
jobs:
  ingest: { last_success: "2026-10-12T20:09:12-07:00", last_status: ok }
  daily-brief: { last_success: "…", last_status: ok, last_target: "2026-10-13" }
  monthly: { last_success: "…", last_status: ok, period_done: "2026-10" }
  quarterly: { last_success: "…", last_status: ok, period_done: "2026-Q4" }
  update-check: { last_success: "…", last_status: ok, last_checked_version: "1.0.0" }
```
`last_status`: `ok | partial | failed | skipped_away | skipped_paused | early_exit`. A job skipped by a routine's `when` modifier leaves `jobs.yaml` unchanged (noted only in the run report). `update-check` also records `last_checked` (timestamp) and `latest_seen_version`.

### triggers.yaml
```yaml
fired:
  - { trigger: deadline_approaching, record: commitments/send-pricing-feedback, key: "2026-10-15", fired_on: "2026-10-12" }
```
A trigger fires at most once per `(trigger, record, key)`; `key` is the occurrence (e.g. the due date).

### setup.yaml
```yaml
started: 2026-10-12
current_step: 6
completed: [1, 2, 3, 4, 5]
skipped: []
notes: { 4: "Project created; stub pasted" }
```

### health.yaml
```yaml
last_user_check: 2026-10-01
last_system_check: 2026-10-01
known_issues:
  - { id: conn-outlook-auth, severity: high, since: 2026-10-10, summary: "Outlook connection expired", fix: "Reconnect Outlook in Settings → Connectors", status: open }
  - { id: routine-env-missing, severity: high, since: 2026-10-12, routine: nightly-cycle, summary: "The nightly-cycle routine ran without NOVA_CONTEXT=routine", fix: "Attach the nightly-cycle routine to the 'Nova routine' environment (nova-setup, reference/automations.md §3)", status: open }
smoke_test: { last_run: 2026-10-01, results: { repo_push: pass, connectors: pass, hooks: pass, artifact_republish: pass } }
routine_availability:              # evidence from routine runs; applied to connectors.yaml in the next chat (N6)
  outlook: { available: true, observed: 2026-10-12, run: nightly-cycle-20261012-2007 }
insight_engagement: { period: 2026-09, by_kind: { risk: { acted: 3, dismissed: 1, expired: 0 }, pattern: { acted: 1, dismissed: 4, expired: 2 } } }   # written by monthly
indicators: { period: 2026-09, time_to_first_brief_hours: 14, cited_answer_share: 0.82, auto_commitments: 41, manual_commitments: 6, automation_success_rate: 0.97, user_action_issues: 1, corrections: 3, active_weeks: 4 }
```

## 2. Transient (`.nova-tmp/`, git-ignored)

### approval.json (single-use, chat only)
```json
{"action": "send_communication", "tool": "mcp__outlook__send_message",
 "target": "draft AAMk… to jordan@acme.com", "user_confirmation": "yes, send it",
 "created": "2026-10-12T15:02:11-07:00", "expires": "2026-10-12T15:04:11-07:00"}
```
Hooks consume (delete) it on the matching call. One record authorizes one call.

### update.lock / purge.lock
```json
{"by": "nova-update", "version_from": "1.0.0", "version_to": "1.1.0", "created": "…", "expires": "…"}
{"by": "nova-memory", "targets": ["user/knowledge/people/jane-doe.md"], "user_confirmation": "yes, permanently erase", "created": "…", "expires": "…"}
```
Update lock expires after 30 minutes; purge lock after 15. Purge locks can only be created in a chat: the hooks refuse them in a session marked `NOVA_CONTEXT=routine`.

## 3. Inbox (`user/inbox/`)

**Counts block.** Each inbox file's frontmatter carries `counts`: how many entries in the file have each status. Every writer updates it in the same edit as the entry, so jobs and the kernel read open items from the frontmatter alone, without parsing entries. The validator checks it matches.
```yaml
---
type: inbox
name: approvals
counts: { pending: 2, approved: 0, rejected: 1, executed: 3, expired: 0 }
---
```
**Lifecycle.** An entry is *resolved* in its final statuses: approvals `rejected | executed | expired`; insights `acted | dismissed | expired`; questions `answered | dismissed`. `maintenance` moves entries resolved more than 14 days ago (by the date of their last status-history line, or `Asked`/answer date for questions) to the dated archive `user/inbox/archive/YYYY-MM-<name>.md`, where `YYYY-MM` is the month they were resolved. It moves them whole and unchanged, newest first, and updates `counts` in both files. Archive files have frontmatter `type: inbox-archive`, `name`, `month`, and their own `counts`; nothing is ever deleted from them. Anything that needs history (insight engagement over 60 days, the monthly automation review, indicators, novelty checks) reads the archive files for its window as well as the live file. Open entries (`pending`, `approved`, `new`, `seen`, `open`) never move.

### approvals.md
```markdown
---
type: inbox
name: approvals
counts: { pending: 1, approved: 0, rejected: 0, executed: 0, expired: 0 }
---
## A-2026-10-12-01 · pending
- **Action:** send_communication: send follow-up to Dana Ruiz
- **Why:** Dana's review is 6 days overdue ([[commitments/dana-contract-review]])
- **Prepared:** Outlook draft "Contract review — quick check-in" (id AAMk…)
- **Requested by:** routine:nightly-cycle · 2026-10-12
- **Status history:** pending 2026-10-12
```
Statuses: `pending | approved | rejected | executed | expired` (expires after 14 days). Newest first.

### insights.md
```markdown
---
type: inbox
name: insights
counts: { new: 1, seen: 0, acted: 0, dismissed: 0, expired: 0 }
---
## I-2026-10-12-03 · new · score 0.82
- **Insight:** Three customers raised the onboarding import bug this month.
- **Why it matters:** Relates to the open risk on Support Revamp and your Q4 retention goal.
- **Sources:** [[sources/2026-10-03-…]], [[sources/2026-10-09-…]], [[sources/2026-10-11-…]]
- **Links:** [[risks/onboarding-import-failures]], [[goals/2026-q4-retention]]
- **Suggested action:** Raise at Thursday's product sync.
- **Status history:** new 2026-10-12
```
Each entry also has a `- **Kind:** <kind>` line (kinds defined in `.claude/skills/nova-insights/reference/insight-kinds.md`). When the suggested action is a message to someone, the entry has `- **Draft for:** [[people/<slug>]] · email | message`; once the draft exists, `email-drafts` adds `- **Draft:** <where, plain words> "<subject>" (draft id …)` (or `- **Draft:** text below` followed by the text indented, when no draft tool exists). The `Draft:` line is the marker that stops a second draft. Statuses: `new | seen | acted | dismissed | expired`. An insight is `seen` once it is included in a published brief or shown in chat; unseen insights expire after 30 days. `score` 0–1 = relevance to goals × urgency × novelty. Engagement signals (acted/dismissed counts by insight kind) are summarized in `health.yaml` and used by `nova-insights` to adapt volume.

### questions.md
Nova's questions for the user (profile proposals, migration questions, unclear relationships, vague commitments).
```markdown
---
type: inbox
name: questions
counts: { open: 1, answered: 0, dismissed: 0 }
---
## Q-2026-10-12-02 · open · profile
- **Question:** You shortened my last 4 drafts by about half. Should I default to shorter emails?
- **Proposed change:** voice-personal.md: "Keep emails under ~120 words" [observed · proposed]
- **Asked:** 2026-10-12
```
Kinds: `profile | migration | relationship | commitment | setup | action | other`. Statuses: `open | answered | dismissed`.

**Action entries** (`kind: action`) are things only the user can do, queued by `nova-update` from a release's `### Action needed` list or a higher `bootstrap_version`, and by the chat boot check (kernel §2 step 0):
```markdown
## Q-2026-10-18-01 · open · action
- **Question:** Update your Nova Project's instructions (Nova was updated to 1.1.0).
- **Action key:** bootstrap
- **How:** In the Claude app, open the Nova Project, replace its instructions with the text below, and save.
- **Copy text:**
    This Project is my Nova (Nova bootstrap 3). At the start of every conversation:
    …
- **Asked:** 2026-10-18
```
- `Action key` deduplicates: there is at most one open entry per key. `bootstrap` for the Project instructions; `release-<version>-<n>` for the n-th `Action needed` line of a release. `How` and `Copy text` (indented block, filled in for this user) are optional.
- Done → status `answered` with `- **Done:** <date> · <confirmed by Nova | user said done>`; the user can also skip it (`dismissed`). Never closed just because time passed.
- Open action entries come first wherever questions are shown (Daily Brief "Action needed", Control Center, chat), oldest first, and are never cut by question caps.

### drop/
Files attached in chat land here, then are filed by `nova-capture` and removed from `drop/` (the source record keeps a pointer; the file itself moves to `user/library/YYYY/<file>` only if its data-rule handling is `full` and it is 10 MB or less). Removing processed files from `drop/` is housekeeping, not a destructive action (hooks allow it).

## 4. Logs (`user/logs/`)

### activity/YYYY-MM.md (one line per change set, newest last)
```
- 2026-10-12 20:09 · routine:nightly-cycle · ingest · filed 14 sources, 3 commitments, 2 decisions · commit 4f2a9c1
- 2026-10-12 15:02 · chat · send_communication (approved) · follow-up to Dana Ruiz · commit 9b31e07
```
Format: `- <date> <time> · <actor> · <job or action> · <summary> · commit <short-sha>`. Never includes sensitive content.

### runs/YYYY-MM/<routine>-<YYYYMMDD-HHMM>.md
```markdown
---
type: run-report
routine: nightly-cycle
started: 2026-10-12T20:07:03-07:00
finished: 2026-10-12T20:31:40-07:00
status: ok              # ok | partial | failed
nova_context: routine   # the NOVA_CONTEXT value observed at the start of the run, verbatim ("unset" if missing); anything but routine means routine-env-missing
---
| Job | Status | Items | Notes |
|---|---|---|---|
| ingest | ok | 37 in / 14 filed | Outlook, Zoom, Drop |
| triage | ok | 22 reviewed, 2 closed, 1 slipped | |
| intelligence | ok | 3 new insights | |
| email-drafts | ok | 4 drafts | |
| meeting-prep | ok | 2 prep notes | |
| daily-brief | ok | brief for 2026-10-13 | republished 4 dashboards |

## Approvals queued
## Errors
## Connector health
## Suspicious content flagged
```

## 5. Indexes (`user/knowledge/_index/`)
Regenerable; never edited by hand.
- `<folder>.md` (e.g. `people.md`): one line per non-archived record:
  `- [[people/dana-ruiz]] | Dana Ruiz | aliases: dana@acme.com, D. Ruiz | active | 2026-10-12 | Acme's legal counsel; reviewing the MSA.`
- `hot.md`: what's live right now, for session start (L0). **At most 75 lines**, same line format, grouped by type in this order: commitments, events, goals, projects, risks, questions, decisions, ideas, playbooks, topics, then user types. It includes only records that are **not closed** (`schema.yaml: closed_statuses`), not archived, and not superseded, and that are one of:
  - open or slipped commitments due within 14 days, or slipped;
  - scheduled events in the next 7 days;
  - active goals;
  - other records updated in the last 14 days.

  **Never in hot:** sources, people, and organizations (they are one lookup away in `sources.md`, `people.md`, `people-map.md`, and `organizations.md`), and anything done, processed, or held. If more than 75 qualify, keep in this order and drop the rest: slipped commitments, commitments by due date, events by start, ranked then unranked active goals, then everything else by most recent `updated`. The last line reads `- … <N> more: see the type indexes` when anything was dropped.
- `people-map.md`: `- [[people/dana-ruiz]] | Dana Ruiz | Acme (customer) | legal counsel | aliases`.
- `archive.md`: archived records, same line format.

`maintenance` rebuilds all indexes from the records; any session that writes records updates the affected lines.

## 6. Journal (`user/journal/YYYY/MM/YYYY-MM-DD.md`)
```markdown
---
type: journal
date: 2026-10-12
processed: [morning]          # sections already filed: morning, evening
source: "[[sources/2026-10-12-journal]]"
---
## Morning Thoughts
<verbatim>

## Evening Thoughts
<verbatim>
```

## 7. Outputs (`user/work/`)
| Output | Path |
|---|---|
| Daily Brief | `user/work/briefs/YYYY-MM-DD.md` |
| Catch-up brief (after away) | `user/work/briefs/YYYY-MM-DD-catch-up.md` |
| Meeting prep note | `user/work/prep/YYYY-MM-DD-<event-slug>.md` |
| Person / topic / deal prep note | `user/work/prep/YYYY-MM-DD-<subject-slug>.md` (frontmatter `subject:` with the record ID) |
| Weekly Review | `user/work/reviews/YYYY-Www.md` (ISO week) |
| Status update draft | `user/work/status/YYYY-MM-DD-<audience-slug>.md` |
| Monthly report (goal progress, health, automation review, indicators) | `user/work/reports/YYYY-MM.md`, named for the **month reviewed** (the November run writes `2026-10.md` and sets `period_done: 2026-11`) |
| Quarterly report (reset, role refresh) | `user/work/reports/YYYY-Qn.md`, named for the **quarter reviewed** |
| Performance review pack | `user/work/reports/YYYY-Qn-performance.md` |
| Accomplishments | Appended to the relevant goal's `accomplishments` field and `user/work/accomplishments.md` (running list; line format in `.claude/skills/nova-review/reference/weekly.md`) |
| Deliverable working files | `user/work/deliverables/<YYYY-MM-DD-slug>/` (markdown/data used to build it; the finished binary goes to the deliverables folder per `.claude/skills/nova-write/reference/deliverables.md`) |
| Project page data | rendered on request; no file |
| Deliverable template | `user/work/templates/<slug>.md` (below) |

Each output has frontmatter `type: <brief|prep|review|status|report|performance>`, `date`, and `sources`, plus as relevant: `generated` (timestamp), `window_start`/`window_end`, `period`, `kind: catch-up`, `audience`, `subject`. Section structure: Daily Brief and catch-up brief per `.claude/skills/nova-brief/reference/`; reviews and reports per `.claude/skills/nova-review/reference/`; prep notes per `.claude/skills/nova-prep/reference/templates.md`.

### Deliverable templates (`user/work/templates/<slug>.md`)
A reusable shape for something the user produces again and again: the weekly status email, the monthly board update, the QBR deck, the month-end close summary. `nova-write` uses a matching active template, so every edition is consistent and faster to make.
```markdown
---
type: template
name: monthly-board-update
title: Monthly board update
status: active                 # draft (proposed by Nova) | active | retired
kind: doc                      # email | message | doc | deck | sheet
used_for: The update Maya sends the board in the first week of each month
audience: ["[[people/jordan-lee]]"]   # optional
cadence: monthly               # optional: weekly | biweekly | monthly | quarterly | ad hoc
examples: ["[[sources/2026-09-03-board-update]]", "[[sources/2026-10-02-board-update]]"]   # past editions it was learned from
base_file: null                # optional: the user's own file template (library path or drive link) to build on
updated: 2026-10-12
---
## Structure
1. **Headline** (2 sentences): the month in one line, then the one thing the board should know.
   - Pull from: the monthly report's summary; goal progress.
2. **Metrics**: table of ARR, net retention, burn, runway (this month, last month, change).
   - Pull from: the finance sheet named in the last edition; never estimate missing numbers, mark them [needed].
…
## Voice and format
- House voice; numbers first; under 2 pages; same section order every month.
## Notes
- Last edition's open items are carried into "Follow-ups" (the user asked for this on 2026-10-02).
```
Rules: one file per recurring deliverable; only the user's confirmation makes a `draft` template `active`; edits the user makes to an edition are proposed back into the template with the same learning rule as voice (`nova-write` §6). Templates never store data values, only where to get them.

## 8. Extensions registry (`user/extensions/registry.yaml`)
```yaml
extensions:
  - name: deals
    kind: type          # skill | job | routine | trigger | type | dashboard | playbook
    path: types/deal.md
    overrides: null     # or the name of a system component, explicitly
    requires_nova: ">=1.0"
    created: 2026-10-20
    description: "Sales deals with stage and value."
```
- `kind: routine` entries have `path: null` (the routine lives in `user/settings/routines.yaml`).
- `kind: playbook` entries point to a `type: playbook-extension` file that links to a knowledge playbook record.
- User types use the schema outline in `system/guide/authoring.md`, get their own folder under `user/knowledge/` (frontmatter `folder:`), and declare machine-readable `fields:` and `enums:` in their frontmatter so the validator can check their records.
- Removed extensions move to `user/extensions/_retired/` (not deleted) and leave the registry.

## 9. Manifest (`system/manifest.yaml`)
Fields: `name`, `version`, `data_version`, `min_plan`, `support_email`, `upstream`, `owned_paths` (list), `models` (`fast`, `strongest`), `profiles`.
