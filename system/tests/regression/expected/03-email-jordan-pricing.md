---
type: regression-expected
input: "03"
input_file: inputs/03-email-jordan-pricing.md
covers: [source, decision(with rationale), commitment(i_owe), topic, organization(mention)]
---
# Expected: 03 Jordan pricing email

Tests a decision reported second-hand (made the previous day) with its rationale, and an `i_owe` with a weekday due date.

## Sources
| ID | Level | Expectation |
|---|---|---|
| E03-S1 | M | One source, `kind: email`, participants Jordan and Maya. |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E03-R1 | M | decision | Enterprise tier priced per seat with a 25-seat minimum (instead of per workspace). `status: made`; `decided_on` 2026-10-12; `deciders` include Jordan (leadership staff may be noted in text); `rationale` says buyers' procurement budgets per seat and per-workspace pricing stalled deals (Initech, Hooli). Linked to `projects/enterprise-launch`. |
| E03-R2 | S | decision field | `alternatives` lists per-workspace pricing. |
| E03-R3 | S | topic | A pricing topic (e.g. `topics/pricing` or `topics/enterprise-pricing`) linking this decision; it should also link the pilot-credit idea from input 07 (see 00). |
| E03-R4 | S | organization | Initech, `kind: prospect` (may be created here or from input 05). Hooli: optional, no penalty either way. |
| E03-R5 | M | person (existing) | `people/jordan-lee` reused (no duplicate); `last_contact` 2026-10-13. |

## Commitments
| ID | Level | Direction | Owner | Counterparty | Due | Notes |
|---|---|---|---|---|---|---|
| E03-C1 | M | i_owe | Maya | Jordan | 2026-10-15 | Feedback on the enterprise pricing proposal (discount bands). Status `open`. |

## Must not
| ID | Expectation |
|---|---|
| E03-X1 | The decision recorded with `status: proposed` or without a rationale. |
| E03-X2 | A commitment owed by Jordan for "lock pricing". |
