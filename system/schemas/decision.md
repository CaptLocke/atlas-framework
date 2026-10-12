---
type: schema
name: decision
folder: user/knowledge/decisions/
---
# Schema: decision

## What it is
A choice that was made, with who decided, when, and why.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `decided_on` | date | no |  |
| `deciders` | list of IDs | no |  |
| `rationale` | text | no | The why. Always capture it if stated. |
| `alternatives` | list | no | Options considered. |
| `reversible` | bool | no |  |
| `revisit_on` | date | no |  |

## Status vocabulary
proposed, made, reversed, superseded

## Links
Typically links to: projects, events (where made), people, topics, sources.

## Capture guidance
Capture decisions from meetings, threads, and chat. A decision without a rationale is still recorded; add `rationale: unknown` and consider a question.
