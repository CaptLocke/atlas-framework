---
type: skill-reference
skill: nova-away
---
# What continues and what pauses

Source of intent: tactical §9.4a and strategy §7.18. Each job's own spec (`system/jobs/<job>.md`, section "Away and paused") is authoritative; this table is what to tell the user.

## During away (`start ≤ today` and `end` null or `today ≤ end`)
`end: null` means open-ended away until the user says "I'm back".

**Catch-up rule (authoritative):** the catch-up brief is written by the first `daily-brief` run whose target date is after `away.end` (or after the user ends an open-ended away); that run clears away.
| Job / behavior | During away | Why |
|---|---|---|
| `ingest` | Runs normally | Nothing is lost; everything is filed |
| `maintenance` | Runs normally | Keeps knowledge tidy |
| `triage` | Runs: updates records (closes on evidence, marks slipped) but produces no nudges or drafts | Records stay accurate for the catch-up brief |
| `intelligence` | Runs: insights are written to `insights.md` but held for the catch-up brief | Nothing surfaces until return |
| `daily-brief` | Exits early (`skipped_away`) while the target date is within away; the catch-up rule above decides when it writes the catch-up brief and clears away | No briefs while away |
| `email-drafts` | Exits early | No drafts piling up |
| `meeting-prep` | Exits early (prep resumes for meetings on or after the return day) | |
| `status-updates` | Exits early | |
| `weekly-review` | Runs normally (reviews are written and wait for the user); it stops only if the user pauses it | The catch-up brief links reviews written while away |
| `monthly` / `quarterly` | Wait until return (the period stays "not done", so they run on the first run after away) | They need the user's attention |
| `update-check` | Patch/minor updates apply as usual; major ones wait for a chat | |
| Triggers | Evaluated; record creation still happens; user-facing actions are held for the catch-up brief | `system/triggers.md` |
| Approvals and insights | New ones queue; none are executed; nothing expires while away (maintenance pauses expiry) | The catch-up brief lists everything still pending |
| Dashboards | Republished by jobs that run, with an "Away until …" banner | |
| Chats | Work normally; Nova mentions away once and offers to end it | |

## Paused items (`rhythms.yaml: paused`)
- A paused **job** exits early with `skipped_paused` while `until` is null or in the future (resumes on `until`).
- A paused **moment** stops the user-facing output of that moment (e.g., `daily_brief` stops the brief; `status_updates` stops the drafts) while the underlying records keep updating.
- Pausing `ingest` or `maintenance` is allowed only on explicit request, with a warning.

## Catch-up brief contents (produced by `nova-brief`)
1. **Needs you first:** open `action` questions (things only the user can do), approvals waiting, slipped `i_owe` commitments, deadlines in the next 3 days, held trigger actions.
2. **What changed:** decisions, new projects and people, risk changes, grouped by project.
3. **Waiting on others:** overdue `waiting_on` items, with offered follow-up drafts.
4. **Top insights** held during away (max 3; the rest stay in the inbox).
5. **Can wait:** everything else, one line each.
Readable in five minutes; every item linked to its record.

## Date examples (fictional, today = 2026-11-06, Friday)
- "I'm off next week" → `start: 2026-11-09`, `end: 2026-11-13`; catch-up = the first brief targeting a day after Nov 13 (Mon 2026-11-16 on weekday briefs; Sat Nov 14 if briefs run daily).
- "I'm off, not sure when I'm back" → `start: 2026-11-06`, `end: null`; catch-up after the user says "I'm back".
- "Out from the 12th to the 20th" → `start: 2026-11-12`, `end: 2026-11-20`.
- "Back on the 23rd" (away from today) → `start: 2026-11-06`, `end: 2026-11-22`.
