---
type: dashboard-contract
name: week-ahead
template: week-ahead.html
republished_by: [daily-brief, weekly-review]
size_budget_kb: 150
---
# Dashboard: week-ahead

## Purpose
The next seven days, one day per row: meetings with prep status, deadlines and commitments due, meeting load, and suggested focus time. Suggestions are only suggestions; putting a hold on the calendar is `own_calendar_manage` (propose) and happens in chat.

Republished by `daily-brief` each cycle and by `weekly-review` (Friday preview of next week).

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "week-ahead", "schema_version": 1, "as_of": "2026-10-13", "…": "…" },
  "range": { "start": "2026-10-13", "end": "2026-10-19" },
  "headline": "Meeting-heavy Tuesday and Thursday; Wednesday morning is your best window.",
  "work_hours_per_day": 10,
  "summary": { "meetings": 9, "meeting_hours": 8.5, "deadlines": 5, "prep_missing": 1 },
  "days": [
    { "date": "2026-10-14", "work_day": true, "meeting_hours": 0.5,
      "events": [ { "id": "events/2026-10-14-design-crit", "title": "Design crit: import flow", "kind": "meeting",
                    "start": "2026-10-14T15:00:00-07:00", "end": "2026-10-14T15:15:00-07:00", "all_day": false,
                    "location": "Zoom", "attendees": [ { "id": "people/priya-nair", "title": "Priya Nair" } ],
                    "prep": { "status": "not_needed", "path": null }, "note": null } ],
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

## Sources (file → field)
| Field | Source |
|---|---|
| `events[]` | Event records with `start` in the range, `status: scheduled`, `kind` not `deadline`, and shown by the meeting filter (`rhythms.yaml: meetings`, rule in `system/schemas/settings.md`): `id, title, kind, start, end, location, attendees`; `prep.path` = `prep` |
| `prep.status` | `ready` if `prep` is set; `planned` if the meeting meets `key_meeting_upcoming` (`system/triggers.md`) and has no note yet but `meeting-prep` will run before it; `none` if it meets it and no run will; else `not_needed` |
| `due[]` | Commitments (`open|slipped`) with `due` in the range, both directions; deadline events (`kind: deadline`) in the range |
| `focus[]` | Computed by `nova-brief`: gaps of ≥ 90 minutes inside `rhythms.yaml: work_hours` on work days, matched to the highest-priority `i_owe` work due within the week; at most 1 per day, 4 per week; respects `user/profile/working-style.md` and `preferences.md` (e.g. no Friday afternoons); meetings hidden by the meeting filter still count as busy |
| `meeting_hours`, `summary` | Sums over `events[]` (all-day items excluded) |
| `work_day`, `work_hours_per_day` | `rhythms.yaml: work_hours` (`days`, `start`, `end`) |
| `headline` | One line from `nova-brief` |

## Rendering notes
- Within a day, events and focus suggestions are interleaved by start time; due items are listed after them.
- Caps: 20 events per day, 10 due items per day; `meta.truncated` keys are `days.<date>`.
- Text limits: `note` and `reason` 200 characters.
- Non-work days render muted with "Nothing scheduled" when empty.
