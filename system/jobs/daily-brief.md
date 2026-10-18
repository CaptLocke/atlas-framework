---
type: job
name: daily-brief
model: strongest
skills: [atlas-brief, atlas-dashboards]
---
# Job: daily-brief

## Purpose
Have the Daily Brief ready before the workday starts and the dashboards fresh: today's events with prep notes, due and slipping commitments, overnight changes, waiting-on items, top priorities, up to `brief_max` insights, drafts ready to review, approvals and questions waiting. After away, also produce the catch-up brief, linked from the top of that day's brief.

## Runs when
- Lean: `nightly-cycle` with `target: tomorrow` (last job). Standard: `morning-cycle` (last job). Full: `morning-brief` after `monthly` and `quarterly`.
- Modifiers: `when`; `target` = the brief's date (`today` default, or `tomorrow`). `mode` is ignored.

## Away and paused
Let T be the target date.
- **T within away:** exit with `skipped_away`.
- **T within an open-ended away** (`away.start <= T`, `away.end: null`): exit with `skipped_away`; the user ends it in chat (`atlas-away`), which sets `end`.
- **Catch-up:** the first daily-brief run whose target date is after `away.end` (or, for an open-ended away, after the user ends it) writes the catch-up brief as well as the normal brief, which links to it at the top (`atlas-brief` §B), then clears `away` in `rhythms.yaml` (`start`, `end`, `set_on` to null) and commits. This happens once.
- **Paused** (`{ job: daily-brief }` or moment `daily_brief` paused/off): exit with `skipped_paused`. A catch-up brief is still written when away ends.

## Readiness check
Read `user/.state/jobs.yaml`. For upstream jobs not earlier in this routine:
- `ingest` not successful in the last 12 hours → run `ingest` first.
- `triage` not successful in the last 24 hours → run `triage` in `light` mode first.
- `meeting-prep` with no run covering T → proceed; list T's meaningful meetings without prep and note it.
- `intelligence`, `email-drafts` stale → proceed and note it.
If `jobs.yaml: daily-brief.last_target` already equals T, refresh the existing brief rather than creating a second one.

## Inputs
- Records changed since the previous brief, `hot.md`, open commitments (due soon, slipped, waiting on), events on T with their `prep` links.
- Run reports since the previous brief (`user/logs/runs/`) for drafts created, prep notes, insights, errors.
- `user/inbox/approvals.md` (pending), `questions.md` (open), `insights.md` (`new`, top `brief_max` by score).
- `user/.state/health.yaml` known issues; "What's new" after an update (`atlas-update`); `user/profile/communication-style.md`.

## Steps
1. Invoke `atlas-brief` for date T. Normal brief sections follow the skill; items cite their records (`system/rules/writing.md`); triggers' brief items (`deadline_approaching`, `commitment_overdue`, `key_meeting_upcoming`) are placed as `system/triggers.md` says.
2. Catch-up brief (after away): invoke `atlas-brief` in catch-up mode for the whole away period: what happened, what changed, what needs the user first, what can wait, held approvals and insights, and drafts to consider now. Readable in five minutes.
3. Write the file (`type: brief`, `date: T`, `sources`). On the first brief ever, set `atlas.yaml: first_brief_delivered` to T.
4. Invoke `atlas-dashboards` to republish every dashboard whose contract (`system/dashboards/<name>.contract.md: republished_by`) lists `daily-brief` and whose data changed. Record `last_published` in `user/settings/dashboards.yaml`.
5. Set `jobs.yaml: daily-brief.last_target` to T. Commit.

## Outputs
- `user/work/briefs/YYYY-MM-DD.md` (T); after away, also `user/work/briefs/YYYY-MM-DD-catch-up.md`, linked from the top of T's brief (`atlas-brief` §B).
- Republished dashboards; `user/settings/dashboards.yaml` `last_published` values.
- `rhythms.yaml: away` cleared after a catch-up brief; `atlas.yaml: first_brief_delivered` on the first brief.

## Early exit
Never skipped for lack of news: an empty day still gets a short brief ("Nothing urgent; here's today"). Exits early only for away, paused, or when `last_target` equals T and nothing changed since that brief was written (`early_exit`).

## Guardrails
- The brief and dashboards are views. Nothing in them is sent or shared; dashboards stay private, page-only, without connector grants (unattended republish).
- If a dashboard can't be republished unattended, keep the brief file, record a known issue with the fix, and continue.
- Clearing `away` after the catch-up brief completes the user's own instruction; it is not a behavior change.

## Run report
Row: `daily-brief | <status> | brief for <T> (or catch-up <start>–<end>) | republished <n> dashboards; stale: <jobs>`.
