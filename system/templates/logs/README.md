# Atlas logs

This folder is Atlas's record of what it did. Atlas writes it; you never need to edit it. The Control Center dashboard shows the highlights.

- `activity/YYYY-MM.md`: one line per change Atlas made (date, who acted, what, commit). Never contains sensitive content.
- `runs/YYYY-MM/<routine>-<YYYYMMDD-HHMM>.md`: one report per scheduled run (jobs run, items processed, drafts created, approvals queued, errors, connector health).

Exact formats: `system/schemas/formats.md` §4.
