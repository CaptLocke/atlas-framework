# Triage signals

Fictional examples (user Maya Chen; manager Jordan Lee; Acme counsel Dana Ruiz).

## Completion evidence
| Strong (close it) | Weak (ask instead) |
|---|---|
| Sent email to the counterparty containing the promised file or answer | Sent email to the counterparty about the topic, no attachment |
| Counterparty replies "got it, thanks" to the deliverable | Meeting with the counterparty happened (may or may not have covered it) |
| Task in the task tool marked complete and it maps to this commitment | Deliverable file created in `user/work/deliverables/` but no send evidence |
| The user says it's done (in chat or journal) | Someone else says "I think Maya sent it" |
| A `deliverable` Source linked to the commitment and the user confirmed delivery | Calendar event titled like the deliverable |

For `waiting_on`: the counterparty's message delivering it, or a Source showing the thing exists (e.g. the signed MSA arrived).

## Priority rubric
Score each open commitment, then map: high (top ~20%), medium, low.
1. **Goal link:** linked (directly or via its project) to an active goal → strong boost; to the user's manager's stated priorities → boost.
2. **Who's waiting:** manager, executive, or customer counterparty → boost; internal peer → neutral.
3. **Time:** due within 3 days or already slipped → boost; no date → neutral.
4. **Consequence:** blocks others (others' commitments or a decision depend on it), or affects revenue, legal, or launch dates → boost.
5. **Effort hint:** quick wins (<30 min) due soon can be raised to clear them.
Never rank purely by due date. Top priorities in the brief are the top 3–5 by this rubric, each with its reason.

## Aging waiting-on
- Days waiting = business days since `created`, or since the last follow-up line in Updates.
- Aging if: past due; or >5 business days with no movement; or due within 2 days with no sign of progress.
- Use person cadence and history for the channel: "Dana usually replies within a day to calls; email has gone unanswered twice".

## Insight and next-step examples
| Record | insight | next_step |
|---|---|---|
| `waiting_on` Dana: MSA redlines (6 days late) | Dana hasn't replied in 6 days; she answered faster by phone last time. | Call Dana before Thursday's steering meeting. |
| `i_owe` pricing feedback to Jordan (due tomorrow) | Due tomorrow; Jordan needs it for Friday's exec review. | Finish section 3 tonight; send before the 11:00 1:1. |
| `i_owe` SOC report to Acme (slipped 2 days) | Blocked on Security; Acme's renewal decision depends on it. | Ask Sam in Security for the PDF today. |
| Project Atlas launch (at_risk) | Two supplier commitments slipped and the launch is 3 weeks out. | Confirm supplier dates at Wednesday's ops sync. |
| `i_owe` survey analysis (no due date) | No date agreed; Jordan mentioned it twice this month. | Propose a date to Jordan: suggest Fri 10/23. |

Bad examples (too generic): "Follow up soon." "This is important." "Keep an eye on it."

## Follow-up draft guidance (overdue waiting_on)
- Short (3–5 sentences), friendly, specific: what, when it was due, what the user needs, an easy next step.
- Voice per `system/rules/writing.md` (internal → personal; customer → house unless the relationship is personal and informal).
- Reply in the original thread when there is one.
- Approvals entry example:
```markdown
## A-2026-10-12-01 · pending
- **Action:** send_communication: send follow-up to Dana Ruiz
- **Why:** Dana's MSA redlines are 6 days overdue ([[commitments/dana-msa-redlines]])
- **Prepared:** Outlook draft "MSA redlines: quick check-in" (id AAMk…)
- **Requested by:** routine:nightly-cycle · 2026-10-12
- **Status history:** pending 2026-10-12
```

## Light mode (daytime runs)
Only: new sources since the last run → missed commitments, completion evidence, newly past-due items. No re-ranking, no project insight refresh, no dedupe sweep beyond new items.
