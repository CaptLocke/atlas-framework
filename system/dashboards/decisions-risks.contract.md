---
type: dashboard-contract
name: decisions-risks
template: decisions-risks.html
republished_by: [weekly-review]
size_budget_kb: 300
stale_after_hours: 192
---
# Dashboard: decisions-risks

## Purpose
A searchable decision log with the reasoning behind each decision, and the risk and issue register (an issue is a risk with `status: active`). One search box filters both; each list has its own status filter.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "decisions-risks", "schema_version": 1, "as_of": "2026-10-09", "…": "…" },
  "summary": { "issues": 1, "open_risks": 2, "decisions_90d": 35 },
  "risks": [
    { "id": "risks/onboarding-import-failures", "title": "Onboarding import failures",
      "summary": "CSV imports fail silently for files over 5,000 rows.", "status": "active",
      "likelihood": "high", "impact": "high", "owner": { "id": "people/tomas-herrera", "title": "Tomás Herrera" },
      "mitigation": "Status page shipped Oct 6; fix targeted for Oct 24.",
      "projects": [ { "id": "projects/onboarding-import-fix", "title": "Onboarding import fix" } ],
      "updated": "2026-10-08", "insight": "Touches three renewing accounts." }
  ],
  "decisions": [
    { "id": "decisions/2026-10-12-enterprise-tier-pricing", "title": "Enterprise tier priced per seat",
      "summary": "Per-seat pricing with a 25-seat minimum.", "status": "made", "decided_on": "2026-10-08",
      "deciders": [ { "id": "people/maya-chen", "title": "Maya Chen" } ],
      "rationale": "Buyers budget per seat; per-workspace pricing stalled two deals.",
      "alternatives": ["Per workspace", "Usage-based"], "reversible": true, "revisit_on": "2027-01-15",
      "projects": [ { "id": "projects/enterprise-launch", "title": "Enterprise launch" } ] }
  ],
  "insights": []
}
```
Full example: `system/tests/dashboards/decisions-risks.json`. `rationale: "unknown"` renders as "Not recorded".

## Sources (file → field)
| Field | Source |
|---|---|
| `risks[]` | `user/knowledge/risks/*.md`: all `potential` and `active`, plus `resolved` updated in the last 90 days: `id, title, summary, status, likelihood, impact, owner, mitigation, updated`; `projects` = `links.projects` |
| `risks[].insight` | Latest `user/inbox/insights.md` entry linking the risk (status `new|seen`), else `null` |
| `decisions[]` | `user/knowledge/decisions/*.md`, not superseded: `proposed` (any age) and `made`/`reversed` with `decided_on` in the last 365 days: `id, title, summary, status, decided_on, deciders, rationale, alternatives, reversible, revisit_on`; `projects` = `links.projects` |
| `insights[]` | `user/inbox/insights.md`, status `new|seen`, linking a decision or risk and not already attached to a risk, max 5 |
| `summary` | Counts over the full sets: `issues` (active risks), `open_risks` (potential), `decisions_90d` (made in the last 90 days) |

## Rendering notes
- Risks sort: `active` first, then exposure (likelihood × impact, high = 3, medium = 2, low = 1) descending, then `updated` (newest first); resolved last. Default filter "Open".
- Decisions sort: `proposed` with a `revisit_on` or none first, then `decided_on` newest first. Default filter "All". "Revisit soon" = `revisit_on` within 14 days.
- Caps: 100 risks, 150 decisions. Over budget, drop resolved risks first, then the oldest decisions; record `meta.truncated.risks` / `meta.truncated.decisions`. Older decisions remain searchable in chat.
- Text limits: `summary` 200, `rationale` 400, `mitigation` 300 characters; at most 5 `alternatives`.
