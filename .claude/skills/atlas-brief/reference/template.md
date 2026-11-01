# Daily Brief template

Fictional example. Adapt headings' wording and density to `communication-style.md` (e.g. numbers-first for a CFO), but keep the order. Omit empty sections except Top priorities.

```markdown
---
type: brief
date: 2026-10-13
generated: 2026-10-12T20:29:40-07:00
window_start: 2026-10-11T20:31:00-07:00
target: tomorrow
sources: ["[[events/2026-10-13-acme-msa-call]]", "[[commitments/maya-pricing-feedback]]", "..."]
---
# Tuesday, Oct 13

## Action needed
- **Update your Atlas Project's instructions** (Atlas was updated to 1.1.0). The text to copy is on the Guide page, or ask me in chat.

## Today
- **9:30 Acme MSA call** with Dana Ruiz. Two open items both ways. Prep: [prep note](../prep/2026-10-13-acme-msa-call.md) · [[events/2026-10-13-acme-msa-call]]
- **11:00 1:1 with Jordan.** Bring the pricing feedback. Prep: [prep note](../prep/2026-10-13-jordan-1-1.md)
- 14:00 Design review (no prep needed). Back-to-back with 14:30 hiring sync.

## Due soon / slipping
- **Tomorrow: pricing feedback to Jordan.** Next step: finish section 3 before the 1:1. [[commitments/maya-pricing-feedback]]
- Thu 10/15: Q4 hiring plan to Finance. [[commitments/maya-hiring-plan-finance]]
- Slipped 2 days: SOC report to Acme. Next step: ask Security for the PDF. [[commitments/maya-soc-report-acme]]

## Waiting on
- Dana Ruiz: MSA redlines, 6 days (due 10/09). Follow-up draft ready. [[commitments/dana-msa-redlines]]
- Sam Okafor: Q4 budget numbers, 4 days. [[commitments/sam-q4-numbers]]

## What changed
- Orion launch back on track: supplier confirmed dates. [[projects/orion-launch]]
- Decided: enterprise minimum applies to renewals. [[decisions/2026-10-12-enterprise-minimum-renewals]]
- From your Evening Thoughts: 1 commitment (call Priya Thursday), 1 idea (partner tier). [[sources/2026-10-12-journal]]

## Top priorities
1. Pricing feedback to Jordan: due tomorrow and tied to your Q4 revenue goal. [[goals/2026-q4-enterprise-revenue]]
2. Unblock the Acme MSA: Dana's review gates your Q4 revenue goal. [[projects/acme-expansion]]
3. Hiring plan: Finance locks budgets Friday. [[goals/2026-q4-team-growth]]

## Insights
- Three customers hit the same import bug this month; it relates to your retention goal. [[risks/onboarding-import-failures]]
- Jordan hasn't had a status update from you in 3 weeks. [[people/jordan-lee]]

## Drafts ready to review
- Reply to Dana Ruiz, "MSA redlines: quick check-in" (follow-up, 6 days overdue). In your Outlook drafts.
- Weekly status to Jordan. [status draft](../status/2026-10-09-jordan-lee.md)

## Awaiting your approval
- A-2026-10-12-01: send the follow-up to Dana. Expires 10/26.

## Questions from Atlas
- **Looks done (2):** SOC report to Acme (email with attachment, 10/12) · launch checklist to Jordan (shared in Slack, 10/13). Say which are done, or all.
- Did you commit to sending Acme the onboarding guide? (from Friday's call) [[sources/2026-10-09-acme-onboarding-call]]
- Is Lee Park at Acme a customer contact or their auditor? [[people/lee-park]]

## Needs attention
- Your calendar connection expired. Reconnect it in Settings → Connectors.
```

## "Since last night" (appended in the morning)
```markdown
## Since last night
- Dana replied: redlines coming by noon today. Waiting-on updated. [[commitments/dana-msa-redlines]]
- The design review moved to 15:00. [[events/2026-10-13-design-review]]
```

## Writing tips
- One line per item. Lead with the thing, then why, then the link.
- Bold only what is due tomorrow/today or needs the user before anything else.
- Use the user's names for things (project nicknames from aliases).
- Dates relative where clearer ("tomorrow", "Thu 10/15"), in the user's timezone.
