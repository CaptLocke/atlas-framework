---
type: skill-reference
skill: atlas-review
---
# Weekly Review: sections and rules

Period: the ISO week (`YYYY-Www`) being reviewed; a Friday run covers Monday to now, and anything after the run is picked up next week. "Next week" = the following Monday–Sunday.

| Section | What goes in | Selection rule |
|---|---|---|
| **Summary** | 2–3 lines: the shape of the week and the one thing to act on | Written last |
| **Wins** | Things that moved forward: deliverables sent, decisions driven, milestones, problems solved | Evidence in a source; user's own work first |
| **Decisions made** | Decisions with `decided_on` in the week; who decided and the one-line why | All; group by project if >5 |
| **Commitments kept** | Commitments closed `done` in the week, both directions | Count + the notable ones |
| **Commitments slipped** | `slipped` (or open and past due) at the time of review; `i_owe` first | All `i_owe`; `waiting_on` past due > 3 days |
| **Stalled projects** | `active` projects with no update in 14+ days, or `health: at_risk|off_track` without a recent update | Each with its `next_step` or a suggested one |
| **Aging waiting-on** | Open `waiting_on` older than 7 days or past due | With counterparty, age, and a suggested nudge (offer a draft via `atlas-write`) |
| **People to reconnect with** | Key people (manager, reports, customers, stakeholders) past their `cadence` or with no contact in 30+ days, and people with open items both ways | Max 5 |
| **Next week** | Meetings that matter (1:1s, external, linked to open items), deadlines, commitments due, events needing prep | From calendar (`calendar.list_range`) and records |
| **Suggested priorities** | Max 5, ranked by active goals, then due dates and risk; each written as an outcome for the week ("Get Dana's MSA review unblocked"), since they become the Week Ahead's "This week's outcomes" | One-line reason each, citing the goal |
| **Accomplishments recorded** | The entries appended this week | Links to goals |

## File format
```markdown
---
type: review
date: 2026-10-16
period: 2026-W42
sources: ["[[sources/...]]"]
---
# Weekly Review · week 42 (Oct 12–18)

Good week for the enterprise launch: pricing is decided and the MSA is with legal. One thing to act on: Dana's contract review is a week overdue.

## Wins
- Shipped the pricing proposal to Jordan ([[commitments/send-pricing-feedback]]).
...
## Suggested priorities for next week
1. Close the MSA review with Dana: it gates the Q4 revenue goal ([[goals/2026-q4-enterprise-revenue]]).
```
Follow `user/profile/communication-style.md` for length and format. Sections with nothing say so in one line ("No decisions recorded this week.").

## Accomplishments
- **Goal record:** append to `accomplishments` a short dated entry, e.g. `"2026-10-16: Pricing model approved by leadership ([[decisions/2026-10-14-enterprise-tier-pricing]])"`, update `updated`, and add an `## Updates` line.
- **Running list** `user/work/accomplishments.md` (create with frontmatter `type: accomplishments` if missing), newest last, one line each:
  `- 2026-10-16 · Pricing model approved by leadership · [[goals/2026-q4-enterprise-revenue]] · [[decisions/2026-10-14-enterprise-tier-pricing]]`
  Accomplishments without a goal use `-` for the goal field.
- Dedupe by meaning: if the same accomplishment is already recorded (e.g., from a status update), skip it.
- An accomplishment is an outcome, not an activity: "Closed the Acme renewal" yes; "Had 12 meetings" no.
