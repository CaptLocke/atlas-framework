---
type: job
name: triage
model: strongest
skills: [nova-triage]
---
# Job: triage

## Purpose
Keep commitments true and prioritized: catch commitments ingest missed, close those with evidence of completion, re-prioritize against goals, flag slipping and aging items, and set one next step on each open commitment.

## Runs when
- Lean: `nightly-cycle`. Standard: `morning-cycle`, `evening-cycle`, and `daytime-ingest` with `mode: light`. Full: `triage-drafts` (every 2 hours in work hours).
- Run first (light) by `daily-brief` when stale (see that job).
- Modifiers: `when`, `mode`. `mode: light` = only commitments created or changed since the last triage, plus overdue and due-soon checks; no re-prioritization of the whole set. `mode: full` (default) = all open commitments.

## Away and paused
Runs during away so records stay accurate (statuses, `slipped`, closures). User-facing results are held: no follow-up drafts are created, and due-soon and overdue items go to the catch-up brief instead of a daily brief. Paused per `system/jobs/README.md`.

## Readiness check
If `ingest` has not succeeded in the last 24 hours and is not earlier in this routine, proceed and note "evidence may be stale since <time>" in the run report and on the commitments' `insight` only where it matters.

## Inputs
- Open commitments (`user/knowledge/commitments/`, via `_index/commitments.md` and `hot.md`), records and sources updated since `jobs.yaml: triage.last_success`.
- Active goals (`user/knowledge/goals/`), calendar for the next 14 days (events records), `rhythms.yaml: triggers`.

## Steps
1. Invoke `nova-triage` in the requested mode with the window "since last triage success".
2. Catch: scan new sources for explicit promises not yet recorded; create commitments per `system/rules/knowledge.md` (direction `i_owe` or `waiting_on` only). Vague intentions become questions.
3. Close: mark `done` only on evidence (sent message, delivered file, user's word, source showing completion), with `completed_on` and an Updates line citing the evidence.
4. Prioritize (full mode only): set `priority` against active goals, deadlines, and who is waiting; set a one-line `insight` and `next_step`.
5. Dedupe obvious duplicate commitments (`merge_supersede`); ambiguous ones become questions.
6. Evaluate triggers: `commitment_overdue` (set `status: slipped`; flag for the brief; for `waiting_on`, create a follow-up draft via `nova-write` and a pending approval entry to send it) and `deadline_approaching` (due within `days`, default 3: mark for the next brief's "Due soon"; the day before, mark for the top). Fire once per key.
7. If commitments changed and this routine does not run `daily-brief` later, republish (`nova-dashboards`, `dashboards_refresh`) every dashboard whose contract (`system/dashboards/*.contract.md`) lists `triage` in `republished_by`.

## Outputs
- Updated commitment records (and new ones), index lines, `user/.state/triggers.yaml`.
- Follow-up drafts in the user's mail tool and entries in `user/inbox/approvals.md` for sending them.
- Questions in `user/inbox/questions.md` (vague commitments, ambiguous duplicates).
- Dashboards listing `triage` in `republished_by`, republished when no brief follows.

## Early exit
In light mode: no commitments created or changed since the last triage and none crossing a due/overdue threshold today → `early_exit`. In full mode: no open commitments and nothing new since last run → `early_exit`.

## Guardrails
- Status changes from evidence are `records_write` (auto); closing without evidence is not allowed.
- Follow-up messages are drafts only (`drafts_create`); sending is `send_communication` (locked): queue an approval, never send.
- Changing tasks in a task tool is `tasks_manage` (propose): queue, don't act.
- Never set a `due` the user didn't give; propose one in `next_step` or a question.

## Run report
Row: `triage | <status> | <N> reviewed, <c> closed, <s> slipped, <n> new | <mode>`. Adds approvals queued (follow-ups) and triggers fired.
