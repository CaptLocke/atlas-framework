---
type: dashboard-contract
name: commitments
template: commitments.html
republished_by: [daily-brief, triage, weekly-review, monthly, quarterly]
size_budget_kb: 400
stale_after_hours: 36
---
# Dashboard: Work (`commitments`)

## Purpose
**Where does my work stand?** One page, titled **Work**, that replaces the Commitments, Projects, Goals, Decisions & Risks and People pages. It keeps the `commitments` slug, so its URL and `last_published` survive. Jump links at the top lead to five sections, in this order:
1. **Commitments:** I owe, then Waiting on.
2. **Projects:** cards, each with owner, target, insight and its one next step.
3. **Goals:** by rank, with a progress bar, the assessment, and evidence for and against.
4. **Decisions & risks:** recent decisions with their reasons, beside open risks and issues.
5. **People:** only people with something open either way, a meeting in the next 7 days, or who've gone quiet. A line below says anyone else is a chat question.

One filter applies to the whole page: **Everything / Needs attention** (below). Finished items aren't shown (done commitments, resolved risks, achieved or missed goals); history and anyone not listed are chat questions. Sizes stay bounded by current activity, not history.

Republished by `daily-brief` every run; by `triage` when this run changed its data and the routine does not run `daily-brief` later (the brief republishes it then; `system/jobs/triage.md` step 7); by `weekly-review` (project health, risks, decisions, people gone quiet); by `monthly` (goal progress); and by `quarterly` (goal reset). That is the union of the five pages it replaces.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "commitments", "schema_version": 2, "title": "Work", "as_of": "2026-10-13", "…": "…" },
  "summary": { "i_owe": 6, "waiting_on": 4, "overdue": 3, "projects_attention": 2, "goals_attention": 1,
               "issues": 1, "open_risks": 2, "people": 7, "quiet": 2 },
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
      "goal": { "id": "goals/2026-q4-enterprise-revenue", "title": "Launch the enterprise tier" },
      "target": "2026-11-30", "summary": "…", "insight": "…", "next_step": "…",
      "page_url": "https://claude.ai/artifact/…" }
  ],
  "period": { "label": "2026-Q4", "start": "2026-10-01", "end": "2026-12-31" },
  "goals": [
    { "id": "goals/2026-q4-retention", "title": "Keep gross retention at 92% or better", "status": "active",
      "period": "2026-Q4", "rank": 2, "summary": "…", "metric": "Gross revenue retention", "target": "92%",
      "current": "90.5%", "current_as_of": "2026-10-01", "progress": 0.84, "assessment": "at_risk",
      "owner": { "id": "people/maya-chen", "title": "Maya Chen" }, "insight": "…",
      "evidence": [ { "direction": "against", "text": "Three customers raised the import bug this month.",
                      "ref": { "id": "risks/onboarding-import-failures", "title": "Onboarding import failures" } } ] }
  ],
  "decisions": [
    { "id": "decisions/2026-10-12-enterprise-tier-pricing", "title": "Enterprise tier priced per seat",
      "summary": "Per-seat pricing with a 25-seat minimum.", "status": "made", "decided_on": "2026-10-08",
      "deciders": [ { "id": "people/maya-chen", "title": "Maya Chen" } ],
      "rationale": "Buyers budget per seat; per-workspace pricing stalled two deals.",
      "alternatives": ["Per workspace", "Usage-based"], "reversible": true, "revisit_on": "2027-01-15",
      "projects": [ { "id": "projects/enterprise-launch", "title": "Enterprise launch" } ] }
  ],
  "risks": [
    { "id": "risks/onboarding-import-failures", "title": "Onboarding import failures",
      "summary": "CSV imports fail silently for files over 5,000 rows.", "status": "active",
      "likelihood": "high", "impact": "high", "owner": { "id": "people/tomas-herrera", "title": "Tomás Herrera" },
      "mitigation": "Status page shipped Oct 6; fix targeted for Oct 24.",
      "projects": [ { "id": "projects/onboarding-import-fix", "title": "Onboarding import fix" } ],
      "updated": "2026-10-08", "insight": "Touches three renewing accounts." }
  ],
  "people": [
    { "id": "people/dana-ruiz", "title": "Dana Ruiz", "role": "Senior counsel",
      "org": { "id": "organizations/acme", "title": "Acme" }, "relationship": "stakeholder",
      "last_contact": "2026-09-30", "cadence": null,
      "quiet": true, "quiet_reason": "No reply in 13 days while she owes you the MSA review.",
      "insight": null,
      "next_meeting": { "id": "events/2026-10-15-enterprise-tier-review", "title": "Enterprise tier review",
                        "start": "2026-10-15T13:00:00-07:00" } }
  ]
}
```
`summary` counts cover **all** matching records, including any truncated from the lists. `schema_version` is 2: the shape changed when the five pages merged.

**Derived on the page, not carried in the data** (so nothing is listed twice): what each person owes you and what you owe them (from `commitments`: `waiting_on` items whose `owner` is the person, and `i_owe` items whose `counterparty` is the person); each project's open commitments and risks, shown in its record panel (commitments whose `project` is it, risks whose `projects` include it); and each goal's projects (projects whose `goal` is it).

| Field | Notes |
|---|---|
| `goals[].progress` | 0–1, or `null`. Set only when `current` and `target` are comparable numbers (`current / target`, or the inverse for "reduce to" goals). Never invented. |
| `goals[].assessment` | `on_track`, `at_risk`, `off_track`, or `null` (not yet assessed). |
| `goals[].evidence[].direction` | `for`, `against`, or `neutral`. Each line cites its record in `ref` (not shown). |
| `goals[].rank` | The user's rank for an active goal (1 = most important), or `null` (`system/schemas/goal.md` §Ranking). |
| `decisions[].rationale` | `"unknown"` renders as "Not recorded". |
| `people[].quiet` | `true` when the person is a key relationship and contact has lapsed: days since `last_contact` > 1.5 × the expected `cadence` interval, or > 30 days with no cadence while there are open items either way. |
| `people[].quiet_reason` | One line saying why, shown as "Gone quiet: …" in place of `insight`. |
| `people[].next_meeting` | `{ id, title, start }`, or `null`: the earliest scheduled event in the next 7 days with the person in `attendees`. |

## Sources (file → field)
| Field | Source |
|---|---|
| `commitments[]` | `user/knowledge/commitments/*.md` with `status: open|slipped`, not archived/superseded: `id, title, direction, status, due, priority, owner, counterparty, insight, next_step`; `project` = first `links.projects` entry (or `null`) |
| `projects[]` | `user/knowledge/projects/*.md` with `status: active|proposed|paused`: `id, title, status, health, scale, owner, goal, target, insight, next_step`; optional `summary` |
| `projects[].page_url` | `user/settings/dashboards.yaml: project_pages[<project ID>]` when the project has its own project page (`https://` only), else `null` |
| `period` | The current quarter (or the period most active goals share), from the goals' `period` |
| `goals[]` | `user/knowledge/goals/*.md` with `status: active|draft`: `id, title, status, period, rank, summary, metric, target, current, owner` |
| `goals[].current_as_of` | The date in the goal's `current` text or its latest `## Updates` line that changed `current` |
| `goals[].assessment`, `insight`, `evidence` | Weekly review / monthly goal progress output (`user/work/reviews/YYYY-Www.md`, `user/work/reports/YYYY-MM.md`) and linked records (projects' `health`, risks, decisions) |
| `decisions[]` | `user/knowledge/decisions/*.md`, not superseded: `proposed` (any age) and `made`/`reversed` with `decided_on` in the last 30 days: `id, title, summary, status, decided_on, deciders, rationale, alternatives, reversible, revisit_on`; `projects` = `links.projects` |
| `risks[]` | `user/knowledge/risks/*.md` with `status: potential|active`: `id, title, summary, status, likelihood, impact, owner, mitigation, updated`; `projects` = `links.projects` |
| `people[]` | `user/knowledge/people/*.md`, `status: active`, `relationship` not `self`, and only those with an open or slipped commitment either way, a `next_meeting`, or `quiet: true`: `id, title, role, org, relationship, last_contact, cadence` |
| `people[].quiet`, `quiet_reason` | `weekly-review` ("people to reconnect with", `user/work/reviews/YYYY-Www.md`) |
| `insight` (commitments, projects, goals, risks, people) | The record's `insight` field, else the latest `user/inbox/insights.md` entry (status `new|seen`) linking the record, else `null` |
| `summary` | Counts over the full sets: `i_owe`, `waiting_on`; `overdue` (`slipped` or `due` < `as_of`); `projects_attention` (active, health `off_track|at_risk`); `goals_attention` (assessment `at_risk|off_track`); `issues` (active risks); `open_risks` (potential); `people`; `quiet` |
| Ref titles | Title of the referenced record (index line in `user/knowledge/_index/`) |
| Excluded always | `notes_private`, `emails`, `phone`, `location`; done/dropped commitments, cancelled projects, achieved/missed goals, resolved risks, superseded decisions |

## Needs attention
The page computes this from the data, so the builder sets no flag. Under "Needs attention" each section keeps only:
- **Commitments:** overdue (`slipped`, or `due` before `as_of`), or due today or tomorrow.
- **Projects:** active and `off_track` or `at_risk`.
- **Goals:** assessed `at_risk` or `off_track`.
- **Decisions:** `proposed`, or `revisit_on` within 14 days.
- **Risks:** issues (`active`), or exposure (likelihood × impact, high = 3, medium = 2, low = 1, unrated = 1) of 6 or more.
- **People:** gone quiet, or with a commitment either way that needs attention.

## Rendering notes
- **Header:** title "Work"; subtitle "Where everything you're responsible for stands."; headline (`meta.headline`): what's slipping or blocked most, in either direction, and the project or goal it threatens. Stat cards: you owe, waiting on others, overdue, projects need attention, goals at risk.
- **Jump links** under the header, one per section with its count; the Projects link shows "N need attention" as a warning when any do. The counts follow the filter. The filter sits in the same row; default "Everything", and the viewer's last choice is remembered in browser storage when available.
- **Record panel** (`system/dashboards/README.md` §Record panel): commitments, projects without a project page, decisions, risks and people open in it; goals do not. Every item that opens may carry the panel data fields (`details`, `body`, `body_truncated`, `links`, `created`, `updated`; same section). Linked items on this page open in the panel with Back.
- **Project pages:** a project with `page_url` is a link: clicking anywhere on its card opens its project page in a new tab, and the card shows a "Project page ↗" chip.
- **Sort** (the page applies these, so data order doesn't matter):
  - Commitments: I owe, then Waiting on; within each, overdue first, then priority (high → low, none last), then `due` ascending (`null` last), then title. Priority leads because triage's rubric already counts urgency (`atlas-triage/reference/signals.md` §Priority rubric); Today's Due soon is the date-ordered view. A person's card lists what's owed either way by `due` (none last).
  - Projects: active by health (off track, at risk, not assessed, on track), then proposed, then paused; then `target` ascending (`null` last).
  - Goals: active before draft; ranked by `rank`, then unranked by assessment (off track, at risk, not assessed, on track); then title.
  - Decisions: `proposed` first, then `decided_on` newest first. Risks: issues first, then exposure descending, then `updated` newest first.
  - People: gone quiet first, then anyone with an overdue item either way, then relationship (manager, report, board, customer, stakeholder, prospect, partner, peer, vendor, external, other), then most open items.
- Below People, one fixed line: anyone else is a chat question.

## Caps and truncation
Caps: 200 commitments, 60 projects, 20 goals, 30 decisions, 60 risks, 60 people. Text limits: `insight`, `next_step`, `quiet_reason`, `summary` (project, goal) and evidence `text` 240 characters; decision and risk `summary` 200; `rationale` 400; `mitigation` 300; at most 5 `alternatives` and 8 evidence lines per goal.

**Budget: 400 KB**, one for the page. The five pages it replaces had 1,300 KB between them, but most of that paid for history (365 days of decisions, resolved risks, accomplishments, people by last contact); Work shows only what's open now. The template is about 75 KB with the base; a heavy month (80 open commitments, 20 projects, 30 risks, 40 people, all with 800-character bodies) comes to about 300 KB, so 400 leaves headroom without inviting a slow page on a phone.

When over budget or a cap, apply in order until it fits, recording each list's dropped count in `meta.truncated` (keys `i_owe`, `waiting_on`, `projects`, `goals`, `decisions`, `risks`, `people`; each list shows its own "N more not shown here"):
1. Cut each `body` to 800 characters, then drop `body` from the oldest items first (README §Record panel).
2. Drop `details` and `links` from every item.
3. Commitments: low-priority with no due date, then those due more than 30 days out.
4. Decisions older than 14 days, oldest first.
5. Projects: paused, then proposed, oldest `updated` first.
6. People: lowest in the sort order first (never anyone gone quiet).
7. Risks: lowest exposure first (never an issue).

Never dropped: overdue commitments, active projects, active goals, issues, people gone quiet.
