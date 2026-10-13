# Status update template

Fictional examples. User Maya Chen, PM at Brightline; manager Jordan Lee; customer Acme.

## File
```markdown
---
type: status
date: 2026-10-16
audience: "[[people/jordan-lee]]"
period_start: 2026-10-09
period_end: 2026-10-16
voice: personal
sources: ["[[projects/orion-launch]]", "[[decisions/2026-10-15-orion-launch-date]]", "..."]
---
**Subject:** Weekly update: Orion on track, Acme MSA pending, hiring plan in

**Headline:** Orion is back on track for 11/03; Acme's MSA is the main open risk.

**Highlights**
- Orion launch date confirmed for 11/03 after the supplier locked dates.
- Hiring plan delivered to Finance on time.
- Two enterprise deals moved to legal review.

**Decisions**
- Enterprise 25-seat minimum applies at renewal (decided 10/12).

**Risks and issues**
- Acme MSA redlines are a week late; I'm calling Dana Monday. If they slip past 10/23, the Q4 close is at risk.
- Onboarding import bug hit 5 customers; fix ships 10/30.

**Asks**
- Need your go/no-go on exploring a partner tier by 10/23.

**Next week**
- Final pricing sheets for Orion; Acme MSA call; board pre-read section.

## Sources (for you)
[[projects/orion-launch]] · [[decisions/2026-10-12-enterprise-minimum-renewals]] · [[commitments/dana-msa-redlines]] · [[risks/onboarding-import-failures]]
```

## Shaping by audience
| Audience | Voice | Shape |
|---|---|---|
| Manager | Personal | Headline + bullets; risks with your plan; explicit asks; ~150–250 words |
| Executive / steering group | Personal (house if formal company forum) | Headline, 3 numbers, decisions needed, risks; ≤150 words |
| Customer or partner | House | Progress against what was promised to them, next milestones, what you need from them; no internal risks or internal names they don't know |
| Cross-functional peers | Personal | What changed that affects them, dependencies, dates |

## Rules
- Lead with the overall state in one line.
- Outcomes over activity ("shipped X", not "worked on X").
- Every risk has a mitigation or an ask.
- Never mention internal Atlas terms, record IDs, or sources in the sendable part.
