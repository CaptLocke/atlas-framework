---
type: dashboard-contract
name: goals
template: goals.html
republished_by: [weekly-review, monthly, quarterly]
size_budget_kb: 200
stale_after_hours: 192
---
# Dashboard: goals

## Purpose
Each goal for the current period with its measure, progress, an assessment, evidence for and against, the projects behind it, and its accomplishments; plus the running accomplishments list that feeds the quarterly performance review.

Republished by `weekly-review` (which appends accomplishments), `monthly` (goal progress), and `quarterly` (goal reset).

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "goals", "schema_version": 1, "as_of": "2026-10-09", "…": "…" },
  "period": { "label": "2026-Q4", "start": "2026-10-01", "end": "2026-12-31" },
  "goals": [
    { "id": "goals/2026-q4-retention", "title": "Keep gross retention at 92% or better", "status": "active",
      "horizon": "quarter", "period": "2026-Q4", "rank": 1, "summary": "…",
      "metric": "Gross revenue retention", "target": "92%", "current": "90.5%", "current_as_of": "2026-10-01",
      "progress": 0.84, "assessment": "at_risk",
      "owner": { "id": "people/maya-chen", "title": "Maya Chen" }, "insight": "…",
      "evidence": [ { "direction": "against", "text": "Three customers raised the import bug this month.",
                      "ref": { "id": "risks/onboarding-import-failures", "title": "Onboarding import failures" } } ],
      "projects": [ { "id": "projects/onboarding-import-fix", "title": "Onboarding import fix", "health": "off_track" } ],
      "accomplishments": [ { "date": "2026-10-06", "text": "Shipped the in-app import status page…",
                             "ref": { "id": "sources/2026-10-06-release-notes", "title": "Release notes" } } ] }
  ],
  "accomplishments": [
    { "date": "2026-10-06", "text": "…", "goal": { "id": "goals/2026-q4-retention", "title": "Q4 retention" },
      "ref": { "id": "sources/2026-10-06-release-notes", "title": "Release notes" } }
  ]
}
```

| Field | Notes |
|---|---|
| `progress` | 0–1, or `null`. Set only when `current` and `target` are comparable numbers (`current / target`, or the inverse for "reduce to" goals). Never invented. |
| `assessment` | `on_track`, `at_risk`, `off_track`, or `null` (not yet assessed). Atlas's judgment from evidence; shown as a chip. |
| `evidence[].direction` | `for`, `against`, or `neutral`. |
| `rank` | The user's rank for an active goal (1 = most important), or `null` if unranked (`system/schemas/goal.md` §Ranking). Shown as "#1". |

## Sources (file → field)
| Field | Source |
|---|---|
| `period` | The current quarter (or the period most active goals share), from the goals' `period` |
| `goals[]` | `user/knowledge/goals/*.md` with `status: active|draft`, plus `achieved|missed` goals whose `period` is the current one: `id, title, status, horizon, period, rank, summary, metric, target, current, owner` |
| `current_as_of` | The date in the goal's `current` text or its latest `## Updates` line that changed `current` |
| `assessment`, `insight`, `evidence` | Weekly review / monthly goal progress output (`user/work/reviews/YYYY-Www.md`, `user/work/reports/YYYY-MM.md`) and linked records (projects' `health`, risks, decisions); each evidence line cites its record |
| `projects[]` | Projects whose `goal` is this goal or that link to it: `id, title, health` |
| `goals[].accomplishments` | The goal's `accomplishments` field (dated entries), newest first |
| `accomplishments[]` | `user/work/accomplishments.md` (running list), newest first; `goal` = the goal the entry is filed under, or `null` |

## Rendering notes
- Goals sort: active before draft before achieved/missed; within active, ranked goals by `rank` (1 first), then unranked by `assessment` off_track, at_risk, null, on_track; then title. The page applies the same order, so data order doesn't matter for active goals.
- Caps: 20 goals; 8 accomplishments per goal; 60 entries in `accomplishments` (current and previous period). Older entries are dropped first; `meta.truncated.accomplishments` counts them.
- Text limits: `summary`, `insight`, evidence `text` 240 characters; accomplishment `text` 300.
- Goals without a metric show no progress bar; that is expected, not an error.
