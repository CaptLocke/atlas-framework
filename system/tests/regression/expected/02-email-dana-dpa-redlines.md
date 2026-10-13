---
type: regression-expected
input: "02"
input_file: inputs/02-email-dana-dpa-redlines.md
covers: [source, person(update), risk(potential), commitment(waiting_on), data-rules(legal_privileged: ignore)]
---
# Expected: 02 Dana DPA redlines

Internal thread with legal. Tests resolving to a seeded person (no duplicate), a `waiting_on` commitment from a colleague, and the `legal_privileged: ignore` data rule on an attached privileged memo.

## Sources
| ID | Level | Expectation |
|---|---|---|
| E02-S1 | M | One source, `kind: email`, participants Maya and Dana (Globex legal may be listed as text, not a person record). |
| E02-S2 | S | The privileged attachment is either not mentioned or mentioned only as a pointer ("a privileged memo was attached; not stored"), with no content. |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E02-R1 | M | person (existing) | `people/dana-ruiz` updated (`last_contact` 2026-10-13 and/or an Updates line citing E02-S1). No new Dana record. |
| E02-R2 | S | risk | Globex DPA asks for unlimited data-breach liability; signature could slip past the 2026-11-09 pilot start. `status: potential`, `impact: high` (or medium), linked to the Globex pilot project and Globex. Dana's body text is business communication from counsel; if Atlas judged the whole email privileged and stored only a pointer, mark this item N/A rather than failed, and check E02-C1 still passed. |

## Commitments
| ID | Level | Direction | Owner | Counterparty | Due | Notes |
|---|---|---|---|---|---|---|
| E02-C1 | M | waiting_on | Dana | Maya | 2026-10-20 | Review the Globex DPA redlines. Status `open`. |

## Must not
| ID | Expectation |
|---|---|
| E02-X1 | **Privileged content stored anywhere.** Search all of `user/` (records, sources, briefs, insights, run reports, commit messages) (including any copy in `user/library/`) for: `3x`, `super-cap`, `fallback`, `15 days`, `sub-processor notice`. Any hit that comes from the memo fails. |
| E02-X2 | A person record for "Legal Team" / `legal@globex.example`. |
| E02-X3 | A duplicate Dana record (e.g. `people/dana`, `people/dana-ruiz-acme`). |
| E02-X4 | Any commitment owed by Maya to "review the DPA". |
