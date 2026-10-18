---
type: dashboard-contract
name: commitments
template: commitments.html
republished_by: [daily-brief, triage]
size_budget_kb: 300
stale_after_hours: 36
---
# Dashboard: commitments

## Purpose
Every open commitment, in two sections so the direction is never in doubt: **Waiting on** (what other people have promised the user) and **I owe** (what the user has promised others). Each shows who, when it's due, priority, project, a short insight, and one recommended next step. One filter row applies to both sections: All / Overdue / High priority, plus a search by title, person, or project. Projects have their own dashboard (`projects`).

Republished by `daily-brief` every run, and by `triage` when this run changed its data and the routine does not run `daily-brief` later (the brief republishes it then; `system/jobs/triage.md` step 7), so Standard and Full profiles see fresher priorities during the day.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "commitments", "schema_version": 1, "as_of": "2026-10-13", "…": "…" },
  "summary": { "overdue": 3, "i_owe": 5, "waiting_on": 4 },
  "commitments": [
    { "id": "commitments/dana-msa-review", "title": "Dana reviews the enterprise MSA",
      "direction": "waiting_on", "status": "slipped", "due": "2026-10-07", "priority": "high",
      "owner": { "id": "people/dana-ruiz", "title": "Dana Ruiz" },
      "counterparty": { "id": "people/maya-chen", "title": "Maya Chen" },
      "project": { "id": "projects/enterprise-launch", "title": "Enterprise launch" },
      "insight": "Dana hasn't replied in 6 days; she usually responds faster to a call.",
      "next_step": "Call before Thursday's review." }
  ]
}
```
`summary` counts cover **all** matching records, including any truncated from the list.

## Sources (file → field)
| Field | Source |
|---|---|
| `commitments[]` | `user/knowledge/commitments/*.md` with `status: open|slipped`, not archived/superseded: `id, title, direction, status, due, priority, owner, counterparty, insight, next_step`; `project` = first `links.projects` entry (or `null`) |
| `summary` | Counts over the full filtered set above; `overdue` = `slipped` or `due` < `as_of` |
| Ref titles | Title of the referenced record (index line in `user/knowledge/_index/`) |

## Rendering notes
- **Record panel:** clicking a card opens it in the record panel (`system/dashboards/README.md` §Record panel). Every item may carry the panel data fields (`details`, `body`, `body_truncated`, `links`, `created`, `updated`; same section). Before the caps below drop any item, cut each `body` to 800 characters, then drop `body` from the oldest items first.
- Sections: Waiting on (`direction: waiting_on`), then I owe (`direction: i_owe`). Each has a one-line description and no count. Each shows its own empty message when it has nothing.
- Sort within each section: overdue/slipped first (most overdue first), then by `due` ascending, `due: null` last; ties by priority (high → low), then title.
- Default filter "All"; the viewer's last choice is remembered in browser storage when available.
- Caps: 200 commitments. When over budget or cap, drop in this order: low-priority commitments with no due date, then commitments due more than 30 days out; record the counts per section in `meta.truncated.waiting_on` and `meta.truncated.i_owe` (each section shows its own "N more not shown here").
- Text limits: `insight` and `next_step` 240 characters.
