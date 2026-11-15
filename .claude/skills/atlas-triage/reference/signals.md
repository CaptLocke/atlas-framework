# Triage signals

Fictional examples (user Maya Chen; manager Jordan Lee; Acme counsel Dana Ruiz).

## Completion evidence
| Strong (close it) | Weak (ask instead) |
|---|---|
| Sent email to the counterparty containing the promised file or answer, or a link to it | Sent email to the counterparty about the topic, no attachment or link |
| Counterparty replies "got it, thanks" to the deliverable | Meeting with the counterparty about it happened (may or may not have covered it) |
| Task in the task tool marked complete and it maps to this commitment | Deliverable file created in `user/work/deliverables/` but no send evidence |
| The user says it's done (in chat or journal) | Someone else says "I think Maya sent it" |
| A `deliverable` Source linked to the commitment and the user confirmed delivery | Calendar event titled like the deliverable, when the deliverable is a thing, not the meeting |
| A held meeting with the counterparty that was itself the deliverable ("walk Jordan through the mockups") | |

For `waiting_on`: the counterparty's message delivering it, or a Source showing the thing exists (e.g. the signed MSA arrived).

**Where to look.** Every category mapped in `connectors.yaml`, not only mail. Read since the commitment was created, on the counterparty and the deliverable:
| Category | Strong | Weak |
|---|---|---|
| mail | Sent to the counterparty with the file, a link to it, or the answer; their "got it" | Sent about the topic, nothing attached or linked |
| messaging | The user's message to the counterparty (DM or channel) delivering it or linking it; their "thanks, got it" | A message about the topic; a thumbs-up reaction |
| tasks | The mapped task marked complete | The task moved to review or a done-like column |
| files | — | The deliverable shared with the counterparty with no message, or edited after its last mention |
| calendar | A `held` event with the counterparty that was the deliverable itself (a walkthrough, demo, review or session the user promised to run), on or after `created`, that the user organized or accepted | An event about the deliverable; one still `scheduled`, `cancelled`, or declined |
| meetings | The transcript has the counterparty confirming it | It came up in a meeting with them |

A `waiting_on` reads the same table the other way round: the owner's message, task or file delivering it to the user.

### Closing without asking
A wrong close hides something the user still owes until someone chases them; a question costs one line in the brief. So a signal closes without asking only when all three hold, and is a Looks done question otherwise:
1. **It reached them.** The thing reached the counterparty (for `waiting_on`, the user), or the meeting was the thing.
2. **It's this commitment.** Same counterparty and deliverable, on or after `created`.
3. **Nothing since says otherwise:** the counterparty asking for it again, "still waiting on…", the meeting moved.

| Signal | Closes? | Why |
|---|---|---|
| A sent message to them with the file, a link to it, or the answer | Yes | A link delivers it as an attachment does |
| A held meeting that was the deliverable | Yes | Holding it was the promise; a cancelled, declined or still `scheduled` one doesn't count |
| A meeting about it, a file shared with no message | No: ask | It may not have covered it; sharing isn't sending |
| A `due` long past and nothing since | Never | Absence isn't evidence; §Aging asks instead |

Each close without the user's word is shown once in the next brief (`atlas-brief` §A step 4.4), so a wrong one is seen. When a later source says otherwise (condition 3) about a commitment Atlas closed, reopen it (`open`, or `slipped` if past `due`), with an Updates line citing that source, and log `wrong_close` (`reference/learning.md` §1), which the monthly review counts.

