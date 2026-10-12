# Finished deliverables (docx, pptx, xlsx, pdf)

Strategy §7.5, tactical §9.6a. Fictional examples.

## 1. Set up the working folder
`user/work/deliverables/<YYYY-MM-DD-slug>/` (e.g. `2026-10-14-vendor-scoring/`), committed:
- `brief.md`: audience, purpose, format, voice, key messages, sources used (record IDs).
- `content.md`: the full text (sections, slide-by-slide content, or table definitions).
- `data/`: CSV/JSON used for tables and charts (only data the data rules allow storing).
- `build.py` (optional): the script that produced the file, so it can be rebuilt.
Build output goes to `.nova-tmp/deliverables/<slug>/` (git-ignored). Binaries are never committed.

## 2. Choose the builder
1. If the session offers a Claude skill for the format (e.g. docx, pptx, xlsx, pdf skills), read and follow it.
2. Otherwise use Python:
   - docx → `python-docx`; pptx → `python-pptx`; xlsx → `openpyxl` (formulas, number formats, frozen headers); pdf → `reportlab`, or build HTML and convert (e.g. `weasyprint` if present).
   - If a library is missing, install it in the session (`pip install --quiet <pkg>`); if installation isn't possible, offer the nearest alternative (e.g. PDF from HTML, or a Google Doc via `docs_create` if a files connector supports it).
3. Fonts: use the design system's families if available in the environment; otherwise its listed fallbacks.

## 3. Apply the design system (`user/profile/design-system.md`)
- Colors by role (primary, accent, text, background), chart palette order, number formats.
- Logo from `user/profile/assets/` with its placement and clear-space rules.
- Document patterns: title slide, one-pager layout, memo header.
- Empty design system → clean neutral style (dark text on white, one accent color, generous spacing) and offer to build the design system from a brand guide or the company website.

## 4. Content standards by format
| Format | Standards |
|---|---|
| One-pager / memo (docx/pdf) | Headline that states the point; 3–5 sections; ≤1 page; decision or ask stated explicitly |
| Deck (pptx) | One message per slide in the title; ≤6 bullets; charts over tables where possible; speaker notes with sources; title + agenda + close slides |
| Sheet (xlsx) | Inputs, calculations, outputs separated; real formulas (not pasted values) for derived numbers; header row frozen; units in headers; a "Notes" tab with sources and assumptions |
| PDF | Built from the doc or HTML; check page breaks and fonts embedded |

## 5. Check before delivering
- Convert to images or PDF and look at every page/slide: overflow, overlapping elements, empty placeholders, wrong logo, unreadable chart colors.
- Recompute key numbers from the data; spot-check formulas in sheets.
- Read the text once in the voice guide's terms.
- File name: `<Short Title> - <YYYY-MM-DD>.<ext>` (user-friendly, no IDs).

## 6. Save and deliver
1. `files.upload` to `nova.yaml: deliverables_folder` (`connector`, `folder_id`; create the folder with `files.create_folder` only if missing and record the ID through `nova-settings`). Autonomy: `deliverables_save`. If the level is `propose`, ask in chat; in routines queue an approvals entry.
2. Never overwrite: if the name exists, save as `… - v2`.
3. Send the file to the user in chat as a download (the session's file-delivery tool), with one line: what it is, where it was saved.
4. Pointer Source via `nova-capture` (`kind: deliverable`, `file_pointer` = drive link/path or "download only; not saved to a drive"), linked to project/people/commitment.
5. Commit the working folder and Source (`nova(chat): deliverable <title>`); activity-log line.

## 7. Revisions
"Change slide 3" → edit `content.md`/data, rebuild, save as a new version, deliver again, add an Updates line to the Source. Editing the old file in the drive in place is `docs_edit` (propose).
