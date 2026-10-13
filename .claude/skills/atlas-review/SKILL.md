---
name: atlas-review
description: "Produce Atlas's periodic reviews: the Weekly Review (wins, decisions, commitments kept and slipped, stalled projects, aging waiting-on items, people to reconnect with, next week and suggested priorities, plus accomplishments), the monthly report (goal progress, user and system health, automation review with private success indicators), and the quarterly moments (goal reset, role refresh with permission re-confirmation, performance review pack). Use for the `weekly-review`, `monthly`, and `quarterly` jobs, and for \"review my week\", \"how did this month go?\", \"how are my goals tracking?\", \"prep my self-review\", \"what did I accomplish this quarter?\", \"reset my goals\", \"my role changed\"."
---
# Reviews

## Purpose
Turn the record of the user's work into perspective: what got done, what slipped, what's drifting, and what to focus on next, at weekly, monthly, and quarterly rhythm. Keep a running list of accomplishments so performance reviews write themselves, and check periodically that Atlas itself is useful (automation review) and still permitted (attestation).

## When to use
| Moment | Invoked by | On/off switch (`rhythms.yaml: moments`) | Output |
|---|---|---|---|
| Weekly Review | `weekly-review` job; chat "review my week" | `weekly_review` | `user/work/reviews/YYYY-Www.md` |
| Goal progress, health checks, automation review | `monthly` job; chat "how did this month go?" | `goal_progress`, `user_health_check`, `system_health_check`, `automation_review` | `user/work/reports/YYYY-MM.md` |
| Goal reset, role refresh | `quarterly` job; chat "reset my goals", "my role changed" | `reset_goals`, `role_refresh` | `user/work/reports/YYYY-Qn.md` |
| Performance review pack | `quarterly` job; chat "prep my self-review" | `performance_review` | `user/work/reports/YYYY-Qn-performance.md` |
The jobs own scheduling, period bookkeeping in `user/.state/jobs.yaml`, away/paused checks, and early exit (`system/jobs/<job>.md`). A moment that is `off` or paused is skipped; its section says so in one line if the report is produced anyway.

## Inputs
- Records (via indexes first): commitments, decisions, projects, goals, people, events, risks, questions, ideas; `hot.md`; `people-map.md`.
- `user/logs/activity/`, `user/logs/runs/`, `user/.state/{jobs,health}.yaml`, `user/inbox/{approvals,insights,questions}.md`, `user/journal/`.
- Calendar via the mapped `calendar.list_range` (next week preview), within data rules.
- Profile (`profile.md`, communication style) and settings (`rhythms.yaml`, `routines.yaml`, `atlas.yaml`).
- Section-by-section detail: `reference/weekly.md`, `reference/monthly.md` (incl. `reference/indicators.md`), `reference/quarterly.md`.

## Procedure
### Weekly Review (ISO week, Monday–Sunday; run Friday covers Monday to now)
1. Gather the week's changes (activity log, records with `updated` in the week, run reports).
2. Write the sections in `reference/weekly.md`: **Wins · Decisions made · Commitments kept · Commitments slipped · Stalled projects · Aging waiting-on · People to reconnect with · Next week · Suggested priorities**. Every item cites its record. Lead with a 2–3 line summary.
3. **Accomplishments:** pick the week's real accomplishments (delivered work, decisions driven, milestones, problems solved; not activity). For each, append a short dated entry to the relevant goal's `accomplishments` field (record update with an `## Updates` line) and a line to `user/work/accomplishments.md` (format in `reference/weekly.md`). Don't duplicate an entry already recorded.
4. Suggested priorities (max 5) are ranked against active goals, then due dates; each with a one-line reason.
5. Republish the dashboards whose contracts list this job in `republished_by` (`system/dashboards/*.contract.md`) with `atlas-dashboards`; the next brief links the review.

