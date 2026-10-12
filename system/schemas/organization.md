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
| `industry` | text | no | Industry and sub-industry, e.g. `Financial services · payments`. |
| `website` | text | no | Main website URL. |
| `size` | text | no | Free text, e.g. `about 2,000 employees`. |
| `headquarters` | text | no | City and country. |

## Status vocabulary
active, inactive

## Links
Typically links to: people, projects, topics, risks.

## Employer
The user's employer (`kind: employer`) is the company profile Nova works from. Built at setup (steps 6–8: website, LinkedIn, uploads, research, then confirmation) and refreshed at the quarterly role refresh. Frontmatter: `domain` (primary email domain), `industry`, `website`, `size`, `headquarters`. The full list of email domains and the fiscal year live in `user/settings/nova.yaml: company`. Body sections, in this order, each line tagged with provenance and citations like profile statements (`system/schemas/profile.md`):
- `## What they do`: products or services, and the customers or segments they serve.
- `## Business model`: how the company makes money.
- `## Locations`: headquarters and main offices or markets.
- `## Competitors`
- `## Structure and teams`: where the user's team sits; links to `kind: team` organizations.
- `## Terms and acronyms`: internal vocabulary, learned over time.
- `## Recent news`: dated lines with source links (last 12 months; older lines move to Updates).
Unconfirmed researched lines stay out of the record and live as proposals in `user/inbox/questions.md`.

## Capture guidance
Create for organizations the user actually deals with. Internal teams are `kind: team` linked to the employer.
