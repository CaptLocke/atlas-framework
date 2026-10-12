---
type: connector-hint
connector: salesforce
categories: [crm]
checked: "2026-10: general knowledge of Salesforce data model and SOQL; tool names not verified"
---
# Hint: Salesforce

Tool names vary; always verify from the live tool list. Guide: `system/connectors/crm.md`.

## Likely categories
`crm`. Some Salesforce connectors also expose reports/analytics (`data`-like); keep them under `crm` reads unless the user wants metrics jobs.

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | A query tool accepting SOQL, filtered on last-modified date |
| `read_item` | Get record by ID (Account, Contact, Opportunity, Case, Task, Event) |
| `search` | Text search (SOSL-style) or query |
| `update_item` | Update record, create record, log activity/note |
| `delete` | Delete record |
| (read) | Describe object (fields, picklists), list reports, run report |

## Cursor ideas
- SOQL filter such as `LastModifiedDate > <ISO-8601 datetime>` (or `SystemModstamp`), ordered ascending, with the user's ownership or team filter (e.g. `OwnerId = <user's ID>`, or account team membership). Record the exact form in `connectors.yaml`.
- One cursor per object (`crm:salesforce:opportunity`, `crm:salesforce:account`) keeps queries simple.

## Known quirks
- Orgs are heavily customized: custom objects and fields end in `__c`. Describe objects at mapping to learn the real stage, next-step, and close-date fields.
- Record IDs are 15 or 18 characters; links look like `https://<instance>.lightning.force.com/<Id>` (verify at probe).
- "Next Step" is often free text without an owner or date: a commitment only when the text makes owner and timing clear.
- Integration users and automations generate many modifications; skip changes made by known integration users.
- API limits per org: keep queries narrow and paged.

## Risk-sensitive tools
- `write` (→ `shared_records_update`, propose): create/update record, log call, add note.
- `delete`: delete record, mass delete, merge records (destructive bulk overwrite).
- `send`: send email, enroll in cadence/sequence, post to Chatter, @mentions in notes.
- `share`: change owner, sharing rules, record access.
- `security`: execute anonymous code, user/permission administration, approve/submit approval processes.

## Fallback
"Run your *My Open Opportunities* report → *Export* (CSV) weekly into your **Nova Drop** folder."
