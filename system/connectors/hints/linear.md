---
type: connector-hint
connector: linear
categories: [tasks]
checked: "2026-10: general knowledge of Linear's model; tool names not verified"
---
# Hint: Linear

Tool names vary; always verify from the live tool list. Guide: `system/connectors/tasks.md`.

## Likely categories
`tasks`. Linear projects and initiatives map well to Nova `project` records; project updates carry health.

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | List issues assigned to me (or created by me) with an updated-after filter |
| `read_item` | Get issue (with comments, labels, project, cycle) |
| `create_item` / `update_item` | Create issue, update issue, change state |
| `delete` | Delete or archive issue |
| (read) | List projects, project updates, teams, cycles, users |

## Cursor ideas
- `updatedAt` greater than `last_seen`, ordered by update time; page with the returned cursor.
- First run: open issues assigned to the user (state type not completed/canceled).

## Known quirks
- Issue identifiers (`ATL-42`) are human-readable; use them in `aliases`.
- Workflow states vary by team; use the state *type* (backlog, unstarted, started, completed, canceled).
- Triage and backlog issues are not commitments until assigned and scheduled.
- Integrations (Git, Slack, support tools) add many automated updates; filter by human actors.
- Project updates include a health value (on track / at risk / off track) → project `health`.

## Risk-sensitive tools
- `send`: create comment, @mention, assign to others, subscribe others, post project update (visible to the team).
- `write` (→ `shared_records_update`, or `tasks_manage` for purely personal issues): create/update issue, change state, set labels.
- `delete`: delete issue, delete comment, **archive** (treat as delete; it removes items from views).
- `share`: team membership, workspace invites.

## Fallback
"Use *Export → CSV* on a filtered view weekly into your **Nova Drop** folder, or keep Linear email notifications on."
