---
type: connector-hint
connector: microsoft-teams (Microsoft 365)
categories: [messaging, meetings, calendar]
checked: "2026-10: Claude docs, Microsoft 365 connector page; tool names not verified"
---
# Hint: Microsoft Teams

Tool names vary; always verify from the live tool list. Guides: `system/connectors/messaging.md`, `meetings.md`, `calendar.md`.

## Likely categories
- **messaging**: chats and channel messages.
- **meetings**: meeting information, summaries, and attendance (transcript text may or may not be exposed; probe).
- **calendar**: Teams meetings live in the Outlook calendar; prefer the Outlook calendar mapping for `calendar.list_range` and use Teams only for meeting content.
Usually part of the Microsoft 365 connector (`outlook.md`); map as one connector.

## Typical operations
| Operation | What to look for |
|---|---|
| `messaging.list_recent` | List chats / channel messages with a modified or created time |
| `messaging.read_thread` | Get replies to a channel message |
| `messaging.search` | Search Teams messages |
| `messaging.post` | Send chat message, send channel message, create chat |
| `meetings.list_recent` | List recent online meetings / meeting recaps |
| `meetings.read_summary` / `read_transcript` | Meeting summary, notes, attendance, transcript (if available) |

## Cursor ideas
- Messages: last-modified time per chat or channel (`messaging:<connector>:<chat-or-channel>`).
- Meetings: meeting end time; recaps and transcripts can lag, so hold the cursor per the meetings guide.

## Known quirks
- **Message sending is often blocked by the organization** (per-tool restrictions); the connector may be read-only for Teams. Atlas never needs to post anyway.
- Listing teams and people may require extra tenant permissions; a permission error means "ask the admin", not "re-map".
- Channel messages and chat messages are different objects; replies hang off a parent.
- Message bodies are HTML: strip markup before summarizing.
- Meeting chat often contains the agenda and links: attach it to the meeting's Source.

## Risk-sensitive tools
- `send`: send chat/channel message, reply, create chat (it messages people), react.
- `delete`: delete message.
- `share`: add members, change team/channel membership.

## Fallback
Messaging: copy link or text into chat, or forward to email. Meetings: *Recap → Download transcript* into Atlas Drop.
