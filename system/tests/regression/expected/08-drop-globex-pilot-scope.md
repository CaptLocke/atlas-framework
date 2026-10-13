---
type: regression-expected
input: "08"
input_file: inputs/08-drop-globex-pilot-scope.md
placed_at: user/inbox/drop/Globex_Pilot_Scope_v2.md
covers: [source(file), project(update), event(milestone), drop handling, evidence discipline]
---
# Expected: 08 Dropped file: Globex pilot scope v2

A draft document dropped for Atlas. Tests filing a dropped file, enriching the existing project instead of duplicating it, and **not** closing a commitment on insufficient evidence.

## Sources
| ID | Level | Expectation |
|---|---|---|
| E08-S1 | M | One source, `kind: file` (or `doc`), title naming the pilot scope v2; `retention: summary` (or full); `file_pointer`/`origin_uri` names the dropped file; summary notes it's an **unsigned draft**. |
| E08-S2 | M | The file is gone from `user/inbox/drop/` after the run (copied to `user/library/` is optional). |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E08-R1 | M | project (existing) | The single Globex pilot project gains `start` 2026-11-09 and `target` 2026-12-18 (or both in the body), success criteria summarized in the body, and an Updates line citing E08-S1. |
| E08-R2 | S | events | Milestones for pilot start (2026-11-09) and pilot end/results review (2026-12-18); mid-pilot review (2026-11-30) optional. `kind: milestone` or `deadline`, `status: scheduled`, linked to the project. |
| E08-R3 | S | links | The project's open items link to the existing data residency question and Tom's SAML commitment rather than creating new ones. |

## Commitments
| ID | Level | Expectation |
|---|---|---|
| E08-C1 | M | E01-C2 (Priya: signed pilot scope, due 2026-10-21) is still `open`. A v2 draft "for review, not signed" is not evidence of completion. |
| E08-C2 | M | No new commitment duplicating E04-C3 ("pilot workspace ready, admins invited 2 Nov"). |

## Must not
| ID | Expectation |
|---|---|
| E08-X1 | E01-C2 marked `done`. |
| E08-X2 | A second Globex pilot project, or a second "workspace/admin invites" commitment. |
| E08-X3 | The binary original (or this file) committed under `user/knowledge/`. |
