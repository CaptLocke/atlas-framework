# Connector items: per-category handling

Used by the `ingest` job through `nova-capture` §4. Operation names come from `system/connectors/README.md`; the actual tool for each operation is looked up in `user/settings/connectors.yaml`. The category guide `system/connectors/<category>.md` is authoritative for noise filters and cursor strategy; this file says what to **file** from each category.

General rules for every category:
- Query from the cursor; respect `sources.yaml` scopes; apply exclusions in the query and again on results.
- One Source per thread/meeting/document; update the existing Source when a thread grows (append Updates, extend `participants`).
- Process oldest to newest so cursors can advance safely.
- Page through results; if the run is long, commit in batches and advance the cursor after each committed batch.
- An item that fails to read or file: leave the cursor before it, note it in the run report's Errors, continue with other categories.

| Category | Read with | File | Usually skip |
|---|---|---|---|
| **mail** | `list_recent`, `read_item`; `list_sent` for evidence | Source per thread (`kind: email`, `origin_uri` = permalink). People (senders/recipients in substantive threads), organizations (by domain), commitments (explicit promises either way), decisions, questions asked of the user, risks raised, event changes (reschedules), attachments as pointers (name, type) | Newsletters, notifications, receipts, automated senders, calendar auto-mails, CC-only chatter with nothing new |
| **mail (sent)** | `list_sent` | Evidence: closes `i_owe` commitments (promised file sent, reply given); creates `i_owe` commitments the user made in writing; updates `last_contact`; collects voice samples for `nova-write` learning (no records) | Auto-replies |
| **calendar** | `list_range` (cursor `synced_through`; look ahead 14 days) | Event records for meaningful meetings (external attendees, 1:1s, decision forums, anything that will have a transcript) and real deadlines; update reschedules/cancellations (`status: cancelled`, Updates line); `all_day` and the user's `response` refreshed each sync; attendees resolved to people | Holds, focus blocks, personal series, declined events, all-hands with no role for the user |
| **meetings** | `list_recent`, `read_transcript` (or `read_summary` when data rules say `summary`) | Source (`kind: meeting`) linked to the event (`status: held`, `outcomes`); decisions with deciders and rationale; commitments for each explicit "I'll…/we'll…/can you… by…" with the right direction; questions left open; risks raised; people present | Small talk; vendor auto-summaries that duplicate the transcript (use one, not both) |
| **messaging** | `list_recent`, `read_thread` for allowed channels/DMs | Source per thread (`kind: message`); same extraction as mail; prefer threads where the user is mentioned, participates, or that are on tracked projects | Joins/leaves, emoji-only replies, bot posts, social channels, excluded channels |
| **files** (Nova Drop) | `list_folder`, `read_file`, then `move` | See `files.md` | Files already in `Processed` |
| **crm** | `list_recent`, `read_item` | Organization and person updates (stage, owner, last activity), deal facts on the relevant project or user type (e.g. `deals` extension), commitments in notes | Field changes with no meaning (sync timestamps), records owned by others the user doesn't touch |
| **tasks** | `list_recent`, `read_item` | Map tasks assigned to/created by the user to commitments only when they are promises to or from a person; completed tasks are evidence for closing commitments | Personal to-dos with no counterparty (leave in the task tool) |
| **data** | — | Not ingested on a schedule. Queried on demand by skills and user jobs; results that matter are filed as `kind: data` sources | — |
| **web** | — | Not ingested. Research results cited in chat are filed as `kind: web` sources only when they inform a record | — |

## Commitment wording cues
- `i_owe`: the user says "I'll", "I will", "let me get you", "I'll have it by", agrees to a request with a date ("Sure, Thursday works").
- `waiting_on`: another person says "I'll send", "we'll get back to you by", or agrees to the user's request.
- A request without agreement is not a commitment; it may be a question or nothing.
- "We" commitments: owner is whoever is clearly responsible; if unclear, make it a `questions.md` entry (kind `commitment`).

## People and organizations from connectors
- Create a person only for a meaningful context (substantive sender, attendee, named in a decision or commitment). Never for mailing lists, no-reply senders, or signatures.
- Same email → same person; add new addresses to `emails` and `aliases`.
- Organization by email domain, except personal domains (gmail.com, outlook.com…).

## Cursor examples
```yaml
mail:outlook: { last_seen: "2026-10-12T20:07:00-07:00", last_id: "AAMk…" }
calendar:google-calendar: { synced_through: "2026-10-26" }
meetings:zoom: { last_seen: "2026-10-12T17:30:00-07:00" }
files:google-drive:drop: { last_seen: "2026-10-12T20:07:00-07:00" }
```
