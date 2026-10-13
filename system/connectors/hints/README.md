---
type: connector-hints-index
---
# Known-connector hints

Short notes on common connectors that help `atlas-connectors` map them faster: which categories they usually cover, what their tools tend to look like, how to set cursors, known quirks, and which tools to tag as risky.

## Hints are optional accelerators
- **Mapping must never depend on a hint.** The procedure in `system/connectors/README.md` and `atlas-connectors` (read the live tool list, classify, probe read-only, tag risk, record) works for any connector, with or without a hint.
- **The live tool list always wins.** Tool names, parameters, and capabilities vary by connector version, vendor, plan, and the user's organization settings. If a hint disagrees with what the session actually exposes, follow the session and note the difference in the run report or health check.
- **Hints never lower a risk tag.** Tag every tool from its live name and description using the rules in `system/connectors/README.md`. A hint may only point out tools that deserve a *riskier* tag than their name suggests.
- Tool names in hints are examples of what to look for, not facts, unless a line says it was observed (with date).
- Category guides (`system/connectors/<category>.md`) say what to ingest and how; hints only cover vendor specifics.

## Index
| Hint | Usual categories |
|---|---|
| `gmail.md` | mail |
| `outlook.md` (Microsoft 365) | mail, calendar (and files, messaging, meetings via the same connector) |
| `google-calendar.md` | calendar |
| `google-drive.md` | files |
| `onedrive-sharepoint.md` | files |
| `slack.md` | messaging |
| `microsoft-teams.md` | messaging, meetings, calendar |
| `zoom.md` | meetings (sometimes calendar, messaging) |
| `meeting-notetaker.md` | meetings (Fireflies, Otter, Granola, and similar) |
| `salesforce.md` | crm |
| `hubspot.md` | crm |
| `asana.md` | tasks |
| `jira.md` | tasks (Confluence: files) |
| `linear.md` | tasks |
| `notion.md` | files, tasks |
| `bigquery.md` | data |

## Hint format
Frontmatter `type: connector-hint`, `connector`, `categories`, `checked` (date and what was checked). Sections: likely categories, typical operations, cursor ideas, known quirks, risk-sensitive tools, fallback. Keep each under ~50 lines. Never include user data or credentials.
