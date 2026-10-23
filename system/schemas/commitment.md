---
type: schema
name: commitment
folder: user/knowledge/commitments/
---
# Schema: commitment

## What it is
Something someone has promised to do. Direction says who owes it.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `direction` | enum | yes | `i_owe` (the user promised) or `waiting_on` (someone promised the user). |
| `owner` | ID | yes | Person who must act (`[[people/<self>]]` when `i_owe`). |
| `counterparty` | ID | yes | Person it is owed to (or from). |
| `due` | date or null | yes | `null` if no date was given. Only the user's word or evidence sets it; triage proposes one in `next_step` or a question. |
| `origin` | ID | no | Source or event where it was made. |
| `priority` | enum | no | high, medium, low, set by triage against goals. |
| `effort` | enum | no | Rough size of the work, for `i_owe`: `quick` (under 30 min), `hour` (about an hour), `half_day`, `day`. Set by triage (inferred) or the user; used to protect focus time (`focus_time_needed`). |
| `insight` | text | no | One-line insight, e.g. why it may slip. |
| `next_step` | text | no | One recommended action. |
| `completed_on` | date | no |  |

## Status vocabulary
open, done, dropped, slipped (past due and still open; triage sets it)

## Links
Typically links to: people, projects, events, goals.

## Capture guidance
Record **explicit** promises automatically ("I'll send it Friday", "Dana will review by Tuesday"). Vague intentions ("we should look into that") become questions or are listed in the brief for confirmation, not commitments. Close only on evidence (sent email, delivered file, user says so). Promises between two other people (the user is neither owner nor counterparty) are not commitments: note them on the related project or person, or create a question if the user needs to track it.
