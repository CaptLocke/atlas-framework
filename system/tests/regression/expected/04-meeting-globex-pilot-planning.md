---
type: regression-expected
input: "04"
input_file: inputs/04-meeting-globex-pilot-planning.md
covers: [source, event(meeting), person, decision, commitment(i_owe), commitment(waiting_on), question, risk(potential), idea, project(update)]
---
# Expected: 04 Globex pilot planning call

Multi-party customer meeting. Tests a jointly made decision, several commitments in both directions with relative dates, an open question, a stated risk, and a vague suggestion that must not become a commitment.

## Sources
| ID | Level | Expectation |
|---|---|---|
| E04-S1 | M | One source, `kind: meeting`, participants Maya, Raj, Priya, Tom. |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E04-R1 | M | event | Globex pilot planning: `kind: meeting`, `start` 2026-10-13T10:00-07:00, `status: held`, attendees the four people, `outcomes` summarized; linked to the Globex pilot project and E04-S1. |
| E04-R2 | M | person | Tom Becker: `org` Globex, role IT & Procurement (or similar), `relationship: customer` (or `prospect`/`external`; `person.md` maps evaluators in a pilot to `prospect`). |
| E04-R3 | M | decision | Pilot starts with Globex EMEA operations only, 50 seats; North America later as phase 2. `rationale`: NA team is mid data-warehouse migration. `decided_on` 2026-10-13; deciders include Priya and Maya (Raj optional). Linked to the Globex pilot project. |
| E04-R4 | M | project (update) | The single Globex pilot project now reflects EMEA-only, 50 seats, planned start 2026-11-09 (`start` field or body), with an Updates line citing E04-S1. |
| E04-R5 | M | question | EMEA data residency: can Acme guarantee EU-only storage for the pilot workspace? `asked_by` Tom; `status: open`; linked to the Globex pilot project. (A Maya `i_owe` "find out", `due: null`, is also acceptable in addition, not instead.) |
| E04-R6 | M | risk | If the pilot start slips past mid-November, Globex EMEA year-end close (from 2026-12-01) will depress usage and weaken results. `status: potential`; linked to the Globex pilot project. |
| E04-R7 | M | idea | Joint Globex case study if results are good. `status: seed` (or `parked`); linked to Globex. A question record instead of an idea is acceptable. |

## Commitments
| ID | Level | Direction | Owner | Counterparty | Due | Notes |
|---|---|---|---|---|---|---|
| E04-C1 | M | waiting_on | Tom | Maya | 2026-10-23 | Confirm whether Globex security requires SAML SSO for the pilot ("end of next week"). |
| E04-C2 | M | waiting_on | Raj | Maya | 2026-10-19 | Revised order form draft ("by Monday"). |
| E04-C3 | M | i_owe | Maya | Priya (or Tom / Globex) | 2026-11-02 | Set up the pilot workspace and send admin invites. |

## Must not
| ID | Expectation |
|---|---|
| E04-X1 | A commitment for the joint case study ("we should probably think about…"). |
| E04-X2 | A second Globex pilot project (e.g. both `globex-pilot` and `globex-emea-pilot`). |
| E04-X3 | A commitment with direction other than `i_owe`/`waiting_on`, or a commitment between two non-users recorded as if Maya owed it (e.g. Raj's order form as `i_owe`). |
