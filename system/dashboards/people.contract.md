---
type: dashboard-contract
name: people
template: people.html
republished_by: [weekly-review]
size_budget_kb: 250
stale_after_hours: 192
---
# Dashboard: people

## Purpose
Key relationships: last contact, open items each way, who has gone quiet, and upcoming touchpoints, with a relationship insight where Atlas has one. Filters: Everyone / Gone quiet / Open items / Meeting soon, plus search by name or company.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "people", "schema_version": 1, "as_of": "2026-10-09", "…": "…" },
  "summary": { "quiet": 2, "i_owe": 4, "they_owe": 4 },
  "people": [
    { "id": "people/dana-ruiz", "title": "Dana Ruiz", "aliases": ["D. Ruiz"], "role": "Senior counsel",
      "org": { "id": "organizations/acme", "title": "Acme" }, "relationship": "stakeholder",
      "last_contact": "2026-09-30", "cadence": null,
      "quiet": true, "quiet_reason": "No reply in 9 days while she owes you the MSA review.",
      "i_owe": [],
      "they_owe": [ { "id": "commitments/dana-msa-review", "title": "Review the enterprise MSA", "due": "2026-10-07" } ],
      "next_touchpoint": { "id": "events/2026-10-15-enterprise-tier-review", "title": "Enterprise tier review",
                           "start": "2026-10-15T13:00:00-07:00" },
      "insight": null }
  ],
  "insights": [ { "id": "I-2026-10-09-01", "text": "…", "why": "…", "suggested_action": "…" } ]
}
```
Full example: `system/tests/dashboards/people.json`.

| Field | Notes |
|---|---|
| `aliases` | Only names and initials, used for search. **Never** email addresses or phone numbers. |
| `quiet` | `true` when the person is a key relationship and contact has lapsed: days since `last_contact` > 1.5 × the expected `cadence` interval, or > 30 days with no cadence while there are open items either way. |
| `quiet_reason` | One line explaining why, shown instead of `insight` when `quiet`. |

## Sources (file → field)
| Field | Source |
|---|---|
| `people[]` | `user/knowledge/people/*.md`, `status: active`, `relationship` not `self`: `id, title, role, org, relationship, last_contact, cadence`; `aliases` filtered to non-contact strings |
| `i_owe[]` | Open/slipped commitments with `direction: i_owe` and `counterparty` = the person |
| `they_owe[]` | Open/slipped commitments with `direction: waiting_on` and `owner` = the person |
| `next_touchpoint` | Earliest scheduled event in the next 14 days with the person in `attendees` |
| `insight`, `quiet`, `quiet_reason` | `weekly-review` ("people to reconnect with") and `user/inbox/insights.md` entries linking the person |
| `insights[]` | `user/inbox/insights.md`, status `new|seen`, about relationships (linking people), max 5 |
| `summary` | Counts over all included people and their open items |
| Excluded always | `notes_private`, `emails`, `phone`, `location` |

## Rendering notes
- **Record panel:** clicking a card opens it in the record panel (`system/dashboards/README.md` §Record panel). Every item may carry the panel data fields (`details`, `body`, `body_truncated`, `links`, `created`, `updated`; same section). Before the caps below drop any item, cut each `body` to 800 characters, then drop `body` from the oldest items first.
- Which people: everyone with an open item either way, a touchpoint in the next 14 days, `quiet: true`, or a relationship of manager, report, board, customer, prospect, stakeholder, or partner; then others by most recent `last_contact`.
- Sort: quiet first, then by relationship weight (manager, report, board, customer, stakeholder, prospect, partner, peer, vendor, external, other), then by number of open items, then `last_contact` (most recent first).
- Caps: 80 people, 5 items per direction per person, soonest due first (the rest are on the Work Board). `meta.truncated.people` counts people left out (lowest in the sort order go first).
- Text limits: `insight`, `quiet_reason` 240 characters.
