---
type: job
name: monthly
model: strongest
skills: [nova-review, nova-health]
---
# Job: monthly

## Purpose
Run the monthly moments once per month: Goal Progress, User Health Check, System Health Check, and Automation Review (with the success indicators). Bring only real decisions to the user.

## Runs when
- Lean: `nightly-cycle`. Standard: `morning-cycle`. Full: `morning-brief`. It rides along in a daily routine and decides for itself whether to do anything.
- **Period logic.** Let P be the current month (`YYYY-MM`, run date in the user's time zone) and B the first business day of P (first Monday–Friday date; holidays ignored). Run when the run date is on or after B and `jobs.yaml: monthly.period_done` is not P. Otherwise exit early, cheaply. A failed or skipped run is therefore caught up on the next run.
- The run in period P reviews the **previous month** (P−1).
- Modifiers: `when`. `target` and `mode` are ignored.

## Away and paused
During away, exit with `skipped_away` and leave `period_done` unchanged; the first run after away catches up. Each moment is skipped individually when its moment (`goal_progress`, `user_health_check`, `system_health_check`, `automation_review`) is off or paused. If the whole job is paused, exit with `skipped_paused`.

## Readiness check
Period check above. If `maintenance` hasn't succeeded in the last 8 days, run its index rebuild step first (the user health check relies on fresh indexes).

## Inputs
- Previous month's records changes, goals (active), commitments, decisions, run reports (`user/logs/runs/<P−1>/`), activity log (`user/logs/activity/<P−1>.md`).
- `user/inbox/` (approvals, insights engagement, questions), `user/.state/health.yaml`, `user/profile/`, `user/settings/`, `user/extensions/registry.yaml`.

## Steps
1. **Goal Progress** (`nova-review`, monthly mode): progress on each active goal with evidence for and against, and what needs attention. Update goal `current` where evidence supports it (`records_write`).
2. **User Health Check** (`nova-health`, user mode): stale records, orphans, duplicates, superseded facts, broken links, unprocessed journal/inbox items, profile proposals and guide drift, settings sanity. Auto-fix only what `system/rules/knowledge.md` allows (rebuild indexes, fix links, merge obvious duplicates, close clearly finished items); everything else becomes questions.
3. **System Health Check** (`nova-health`, system mode): routine run failures, connector auth, hooks present, schema validity (`system/tools/validate.py`), system files unmodified, extension compatibility, repo size. Update `health.yaml` (`last_user_check`, `last_system_check`, `known_issues`).
4. **Automation Review** (`nova-review`): what each job did last month (from run reports), what was used or ignored (insight and draft engagement), cost signals (items and duration), suggested schedule or profile changes. Compute the success indicators into `health.yaml: indicators` (`period: <P−1>`).
5. Write `user/work/reports/<P−1>.md` (`type: report`, `date`, `sources`) with one section per moment run.
6. Queue questions (profile proposals, ambiguous merges, records to archive, suggested routine changes) in `user/inbox/questions.md`; proposed settings changes go to `user/inbox/approvals.md` as `behavior_settings`.
7. Republish every dashboard whose contract (`system/dashboards/*.contract.md`) lists `monthly` in `republished_by`. Set `jobs.yaml: monthly.period_done` to P. Commit.

## Outputs
- `user/work/reports/YYYY-MM.md` (the reviewed month).
- `user/.state/health.yaml` (checks, known issues, indicators); fixed records and indexes.
- Questions and approvals in `user/inbox/`; republished dashboards.

## Early exit
Period not due or already done → `early_exit` (no reads beyond `jobs.yaml`). All four moments off → set `period_done` and `early_exit`.

## Guardrails
- Profile changes are `profile_update` (propose): write proposals, never edit the profile. Settings changes are `behavior_settings` (propose): queue.
- Never restore or modify system files from a routine outside `nova-update`; record a known issue instead.
- Indicators stay local; nothing leaves the repo.

## Run report
Row: `monthly | <status> | report <P−1>; <q> questions, <f> auto-fixes | moments run`. Adds known issues found.
