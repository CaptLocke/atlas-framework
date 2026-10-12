---
type: schema
name: goal
folder: user/knowledge/goals/
---
# Schema: goal

## What it is
An outcome the user or their organization is working toward.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `horizon` | enum | no | quarter, half, year, multi_year |
| `period` | text | no | e.g. `2026-Q4` |
| `metric` | text | no | How progress is measured. |
| `target` | text | no |  |
| `current` | text | no | Latest measured value with date. |
| `owner` | ID | no |  |
| `accomplishments` | list | no | Short dated entries appended by weekly review; feeds the performance review. |

## Status vocabulary
draft, active, achieved, missed, dropped

## Links
Typically links to: projects, decisions, people.

## Capture guidance
Create during setup, quarterly goal reset, or when the user states a goal. Priorities across Nova are ranked against active goals.
