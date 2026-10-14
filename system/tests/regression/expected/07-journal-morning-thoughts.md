---
type: regression-expected
input: "07"
input_file: inputs/07-journal-morning-thoughts.md
placed_at: user/journal/2026/10/2026-10-14.md
covers: [source(journal), journal handling, commitment(dedupe), person(fact update), idea, question(dedupe), vague intention, profile proposal]
---
# Expected: 07 Morning Thoughts (2026-10-14)

A messy brain dump. Tests verbatim journal handling, dedupe against records created from yesterday's inputs, a stated fact about an existing person, an idea, a vague intention, and a profile observation that must be proposed rather than applied.

## Journal and source
| ID | Level | Expectation |
|---|---|---|
| E07-J1 | M | The `## Morning Thoughts` text in `user/journal/2026/10/2026-10-14.md` is byte-identical to the input (no corrections, no reformatting). |
| E07-J2 | M | Journal frontmatter `processed` includes `morning`; `source` points to a journal source. |
| E07-S1 | M | One source, `kind: journal`, for 2026-10-14. |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E07-R1 | M | person (existing) | `people/dana-ruiz` records that she prefers a quick call over email for anything urgent (`provenance: stated` or an Updates line citing the journal source). |
| E07-R2 | M | idea | Pilot-to-production credit: pilot fees count toward year one. `status: seed`; linked to the Globex pilot project or Globex. |
| E07-R3 | S | idea links | Also linked to the pricing topic and Initech. |
| E07-R4 | M | question (existing) | The EMEA data residency question from input 04 is **updated** (Updates line; possible answerers Sam or the infra team), not duplicated. |
| E07-R5 | M | vague intention | "Revisit the analytics dashboard performance thing someday" becomes a question record, a `questions.md` entry (kind `commitment`), or a "confirm?" line in the brief. Not a commitment. |
| E07-R6 | M | profile proposal | "Protect Friday mornings for deep work, no meetings before noon" appears as an open `profile` proposal in `user/inbox/questions.md` (e.g. for `working-style.md` or `preferences.md`, tagged `[stated · proposed]`). |

## Commitments
| ID | Level | Direction | Owner | Counterparty | Due | Notes |
|---|---|---|---|---|---|---|
| E07-C1 | M | i_owe | Maya | Lena | 2026-10-14 | Same record as E05-C2, now dated today, with an Updates line citing the journal source. Exactly one such commitment exists. |

## Must not
| ID | Expectation |
|---|---|
| E07-X1 | Any edit to the user's journal wording. |
| E07-X2 | A commitment for the analytics dashboard performance item. |
| E07-X3 | Any change to files in `user/profile/` (profile updates are `propose`). |
| E07-X4 | A calendar event, hold, or approval to block Friday mornings (calendar management was not requested). |
| E07-X5 | A second "talk to Lena" commitment or a second data residency question. |
