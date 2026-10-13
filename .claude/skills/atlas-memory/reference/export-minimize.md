# Export and minimize

## Export (zip of `user/`)
1. Sync (`git pull --rebase`) so the export is current.
2. Build the zip outside the repo's tracked files:
```bash
mkdir -p .atlas-tmp/export
cd <repo root> && zip -r -q ".atlas-tmp/export/atlas-export-$(date +%Y-%m-%d).zip" user -x '*.gitkeep'
zip -j -q ".atlas-tmp/export/atlas-export-$(date +%Y-%m-%d).zip" .atlas-tmp/export/README.txt   # after step 3
```
   If `zip` is missing, use Python: `python3 -c "import shutil; shutil.make_archive('.atlas-tmp/export/atlas-export-YYYY-MM-DD', 'zip', '.', 'user')"`.
3. Add a short `README.txt` inside the zip root (written to `.atlas-tmp/export/README.txt` and added) explaining the layout: records are markdown with YAML frontmatter, one file per item; folders by type; links in `[[type/slug]]` form; settings in YAML; readable in any text editor or notes app.
4. Deliver the file to the user as a download in chat (the session's file-delivery tool). State its size and that it contains everything Atlas knows, including sensitive items, and should be stored safely.
5. Only if the user asks: also save it to their deliverables folder (`files.upload`, `deliverables_save`). Never share or send it.
6. Delete `.atlas-tmp/export/` after delivery. Log: `chat · export · user/ exported (<size>)`.

## Minimize mode
Purpose: reduce what is stored at rest (R3: employer policy concerns, a new employer, personal preference) by converting full content to summaries or pointers.

### Choose scope (with the user)
Offer clear options with counts:
- By sensitivity: everything `confidential`, `pii`, `financial`, … → pointer or summary.
- By source kind or connector: all email sources, all meeting transcripts, a messaging workspace.
- By age: sources older than N days.
- Library files (`user/library/`): remove copies, keep pointers.
- Everything: all sources to pointer, records keep only non-sensitive structured fields and one-line summaries.

### Show the plan
"I'll convert 412 email sources from full text to short summaries and remove 18 library files (keeping links to the originals). Records stay, minus any sensitive specifics. Older full content stays in version history unless you also permanently erase it." Ask whether future capture should follow the same handling (a `data-rules.yaml` change: governance, separate approval record).

### Execute (after explicit yes; `destructive` approval record)
For each targeted Source:
- `summary`: replace body with a summary that omits sensitive details; remove key excerpts; `retention: summary`.
- `pointer`: body becomes one line ("Email thread with Acme legal, 2026-09-02; content not stored."); keep `origin_uri`; `retention: pointer`.
- Append Updates: "Minimized to <retention> at user request."
For records with a targeted `sensitivity`: remove sensitive specifics from body and fields; keep IDs, links, dates, status; Updates line.
Library files: `git rm` the file; set the Source `file_pointer` to the original location or "not kept".
Commit in batches of ~100 files (`Atlas-Reason: minimize mode (user-approved)`), push, log counts only.

### Close
Report counts, confirm future handling if changed, and offer purge for the minimized paths' history (`reference/purge.md`), noting that purging many paths rewrites most of history and removes undo for them.
