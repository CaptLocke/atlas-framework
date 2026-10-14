---
type: dashboard-contract
name: week-ahead
template: week-ahead.html
republished_by: [daily-brief, weekly-review]
size_budget_kb: 150
stale_after_hours: 36
---
# Dashboard: week-ahead

## Purpose
A plan for the next seven days, not just a calendar. In order: **This week's outcomes** (3 to 5 things that would make the week a success, tied to goals), **The week at a glance** (a strip of seven days showing meeting load, free focus time, items due, and watch-outs; selecting a day narrows the day list to it) with a **time vs. work** line comparing free focus hours to the effort of what the user owes, **Get ready** (meetings that need preparation), **Watch-outs** (problems with the schedule itself), then **each day**: meetings with prep status, suggested focus time, and what's due. Meetings open in the record panel. Focus suggestions are only suggestions; putting a hold on the calendar is `own_calendar_manage` (propose) and happens in chat.

Republished by `daily-brief` each cycle (the 7 days from the brief's target date) and by `weekly-review` (Friday preview of next week: Monday to Sunday, with `meta.as_of` = that Monday). Both compute the planning data with `atlas-brief` §D.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "week-ahead", "schema_version": 1, "as_of": "2026-10-13", "…": "…" },
  "range": { "start": "2026-10-13", "end": "2026-10-19" },
  "work_hours_per_day": 10,
  "summary": { "meetings": 9, "meeting_hours": 8.5, "focus_hours": 22, "work_due_hours": 6.3, "unsized": 1, "deadlines": 5, "prep_missing": 1 },
  "outcomes": [ { "text": "Get Dana's MSA review unblocked so the Globex pilot can start",
                  "goal": { "id": "goals/2026-q4-enterprise-revenue", "title": "Launch the enterprise tier" },
                  "status": "at_risk", "why": "Six days late; a call before Thursday is the fastest route." } ],
  "watchouts": [ { "kind": "unprotected_deadline", "date": "2026-10-15",
                   "text": "Enterprise pricing sign-off is due Thursday and no time is set aside for it." } ],
  "days": [
    { "date": "2026-10-14", "work_day": true, "meeting_hours": 0.5, "free_hours": 6.5,
      "events": [ { "id": "events/2026-10-14-design-crit", "title": "Design crit: import flow", "kind": "meeting",
                    "start": "2026-10-14T15:00:00-07:00", "end": "2026-10-14T15:15:00-07:00", "all_day": false,
                    "location": "Zoom", "attendees": [ { "id": "people/priya-nair", "title": "Priya Nair" } ],
                    "prep": { "status": "not_needed", "path": null, "summary": null, "todo": null },
                    "project": null, "note": null } ],
      "focus": [ { "start": "2026-10-14T09:30:00-07:00", "end": "2026-10-14T11:30:00-07:00",
                   "label": "Review the Q4 roadmap draft", "reason": "Due Thursday and your calendar is clear." } ],
      "due": [ { "id": "commitments/tomas-import-estimate", "title": "Tomás sends the import fix estimate",
                 "direction": "waiting_on", "status": "open", "kind": null,
                 "counterparty": { "id": "people/tomas-herrera", "title": "Tomás Herrera" } } ] }
  ]
}
```
Full example: `system/tests/dashboards/week-ahead.json`. `days` always has 7 entries, `range.start` = `meta.as_of`.

| Field | Notes |
|---|---|
| `prep.status` | As in the Daily Brief contract: `ready`, `planned`, `none`, `not_needed`. |
| `due[].kind` | `"deadline"` for deadline events (then `id` is the event), otherwise `null` for commitments. |
| `note` | One line on why the meeting matters or what to raise, if any. |
| `prep.summary`, `prep.todo` | `summary`: the first line of the prep note's suggested agenda (when `ready`). `todo`: one line on what to prepare, for meetings with `none` or `planned` ("Atlas will write the prep note Wednesday evening."). |
| `free_hours` | Free time that can hold focused work on that day: the sum of gaps of at least 60 minutes inside work hours, after meetings (hidden ones included) and holds. `0` on non-work days. |
| `summary.focus_hours` | Sum of `free_hours` over the seven days. |
| `summary.work_due_hours` | Rough hours of `i_owe` work due in the range (or already overdue): `effort` `quick` 0.25, `hour` 1, `half_day` 4, `day` 8. `summary.unsized` counts such items with no `effort`. |
| `outcomes[]` | 3 to 5 items. `status`: `open`, `on_track`, `at_risk`, or `done`. `goal` is a ref or `null`; `why` one line. |
| `watchouts[].kind` | `overloaded` (meetings over 60% of the day's work hours), `no_break` (3 hours or more of meetings with no gap of 30 minutes), `double_booked` (overlapping meetings the user accepted), `unprotected_deadline` (`i_owe` work of `hour` or more due that day with no focus block and less free time before it than its effort). `text` is one plain sentence; at most 6. |

## Sources (file → field)
| Field | Source |
|---|---|
| `events[]` | Event records with `start` in the range, `status: scheduled`, `kind` not `deadline`, and shown by the meeting filter (`rhythms.yaml: meetings`, rule in `system/schemas/settings.md`): `id, title, kind, start, end, location, attendees`; `prep.path` = `prep` |
| `prep.status` | `ready` if `prep` is set; `planned` if the meeting meets `key_meeting_upcoming` (`system/triggers.md`) and has no note yet but `meeting-prep` will run before it; `none` if it meets it and no run will; else `not_needed` |
| `due[]` | Commitments (`open|slipped`) with `due` in the range, both directions; deadline events (`kind: deadline`) in the range |
| `meeting_hours` | Sum over the day's `events[]` (all-day items excluded) |
| `work_day`, `work_hours_per_day` | `rhythms.yaml: work_hours` (`days`, `start`, `end`) |
| `meta.headline` | One line on the shape of the week (`atlas-brief` §D) |
| `events[].note`, `events[].project`, `prep.summary`, `prep.todo` | `atlas-brief` §D step 4: `note` from the event's `insight` or prep note; `project` = the event's first `links.projects` entry; `summary` and `todo` from the prep note or the `meeting-prep` schedule |
| `summary.meetings`, `summary.meeting_hours` | Count and hours of `events[]` in the range (all-day items excluded) |
| `summary.deadlines` | Items in `due[]` across the range with `direction: i_owe` or `kind: deadline` (what the user has to deliver); shown as "things due" |
| `summary.prep_missing` | Events in the range with `prep.status: none` |
| `outcomes[]` | The latest weekly review covering this week (`user/work/reviews/`, "Suggested priorities for next week"), with `status` refreshed from the linked records each run (`done` when its commitment closed, `at_risk` when it slipped or its project is at risk or off track). Before the first weekly review, `atlas-brief` proposes up to 3 from the top-ranked goals and the `i_owe` work due this week. |
| `focus[]`, `free_hours`, `summary.focus_hours`, `summary.work_due_hours`, `unsized`, `watchouts[]` | `atlas-brief` §D |

## Rendering notes
- Order: outcomes (if any), the week at a glance (with the time vs. work line when `summary.focus_hours` is set), get ready, watch-outs, then the seven days. Every section has a one-line description and no count.
- The glance strip is one button per day (meeting bar against `work_hours_per_day`, amber over 60%; meeting and free hours; "N due"; "Watch-out" when a watch-out names that day). Selecting a day shows only that day's section; selecting it again, or "Show all days", shows all. On phones the strip scrolls sideways inside its own box.
- The time vs. work line is amber when `work_due_hours` > `focus_hours` ("That's N h short"), green otherwise.
- **Record panel:** meetings (in Get ready and the day list) open in the record panel (`system/dashboards/README.md` §Record panel): when, where, who, project, prep status, the prep note's first agenda line, what to prepare. Events may carry the panel data fields.
- Within a day, events and focus suggestions are interleaved by start time; due items are listed after them.
- Caps: 20 events per day, 10 due items per day; `meta.truncated` keys are `days.<date>`.
- Text limits: `note` and `reason` 200 characters.
- Non-work days render muted with "Nothing scheduled" when empty.
