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

### Under the hood
- `rhythms.yaml: meetings` (`all_day`, `tentative`, `not_responded`: `include | skip`), optional with `include` defaults; the filter rule lives in `system/schemas/settings.md` and is referenced by the brief, Week Ahead, meeting prep, `nova-prep`, and `key_meeting_upcoming`. Validator checks the block.
- Event schema: new optional `all_day` (boolean) and `response` (`organizer | accepted | tentative | not_responded | declined`), mapped from Google Calendar and Outlook in the connector hints.
- Person schema: `relationship` adds `board` and `prospect`, with a definitions table and a first-match decision order (§Relationships). People dashboard weights, CRM mapping, the setup interview, `new_key_person`, and the triage priority rubric use them.
- All changes are additive: no migration and no `data_version` change.

## 1.0.0

### What's new
- First public release of Nova.
