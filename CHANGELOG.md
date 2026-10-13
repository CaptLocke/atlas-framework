# Changelog

All notable changes to Nova. Nova follows semantic versioning:
- **Patch** (1.0.x): fixes only.
- **Minor** (1.x.0): additive features, new optional fields, additive migrations. Applied automatically by default.
- **Major** (x.0.0): a migration that needs user input, a non-additive data change, or a breaking change for extensions. Applied after the user says yes.

Each release's "What's new" section is shown to users in the Nova Guide and their next Daily Brief. "Under the hood" notes are for maintainers and are not shown to users.

## Unreleased

### What's new
- Choose which meetings Nova shows: all-day events, tentatively accepted meetings, and invitations you haven't answered can each be included or skipped in your brief, Week Ahead, and meeting prep. Everything is included unless you change it, and deadlines on your calendar always show.
- Two new people categories, **prospect** and **board**, and clear definitions for every category so people are sorted the same way every time.
- **Rank your goals.** Tell Nova which goal matters most, at setup, at the quarterly reset, or any time ("make retention my top goal"). Work tied to your top goals now rises higher in your priorities, and the Goals page lists them in your order.
- **New Records page**: browse and search everything Nova has filed, by name, type, or status, with what each record links to.
- Nova now checks at the start of every chat that it can save to your repository, and fixes it if a chat started read-only. **Please update your Nova Project's instructions**: ask Nova for the latest text, or copy it from the setup guide (step 4).

### Under the hood
- `rhythms.yaml: meetings` (`all_day`, `tentative`, `not_responded`: `include | skip`), optional with `include` defaults; the filter rule lives in `system/schemas/settings.md` and is referenced by the brief, Week Ahead, meeting prep, `nova-prep`, and `key_meeting_upcoming`. Validator checks the block.
- Event schema: new optional `all_day` (boolean) and `response` (`organizer | accepted | tentative | not_responded | declined`), mapped from Google Calendar and Outlook in the connector hints.
- Person schema: `relationship` adds `board` and `prospect`, with a definitions table and a first-match decision order (§Relationships). People dashboard weights, CRM mapping, the setup interview, `new_key_person`, and the triage priority rubric use them.
- Goal schema: optional `rank` (1 = most important among active goals; user-set only; renumbered on change). Triage's goal-link boost is scaled by rank (`1 − 0.6 × (r − 1)/(N − 1)`; unranked = 0.4 while others are ranked, 1.0 when none are). Validator checks rank values and duplicate ranks; the monthly user health check renumbers gaps. Goals dashboard sorts by rank and shows "#n".
- New built-in dashboard `records` (contract, template, fixture), republished by `maintenance` and `weekly-review`, 1500 KB budget. Existing users get it at their next chat (a new dashboard missing from `dashboards.yaml` is published then).
- `sync_start.py` adds a `git push --dry-run` write check after the pull and reports a read-only attachment; kernel §2.1 and `sync.md` say to re-attach with write access. Bootstrap stub now asks for "write (push) access".
- All changes are additive: no migration and no `data_version` change.

## 1.0.0

### What's new
- First public release of Nova.
