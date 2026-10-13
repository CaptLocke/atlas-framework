---
type: schema
name: person
folder: user/knowledge/people/
---
# Schema: person

## What it is
Anyone the user works with or about, including the user themself (`relationship: self`).

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `emails` | list | no | All known addresses; used for dedupe. |
| `org` | ID | no | `[[organizations/...]]` |
| `role` | text | no | Job title or function. |
| `relationship` | enum | no | self, manager, report, peer, stakeholder, board, customer, prospect, vendor, partner, external, other. Definitions and how to choose: §Relationships. |
| `last_contact` | date | no | Most recent interaction seen in any source. |
| `cadence` | text | no | Expected contact rhythm, e.g. `weekly 1:1`, `monthly`. |
| `phone` | text | no | Only if the user's data rules allow PII. |
| `location` | text | no | City/time zone if useful. |
| `notes_private` | text | no | Never shown on dashboards. |

## Relationships
One value per person: their relationship **to the user**, not their importance. "Internal" means their email domain is in `atlas.yaml: company.email_domains`, or they are known to work at the user's employer.

| Value | Who | Examples |
|---|---|---|
| `self` | The user. Exactly one active record. | — |
| `manager` | The person the user reports to directly (solid line). Usually one at a time. | The user's boss |
| `report` | Someone who reports directly to the user. | Team members; contractors the user manages day to day |
| `peer` | An internal colleague the user works alongside day to day, with no reporting line either way. | Teammates; the user's regular partner in legal, design, or finance |
| `stakeholder` | An internal person with a stake in or authority over the user's work who is not a day-to-day collaborator. | The manager's manager; executives; sponsors and approvers; people who receive the user's status updates; a dotted-line manager; skip-level reports |
| `board` | A member of the employer's board of directors or advisory board, including board observers, whatever their email domain. | Directors, the board chair, investor board members, formal company advisors |
| `customer` | Someone at an organization that buys from the employer (`kind: customer`). | Buyers, champions, end users, their procurement or legal teams |
| `prospect` | Someone at an organization the employer is trying to sell to that isn't a customer yet (`kind: prospect`). | Leads, evaluators in a trial or pilot, buying committee members before signature |
| `vendor` | Someone at a company the employer buys from (`kind: vendor`). | Suppliers, agencies, consultants, account reps for tools the company pays for |
| `partner` | Someone at an organization in a two-way business relationship with the employer (`kind: partner`). | Resellers, integration and technology partners, alliance and co-marketing partners |
| `external` | Anyone else outside the company with a work reason to be in Atlas. | Investors who aren't on the board, regulators, auditors, recruiters, journalists, industry contacts |
| `other` | Nothing above fits yet. Setting it adds a `relationship` question to `user/inbox/questions.md`. | — |

**How to choose (first match wins):**
1. It's the user → `self`.
2. A direct reporting line with the user → `manager` or `report`.
3. Sits on the employer's board (or advisory board) → `board`.
4. Internal → `peer` if they work with the user regularly, otherwise `stakeholder`.
5. External → by their organization's `kind`: customer → `customer`, prospect → `prospect`, vendor → `vendor`, partner → `partner`; investor, regulator, or anything else → `external`.
6. Unclear → `other`, plus a `relationship` question.

**Keeping it current:**
- A prospect that signs becomes a customer: update the organization's `kind` and its people's `relationship` together, with an Updates line on each.
- A reorg can turn a peer into a manager or a report into a peer. Propose the change when sources show it (an org chart, "I now report to…", a new 1:1 series); the user confirms.
- A value the user states (`provenance: stated` on the change, or an Updates line quoting them) is never re-guessed from later sources. Only the user changes it.
- Someone who changes companies keeps their record: update `org` and re-run the order above. If they've left the user's world entirely, set `status: inactive`.

## Status vocabulary
active, inactive (left the org, no longer relevant)

## Links
Typically links to: organizations (employer, team), projects, commitments (either direction), events attended, topics.

## Capture guidance
Create when a person appears in a meaningful context (sender of a substantive email, meeting attendee, named in a decision). Do not create records for automated senders, mailing lists, or one-off signatures. Merge on matching email or clear alias. The `new key person` trigger fires on creation when the person appears repeatedly or in an important context.
