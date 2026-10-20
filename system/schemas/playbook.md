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
| `trigger` | text | no | When this playbook applies, in plain words ("a customer renewal is 60 days out"). Atlas matches new work against it. |
| `anchor` | text | no | The date a run counts from ("the renewal date", "the start date"). Step `when` offsets are relative to it. |
| `steps` | list | no | Ordered steps. Each is a string, or a mapping: `step` (what to do, required), `when` (offset from the anchor: `-30d`, `+2d`), `draft` (`email` or `message` when the step is a communication Atlas should pre-draft), `to` (who it goes to, as a role: "customer champion", "my manager"). |
| `auto_start` | bool | no | `true`: Atlas starts a run as soon as the trigger matches. Default `false`: Atlas asks first. |
| `last_used` | date | no | When a run last finished. |
| `automatable` | bool | no | Candidate for a user job (`atlas-extend`), for work beyond a checklist. |

## Status vocabulary
draft, active, retired

## Links
Typically links to: projects, people (owners), topics.

## Runs
A **run** is one use of the playbook: a project record (`scale: task_group`, `links.playbooks: ["[[playbooks/<slug>]]"]`, `target` = the anchor date) with one `i_owe` commitment per step (`origin: "[[playbooks/<slug>]]"`, due = anchor + `when`). Triage, the brief, the Work page, and email drafts then handle the checklist like any other work. How runs start, pre-draft, and flag missed steps: `.claude/skills/atlas-triage/reference/playbooks.md`.

Example:
```yaml
trigger: A customer renewal is 60 days out
anchor: the renewal date
auto_start: false
steps:
  - { step: "Review usage and open issues for the account", when: -60d }
  - { step: "Send the renewal quote", when: -45d, draft: email, to: "customer champion" }
  - { step: "Renewal call", when: -30d }
  - { step: "Send the contract for signature", when: -14d, draft: email, to: "customer champion" }
  - { step: "Tell my manager the outcome", when: +1d, draft: message, to: "my manager" }
```

## Capture guidance
Create with `status: active` when a repeatable process is stated: the user describes one or asks Atlas to remember how something is done ("save how we do renewals as a playbook"), or someone they work with describes it in a source (a manager in a 1:1: "here's how we run launch reviews"). Atlas also proposes one when it sees the same work recur (`.claude/skills/atlas-triage/reference/playbooks.md` §1); a playbook Atlas infers this way is `status: draft` until the user confirms it. Suggest automation when `automatable: true`.
