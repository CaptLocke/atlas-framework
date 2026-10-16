---
type: regression-expected
input: "01"
input_file: inputs/01-email-globex-security-review.md
covers: [source, organization, person, project, event, commitment(i_owe), commitment(waiting_on)]
---
# Expected: 01 Globex security review thread

Customer email thread. Tests new organization and person creation, both commitment directions from one thread, and not recording a promise already fulfilled in the same message.

## Sources
| ID | Level | Expectation |
|---|---|---|
| E01-S1 | M | One source, `kind: email`, for the whole thread (not one per message). `occurred_on` 2026-10-12 or 2026-10-13; `participants` include Priya Shah, Maya Chen, Raj Patel; `retention` summary or full; summary mentions the SOC 2 and DPA requests. |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E01-R1 | M | organization | Globex: `kind: customer` (or `prospect`), `domain: globex.example`. |
| E01-R2 | M | person | Priya Shah: email `priya.shah@globex.example`, `org` Globex, role Head of Operations, `relationship: customer` (or `prospect`/`external`/`stakeholder`; `person.md` maps evaluators in a pilot to `prospect`). |
| E01-R3 | S | person | Raj Patel: email `raj.patel@acme.example`, `org` Acme. (Must exist by end of run; see 00.) |
| E01-R4 | M | project | A Globex pilot project (e.g. `projects/globex-pilot`), created here or from input 04, linked to Globex, Priya, and Maya. Exactly one across the run (see 00). |
| E01-R5 | S | event or org field | Globex's current analytics contract ends 2027-01-31: captured as an event (`kind: deadline`, `start` 2027-01-31) linked to Globex, or in Globex's `relationship_status`/body. |

## Commitments
| ID | Level | Direction | Owner | Counterparty | Due | Notes |
|---|---|---|---|---|---|---|
| E01-C1 | M | i_owe | Maya | Priya | 2026-10-16 | Send SOC 2 Type II report. Status `open`. Linked to the Globex pilot project. |
| E01-C2 | M | waiting_on | Priya | Maya | 2026-10-21 | Signed pilot scope. Status `open` at end of run (input 08 is an unsigned draft). |
| E01-C3 | S | waiting_on | Priya / Globex legal | Maya | 2026-10-13 | DPA redlines "later today". Acceptable: not recorded at all, or recorded and closed `done` (`completed_on` 2026-10-13) with input 02 as evidence. |

## Must not
| ID | Expectation |
|---|---|
| E01-X1 | An open commitment for "send our standard DPA" (Maya attached it in the same message, so it's already done). |
| E01-X2 | The SOC 2 commitment recorded as `waiting_on`, or the signed scope as `i_owe`. |
| E01-X3 | E01-C3 recorded and still `open` after the run. |

## Scorer notes
Slugs are suggestions; match on meaning. Due dates must be exact for M items.
