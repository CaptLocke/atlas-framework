---
type: regression-expected
input: "05"
input_file: inputs/05-meeting-1on1-jordan.md
covers: [source, event(one_on_one), goal, decision, project(new, paused), commitment(i_owe), commitment(waiting_on), playbook, person, organization]
---
# Expected: 05 Maya / Jordan 1:1

Manager 1:1. Tests goal capture, a decision that changes a project's status, a playbook described in conversation, and a commitment that input 07 repeats (dedupe).

## Sources
| ID | Level | Expectation |
|---|---|---|
| E05-S1 | M | One source, `kind: meeting`, participants Maya and Jordan. |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E05-R1 | M | event | Weekly 1:1: `kind: one_on_one`, `start` 2026-10-13T15:00-07:00, `status: held`, attendees Maya and Jordan; `series` set (weekly 1:1). |
| E05-R2 | S | event | Next 1:1 on 2026-10-20, `status: scheduled`. |
| E05-R3 | M | goal | Q4 2026: Globex pilot live and signed, plus three enterprise customers signed on the new tier by 2026-12-31. `horizon: quarter`, `period: 2026-Q4`, `target` mentions 3 customers, `owner` Maya, `status: active` (or `draft`); linked to the Globex pilot and enterprise launch projects. |
| E05-R4 | M | decision | Drop the self-serve onboarding revamp from Q4 and focus on the enterprise launch. `rationale` mentions engineering capacity (Sam's team on SSO) and/or enterprise revenue focus. Deciders Jordan (and Maya). `decided_on` 2026-10-13. |
| E05-R5 | S | decision field | `revisit_on` in January 2027, or "revisit in January" in the body. |
| E05-R6 | M | project | Self-serve onboarding revamp: `status: paused` (or `cancelled`), never `active`; linked to E05-R4. |
| E05-R7 | M | person | Lena Park: `org` Acme, design (role may be inferred as design lead; mark `provenance` accordingly). |
| E05-R8 | S | person | Carla Mendes: `org` Initech, role VP of Data. |
| E05-R9 | S | organization | Initech, `kind: prospect` (one record across the run). |
| E05-R10 | M | playbook | Launch readiness review: `trigger` about one week before a launch; `steps` cover the cross-functional review (eng, support, sales, legal), checklist (docs, support trained, pricing live in billing, contracts approved), red items get owner and date, go/no-go two days before launch. `status: active`. |
| E05-R11 | S | playbook link | Playbook linked to `projects/enterprise-launch`. |

## Commitments
| ID | Level | Direction | Owner | Counterparty | Due | Notes |
|---|---|---|---|---|---|---|
| E05-C1 | M | i_owe | Maya | Jordan | 2026-10-20 | Q4 roadmap one-pager "before our next 1:1". |
| E05-C2 | M | i_owe | Maya | Lena (or Jordan) | null here; 2026-10-14 after input 07 | Tell Lena the onboarding revamp is dropped. **One record** shared with input 07 (see E07-C1). |
| E05-C3 | M | waiting_on | Jordan | Maya | null, or a date 2026-10-19 to 2026-10-23 | Intro to Carla Mendes at Initech ("next week"). |

## Must not
| ID | Expectation |
|---|---|
| E05-X1 | The self-serve onboarding revamp project left `active` or `proposed`. |
| E05-X2 | The goal written into `user/profile/profile.md` directly (goal records are knowledge; the profile only links goals, and profile edits are `propose`). |
| E05-X3 | A commitment for "revisit onboarding in January". |
