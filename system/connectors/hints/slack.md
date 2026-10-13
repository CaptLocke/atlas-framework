---
type: connector-hint
connector: slack
categories: [messaging]
checked: "2026-10: general knowledge of Slack's API model; tool names not verified"
---
# Hint: Slack

Tool names vary; always verify from the live tool list. Guide: `system/connectors/messaging.md`.

## Likely categories
`messaging`. Huddle notes or canvases may appear as documents (`files`) on some versions.

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | Channel/conversation history with an "oldest"-style timestamp, or search with `after:` / `on:` dates |
| `read_thread` | Thread replies by parent timestamp |
| `search` | Search messages (Slack modifiers such as `in:#channel`, `from:@user`, `after:YYYY-MM-DD`, `to:me`) |
| `post` | Send message, reply in thread, schedule message |
| `delete` | Delete message |
| (read) | List channels, user profile lookup |

## Cursor ideas
- Slack message timestamps (`1697040000.000100` style) are both an ID and a time: store as `last_id` and convert for `last_seen`.
- Per-channel cursors (`messaging:slack:<channel>`) work best when history is fetched per channel; a single search-based cursor works when the tool only offers search.
- Threads: track parent timestamps of active threads and re-read them when replies arrive.

## Known quirks
- Users appear as IDs: look up profiles to get names and emails for dedupe; add the handle to the person's `aliases`.
- The connector sees only channels the user can see; private channels only if they are a member.
- DMs and mentions are the highest-signal items; big public channels are mostly noise.
- Rate limits are common on history calls: page patiently, and process newest first on first run.
- Shared (Slack Connect) channels contain another company's messages: out of scope unless listed.

## Risk-sensitive tools
- `send`: send/post, reply, schedule message, add reaction, update/edit message, set status, create or post a canvas in a channel, invite to channel.
- `delete`: delete message, delete scheduled message.
- `share`: change channel membership or sharing, share files externally.

## Fallback
*More actions → Share message / Copy link* and email it to the connected inbox with **[atlas]**; or paste into chat.
