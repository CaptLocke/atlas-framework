---
type: connector-hint
connector: jira (Atlassian)
categories: [tasks]
checked: "2026-10: general knowledge of Jira and JQL; tool names not verified"
---
# Hint: Jira

Tool names vary; always verify from the live tool list. Guide: `system/connectors/tasks.md`.

## Likely categories
`tasks`. Atlassian connectors often bundle **Confluence** too: map Confluence pages to `files` (search/read pages; creating pages is `docs_create`, editing is `docs_edit`).

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | Search issues with JQL |
| `read_item` | Get issue (fields, comments, links, transitions) |
| `create_item` / `update_item` | Create issue, edit fields, transition status |
| `delete` | Delete issue |
| (read) | List projects, boards, sprints; get user |

## Cursor ideas
- JQL such as `(assignee = currentUser() OR reporter = currentUser()) AND updated >= "<yyyy-MM-dd HH:mm>" ORDER BY updated ASC`. JQL times are in the Jira user's timezone and minute precision: overlap a few minutes and dedupe by issue key.
- First run: `assignee = currentUser() AND statusCategory != Done` for open work.

## Known quirks
- Issue keys (`ATLAS-123`) are stable, human-readable IDs: put them in `aliases` of the matching commitment.
- Status names vary by project workflow; use the status *category* (To Do / In Progress / Done) to decide open vs. done.
- Engineering projects generate heavy automated churn (CI links, sprint moves, bot comments): filter by human authors.
- Cloud site URL is needed for links (`https://<site>.atlassian.net/browse/<KEY>`); confirm at probe.
- Rich-text fields come in a document format; extract plain text.

## Risk-sensitive tools
- `send`: add comment, @mention, assign issue to someone else, add watcher, transition that triggers notifications (most do).
- `write` (→ `shared_records_update`, propose): create/edit issue, transition status, log work, link issues.
- `delete`: delete issue, delete comment, bulk change.
- `share`: change permissions, project roles.
- Confluence: create page → `write` (`docs_create`); edit page → `write` (`docs_edit`); comment → `send`; restrictions → `share`.

## Fallback
"From an issue filter, use *Export → CSV* weekly into your **Nova Drop** folder, or keep Jira email notifications on."
