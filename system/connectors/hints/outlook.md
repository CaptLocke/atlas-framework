---
type: connector-hint
connector: outlook (Microsoft 365)
categories: [mail, calendar]
checked: "2026-10: Claude docs, Microsoft 365 connector page; tool names not verified"
---
# Hint: Outlook (Microsoft 365 mail and calendar)

Tool names vary; always verify from the live tool list. Guides: `system/connectors/mail.md`, `calendar.md`.

## Likely categories
The Microsoft 365 connector is usually **one connector spanning several categories**: Outlook mail → `mail`, Outlook calendar → `calendar`, OneDrive/SharePoint → `files` (`onedrive-sharepoint.md`), Teams chat → `messaging` and Teams meetings → `meetings` (`microsoft-teams.md`). Map it once, into every category it covers. A standalone "Outlook" connector may cover only mail and calendar.

## Typical operations
| Operation | What to look for |
|---|---|
| `mail.list_recent` / `search` | Search or list messages with a received-date filter |
| `mail.read_item` | Get message / get conversation |
| `mail.create_draft` | Create draft / create reply draft |
| `mail.send` | Send mail, reply, forward |
| `mail.label` | Categories, move to folder, flags, mail rules |
| `calendar.list_range` | List events / calendar view with start and end |
| `calendar.create_event`, `respond` | Create/update event, find meeting times, accept/decline |

## Cursor ideas
- Mail: received date/time (Graph-style `receivedDateTime`) or a KQL-like `received>=` in search; record whichever the live tool accepts.
- Calendar: use a calendar-view style range (start/end) so recurring meetings are expanded into occurrences.

## Known quirks
- Requires a **work or school** account; personal outlook.com/hotmail accounts may not be supported. A tenant administrator must consent.
- **Write actions may be turned off** by the organization: the connector can be read-only. Record only the tools that exist; email drafts then fall back to text shown in chat or the brief.
- Drafts created through the connector may not support attachments: link to the file in the deliverables folder instead (the user's own private link; do not change sharing).
- Search results can be partial for large mailboxes; narrow by date range.
- Mail rules, automatic replies, and mailbox settings tools exist on some versions.
- Calendar: `isAllDay` → `all_day`. The user's RSVP is `responseStatus.response`: `organizer` → organizer, `accepted` → accepted, `tentativelyAccepted` → tentative, `notResponded` or `none` → not_responded (but `none` on an event with no attendees → organizer), `declined` → declined.

## Risk-sensitive tools
- `send`: send, reply, forward, **automatic replies** (they send to others), create/update event **with attendees**, respond to invitation, find-and-book meeting tools.
- `delete`: delete message/event, empty folders.
- `security`: mailbox permissions, delegate access, forwarding rules to external addresses (a classic exfiltration path).
- `write`: categories, flags, move, mail rules (internal only).

## Fallback
Mail: forward from another inbox, Save as PDF to Atlas Drop, or paste. Calendar: *File → Save Calendar* (.ics) to Atlas Drop, or Morning Thoughts.
