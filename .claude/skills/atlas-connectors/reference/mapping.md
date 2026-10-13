---
type: skill-reference
skill: atlas-connectors
---
# Connector mapping: detail

## Discover
- Tool names appear as `mcp__<server>__<tool>`. The `<server>` part identifies the connector; record it as `mcp_prefix: mcp__<server>__` so hooks can match calls. If chats and routines show different prefixes for the same connector, record the chat one and note the routine one in the run report; the health check flags the mismatch.
- `connector:` is the human name the user sees in Claude's connector list (e.g. "Gmail", "Google Calendar", "Slack"). Use lowercase-hyphen form in YAML (`google-calendar`) consistently with `cursors.yaml` keys (`mail:gmail`).
- Ignore tools that are part of Atlas's own platform (repo, artifacts, routines) and the session's built-in tools; map only the user's connectors.

## Classify (signals, strongest first)
1. Tool set: list/read message + draft/send → `mail`; events in a range → `calendar`; recordings/transcripts → `meetings`; channels/threads/posts → `messaging`; folders/files/upload → `files`; accounts/contacts/deals/opportunities → `crm`; tasks/issues/tickets assigned → `tasks`; SQL/query/datasets/tables → `data`; search the web/fetch a URL → `web`.
2. Server name and description.
3. A hint in `system/connectors/hints/` (speeds things up, never required).
A connector covers a category for ingestion only if every † operation for it maps to a tool.

## Operations
Map each operation in `system/connectors/README.md` to one tool. Record parameter notes jobs need:
```yaml
mail.list_recent: { tool: search_threads, since_param: "query 'after:<epoch>'", page_param: pageToken }
calendar.list_range: { tool: list_events, range_params: [timeMin, timeMax] }
files.list_folder: { tool: list_files, query: "'<folder_id>' in parents" }
```
If two tools could serve an operation, prefer the one that is read-only, returns IDs and timestamps, and supports a "since" filter. If none supports "since", note `since_param: null` and the cursor strategy from the category guide (e.g., newest-first with `last_id`).

## Safe probes
- Only tools tagged `read`. Smallest request: `limit/max_results/page_size = 1`, or a one-day calendar range.
- Learn: required parameters and their names; the timestamp field usable as a cursor; ID shape (`id_format`, e.g. "opaque string", "numeric", "URL"); a permalink pattern (`link_format` with `{id}`); page size and any rate notes (`limits`).
- Don't probe excluded sources. Don't save the returned content anywhere, including run reports.
- If a probe fails with an auth error: stop mapping that connector, tell the user to reconnect it (Settings → Connectors → reconnect), and record a known issue.

## Risk tags
Apply `system/connectors/README.md` rules to every exposed tool:
| Pattern in name or clear behavior | Tag |
|---|---|
| send, reply, forward, post, publish, invite, respond | `send` |
| share, permission, grant, (invite to a file/space) | `share` |
| delete, trash, remove, purge, archive_permanently | `delete` |
| pay, purchase, charge, sign, password, credential, token, 2fa, mfa | `security` |
| create, update, edit, move, label, set | `write` |
| draft | `draft` |
| clearly read-only (list, get, search, read, fetch, query with no side effects) | `read` |
Read the description too: `update_event` that notifies attendees → `send`; `create_event` with attendees → `send` (the README notes this). Multi-purpose tools take the riskiest applicable tag. Unsure → riskier.

## Fingerprint
`tool_fingerprint` = first 12 hex characters of SHA-256 over the connector's tool list, sorted by tool name, one line per tool: `<tool name>|<comma-separated sorted parameter names>`. Example (Python, run in the session):
```python
import hashlib
lines = sorted(f"{t['name']}|{','.join(sorted(t['params']))}" for t in tools)
fp = hashlib.sha256("\n".join(lines).encode()).hexdigest()[:12]
```
A different fingerprint means tools were added, removed, or changed: re-map that connector (steps 2–6) and highlight any newly risky tools to the user.

## Routine availability
- New connectors start `available_in_routines: unknown`.
- Evidence: a run report's "Connector health" section listing the connector's tools as used successfully (→ `true`) or unavailable (→ `false`). Routines can't write `connectors.yaml`, so the change is made in the next chat; mention it in one line with the other connector news and include it in the same confirmation ("Gmail works in your nightly runs; I'll note that."). One approval record covers the single file write.
- `false` for a category the jobs need → set that category's fallback in `sources.yaml` for routine use and tell the user (e.g., the evening run can't read Teams; the morning chat catch-up will).

## Removal
When a connector disappears: remove its entry, drop its `sources.yaml: ingest` lines, add the fallback for its categories, keep its cursors in `cursors.yaml` (harmless; reused if it returns), and check `atlas.yaml` folders and routine connector lists. Tell the user what Atlas can no longer see.

## Example entry (fictional)
```yaml
- connector: gmail
  mcp_prefix: mcp__gmail__
  categories: [mail]
  operations:
    mail.list_recent: { tool: search_threads, since_param: "q=after:<epoch>", page_param: pageToken }
    mail.read_item: { tool: get_thread }
    mail.search: { tool: search_threads }
    mail.list_sent: { tool: search_threads, query: "in:sent" }
    mail.create_draft: { tool: create_draft }
    mail.update_draft: { tool: update_draft }
    mail.send: { tool: send_message }
    mail.label: { tool: label_thread }
    mail.delete: { tool: trash_thread }
  tool_risk:
    search_threads: read
    get_thread: read
    get_message: read
    list_labels: read
    create_draft: draft
    update_draft: draft
    send_message: send
    reply: send
    forward: send
    label_thread: write
    create_label: write
    trash_thread: delete
    delete_draft: delete
  id_format: "opaque string"
  link_format: "https://mail.google.com/mail/u/0/#all/{id}"
  limits: "up to 50 threads per page"
  available_in_routines: unknown
  mapped_on: 2026-10-12
  tool_fingerprint: 7c41d09a2be3
```
