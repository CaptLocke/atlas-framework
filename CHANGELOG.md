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
- **Nova learns from your corrections.** When you keep dropping the same kind of "commitment", reranking the same kind of work, or dismissing the same kind of insight, Nova suggests a rule and follows it once you agree. The monthly report shows what it learned.
- **Playbooks.** Nova notices work you repeat and offers to save it as a playbook. When one starts, it sets up the checklist with dates, drafts the messages as each step comes due, and flags steps that are missed or out of order.
- **Insights come with the draft.** When an insight suggests messaging someone, the draft is already waiting in your mail.

### Under the hood
- `rhythms.yaml: meetings` (`all_day`, `tentative`, `not_responded`: `include | skip`), optional with `include` defaults; the filter rule lives in `system/schemas/settings.md` and is referenced by the brief, Week Ahead, meeting prep, `nova-prep`, and `key_meeting_upcoming`. Validator checks the block.
- Event schema: new optional `all_day` (boolean) and `response` (`organizer | accepted | tentative | not_responded | declined`), mapped from Google Calendar and Outlook in the connector hints.
- Person schema: `relationship` adds `board` and `prospect`, with a definitions table and a first-match decision order (§Relationships). People dashboard weights, CRM mapping, the setup interview, `new_key_person`, and the triage priority rubric use them.
- Goal schema: optional `rank` (1 = most important among active goals; user-set only; renumbered on change). Triage's goal-link boost is scaled by rank (`1 − 0.6 × (r − 1)/(N − 1)`; unranked = 0.4 while others are ranked, 1.0 when none are). Validator checks rank values and duplicate ranks; the monthly user health check renumbers gaps. Goals dashboard sorts by rank and shows "#n".
- New built-in dashboard `records` (contract, template, fixture), republished by `maintenance` and `weekly-review`, 1500 KB budget. Existing users get it at their next chat (a new dashboard missing from `dashboards.yaml` is published then).
- `sync_start.py` adds a `git push --dry-run` write check after the pull and reports a read-only attachment; kernel §2.1 and `sync.md` say to re-attach with write access. Bootstrap stub now asks for "write (push) access".
- Learning loop: `feedback` activity-log lines (`not_a_commitment`, `missed_commitment`, `wrong_close`, `priority_up/down`, `noise`, `insight_useful/noise`), a monthly learning pass (≥3 consistent signals in 60 days → max 3 proposals), confirmed rules in `preferences.md` `## Triage rules` / `## Insight rules`, applied by capture, triage, and insights (`.claude/skills/nova-triage/reference/learning.md`). Sender/channel noise becomes a proposed data-rule exclusion (approval in chat).
- Playbooks: schema adds `anchor`, `auto_start`, structured `steps` (`step`, `when`, `draft`, `to`); runs are a `task_group` project with one commitment per step; new built-in trigger `playbook_start`; intelligence proposes playbooks from work repeated 3+ times in 12 months; email-drafts pre-drafts communication steps; triage flags out-of-order and skipped steps (`.claude/skills/nova-triage/reference/playbooks.md`).
- Insight drafts: `Draft for:` / `Draft:` lines on insight entries; `email-drafts` drafts for the top `brief_max` insights; the brief shows "Draft ready".
- Inbox lifecycle: a `counts` block in each inbox file's frontmatter, kept by every writer and checked by the validator; `maintenance` moves entries resolved more than 14 days ago to `user/inbox/archive/YYYY-MM-<name>.md`. History readers (insight engagement, monthly review) include the archive.
- Field formats: `schema.yaml: field_formats` declares ref/refs/list/emails/date/dt/bool/int/steps per field; the validator enforces them; new `system/tools/normalize.py` fixes mechanical problems in place (bare IDs, scalar lists, email case, enum spelling, date-only fields), run on write and by `maintenance`.
- All changes are additive: no migration and no `data_version` change. Existing inbox files without a `counts` block get a warning until the next `maintenance` run adds it.

## 1.0.0

### What's new
- First public release of Nova.
