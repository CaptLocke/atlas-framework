# Insight kinds, detection, and scoring

Fictional examples (user Maya Chen, PM at Brightline; manager Jordan Lee; customer Acme).

## Kinds
| Kind | Look for | Example insight |
|---|---|---|
| `risk` | Repeated slips on one project; a dependency's owner gone quiet; target date close with health not on track; the same problem in several sources; a decision reversed late | "Orion has had 3 supplier slips in 2 weeks and launches in 3 weeks." |
| `gap` | Decisions with no owner or no rationale; questions open > 14 days on active projects; projects without `next_step` or owner; commitments with no due date that a goal depends on; meetings held with no recorded outcome. Sweep: an open risk with no `mitigation` or no `owner` and nothing linked in 21 days; a `proposed` decision whose affected people (on its linked projects) appear in none of its sources; a `proposed` decision with a meeting on it within 3 days (the suggested action offers a decision brief, `SKILL.md` §D) | "No decision recorded on the pricing question raised two weeks ago." |
| `quiet_person` | Contact has lapsed with a key person (manager, reports, key customers, stakeholders): days since `last_contact` > 1.5 × their `cadence` interval, or > 30 days with no `cadence` while there are open items either way (the same test as `quiet` in Work's People section); a stakeholder not updated on a project they care about. Sweep: a `waiting_on` commitment whose owner hasn't been in a source for 14 days, or since half the time to its `due` passed | "You haven't sent Jordan a status update in 3 weeks; your usual rhythm is weekly." |
| `pattern` | A topic gaining ≥3 newly linked records from ≥3 sources in 30 days, after it was created (link the topic); recurring meeting overruns; one person behind many slipped items | "Three customers raised the onboarding import bug this month." |
| `connection` | Two projects or people working on overlapping things without links; a new item that answers an open question elsewhere. Sweep: a `buried` pair from `relations.py` (two records nothing links that share people, topics or sources), including ideas meeting: an idea that would answer a risk or question, or two ideas or an idea and a project that would combine or clash | "Sam's budget model answers the open question on the pilot ceiling." |
| `contradiction` | Two non-superseded records disagree (dates, owners, figures) | "The MSA due date is 10/14 in one record and 10/16 in Dana's latest email." |
| `opportunity` | A request from several customers matching an idea; a free slot before a deadline; a win worth sharing with a stakeholder; a reusable playbook from repeated work | "Two prospects asked for a partner tier; it matches your seed idea." |
| `goal_drift` | Active goal with little linked activity this month, or time spent mostly on unlinked work. Sweep: every active goal, changed or not, with nothing linked updated in 21 days |
| `collision` | Within the next 28 days: two things that need the user at once, or one thing landing where it can't be done. Time off, travel or a holiday over a due date, a key meeting or a playbook step; two due dates or key meetings for different people on one day with no slack; a `waiting_on` due after the `i_owe` or event that needs it; a launch or target date before a dependency's | "Your time off (11/18–11/22) covers the Orion launch review on 11/20." |
| `stale_decision` | A `made`, non-superseded decision whose `rationale` a newer fact undercuts: the price, date, person, constraint or assumption it rests on has changed. Cite the decision, quote its rationale, and cite the new fact | "You chose Fastparts for its 2-week lead time; their latest quote says 6 weeks." |
| `correlation` | A `together` or `follows` candidate from `relations.py` that holds up when its records are read: two topics, organizations or people that keep turning up in the same sources, or one whose sources are often followed by a slip, an active risk, an off-track project or a reversed decision on the same work. Never stated as a cause | "The last 3 of 4 times Fastparts sent a delay notice, a commitment of yours slipped within two weeks." | "Your Q4 retention goal has had no linked work in 3 weeks." |

## Scoring (0–1 each; multiply)
**Goal relevance**
- 1.0 directly affects an active goal or the user's manager's stated priority
- 0.7 affects an active project linked to a goal, or a key relationship
- 0.4 affects other active work
- 0.1 general interest

**Urgency**
- 1.0 consequence within 3 days, or already happening
- 0.7 within 2 weeks
- 0.4 within the quarter
- 0.2 no time pressure

**Novelty**
- 1.0 not surfaced before
- 0.6 surfaced before but something material changed (state what)
- 0.2 same as an insight in the last 30 days (usually: don't write it)
- 0.0 dismissed before and nothing changed

Example: import bug pattern → relevance 1.0 (retention goal) × urgency 0.7 × novelty 1.0 = 0.70.

## Engagement adaptation
Per kind over the last 60 days: `act_rate = acted / (acted + dismissed + expired)`, `dismiss_rate = dismissed / same`.
- Adjusted score = score × (0.6 + 0.8 × act_rate − 0.4 × dismiss_rate), clamped to 0–1.
- Kinds with fewer than 5 outcomes: no adjustment yet.
- `risk` insights with impact high are never adjusted below 0.4.
- If a summary exists in `user/.state/health.yaml` (computed monthly), prefer it; otherwise compute from `insights.md` plus the archive files for the window (`user/inbox/archive/*-insights.md`).

## Relationship candidates (`relations.py`)
The tool finds where to look; reading decides. For each candidate the sweep weighs, read the records it names (and, for `follows`, each instance's source and outcome) and keep it only if:
- the link is real work, not an artifact (two records citing one big meeting share nothing more than that meeting; a person who is in every source on a project follows everything on it);
- it tells the user something no single record says, and something they'd act on: link the records, raise it, ask someone, plan around it;
- for `follows`, the outcomes plausibly connect to the earlier sources (the delay notice is about what slipped), and the counts are given as they are: "3 of 4", never "always" or "causes".
Most candidates won't make it: that's expected. A kept candidate is a `connection` (buried) or a `correlation` (together, follows), and its suggested action can be to link the records ("Link Orion and Helix: they share Dana, Sam and SSO"), which Atlas does on a yes (`records_write`).

## Writing an insight
- **Insight:** one sentence, specific, with the number or fact that makes it real. A `correlation` says what moved together or what tended to follow what, with the counts; it never says one thing caused another ("tends to come before", "keeps turning up with").
- **Why it matters:** tie to a goal, person, project, or date.
- **Sources:** the records/sources that show it (≥1; ≥3 for patterns).
- **Suggested action:** one concrete, optional step. When the step is a message to one person or a small group ("Email Sam a holding answer", "Ping Tomás in #eng"), name the recipient and the channel, and add `- **Draft for:** [[people/<slug>]] · email` (or `message`). `email-drafts` then writes the draft, so the insight arrives ready to send. Don't add it for actions that are meetings, decisions, or the user's own work.

Entry example:
```markdown
## I-2026-10-12-03 · new · score 0.70
- **Kind:** pattern
- **Insight:** Three customers raised the onboarding import bug this month.
- **Why it matters:** Relates to the open risk on Support Revamp and your Q4 retention goal.
- **Sources:** [[sources/2026-10-03-globex-ticket]], [[sources/2026-10-09-acme-call]], [[sources/2026-10-11-initech-email]]
- **Links:** [[topics/onboarding-import]], [[risks/onboarding-import-failures]], [[goals/2026-q4-retention]]
- **Suggested action:** Raise at Thursday's product sync.
- **Status history:** new 2026-10-12
```
