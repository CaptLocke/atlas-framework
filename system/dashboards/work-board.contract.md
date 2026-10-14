---
type: dashboard-contract
name: work-board
template: work-board.html
republished_by: [daily-brief, triage]
size_budget_kb: 300
stale_after_hours: 36
---
# Dashboard: work-board

## Purpose
Every active project and open commitment at a glance: status, owner, due date, health, and for each one a short insight and one recommended next step. Commitments filter by All / Mine (`i_owe`) / Waiting on (`waiting_on`) / Overdue, and can be searched by title, person, or project.

Republished by `daily-brief` every run. `triage` may republish it after a full (not `light`) run that changed commitments, so Standard and Full profiles see fresher priorities during the day.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "work-board", "schema_version": 1, "as_of": "2026-10-13", "…": "…" },
  "summary": { "overdue": 3, "i_owe": 5, "waiting_on": 4, "projects": 5 },
  "commitments": [
    { "id": "commitments/dana-msa-review", "title": "Dana reviews the enterprise MSA",
      "direction": "waiting_on", "status": "slipped", "due": "2026-10-07", "priority": "high",
      "owner": { "id": "people/dana-ruiz", "title": "Dana Ruiz" },
      "counterparty": { "id": "people/maya-chen", "title": "Maya Chen" },
      "project": { "id": "projects/enterprise-launch", "title": "Enterprise launch" },
      "insight": "Dana hasn't replied in 6 days; she usually responds faster to a call.",
      "next_step": "Call before Thursday's review." }
  ],
  "projects": [
    { "id": "projects/enterprise-launch", "title": "Enterprise launch", "status": "active", "health": "at_risk",
      "scale": "initiative", "owner": { "id": "people/maya-chen", "title": "Maya Chen" },
      "goal": { "id": "goals/2026-q4-enterprise-revenue", "title": "Q4 enterprise revenue" },
      "target": "2026-11-30", "insight": "…", "next_step": "…", "open_commitments": 3, "active_risks": 2 }
  ]
}
```
Full example: `system/tests/dashboards/work-board.json`. `summary` counts cover **all** matching records, including any truncated from the lists.

## Sources (file → field)
| Field | Source |
|---|---|
| `commitments[]` | `user/knowledge/commitments/*.md` with `status: open|slipped`, not archived/superseded: `id, title, direction, status, due, priority, owner, counterparty, insight, next_step`; `project` = first `links.projects` entry (or `null`) |
| `projects[]` | `user/knowledge/projects/*.md` with `status: active|proposed|paused`: `id, title, status, health, scale, owner, goal, target, insight, next_step` |
| `projects[].open_commitments` | Count of open/slipped commitments linking to the project |
| `projects[].active_risks` | Count of risks with `status: potential|active` linking to the project |
| `summary` | Counts over the full filtered sets above; `overdue` = `slipped` or `due` < `as_of` |
| Ref titles | Title of the referenced record (index line in `user/knowledge/_index/`) |

## Rendering notes
- **Record panel:** clicking a card opens it in the record panel (`system/dashboards/README.md` §Record panel). Every item may carry the panel data fields (`details`, `body`, `body_truncated`, `links`, `created`, `updated`; same section). Before the caps below drop any item, cut each `body` to 800 characters, then drop `body` from the oldest items first.
- Commitments sort: overdue/slipped first (most overdue first), then by `due` ascending, `due: null` last; ties by priority (high → low), then title.
- Projects sort: `health` off_track, at_risk, unknown, on_track; then `status` active, proposed, paused; then `target` ascending (nulls last).
- Default filter "All"; the viewer's last choice is remembered in browser storage when available.
- Caps: 200 commitments, 60 projects. When over budget or cap, drop in this order: low-priority commitments with no due date, then commitments due more than 30 days out, then paused projects; record counts in `meta.truncated.commitments` / `meta.truncated.projects`.
- Text limits: `insight` and `next_step` 240 characters.
