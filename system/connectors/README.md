---
type: connector-spec
version: 1.0.0
---
# Connectors: categories and operations

Atlas never hard-codes a vendor. `atlas-connectors` maps each connected tool to one or more **categories** and records which tool performs each **operation** (`user/settings/connectors.yaml`, format in `system/schemas/settings.md`). Jobs call operations ("the user's `mail.list_recent`"), then look up the connector and tool.

Category guides (`<category>.md`) say what to ingest, how to filter noise, how to set cursors, and the fallback when no connector exists. `hints/` holds optional notes for common connectors to speed mapping; mapping must work without them.

## Operation vocabulary
Operations marked † are required for a connector to count as covering the category for ingestion. Risk tags are the default classification of the tool that performs the operation.

| Category | Operation | Purpose | Risk |
|---|---|---|---|
| **mail** | `list_recent`† | Messages since a time/ID (cursor) | read |
| | `read_item`† | Full message/thread | read |
| | `search` | Query messages | read |
| | `list_sent` | Sent messages since a time (voice learning, commitment evidence) | read |
| | `list_drafts` | Existing drafts (avoid duplicates) | read |
| | `create_draft` | Draft a message/reply | draft |
| | `update_draft` | Change a draft | draft |
| | `send` | Send/reply/forward | send |
| | `label` | Label/move a message | write |
| | `delete` | Trash/delete | delete |
| **calendar** | `list_range`† | Events in a date range | read |
| | `read_item` | Event details | read |
| | `create_event` | Create an event (own calendar) | write (with attendees: send) |
| | `update_event` | Change an event | write (with attendees: send) |
| | `respond` | Accept/decline/propose | send |
| | `delete` | Remove an event | delete |
| **meetings** | `list_recent`† | Recordings/transcripts since a time | read |
| | `read_transcript`† | Transcript text | read |
| | `read_summary` | Vendor summary/action items | read |
| **messaging** | `list_recent`† | Messages since a time in allowed channels/DMs | read |
| | `read_thread` | Thread content | read |
| | `search` | Query messages | read |
| | `post` | Post/reply | send |
| | `delete` | Delete message | delete |
| **files** | `list_folder`† | Files in a folder (drop folder) | read |
| | `read_file`† | File content/export | read |
| | `search` | Query files | read |
| | `create_folder` | Create folder (setup: Atlas Drop, deliverables) | write |
| | `upload` | Create/upload file (deliverables) | write |
| | `move` | Move file (drop → Processed) | write |
| | `edit` | Change an existing document | write |
| | `share` | Share or change permissions | share |
| | `delete` | Delete/trash | delete |
| **crm** | `list_recent`† | Records changed since a time | read |
| | `read_item` | Account/contact/deal | read |
| | `search` | Query records | read |
| | `update_item` | Change fields/notes | write |
| | `delete` | Delete record | delete |
| **tasks** | `list_recent`† | Tasks changed since a time (assigned to/created by user) | read |
| | `read_item` | Task detail | read |
| | `create_item` | Create task | write |
| | `update_item` | Update/complete task | write |
| | `delete` | Delete task | delete |
| **data** | `query`† | Run a read-only query | read |
| | `list_tables` | Discover datasets | read |
| **web** | `search`† | Web search | read |
| | `fetch` | Read a page | read |
| **other** | (recorded as found) | | classify each tool |

**Risk classification rules for unknown tools:** names containing `send|reply|forward|post|publish|invite|respond` → `send`; `share|permission|grant|invite` → `share`; `delete|trash|remove|purge|archive_permanently` → `delete`; `pay|purchase|charge|sign|password|credential|token|2fa|mfa` → `security`; `create|update|edit|move|label|set` → `write`; `draft` → `draft`; otherwise `read` only if it clearly reads. When ambiguous, choose the riskier tag. A general "run SQL" tool that can modify data is tagged `write` even when mapped to `data.query` (Atlas sends read-only SELECT statements only). Hooks apply the name patterns regardless of tags.

## Mapping procedure (summary; full procedure in `atlas-connectors`)
1. List connectors and their tools available in this session.
2. Classify each connector into categories; assign operations from tool definitions.
3. Probe with safe read-only calls (list 1 item) to confirm parameters, cursor field, ID and link format, page size.
4. Tag every tool's risk.
5. Record in `connectors.yaml` with `tool_fingerprint` and `available_in_routines: unknown` until a routine run confirms it.
6. Update `sources.yaml` (what to ingest) and fallbacks for uncovered categories.
