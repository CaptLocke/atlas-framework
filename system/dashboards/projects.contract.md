---
type: dashboard-contract
name: projects
template: projects.html
republished_by: [daily-brief, triage, weekly-review]
size_budget_kb: 250
stale_after_hours: 36
---
# Dashboard: projects

## Purpose
Every active, proposed, and paused project at a glance: health, status, owner, target date, the goal it serves, a short insight, and one recommended next step. Filters: All / Needs attention (off track or at risk) / On track / Proposed or paused, plus a search by project, owner, or goal. A project with its own project page (`project-page`, made on request) opens that page; any other project opens in the record panel with its open commitments and risks.

Republished by `daily-brief` every run, by `triage` after a full run that changed project health or next steps, and by `weekly-review`.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "projects", "schema_version": 1, "as_of": "2026-10-13", "…": "…" },
  "summary": { "active": 4, "attention": 2, "on_track": 2, "later": 1 },
  "projects": [
    { "id": "projects/enterprise-launch", "title": "Enterprise launch", "status": "active", "health": "at_risk",
      "scale": "initiative", "owner": { "id": "people/maya-chen", "title": "Maya Chen" },
      "goal": { "id": "goals/2026-q4-enterprise-revenue", "title": "Q4 enterprise revenue" },
      "target": "2026-11-30", "insight": "…", "next_step": "…", "open_commitments": 3, "active_risks": 2,
      "commitments": [ { "id": "commitments/dana-msa-review", "title": "Dana reviews the enterprise MSA", "direction": "waiting_on", "due": "2026-10-07", "status": "slipped" } ],
      "risks": [ { "id": "risks/msa-review-delay", "title": "Legal review delays enterprise launch", "status": "potential" } ],
      "page_url": "https://claude.ai/artifact/…" }
  ]
}
```
`summary` counts cover **all** matching projects, including any truncated from the list.

## Sources (file → field)
| Field | Source |
|---|---|
| `projects[]` | `user/knowledge/projects/*.md` with `status: active|proposed|paused`: `id, title, status, health, scale, owner, goal, target, insight, next_step`; optional `summary` |
| `projects[].commitments` | Open/slipped commitments linking to the project, soonest due first, up to 10: `id, title, direction, due, status` |
| `projects[].risks` | Risks with `status: potential|active` linking to the project, active first, up to 5: `id, title, status` |
| `projects[].page_url` | `user/settings/dashboards.yaml: project_pages[<project ID>]` when the project has its own project page (`https://` only), else `null` |
| `projects[].open_commitments`, `active_risks` | Counts behind the two lists above (before their caps) |
| `summary` | `active` (status active), `attention` (health off_track or at_risk), `on_track`, `later` (status proposed or paused), over the full set |
| Ref titles | Title of the referenced record (index line in `user/knowledge/_index/`) |

## Rendering notes
- **Project pages:** a project with `page_url` is a link: clicking anywhere on its card opens its project page (a new tab, like every dashboard link), and the card shows a "Project page ↗" chip. Every other card opens the record panel.
- **Record panel:** clicking a card without a project page opens it in the record panel (`system/dashboards/README.md` §Record panel), with the project's open commitments and risks as sections. Every project may carry the panel data fields (`details`, `body`, `body_truncated`, `links`, `created`, `updated`; same section). Before the caps below drop any project, cut each `body` to 800 characters, then drop `body` from the oldest projects first.
- Layout: the filter row, then the project cards across the full width, with no section heading (the page title says "Projects").
- Sort: `health` off_track, at_risk, unknown, on_track; then `status` active, proposed, paused; then `target` ascending (nulls last).
- Cards in a grid (one column on phones), each with a colored top edge for its health.
- Default filter "All"; the viewer's last choice is remembered in browser storage when available.
- Caps: 60 projects. When over budget or cap, drop paused projects first, then proposed ones, oldest `updated` first; record the count in `meta.truncated.projects`.
- Text limits: `insight` and `next_step` 240 characters, `summary` 240.
