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
`last_status`: `ok | partial | failed | skipped_away | skipped_paused | early_exit`.

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
smoke_test: { last_run: 2026-10-01, results: { repo_push: pass, connectors: pass, hooks: pass, artifact_republish: pass } }
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
Update lock expires after 30 minutes; purge lock after 15. Purge locks can't be created when `NOVA_CONTEXT` isn't `chat`.

## 3. Inbox (`user/inbox/`)

### approvals.md
```markdown
---
type: inbox
name: approvals
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
---
## I-2026-10-12-03 · new · score 0.82
- **Insight:** Three customers raised the onboarding import bug this month.
- **Why it matters:** Relates to the open risk on Support Revamp and your Q4 retention goal.
- **Sources:** [[sources/2026-10-03-…]], [[sources/2026-10-09-…]], [[sources/2026-10-11-…]]
- **Links:** [[risks/onboarding-import-failures]], [[goals/2026-q4-retention]]
- **Suggested action:** Raise at Thursday's product sync.
- **Status history:** new 2026-10-12
```
Statuses: `new | seen | acted | dismissed | expired` (expire after 30 days unseen). `score` 0–1 = relevance to goals × urgency × novelty. Engagement signals (acted/dismissed counts by insight kind) are summarized in `health.yaml` and used by `nova-insights` to adapt volume.

### questions.md
Nova's questions for the user (profile proposals, migration questions, unclear relationships, vague commitments).
```markdown
## Q-2026-10-12-02 · open · profile
- **Question:** You shortened my last 4 drafts by about half. Should I default to shorter emails?
- **Proposed change:** voice-personal.md: "Keep emails under ~120 words" [observed · proposed]
- **Asked:** 2026-10-12
```
Kinds: `profile | migration | relationship | commitment | setup | other`. Statuses: `open | answered | dismissed`.

### drop/
Files attached in chat land here, then are filed by `nova-capture` and removed from `drop/` (the source record keeps a pointer; the file itself moves to `user/library/` only if data rules and size allow, max 10 MB).

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
- `hot.md`: records updated in the last 14 days plus open commitments due within 14 days, grouped by type, same line format.
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
| Weekly Review | `user/work/reviews/YYYY-Www.md` (ISO week) |
| Status update draft | `user/work/status/YYYY-MM-DD-<audience-slug>.md` |
| Monthly report (goal progress, health, automation review, indicators) | `user/work/reports/YYYY-MM.md` |
| Quarterly report (reset, role refresh) | `user/work/reports/YYYY-Qn.md` |
| Performance review pack | `user/work/reports/YYYY-Qn-performance.md` |
| Accomplishments | Appended to the relevant goal's `accomplishments` field and `user/work/accomplishments.md` (running list) |
| Deliverable working files | `user/work/deliverables/<YYYY-MM-DD-slug>/` (markdown/data used to build it; the finished binary goes to the deliverables folder, §9.6a) |
| Project page data | rendered on request; no file |

Each output has frontmatter `type: <brief|prep|review|status|report|performance>`, `date`, and `sources`.

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
User types use the schema outline in `system/guide/authoring.md` and get their own folder under `user/knowledge/` (named in the type file's frontmatter `folder:`).

## 9. Manifest (`system/manifest.yaml`)
Fields: `name`, `version`, `data_version`, `min_plan`, `support_email`, `upstream`, `owned_paths` (list), `models` (`fast`, `strongest`), `profiles`.
