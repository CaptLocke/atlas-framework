---
type: connector-hint
connector: google-drive
categories: [files]
checked: "2026-10: Anthropic help center (Google Workspace connectors); tool names not verified"
---
# Hint: Google Drive

Tool names vary; always verify from the live tool list. Guide: `system/connectors/files.md` (Nova Drop and deliverables folder).

## Likely categories
`files`. Good choice for both the **Nova Drop** folder and the **deliverables** folder.

## Typical operations
| Operation | What to look for |
|---|---|
| `list_folder` | Search/list with a parent-folder filter (e.g. "`<folderId>` in parents") |
| `read_file` | Fetch / read / export file content (Google Docs, Sheets, Slides exported to text; PDF and Office text extraction) |
| `search` | Search files by name or full text |
| `create_folder` | Create folder |
| `upload` | Upload/create file (optionally converting to Google format) |
| `move` | Move file (change parent) |
| `share`, `delete` | Share / update permissions; trash |
| (read) | File metadata, permissions, list recent changes |

## Cursor ideas
- Scoped folders: modified-time filter (e.g. "modifiedTime > `<ISO time>`") plus the parent filter.
- Nova Drop: list the folder's direct children; the move to `Processed` is the real guard.

## Known quirks
- **Use folder IDs, not names**: Drive allows duplicate folder names. Record `folder_id` in `nova.yaml` at setup; search for an existing "Nova Drop" before creating one.
- Saving Claude-generated files may require code execution / file creation to be enabled in Claude settings; if upload fails, deliver as download.
- Text is extracted from files; images inside documents may not be processed.
- Shared drives and shortcuts behave differently from My Drive: create Nova folders in My Drive.
- Moving a file into a shared folder changes who can see it (see risk).

## Risk-sensitive tools
- `share`: share, add permission, change link sharing, **move into a shared drive or shared folder**, transfer ownership.
- `delete`: trash, delete permanently, empty trash.
- `write`: create folder, upload, move (within the user's own folders), copy, rename, edit content.

## Fallback
No drive connected: drops by chat attachment; deliverables as downloads (`nova.yaml` connectors set to `null`).
