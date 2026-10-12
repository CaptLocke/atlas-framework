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
| `relationship` | enum | no | self, manager, report, peer, stakeholder, customer, vendor, partner, external, other |
| `last_contact` | date | no | Most recent interaction seen in any source. |
| `cadence` | text | no | Expected contact rhythm, e.g. `weekly 1:1`, `monthly`. |
| `phone` | text | no | Only if the user's data rules allow PII. |
| `location` | text | no | City/time zone if useful. |
| `notes_private` | text | no | Never shown on dashboards. |

## Status vocabulary
active, inactive (left the org, no longer relevant)

## Links
Typically links to: organizations (employer, team), projects, commitments (either direction), events attended, topics.

## Capture guidance
Create when a person appears in a meaningful context (sender of a substantive email, meeting attendee, named in a decision). Do not create records for automated senders, mailing lists, or one-off signatures. Merge on matching email or clear alias. The `new key person` trigger fires on creation when the person appears repeatedly or in an important context.
