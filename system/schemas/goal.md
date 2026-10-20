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
| `period` | text | no | e.g. `2026-Q4`; quarters follow the company's fiscal year (`atlas.yaml: company`) |
| `metric` | text | no | How progress is measured. |
| `target` | text | no |  |
| `current` | text | no | Latest measured value with date. |
| `owner` | ID | no |  |
| `accomplishments` | list | no | Short dated entries appended by weekly review; feeds the performance review. |
| `rank` | integer | no | The user's order of importance among active goals: 1 = most important. Set only by the user (§Ranking). `null` or missing = unranked. |

## Ranking
The user ranks their **active** goals so priorities across Atlas follow what matters most to them, not just which goals exist.
- **When:** at setup (step 8, right after confirming goals), at the quarterly goal reset (when drafts become active), and any time in chat ("make retention my top goal", "rank my goals", "hiring matters more than the launch now").
- **Who sets it:** only the user. Atlas may suggest an order (from manager priorities, decisions, or what the user says), but writes `rank` only after the user confirms it. Every rank change gets an Updates line (`rank 2 → 1, per the user`) and is `provenance: stated`.
- **Shape:** ranks are 1, 2, 3, … with no gaps or ties. When one goal moves, renumber the others to keep that order. When a goal leaves `active` (achieved, missed, dropped), clear its `rank` and close the gap.
- **Partial ranking is fine.** The user may rank only their top one or two; the rest stay unranked.
- **A new active goal** starts unranked. If other goals are ranked, add one question to `user/inbox/questions.md` (kind `other`): "Where does <goal> rank among your goals?"
- **Effect:** triage scales the goal-link boost by rank (`.claude/skills/atlas-triage/reference/signals.md` §Priority rubric), and Work lists active goals in rank order. A rank change in chat is followed by a full priority pass (`atlas-triage`) so the brief and Work reflect it.

## Status vocabulary
draft, active, achieved, missed, dropped

## Links
Typically links to: projects, decisions, people.

## Capture guidance
Create during setup, quarterly goal reset, or when the user states a goal. Priorities across Atlas are ranked against active goals, weighted by the user's `rank` (§Ranking).
