---
type: schema
name: playbook
folder: user/knowledge/playbooks/
---
# Schema: playbook

## What it is
How something gets done, step by step.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `trigger` | text | no | When this playbook applies. |
| `steps` | list | no | Ordered steps. |
| `last_used` | date | no |  |
| `automatable` | bool | no | Candidate for a user job. |

## Status vocabulary
draft, active, retired

## Links
Typically links to: projects, people (owners), topics.

## Capture guidance
Create when the user describes a repeatable process or asks Nova to remember how something is done. Suggest automation when `automatable: true`.
