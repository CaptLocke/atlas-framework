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

## Status vocabulary
scheduled, held, cancelled

## Links
Typically links to: people, projects, decisions, commitments, sources (transcript).

## Capture guidance
Create for meaningful meetings (external attendees, 1:1s, decision forums, anything with a transcript) and real deadlines. Skip holds, focus blocks, and personal calendar items unless the user asks.
