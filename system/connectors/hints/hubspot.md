---
type: connector-hint
connector: hubspot
categories: [crm]
checked: "2026-10: general knowledge of HubSpot CRM objects; tool names not verified"
---
# Hint: HubSpot

Tool names vary; always verify from the live tool list. Guide: `system/connectors/crm.md`.

## Likely categories
`crm`. Marketing and sales-email features are out of scope for ingestion.

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | Search objects (contacts, companies, deals, tickets) with a filter on last-modified date, sorted ascending |
| `read_item` | Get object by ID, with associations (deal ↔ company ↔ contacts) |
| `search` | Search objects by property or text |
| `update_item` | Create/update object, add note/engagement, associate objects |
| `delete` | Archive/delete object |
| (read) | List owners, pipelines and stages, properties |

## Cursor ideas
- Filter on the object's last-modified property (often `hs_lastmodifieddate`; contacts may use `lastmodifieddate`) with greater-than-or-equal to `last_seen`; page with the returned cursor/after token.
- Restrict to the user's records via the owner property (look up the user's owner ID at mapping).

## Known quirks
- Deal stages are pipeline-specific IDs: fetch pipelines at mapping to translate stage IDs to names.
- Associations are separate lookups; fetch them for deals to link the organization and people.
- Engagement properties (email opens, page views, lead scores) change constantly: ignore them as noise.
- Search results may be capped per query; narrow by date for large accounts.

## Risk-sensitive tools
- `write` (→ `shared_records_update`, propose): create/update contacts, companies, deals, tickets, notes, associations.
- `delete`: archive/delete objects, merge records, batch archive.
- `send`: send email, enroll in sequence or workflow, log-and-send, chat/conversation replies, forms that notify.
- `share`: change owner, team assignment.

## Fallback
"Export your deals view (*Export* → CSV) weekly into your **Atlas Drop** folder, or forward deal emails with **[atlas]** in the subject."
