---
type: schema
name: risk
folder: user/knowledge/risks/
---
# Schema: risk

## What it is
Something that could go wrong (`potential`) or already has (`active`, i.e. an issue).

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `likelihood` | enum | no | low, medium, high |
| `impact` | enum | no | low, medium, high |
| `owner` | ID | no |  |
| `mitigation` | text | no |  |

## Status vocabulary
potential, active (an issue), resolved

## Links
Typically links to: projects, goals, organizations, people.

## Capture guidance
Create from explicit concerns, blocking problems, or patterns `intelligence` finds (with reasoning and sources).
