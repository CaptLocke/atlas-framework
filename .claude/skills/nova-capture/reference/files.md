# Files: chat attachments, Nova Drop, deliverables

Formats: `system/schemas/formats.md` §3 (drop) and §7 (outputs); `system/schemas/source.md`.

## Chat attachments
1. **Save** the attached file to `user/inbox/drop/<original-name>` (keep the name; add `-2` if it exists).
2. **Check data rules** before reading in depth: if the file's apparent category is `ignore`, stop, clear it from `drop/`, and tell the user it wasn't kept and why.
3. **Read** it (text, tables, slides). For large files, read the structure first, then the relevant parts.
4. **Source:** `sources/YYYY-MM-DD-<file-slug>`, `kind: file`, `origin_uri: "chat upload: <name>"`, `retention` per data rules, summary and key excerpts in the body (if retention allows).
5. **Extract** records through the write path (SKILL §1). If the user attached it for a task ("turn this into a one-pager"), do the extraction quietly and get on with the task.
6. **Place the file:**
   - Size ≤ 10 MB and handling `full` or `summary`, and the file is worth keeping as reference (contracts, brand guides, org charts, strategy docs, samples) → `git mv` it to `user/library/<YYYY>/<file-name>`; set `file_pointer: user/library/<YYYY>/<file-name>`.
   - Otherwise → keep only the Source (pointer/summary) and clear the file from `drop/`; set `file_pointer: "not kept (size or data rules); original with the user"`.
7. **Commit** and tell the user in one line what was filed and where the file went.

Clearing a processed file from `user/inbox/drop/` is inbox housekeeping described in `formats.md` §3 (the Source keeps the pointer). It never applies to files anywhere else.

## Nova Drop folder (ingest)
1. Read `nova.yaml: drop_folder` (connector, `folder_id`). If `connector: null`, skip (fallback: chat attachments).
2. `files.list_folder` on the drop folder since cursor `files:<connector>:drop`; ignore the `Processed` subfolder.
3. For each file: `files.read_file`, then the same steps as chat attachments 2–5. Do not copy the binary into the repo unless the library rule above allows it (then download and save to `user/library/`).
4. Source `origin_uri` / `file_pointer` = the file's link in the drive (after the move).
5. `files.move` the file into `Nova Drop/Processed` (`drop_folder_housekeeping`, normally `auto`; if set to `propose`, queue an approvals entry in routines and leave the file, relying on the cursor to avoid re-processing).
6. Commit; advance the cursor; count files in the run report.

## Deliverable pointers (called by `nova-write`)
- Source `sources/YYYY-MM-DD-<deliverable-slug>`, `kind: deliverable`, `captured_on` today, `retention: summary`, `file_pointer` = the saved file's link or path in the deliverables folder (or "download only; not saved to a drive"), `origin_uri` = same link.
- Body: what it is, audience, the working files path `user/work/deliverables/<YYYY-MM-DD-slug>/`, version note.
- Links: the project, people (audience), decisions or commitments it fulfills. If it fulfills an `i_owe` commitment and the user confirms it was delivered, close the commitment with this Source as evidence.
