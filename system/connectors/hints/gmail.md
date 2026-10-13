---
type: connector-hint
connector: gmail
categories: [mail]
checked: "2026-10: Anthropic help center (Google Workspace connectors); one live Gmail MCP tool list observed"
---
# Hint: Gmail

Tool names vary; always verify from the live tool list. Guide: `system/connectors/mail.md`.

## Likely categories
`mail` only. Google Calendar and Google Drive are separate connectors (see their hints).

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | Usually no dedicated "list since" tool: use the thread/message search tool with a Gmail query such as `after:<unix-seconds>` (or `after:YYYY/MM/DD`) |
| `read_item` | Get thread / get message |
| `search` | Search threads or messages (Gmail search syntax) |
| `list_sent` | Same search tool with `in:sent after:…` |
| `create_draft` / `update_draft` | Create / update draft (may accept a thread ID to draft a reply) |
| `send` | Send message, reply, forward (often three separate tools) |
| `label` | Label/unlabel thread or message, mark spam |
| `delete` | Trash thread/message, delete draft, delete label |

Observed once (2026-10), for orientation only: tools named like `search_threads`, `get_thread`, `get_message`, `create_draft`, `update_draft`, `list_drafts`, `send_message`, `reply`, `forward`, `label_thread`, `trash_thread`, `untrash_thread`, `mark_thread_spam`, `create_label`, `delete_label`.

## Cursor ideas
- `after:` with Unix seconds gives minute-level precision; `YYYY/MM/DD` is day-level (then dedupe by message ID).
- Cheap noise filter in the query: `-category:promotions -category:social -category:forums`; keep `category:updates` but filter further, since it mixes notifications with real mail.
- Exclusions from `data-rules.yaml` translate directly to Gmail syntax (`-from:`, `-label:`).

## Known quirks
- Attachment **content** may not be readable (help center, 2026-10): note attachment names; ask the user to drop important attachments into Atlas Drop.
- Threads are the natural Source unit; message IDs differ from thread IDs.
- Personal Gmail accounts and Workspace accounts look the same; ask the user which inbox is work.

## Risk-sensitive tools
- `send`: send, reply, forward, any draft tool with a "send now" option.
- `delete`: trash, delete draft, delete label, and **untrash** (name contains "trash"; hooks treat it as delete).
- `write`: label, mark spam/not spam, create/update label, "sensitive" labels.

## Fallback
See `system/connectors/mail.md` → forward, drop (Print → Save as PDF), or manual paste.
