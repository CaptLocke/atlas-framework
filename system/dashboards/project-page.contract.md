---
type: dashboard-contract
name: project-page
template: project-page.html
republished_by: [triage, weekly-review]
size_budget_kb: 250
stale_after_hours: 192
---
# Dashboard: project-page

## Purpose
A one-page view of a single project, generated on request in chat ("make a page for the enterprise launch"): current state, health, owner, goal, people, open commitments, risks, decisions, open questions and ideas, meetings, history, and sources. One artifact per project; the URL is stored in `user/settings/dashboards.yaml: project_pages` (project ID → url).

Created only in chat. Once listed in `project_pages`, it is republished by `triage` and `weekly-review` when that project's records changed, and by any chat that changes them. Removing the entry stops refreshes (deleting the page itself is `destructive`).

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "project-page", "schema_version": 1, "title": "Enterprise launch", "as_of": "2026-10-13", "…": "…" },
  "project": { "id": "projects/enterprise-launch", "title": "Enterprise launch", "summary": "Ship the enterprise tier…",
               "description": ["Enterprise is Acme's first tier aimed at…", "Pricing is decided…"],
               "status": "active", "health": "at_risk", "scale": "initiative",
               "owner": { "id": "people/maya-chen", "title": "Maya Chen" },
               "goal": { "id": "goals/2026-q4-enterprise-revenue", "title": "Launch the enterprise tier" },
               "start": "2026-08-18", "target": "2026-11-30", "insight": "…", "next_step": "…",
               "organizations": [ { "id": "organizations/harbor-analytics", "title": "Harbor Analytics" } ],
               "topics": [ { "id": "topics/pricing", "title": "Pricing" } ] },
  "people": [ { "id": "people/dana-ruiz", "title": "Dana Ruiz", "project_role": "Legal review", "org": null } ],
  "commitments": [ { "id": "commitments/dana-msa-review", "title": "…", "direction": "waiting_on", "status": "slipped",
                     "due": "2026-10-07", "owner": { "id": "people/dana-ruiz", "title": "Dana Ruiz" },
                     "counterparty": { "id": "people/maya-chen", "title": "Maya Chen" }, "next_step": "…" } ],
  "risks": [ { "id": "risks/msa-review-delay", "title": "…", "summary": "…", "status": "potential",
               "likelihood": "medium", "impact": "high", "owner": { "id": "people/maya-chen", "title": "Maya Chen" }, "mitigation": null } ],
  "decisions": [ { "id": "decisions/2026-10-12-enterprise-tier-pricing", "title": "…", "status": "made",
                   "decided_on": "2026-10-08", "rationale": "…" } ],
  "questions": [ { "id": "questions/sso-pricing", "title": "How do we price SSO?", "status": "open", "asked_on": "2026-09-29" } ],
  "ideas": [ { "id": "ideas/enterprise-onboarding-concierge", "title": "…", "status": "exploring" } ],
  "events": { "upcoming": [ { "id": "events/2026-10-15-enterprise-tier-review", "title": "…", "kind": "meeting",
                              "start": "2026-10-15T13:00:00-07:00", "outcomes": [] } ],
              "recent": [] },
  "updates": [ { "date": "2026-10-12", "text": "Health changed to at risk ([[commitments/dana-msa-review]])." } ],
  "sources": [ { "id": "sources/2026-10-08-pricing-sync", "title": "Pricing sync transcript", "kind": "meeting", "occurred_on": "2026-10-08" } ]
}
```
`meta.title` = the project title.

## Sources (file → field)
| Field | Source |
|---|---|
| `project` | The project record: frontmatter fields; `description` = paragraphs of the body above `## Updates`; `organizations`, `topics` = `links` groups |
| `people[]` | Project `links.people` plus owners/deciders/attendees of the records below; `project_role` = a short role Atlas infers from the records (owner, sponsor, reviewer…) or the person's `role` |
| `commitments[]` | Commitments linking the project, `status: open|slipped` |
| `risks[]` | Risks linking the project: `potential`, `active`, and `resolved` in the last 90 days |
| `decisions[]` | Decisions linking the project, not superseded, newest first |
| `questions[]`, `ideas[]` | Open questions; ideas not `dropped`, linking the project |
| `events.upcoming` / `events.recent` | Events linking the project: next 30 days / last 30 days (`outcomes` from the record) |
| `updates[]` | The project record's `## Updates` lines, newest first |
| `sources[]` | The project's `sources` plus sources of the listed decisions, newest first |

## Rendering notes
- Only records linked to the project (directly or via its commitments, decisions, and risks) appear; the page never pulls in unrelated work.
- Caps: 40 commitments, 30 risks, 40 decisions, 20 questions, 20 ideas, 20 events, 30 updates, 30 sources, 30 people. Older items go first; `meta.truncated` keys match the list names (`updates`, `sources`, …).
- Text limits: description paragraphs 800, `rationale` 400, update text 300 characters.
- Publishing a project page is `dashboards_refresh` (auto) in chat; sharing it with anyone is `share_expose` (locked).