### Monthly report (previous calendar month)
1. **Goal progress:** for each active goal: progress vs target (`current`), evidence for and against (accomplishments, linked projects' health, decisions), what needs attention; propose `current` updates the evidence supports (records_write) and status changes (`achieved`/`missed`) as questions.
2. **User health check:** run `atlas-health` (user mode); include its "Your knowledge" section.
3. **System health check:** run `atlas-health` (system mode, including smoke test and audits); include its "Atlas's health" section.
4. **Automation review:** per job and routine, what it did, what was used vs ignored, cost proxies, and suggested changes; compute the **success indicators** locally (`reference/indicators.md`), store them in `user/.state/health.yaml: indicators`, and show them in the report. Suggested setting changes are proposals: queue them in `user/inbox/approvals.md` (`behavior_settings`) or `questions.md`; never apply them here.
5. Republish the dashboards whose contracts list this job in `republished_by` (`system/dashboards/*.contract.md`) with `atlas-dashboards`.

### Quarterly (previous fiscal quarter; calendar quarter when the fiscal year starts in January)
Follow `reference/quarterly.md`:
1. **Goal reset prep:** retrospective per goal (achieved / partly / missed, why, evidence); draft next-quarter goals as `goals/*` records with `status: draft` (from carry-overs, the user's stated plans, manager expectations in records); ask the user to confirm, edit, or import goals (questions in routines; conversation in chat). Only the user activates goals.
2. **Role refresh:** questions on role, manager, team, priorities, tools, company context; differences found in records are proposed, not assumed. **Attestation:** ask the user to re-confirm the permission statement; in chat, on a clear yes, update `atlas.yaml: attestation` (`recorded_on`, `atlas_version`, `reconfirm_due` = first business day of next quarter). A change of employer or role requires a **new** attestation (new `employer`, `role`, statement re-affirmed) before any data from the new employer is ingested; until then, pause `ingest` for new-employer sources and say so. In a routine, queue it as a `setup`-kind question; never record an attestation without the user's words in chat.
3. **Performance review pack:** `YYYY-Qn-performance.md`: accomplishments by goal, key decisions and their outcomes, impact (metrics, deliverables, people helped), recognition received, challenges and what was learned, suggested talking points for the self-review or 1:1. Written in the user's personal voice, with a sources list at the end (not inline in the pack's body if the user wants to paste it; keep citations in a closing "Evidence" section).
4. Republish the dashboards whose contracts list this job in `republished_by` (`system/dashboards/*.contract.md`) with `atlas-dashboards`.

### In chat
Produce the requested review on demand for the period the user names (default: this week / last month / last quarter). Present the summary and the "needs you" items in the conversation; write the file as well. Ask quarterly questions conversationally, one at a time.

## Outputs
- `user/work/reviews/YYYY-Www.md` (`type: review`), `user/work/reports/YYYY-MM.md` (`type: report`), `user/work/reports/YYYY-Qn.md` (`type: report`), `user/work/reports/YYYY-Qn-performance.md` (`type: performance`); frontmatter `type`, `date`, `period`, `sources` (formats §7).
- Goal `accomplishments` entries and `user/work/accomplishments.md` lines; goal `current` updates; draft goals.
- `user/.state/health.yaml: indicators`; `questions.md` and `approvals.md` entries; `atlas.yaml: attestation` (chat only).
- Dashboards republished; activity-log lines; commits.

## Guardrails
- Governance: `system/rules/governance.md`. Classes touched: `read`, `records_write` (accomplishments, goal `current`, draft goals), `profile_update` (role refresh findings are proposals unless `auto`), `behavior_settings` (automation-review suggestions are proposals only), `dashboards_refresh`, `external_read` (calendar for next week).
- Indicators are computed and stored only in the user's repo; nothing is sent anywhere. They leave the repo only if the user includes them in an issue report (`atlas-report-issue`).
- Never mark a goal achieved or missed, activate a goal, or change role facts without the user's confirmation.
- Never record or renew an attestation without the user's explicit words in chat.
- Accomplishments must be real and evidenced; never inflate. No `notes_private` in any report.
- The performance pack is for the user; sharing it is `share_expose` (locked) and sending it is `send_communication` (locked).

## Done when
- The period's output file exists with every section filled or explicitly "nothing this week/month", and every item is cited.
- New accomplishments appear in both the goal records and `accomplishments.md`, without duplicates.
- (Monthly) `health.yaml: indicators` has this period; health sections are included; suggestions are queued, not applied.
- (Quarterly) draft goals, role questions, and the attestation re-confirmation are with the user; the performance pack exists.
