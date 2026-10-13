---
type: dashboard-contract
name: records
template: records.html
republished_by: [maintenance, weekly-review]
size_budget_kb: 1500
stale_after_hours: 192
---
# Dashboard: records

## Purpose
Everything Nova has filed, in one place to browse and search: people, organizations, projects, goals, commitments, decisions, events, risks, questions, ideas, topics, playbooks, sources, and any record types the user added. Each record shows its type, status, summary, when it last changed, and what it links to. Filters: record type, Current / Closed / All, and a search box over names, summaries, aliases, and links.

It is a finder, not an editor. To change a record, the user mentions its ID in chat.

Republished by `maintenance` (after indexes are rebuilt) and `weekly-review`. Any chat may republish it on request ("refresh my records page").

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "records", "schema_version": 1, "as_of": "2026-10-12", "…": "…" },
  "summary": { "total": 412, "current": 268, "restricted": 3, "archived": 41 },
  "types": [
    { "type": "person", "label": "People", "count": 96 },
    { "type": "commitment", "label": "Commitments", "count": 74 }
  ],
  "records": [
    { "id": "commitments/dana-msa-review", "type": "commitment", "title": "Dana reviews the enterprise MSA",
      "summary": "Dana owes redlines on the enterprise MSA before the pilot can start.",
      "status": "slipped", "current": true, "updated": "2026-10-09", "created": "2026-09-30",
      "aliases": ["MSA review"],
      "facts": ["Waiting on Dana Ruiz", "Due Oct 7", "High priority"],
      "links": [ { "id": "people/dana-ruiz", "title": "Dana Ruiz" }, { "id": "projects/enterprise-launch", "title": "Enterprise launch" } ] }
  ]
}
```
Full example: `system/tests/dashboards/records.json`.

| Field | Notes |
|---|---|
| `summary.total` | Records included on the page plus any left out by truncation (not restricted or archived ones). |
| `summary.current` | How many of `total` have `current: true`. |
| `summary.restricted` | Records left out because of data rules (below). The page says they exist without naming them. |
| `summary.archived` | Archived records left out. The page tells the user to ask in chat to see them. |
| `types[]` | One entry per type that has at least one included record, in the order of the Sources table below, then user types alphabetically. `label` is the plural display name; user types use the type's name from `user/extensions/types/<type>.md`, pluralized ("Deals"). |
| `current` | `true` unless the status is closed for that type (below). |
| `facts` | Up to 3 short strings, chosen per type (below). Plain text, each ≤ 60 characters. |
| `links` | Up to 8 linked records as references, most important first (people and projects before sources). |

**Closed statuses** (`current: false`): `system/schemas/schema.yaml: closed_statuses`, except that a source with status `processed` stays **current** on this page (sources are reference material). For user types, statuses that clearly mean finished (done, closed, won, lost, cancelled, and the like) count as closed; anything else counts as current.

**Facts per type:**
| Type | Facts (in order, skip empty ones) |
|---|---|
| person | role, organization title, relationship label |
| organization | kind label, industry, `relationship_status` |
| project | health label, "Target <date>", owner title |
| goal | "#<rank>" if ranked, period, "<current> of <target>" |
| commitment | "You owe <counterparty>" or "Waiting on <owner>", "Due <date>" (or "No date"), "<priority> priority" |
| decision | "Decided <date>", deciders (up to 2 names) |
| event | kind label, start date (and time if not all-day), "Prep ready" if `prep` is set |
| risk | "<likelihood> likelihood", "<impact> impact", owner title |
| question | "Asked by <name>", "Answered <date>" if answered |
| idea | origin title |
| topic | `scope`, trimmed |
| playbook | trigger, trimmed, "Last used <date>" |
| source | kind label, "From <connector>" if any, occurred or captured date |
| user types | up to 3 of the type's own fields that best identify the record (Nova's judgment, the same 3 for every record of that type) |

## Sources (file → field)
| Field | Source |
|---|---|
| `records[]` | Every record in `user/knowledge/<folder>/*.md` (index-first: `user/knowledge/_index/*.md`, opening records for fields the index lacks), in type order person, organization, project, goal, commitment, decision, event, risk, question, idea, topic, playbook, source, then registered user types (`user/extensions/registry.yaml`, kind `type`): `id, type, title, summary, status, updated, created, aliases` |
| `aliases` | The record's `aliases`, minus email addresses, phone numbers, and handles that look like contact details |
| `facts` | Per the table above, from the record's own fields (names from linked records' titles) |
| `links` | The record's `links` groups and frontmatter references (`org`, `owner`, `counterparty`, `goal`, `attendees`), resolved to `{ id, title }`; unresolvable links are left out |
| `summary`, `types` | Counts over the records above |
| Left out always | Archived records (`archived: true`) and superseded records (`superseded_by` set); records excluded by `data-rules.yaml: exclusions` (`record:` entries); records whose `sensitivity` maps to handling `ignore` or `pointer` in `data-rules.yaml` (counted in `summary.restricted`); fields `notes_private`, `emails`, `phone`, `location`, and every record body |
| Summary handling | Records whose `sensitivity` maps to `summary` handling show their `summary` only (it is already written without sensitive detail) and no `facts` |

## Rendering notes
- Default view: Current, all types, newest `updated` first. Sort options: Recently updated, Name (A–Z), Type.
- The page shows the first 100 matches and a "Show 100 more" button; search and filters run over every record on the page.
- Search matches title, summary, aliases, record ID, facts, and link titles, case-insensitive, all words must match.
- The type filter is a drop-down with counts; Current / Closed / All is a segmented control. Both remember the last choice.
- Text limits: `summary` 240 characters, each fact 60, `title` 140.
- Caps and truncation, in this order until the page fits the budget: (1) shorten `summary` to 120 characters; (2) drop `links` beyond 3; (3) drop closed records, oldest `updated` first; (4) drop current sources, oldest first; (5) drop other current records, oldest first. Record each dropped record under `meta.truncated.records`. The page shows "N more not shown here. Ask Nova in chat to see them."
- When `summary.restricted` > 0, a muted line under the filters reads "N records are hidden by your data rules. Ask Nova in chat about them." When `summary.archived` > 0, a second line reads "N archived records aren't shown. Ask Nova in chat to see them."
