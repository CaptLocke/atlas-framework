---
type: schema
name: project
folder: user/knowledge/projects/
---
# Schema: project

## What it is
A bounded effort with an outcome, at any scale (a task group to a company initiative).

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `owner` | ID | no | Person accountable. |
| `goal` | ID | no | Goal it serves. |
| `start` | date | no |  |
| `target` | date | no | Target completion. |
| `health` | enum | no | on_track, at_risk, off_track, unknown |
| `insight` | text | no | One-line current insight, written by `triage`/`intelligence` (§ insights). |
| `next_step` | text | no | One recommended next action. |
| `scale` | enum | no | task_group, project, initiative, program |

## Status vocabulary
proposed, active, paused, done, cancelled

## Links
Typically links to: goals, people, organizations, commitments, decisions, risks, questions, events, topics.

## Capture guidance
Create when work with a clear outcome is discussed and no record exists (`new project` trigger). Keep the top of the body as a current-state summary: what, why, where it stands. `insight` and `next_step` are refreshed by triage.
