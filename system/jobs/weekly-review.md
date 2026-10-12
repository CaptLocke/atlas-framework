---
type: job
name: weekly-review
model: strongest
skills: [nova-review]
---
# Job: weekly-review

## Purpose
Produce the Weekly Review: wins, decisions made, commitments kept and slipped, stalled projects, aging waiting-on items, people to reconnect with, next week's preview and suggested priorities. Record the week's accomplishments against goals.

## Runs when
- All profiles: `weekly` routine (Friday 14:07), first job.
- Modifiers: `when`. `target` and `mode` are ignored.
- The review covers the ISO week of the run date (Monday through the run).

## Away and paused
Runs during away (the record of the week is still useful); it is not surfaced until the catch-up brief, which links it. If moment `weekly_review` is off or paused, or the job is paused, exit with `skipped_paused`.

## Readiness check
If `triage` has not succeeded in the last 24 hours, run `triage` in `light` mode first so kept/slipped counts are accurate. If `ingest` is older than 24 hours, proceed and note it.

## Inputs
- Records created or updated during the week; commitments by status change; decisions with `decided_on` in the week; projects with no activity in 14+ days; `waiting_on` items aging over 7 days.
- Person records with `cadence` and `last_contact` (who's gone quiet); calendar and events for next week.
- Active goals and their `accomplishments`; `user/work/briefs/` from the week; the previous review.

## Steps
1. If `user/work/reviews/YYYY-Www.md` exists for this week, refresh it instead of creating a new one.
2. Invoke `nova-review` (weekly mode) to write the review (`type: review`, `date`, `sources`), every item citing its record.
3. Accomplishments: append dated entries for real outcomes this week to the relevant goals' `accomplishments` and to `user/work/accomplishments.md` (running list), skipping entries already present (`records_write`).
4. Suggested priorities for next week go in the review; any change to commitments' priority is left to `triage`.
5. Invoke `nova-dashboards` to republish dashboards whose contract lists `weekly-review` (typically Goals, Week Ahead, People).
6. Commit.

## Outputs
- `user/work/reviews/YYYY-Www.md` (ISO week).
- Goal `accomplishments` entries and `user/work/accomplishments.md`.
- Republished dashboards.

## Early exit
A review is always written for an active week. Exit early only if this week's review exists and nothing changed since it was written.

## Guardrails
- Recording accomplishments is `records_write`; never invent or inflate outcomes; each cites evidence.
- Suggestions to reconnect with people are suggestions; no messages are drafted here.

## Run report
Row: `weekly-review | <status> | review YYYY-Www, <a> accomplishments | <stale notes>`.