## Priority rubric
Score each open commitment, then map: high (top ~20%), medium, low.
1. **Goal link:** linked (directly or via its project) to an active goal → a boost **scaled by the goal's `rank`** (`system/schemas/goal.md` §Ranking); to the user's manager's stated priorities → boost.
   - With N ranked active goals, a goal of rank r gets a weight of `1 − 0.6 × (r − 1) / (N − 1)`: rank 1 = 1.0 (the full strong boost), the lowest-ranked = 0.4. With one ranked goal, its weight is 1.0.
   - Unranked active goals get 0.4 while any goal is ranked, and 1.0 when none are (so a user who never ranks sees the same behavior as before).
   - A commitment linked to several goals takes the highest weight, not the sum.
   - Example, four ranked goals: rank 1 = 1.0, rank 2 = 0.8, rank 3 = 0.6, rank 4 = 0.4.
   - In the `insight` or the brief's reason, name the goal when its rank drove the priority ("Supports your #1 goal, Q4 retention").
2. **Who's on the other side** (`relationship`, `system/schemas/person.md` §Relationships): for `i_owe`, the counterparty's; for `waiting_on`, the owner's, since the counterparty is the user. `manager`, `board`, `customer`, or a senior `stakeholder` → boost; `prospect` in an active deal → boost; `peer`, `report`, `vendor`, `partner`, `external` → neutral.
3. **Time:** due within 3 days or already slipped → boost; no date → neutral.
4. **Consequence:** blocks others (others' commitments or a decision depend on it), or affects revenue, legal, or launch dates → boost.
5. **Effort hint:** quick wins (<30 min) due soon can be raised to clear them.
Never rank purely by due date.

- **Between full passes.** Light mode bands a new commitment against the current set and moves nothing else, so `high` can run past ~20% until the next full pass rebalances it, within a day on Lean and Standard. On Full, full passes (`triage-drafts`) run on weekdays only, so at weekends it can last from Friday evening to Monday morning.
- **Learned rules sit outside the band.** A `## Triage rules` priority line (`reference/learning.md` §3) applies after the rubric and stands even when it takes `high` past ~20%.

## Top priorities
The brief's Top priorities (3, up to 5) come from this rule, so the same records give the same list; only the wording is the brief's.
1. **Candidates:** open or slipped `high` commitments, and `active` projects whose `health` is `at_risk` or `off_track`. Count lines after folding (step 3): fewer than 3 → add `medium` commitments, after the `high` ones, until there are 3.
2. **Order:** goal weight first (item 1 of the rubric; a project takes its `goal`'s weight, anything unlinked 0), then `due` ascending (a project's `target`; none last), then title.
3. **Take** the top 3, then each of the 4th and 5th that ties the 3rd on goal weight, so up to 5; fewer when fewer qualify. A commitment whose project is also a candidate folds into that project's line and takes no slot of its own.
4. **Reason:** one line naming the goal or the person that put it there; a project is phrased as the outcome ("Unblock the Acme MSA").

## Aging
**Waiting on:**
- Days waiting = business days since `created`, or since the last follow-up line in Updates.
- Aging if: past due; or >5 business days with no movement; or due within 2 days with no sign of progress.
- Use person cadence and history for the channel: "Dana usually replies within a day to calls; email has gone unanswered twice".

**I owe, with no date:** it never slips and never reaches Due from you, so it needs its own check.
- **Movement** is an Updates line recording progress or contact, from a source or the user (a draft started, a message about it, the user's word), or the user keeping it undated (below). Triage's own changes to `priority`, `effort`, `insight` or `next_step` are not movement.
- Aging if: no `due`, and more than 10 business days since the latest movement, else since `created`. Days while away mode is on don't count.
- Ask once: a `questions.md` entry (kind `commitment`) with `- **Links:** [[commitments/<slug>]]`, only if no open entry links it and none was answered or dismissed since the latest movement: "You told Jordan you'd do the survey analysis on 10/02 and there's no date. When will you do it, or should I drop it?"
- The answer: a date sets `due` (the user's word); "drop it" drops it; "keep it undated", or a dismissal, adds the Updates line `kept undated <date> (user)`, which is movement, so the clock restarts.
- During away, nothing is asked; the check runs again after the return.

**I owe, slipped and quiet:** a slipped item can sit overdue for weeks with nothing happening, and the brief's Due from you shows it every day.
- Aging if: `slipped`, and more than 10 business days since the latest movement, else since `due` (being filed from history isn't movement). Away days don't count.
- Ask once, under the same rule as above: "You owe Dana the reseller terms comments, due 9/25, and nothing's happened since. Is it done, is there a new date, or should I drop it?"
- The answer: done closes it (the user's word); a date sets `due` and reopens it (step 6); "drop it" drops it; "still on", or a dismissal, adds `kept overdue <date> (user)`, which is movement.

## Never the user's
Since 2.6.0 nothing new is filed unless the user is one side (`system/rules/knowledge.md` §Commitments), but ones filed before stay. A commitment is **never the user's** when the user's own person record (`relationship: self`) is neither its `owner` nor its `counterparty`.
- **Ask once, grouped:** one `questions.md` entry (kind `commitment`) listing every open or slipped one, with `- **Links:**` naming each: "These 2 are between other people, not you: Dana's contract playbook for Jordan, Jordan's approval of Dana's contractor request. Drop them, or keep any?" Asked only when one isn't already linked by an open entry or kept (below). Not during away.
- **Until answered:** `priority: low`, `insight` saying it's between other people; no date question, no follow-up and no `commitment_overdue` approval (the worth-chasing check already needs the user as counterparty).
- **The answer:** drop → `dropped` with the reason "between other people (user, <date>)", and one Updates line on its project or person record keeps the promise as context; keep → `kept as the user's <date> (user)` in Updates, and it is never asked about again. Answers to this question log no feedback (`reference/learning.md` §1): the rule that filed them has already changed.

## Insight and next-step examples
| Record | insight | next_step |
|---|---|---|
| `waiting_on` Dana: MSA redlines (6 days late) | Dana hasn't replied in 6 days; she answered faster by phone last time. | Call Dana before Thursday's steering meeting. |
| `i_owe` pricing feedback to Jordan (due tomorrow) | Due tomorrow; Jordan needs it for Friday's exec review. | Finish section 3 tonight; send before the 11:00 AM 1:1. |
| `i_owe` SOC report to Acme (slipped 2 days) | Blocked on Security; Acme's renewal decision depends on it. | Ask Sam in Security for the PDF today. |
| Project Orion launch (at_risk) | Two supplier commitments slipped and the launch is 3 weeks out. | Confirm supplier dates at Wednesday's ops sync. |
| `i_owe` survey analysis (no due date) | No date agreed; Jordan mentioned it twice this month. | Propose a date to Jordan: suggest Fri 10/23. |

Bad examples (too generic): "Follow up soon." "This is important." "Keep an eye on it."

## Follow-up draft guidance (overdue waiting_on)
Drafted only by the `atlas-write` email-drafts procedure (`atlas-write/reference/email-drafts.md`), guarded by the commitment's Updates marker `follow-up draft created <date>`. Triage adds the approvals entry (once per commitment) and hands off.
- Short (3–5 sentences), friendly, specific: what, when it was due, what the user needs, an easy next step.
- Voice per `system/rules/writing.md` (internal → personal; customer → house unless the relationship is personal and informal).
- Reply in the original thread when there is one.
- Approvals entry example:
```markdown
## A-2026-10-12-01 · pending
- **Action:** send_communication: send follow-up to Dana Ruiz
- **Why:** Dana's MSA redlines are 6 days overdue ([[commitments/dana-msa-redlines]])
- **Prepared:** Outlook draft "MSA redlines: quick check-in" (id AAMk…), filled in by email-drafts; until then "follow-up draft to be created by email-drafts"
- **Requested by:** routine:nightly-cycle · 2026-10-12
- **Status history:** pending 2026-10-12
```

## Light mode (daytime runs)
Only: new sources since the last run → missed commitments, completion evidence, newly past-due items. No re-ranking, no project insight refresh, no dedupe sweep beyond new items.
