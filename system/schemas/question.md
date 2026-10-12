---
type: schema
name: question
folder: user/knowledge/questions/
---
# Schema: question

## What it is
An open question waiting for an answer.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `asked_by` | ID | no |  |
| `asked_on` | date | no |  |
| `answer` | text | no |  |
| `answered_on` | date | no |  |

## Status vocabulary
open, answered, dropped

## Links
Typically links to: projects, people, decisions, topics.

## Capture guidance
Create for unanswered questions that matter to the user's work, and for vague intentions that aren't commitments. When answered, record the answer and the source.
