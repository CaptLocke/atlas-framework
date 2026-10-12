---
type: schema
name: organization
folder: user/knowledge/organizations/
---
# Schema: organization

## What it is
Companies, teams, agencies, institutions, including the user's employer.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `domain` | text | no | Primary web/email domain; used for dedupe. |
| `kind` | enum | no | employer, customer, prospect, vendor, partner, regulator, investor, team, other |
| `relationship_status` | text | no | Free text, e.g. `renewal in Q1`. |
| `industry` | text | no |  |

## Status vocabulary
active, inactive

## Links
Typically links to: people, projects, topics, risks.

## Capture guidance
Create for organizations the user actually deals with. Internal teams are `kind: team` linked to the employer.
