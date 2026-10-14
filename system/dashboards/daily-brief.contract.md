---
type: dashboard-contract
name: daily-brief
template: daily-brief.html
republished_by: [daily-brief]
size_budget_kb: 120
stale_after_hours: 36
---
# Dashboard: daily-brief

## Purpose
Today at a glance, readable in two minutes: anything only the user can do, top priorities, today's meetings with prep status, what is due or slipping, who the user is waiting on, what needs their answer (approvals, questions), up to three insights, and drafts ready to review. It is the page view of the brief file `user/work/briefs/YYYY-MM-DD.md`; the brief file and this page are built in the same step and must agree.

Also republished by any chat that runs the morning catch-up (kernel §2.3); what it brings in shows up in the page's own sections (a new commitment under Due and slipping, a moved meeting under Today), not as a separate list. After away mode it renders the catch-up brief (`brief.kind: "catch-up"`), which adds a "While you were away" section.

## Data (JSON shape embedded in the page)
Envelope: `meta` as in `system/dashboards/README.md`; `meta.as_of` = the brief's date (tomorrow when built with `target: tomorrow`).

```json
{
  "meta": { "dashboard": "daily-brief", "schema_version": 1, "as_of": "2026-10-13", "…": "…" },
  "brief": { "date": "2026-10-13", "kind": "daily", "path": "user/work/briefs/2026-10-13.md",
             "headline": "A customer-heavy day: …", "away": null },
  "actions": [ { "id": "Q-2026-10-13-01", "text": "Update your Atlas Project's instructions (Atlas was updated to 1.1.0).",
                 "how": "In the Claude app, open the Atlas Project, replace its instructions, and save.", "copy_text": true } ],
  "priorities": [ { "text": "Send pricing feedback to Jordan", "why": "Due today; Thursday's decision depends on it.",
                    "ref": { "id": "commitments/send-pricing-feedback", "title": "Send pricing feedback to Jordan" } } ],
  "today": [ { "id": "events/2026-10-13-brightline-renewal-call", "title": "Brightline renewal call", "kind": "meeting",
               "start": "2026-10-13T10:00:00-07:00", "end": "2026-10-13T10:45:00-07:00", "all_day": false,
               "location": "Zoom", "attendees": [ { "id": "people/sam-okafor", "title": "Sam Okafor" } ],
               "prep": { "status": "ready", "path": "user/work/prep/2026-10-13-brightline-renewal-call.md",
                         "summary": "Lead with the import fix date." } } ],
  "due": [ { "id": "commitments/send-pricing-feedback", "title": "Send pricing feedback to Jordan", "direction": "i_owe",
             "status": "open", "due": "2026-10-13", "priority": "high",
             "counterparty": { "id": "people/jordan-lee", "title": "Jordan Lee" }, "next_step": "…" } ],
  "waiting_on": [ { "id": "commitments/dana-msa-review", "title": "Dana reviews the enterprise MSA", "direction": "waiting_on",
                    "status": "slipped", "due": "2026-10-07", "since": "2026-09-30",
                    "counterparty": { "id": "people/dana-ruiz", "title": "Dana Ruiz" }, "next_step": "…" } ],
  "insights": [ { "id": "I-2026-10-12-03", "text": "…", "why": "…", "suggested_action": "…",
                  "draft": { "to": "Sam Okafor", "where": "Outlook drafts" },
                  "refs": [ { "id": "risks/onboarding-import-failures", "title": "Onboarding import failures" } ] } ],
  "drafts": [ { "title": "Contract review: quick check-in", "to": "Dana Ruiz", "where": "Outlook drafts", "why": "…",
                "ref": { "id": "commitments/dana-msa-review", "title": "…" } } ],
  "approvals": [ { "id": "A-2026-10-12-01", "action": "Send follow-up to Dana Ruiz", "why": "…", "requested_on": "2026-10-12" } ],
  "questions": [ { "id": "Q-2026-10-12-02", "kind": "profile", "text": "…" } ]
}
```
Full example: `system/tests/dashboards/daily-brief.json`.

