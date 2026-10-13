---
type: connector-hint
connector: google-calendar
categories: [calendar]
checked: "2026-10: Anthropic help center (Google Workspace connectors); tool names not verified"
---
# Hint: Google Calendar

Tool names vary; always verify from the live tool list. Guide: `system/connectors/calendar.md`.

## Likely categories
`calendar`. Google Meet transcripts, if available, usually arrive as Google Docs in Drive (files) or through a notetaker (meetings), not through this connector.

## Typical operations
| Operation | What to look for |
|---|---|
| `list_range` | List events with time-min / time-max (and an option to expand recurring events into single occurrences) |
| `read_item` | Get event |
| `create_event` | Create / update event |
| `respond` | RSVP, accept/decline/tentative |
| `delete` | Delete event |
| (read) | List calendars, find free time / free-busy |

## Cursor ideas
- Range cursor (`synced_through`) per the calendar guide; ask for single (expanded) occurrences so each meeting is one item.
- If the tool offers an "updated since" filter, use it to catch moved/cancelled events cheaply between full-window reads.

## Known quirks
- Event types: skip **focus time**, **out of office** (keep as context only), and **working location** entries.
- All-day events have dates, not times (`start.date` instead of `start.dateTime`): set `all_day: true`; treat them as deadlines/milestones only if the title says so.
- The user's own attendee entry (`self: true`) has `responseStatus`: `accepted` → accepted, `tentative` → tentative, `needsAction` → not_responded, `declined` → declined. If the user is the organizer (`organizer.self: true`), or the event has no attendees, use `organizer`.
- Shared calendars the user can see (team calendars, a manager's) appear in calendar lists: ingest only the user's primary calendar unless scope says otherwise.
- Descriptions often contain Meet links and dial-in PINs: never store PINs (N10).

## Risk-sensitive tools
- `send`: create or update events **with attendees** (Google can notify guests), RSVP tools, "add guests".
- `delete`: delete event, delete calendar.
- `share`: change calendar sharing / ACL.
- `write`: create event on the user's own calendar with no guests (holds, focus time).

## Fallback
*Settings → Import & export → Export* (.ics) into Atlas Drop, or tell Atlas in Morning Thoughts.
