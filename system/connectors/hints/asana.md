---
type: connector-hint
connector: asana
categories: [tasks]
checked: "2026-10: general knowledge of Asana's model; tool names not verified"
---
# Hint: Asana

Tool names vary; always verify from the live tool list. Guide: `system/connectors/tasks.md`.

## Likely categories
`tasks`. Project status updates and goals may also appear (map as `tasks` reads; they feed project and goal records).

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | Search/list tasks in a workspace with assignee = me (or created by me) and a modified-since filter |
| `read_item` | Get task (with comments/"stories", subtasks, projects, due date) |
| `create_item` / `update_item` | Create task, update task, complete task, add to project |
| `delete` | Delete task |
| (read) | List projects, project status updates, goals, workspaces, users |

## Cursor ideas
- A "modified since" parameter on task listing, scoped to assignee and workspace; page with the offset token.
- First run: also list all incomplete tasks assigned to the user.

## Known quirks
- Everything lives in a workspace or organization: find the user's workspace ID at mapping (ask if there are several).
- "My Tasks" is a special per-user list; tasks there may have no project.
- Comments are "stories" mixed with system events (assigned, moved): keep only human comments.
- Due dates may be date-only or date-time.
- Status updates on projects carry health (on track / at risk / off track): map to the project record's `health`.

## Risk-sensitive tools
- `send`: add comment, @mention, assign to someone else, add followers/collaborators.
- `write` (→ `tasks_manage` for the user's own tasks; `shared_records_update` for team projects): create/update/complete task, move between sections.
- `delete`: delete task, delete project.
- `share`: change project membership or privacy, invite users.

## Fallback
"From a project or My Tasks, use *Export → CSV* weekly into your **Atlas Drop** folder, or turn on Asana email notifications."
