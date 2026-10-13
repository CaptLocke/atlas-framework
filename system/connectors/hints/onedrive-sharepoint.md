---
type: connector-hint
connector: onedrive-sharepoint (Microsoft 365)
categories: [files]
checked: "2026-10: Claude docs, Microsoft 365 connector page; tool names not verified"
---
# Hint: OneDrive and SharePoint

Tool names vary; always verify from the live tool list. Guide: `system/connectors/files.md`.

## Likely categories
`files`. Usually part of the Microsoft 365 connector (see `outlook.md`): map it as the same connector with an extra category.

## Typical operations
| Operation | What to look for |
|---|---|
| `search` | Search documents across OneDrive and SharePoint sites |
| `read_file` | Read/fetch document content |
| `list_folder` | List children of a drive folder (may be missing; then use search scoped to a folder path) |
| `upload`, `create_folder` | Create/update file; create folder |
| `move`, `share`, `delete` | May or may not be exposed |

## Cursor ideas
- Last-modified time filter where available; otherwise search scoped to the folder and compare modified times with existing Sources.
- Atlas Drop: rely on the move to `Processed`.

## Known quirks
- **Write actions depend on the organization's settings.** Documentation (2026-10) describes creating and updating files in SharePoint; OneDrive folder creation and file moves may not be available. Probe at mapping:
  - No `create_folder`: ask the user to create "Atlas Drop" (with "Processed" inside) and "Atlas Deliverables" themselves, then find them by search.
  - No `move`: Atlas cannot tidy the Drop folder; record processed file IDs in their Sources and skip them on later runs (note this in `limits`).
  - No `upload`: deliverables are download-only.
- **Indexing delay:** newly added files may not appear in search for a while; a dropped file may be picked up one run later.
- Work or school accounts only; tenant admin consent required.
- SharePoint sites are shared by nature: never upload deliverables to a team site unless the user explicitly chose it (that exposes the file).

## Migration folder
Used once, read-only, when a user brings notes in from another system (`.claude/skills/atlas-capture/reference/notes-migration.md` §3). Check at mapping:
- Listing reaches subfolders (recursive listing, or listing each child folder by ID).
- A raw `.md` or `.txt` file reads back as plain text, not as a conversion error or binary download.
Either fails → use the attachment route. Never move or rename anything in that folder; track it by file ID.

## Risk-sensitive tools
- `share`: share, create sharing link, grant access, upload to a SharePoint team site or shared library.
- `delete`: delete, recycle.
- `write`: create/update file or folder in the user's own OneDrive, move within it.

## Fallback
Chat attachments for drops; downloads for deliverables. If only search/read works, the user can still drop files into a folder they create, and Atlas reads them (no move).
