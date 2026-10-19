---
type: schema
name: event
folder: user/knowledge/events/
---
# Schema: event

## What it is
Meetings, 1:1s, deadlines, milestones, and notable occurrences.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `kind` | enum | no | meeting, one_on_one, deadline, milestone, occurrence |
| `start` | datetime | no | ISO 8601 with offset. |
| `end` | datetime | no |  |
| `attendees` | list of IDs | no |  |
| `series` | text | no | Recurring series name/ID. |
| `location` | text | no |  |
| `outcomes` | list | no | Short list; details live in linked decisions/commitments. |
| `prep` | path | no | Prep note in `user/work/prep/`. |
| `all_day` | boolean | no | `true` for date-only calendar events. Omitted means `false`. |
| `response` | enum | no | The user's own RSVP, from the calendar: organizer, accepted, tentative, not_responded, declined. Updated on every calendar sync. Used by the meeting filter (`system/schemas/settings.md`, `rhythms.yaml: meetings`). |

## Status vocabulary
scheduled, held, cancelled

## Links
Typically links to: people, projects, decisions, commitments, sources (transcript).

## Capture guidance
Create for meaningful meetings (external attendees, 1:1s, decision forums, anything with a transcript) and real deadlines. Skip holds, focus blocks, and personal calendar items unless the user asks.

**Dated plans in a document or transcript are events too**, not just fields on the project they belong to: a programme's start and end, a go-live, a review date. File each as `kind: milestone` (or `deadline` where something is owed by then), with `all_day: true` when the source gives a date and no time. A date left only in prose or in a project's `start`/`target` reaches no timeline.

**A future meeting named in a transcript: first ask whether a calendar covers it.** Check `user/settings/connectors.yaml` for an attached meetings connector that is available in this context — don't assume one either way.
- **No calendar covering it** (no meetings connector, or none available here): **file it from the prose**, like any other dated plan. Nothing else will, and the meeting is then invisible.
- **A calendar covers it:** leave it to calendar sync, which matches on the connector's event ID (`system/connectors/calendar.md`). A copy filed from prose has no `origin_uri` to match, so it becomes a second record for one occurrence.

Record `response` and `all_day` for calendar events even when the meeting filter skips them: the filter decides what is shown, not what is known.
