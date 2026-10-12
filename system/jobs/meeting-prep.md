---
type: job
name: meeting-prep
model: strongest
skills: [nova-prep]
---
# Job: meeting-prep

## Purpose
Make sure a short, useful prep note exists before every meaningful meeting: who is attending, the history, open items each way, and a suggested agenda and questions.

## Runs when
- Lean: `nightly-cycle` with `target: tomorrow`. Standard: `morning-cycle` (default window) and `evening-cycle` with `target: tomorrow`. Full: `prep` routine at 6:07 and 11:07.
- Modifiers: `when`; `target`: `today` = from now to the end of today; `tomorrow` = all of tomorrow; none = the next 24 hours from now.
- Evaluates the `key_meeting_upcoming` trigger (`system/triggers.md`).

## Away and paused
If the target window falls within away, exit with `skipped_away` (no prep for meetings the user won't attend; the first prep run after away covers the return day). Paused per `system/jobs/README.md`.

## Readiness check
- A calendar must be covered (`calendar.list_range` mapped). If not, exit early with a note.
- If `ingest` has not succeeded in the last 24 hours and is not earlier in this routine, read the calendar directly for the window (`calendar.list_range`) so new meetings are not missed, and note the staleness.

## Inputs
- Event records in the window (`user/knowledge/events/`) and the calendar for the window.
- Attendee person records, their organizations, linked projects, open commitments each way, recent decisions, open risks and questions (L3 via `nova-recall`).
- Existing prep notes in `user/work/prep/`.

## Steps
1. List events in the window. Select meaningful ones: those meeting `key_meeting_upcoming` (a `one_on_one`, external attendees, or at least one linked open commitment or decision) plus any the user has asked to always prep. Skip holds, focus blocks, personal items, and declined or cancelled events.
2. For each selected event, check the fire-once key (`event start`) in `user/.state/triggers.yaml` and whether a prep note exists. If one exists and nothing relevant changed since it was written, skip it.
3. Invoke `nova-prep` (meeting mode) to write or refresh the note at `user/work/prep/YYYY-MM-DD-<event-slug>.md` (frontmatter `type: prep`, `date`, `sources`).
4. Set the event record's `prep` field to the note path (create the event record if missing, per the event schema) and record the trigger firing.
5. Commit.

## Outputs
- `user/work/prep/YYYY-MM-DD-<event-slug>.md` per meaningful meeting.
- Event records with `prep` set; `user/.state/triggers.yaml`.
- The list of prepared meetings in the run report, which `daily-brief` links.

## Early exit
No meaningful meetings in the window, or all already have up-to-date prep notes → `early_exit`.

## Guardrails
- Read-only toward the calendar: never accept, decline, create, or move events (`send_communication` / `own_calendar_manage` are not used here; suggestions go in the note).
- Prep notes are for the user; they may cite records. Respect data rules for sensitive content about attendees.

## Run report
Row: `meeting-prep | <status> | <N> prep notes (<new> new, <ref> refreshed) | window <dates>`.
