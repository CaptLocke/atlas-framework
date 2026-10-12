---
type: skill-reference
skill: nova-away
---
# What continues and what pauses

Source of intent: tactical §9.4a and strategy §7.18. Each job's own spec (`system/jobs/<job>.md`, section "Away and paused") is authoritative; this table is what to tell the user.

## During away (`start ≤ today ≤ end`)
| Job / behavior | During away | Why |
|---|---|---|
| `ingest` | Runs normally | Nothing is lost; everything is filed |
| `maintenance` | Runs normally | Keeps knowledge tidy |
| `triage` | Runs: updates records (closes on evidence, marks slipped) but produces no nudges or drafts | Records stay accurate for the catch-up brief |
| `intelligence` | Runs: insights are written to `insights.md` but held for the catch-up brief | Nothing surfaces until return |
| `daily-brief` | Exits early (`skipped_away`); on the first run on or after `end`, writes the catch-up brief and clears away | No briefs while away |
| `email-drafts` | Exits early | No drafts piling up |
| `meeting-prep` | Exits early (prep resumes for meetings on or after the return day) | |
| `status-updates` | Exits early | |
| `weekly-review` | Exits early; the catch-up brief covers the period | |
| `monthly` / `quarterly` | Wait until return (the period stays "not done", so they run on the first run after away) | They need the user's attention |
| `update-check` | Patch/minor updates apply as usual; major ones wait for a chat | |
| Triggers | Evaluated; record creation still happens; user-facing actions are held for the catch-up brief | `system/triggers.md` |
| Approvals | New ones queue; none are executed; they're listed in the catch-up brief | 14-day expiry still applies |
| Dashboards | Republished by jobs that run, with an "Away until …" banner | |
| Chats | Work normally; Nova mentions away once and offers to end it | |

## Paused items (`rhythms.yaml: paused`)
- A paused **job** exits early with `skipped_paused` while `until` is null or in the future (resumes on `until`).
- A paused **moment** stops the user-facing output of that moment (e.g., `evening_thoughts` stops the evening prompt; `daily_brief` stops the brief) while the underlying records keep updating.
- Pausing `ingest` or `maintenance` is allowed only on explicit request, with a warning.

## Catch-up brief contents (produced by `nova-brief`)
1. **Needs you first:** approvals waiting, slipped `i_owe` commitments, deadlines in the next 3 days, held trigger actions.
2. **What changed:** decisions, new projects and people, risk changes, grouped by project.
3. **Waiting on others:** overdue `waiting_on` items, with offered follow-up drafts.
4. **Top insights** held during away (max 3; the rest stay in the inbox).
5. **Can wait:** everything else, one line each.
Readable in five minutes; every item linked to its record.

## Date examples (fictional, today = 2026-11-06, Friday)
- "I'm off next week" → `start: 2026-11-09`, `end: 2026-11-13`; catch-up on Mon 2026-11-16.
- "Out from the 12th to the 20th" → `start: 2026-11-12`, `end: 2026-11-20`.
- "Back on the 23rd" (away from today) → `start: 2026-11-06`, `end: 2026-11-22`.
