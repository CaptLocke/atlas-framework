---
type: connector-hint
connector: notion
categories: [files, tasks]
checked: "2026-10: general knowledge of Notion pages and databases; tool names not verified"
---
# Hint: Notion

Tool names vary; always verify from the live tool list. Guides: `system/connectors/files.md`, `tasks.md`.

## Likely categories
- **files**: pages and wikis (documents, meeting notes, specs). Notion is not a binary file store: it is **not** suitable as the Nova Drop or deliverables folder; use a cloud drive.
- **tasks**: databases used as task trackers or project lists (identify them by properties like Assignee, Status, Due). Map only if the user tracks work there.

## Typical operations
| Operation | What to look for |
|---|---|
| `files.search` / `list_folder` | Search pages (can sort by last edited); list child pages of a parent page |
| `files.read_file` | Fetch page content (blocks) |
| `tasks.list_recent` | Query a database with a filter on last edited time and assignee |
| `tasks.read_item` | Fetch a database page (properties + content) |
| `files.upload` / `tasks.create_item` | Create page / create database item |
| `files.edit` / `tasks.update_item` | Update page content or properties |

## Cursor ideas
- `last_edited_time` greater than `last_seen` (database queries), or search sorted by last edited time descending, stopping at the first already-filed page.
- One cursor per scoped database or parent page (`files:notion:<page-slug>`, `tasks:notion:<db-slug>`).

## Known quirks
- The connector sees only pages shared with the integration or the user; missing pages usually mean missing access.
- Deeply nested pages: read one level at a time; don't crawl entire workspaces.
- Meeting-notes databases are high value: each note → a meeting Source linked to the event.
- Database property names are user-defined; learn them at mapping and record them in `connectors.yaml` notes.

## Risk-sensitive tools
- `send`: create comment, @mention people (notifies them).
- `write`: create page (`docs_create`), update page or properties (`docs_edit` or `shared_records_update` for shared trackers), move page.
- `delete`: archive/trash page, delete block.
- `share`: change page permissions, publish to web.

## Fallback
"Use *••• → Export* (Markdown or PDF) on important pages and put the file in your **Nova Drop** folder."
