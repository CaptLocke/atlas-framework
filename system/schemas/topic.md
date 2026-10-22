---
type: schema
name: topic
folder: user/knowledge/topics/
---
# Schema: topic

## What it is
A theme that spans projects and time.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `scope` | text | no | What the topic covers and doesn't. |

## Status vocabulary
active, dormant. A topic not `updated` for 90 days goes `dormant` in the user health check (`.claude/skills/atlas-health/reference/user-health.md`); linking a new record to it makes it `active` again.

## Links
Typically links to: everything relevant: projects, decisions, ideas, risks, people.

## Capture guidance
Create when a theme recurs across three or more records from at least two sources (pricing discussed in a decision, a commitment, and an idea), and link those records to it. Topics are the connective tissue for exploration ("what do we know about churn?"). They are Atlas's own structure: create, link and retire them without asking the user.

Capture creates one when the recurrence is visible in what it is filing (an import, a batch, records it just resolved). Inputs that arrive one at a time rarely show it, so the `intelligence` job also searches for each theme its change set touches and creates the topic when this bar is met (`atlas-insights` §A).
