---
type: regression-expected
input: "11"
input_file: inputs/11-email-vague-intentions.md
covers: [source, vague intentions → question/idea, no false commitments]
---
# Expected: 11 Vague intentions ("we should look into…")

A colleague floats ideas with no owner or date, and Maya agrees loosely. Tests that vague intentions become questions or ideas, never commitments.

## Sources
| ID | Level | Expectation |
|---|---|---|
| E11-S1 | M | One source, `kind: email`, participants Raj and Maya. |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E11-R1 | M | question or idea | Globex APAC expansion, to revisit after the pilot: a question (`status: open`), an idea (`seed`/`parked`), or a "confirm?" entry in `questions.md` (kind `commitment`). Linked to Globex. |
| E11-R2 | S | question or nothing | "Someone should update the enterprise one-pager now that we're per-seat": a question/confirm line or nothing. If captured, linked to the per-seat pricing decision or the enterprise launch project. |

## Must not
| ID | Expectation |
|---|---|
| E11-X1 | Any commitment (either direction) for the APAC expansion or a chat with Priya about it. |
| E11-X2 | An `i_owe` (or `waiting_on` from Raj) for updating the enterprise one-pager. |