| Field | Notes |
|---|---|
| `brief.kind` | `daily` or `catch-up`. For `catch-up`, `brief.away` = `{ "start", "end" }` and `since_last_night` holds the "While you were away" summary lines (`[{ "text" }]`). Daily briefs omit it. |
| `brief.headline` | One sentence summarizing the day, in the user's communication style. |
| `prep.status` | `ready` (prep note exists), `planned` (meeting-prep will create one before the meeting), `none` (meaningful meeting without prep), `not_needed`. |
| `due[].status` | `open` or `slipped`. |
| `drafts[].where` | Plain words for where the draft is ("Outlook drafts"). Never the draft body. |
| `actions[]` | Things only the user can do. `how` is optional; `copy_text` is `true` when the entry has text to copy (shown on the Control Center, never on this page). |
| `insights[].draft` | `{ to, where }` when the insight's suggested action already has a draft (its `Draft:` line in `insights.md`), else `null`. Never the draft body. |

## Sources (file → field)
| Field | Source |
|---|---|
| `brief.*`, `priorities`, `since_last_night` (catch-up only) | The brief file `user/work/briefs/<as_of>.md` (or `-catch-up.md`) written by `atlas-brief` in the same run; `priorities[].ref` and `[[…]]` mentions are the record IDs cited there |
| `today[]` | Event records (`user/knowledge/events/`) with `start` on `as_of`, `status: scheduled`, and shown by the meeting filter (`rhythms.yaml: meetings`, rule in `system/schemas/settings.md`): `id, title, kind, start, end, all_day, location, attendees` (→ person refs); `prep.path` = event `prep`; `prep.summary` = first line of the prep note's suggested agenda |
| `due[]` | Commitments, `direction: i_owe`, `status: open|slipped`, `due` ≤ `as_of` + `rhythms.yaml: triggers.deadline_approaching.days` (default 3): `id, title, direction, status, due, priority, counterparty, next_step` |
| `waiting_on[]` | Commitments, `direction: waiting_on`, `status: open|slipped`; `since` = `created` |
| `insights[]` | `user/inbox/insights.md`, status `new`, highest `score` first, max `rhythms.yaml: insights.brief_max` (default 3): heading ID, Insight, Why it matters, Suggested action, Links |
| `drafts[]` | The `email-drafts` job's list for the brief (titles, recipients, reasons) from this run |
| `approvals[]` | `user/inbox/approvals.md`, status `pending` |
| `actions[]` | `user/inbox/questions.md`, kind `action`, status `open`, oldest first: heading ID, Question, How, whether Copy text exists |
| `questions[]` | `user/inbox/questions.md`, status `open`, kind not `action`, newest first |
| `meta.notices` | `user/.state/health.yaml` open high-severity issues affecting ingestion; staleness found by the job's readiness check (`user/.state/jobs.yaml`) |

## Rendering notes
- Order on the page: action needed (if any), while you were away (catch-up only), top priorities (numbered: they are ranked), today, due and slipping, waiting on others, needs you (if any), worth knowing (if any), drafts ready (if any). Every section has a one-line description under its title and no count. The brief file's "What changed" and "Since last night" sections are not shown on the page.
- Sorting: `priorities` in rank order (3 to 5 items); `today` by `start`, all-day items last; `due` overdue first, then by `due`, then priority; `waiting_on` slipped first, then by `due` (nulls last).
- Caps (then `meta.truncated`): `today` 15, `due` 10, `waiting_on` 8, `drafts` 8, `approvals` 5, `questions` 3, `since_last_night` 8 (catch-up). `actions` is never capped. The brief file keeps the full lists.
- Text limits: `headline` 200 characters, `why`/`next_step`/`summary` 240.
- The page is typically under 15 KB of data; the budget only matters after long away periods (catch-up), where `since_last_night` is truncated first.
