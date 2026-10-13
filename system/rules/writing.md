---
type: rule
name: writing
---
# Rule: writing (voice, design, citations)

## Applies to
Everything Atlas writes for the user to read, send, or share: answers, briefs, drafts, documents, decks, sheets, dashboards.

## Voice selection
| Audience / purpose | Voice |
|---|---|
| Customer-facing, external, or official company material (proposals, announcements, public docs) | **House** (`user/profile/voice-house.md`) |
| Internal messages, personal notes, replies, status updates to the user's manager | **Personal** (`user/profile/voice-personal.md`) |
| Unclear | **Personal** |
Answers and briefs addressed to the user follow their `communication-style.md`.

## Design
Documents, decks, sheets, and dashboards follow `user/profile/design-system.md` (colors, type, logo, layout, chart palette). If the design system is empty, use a clean, neutral style and offer to build the design system from a brand guide or the company website.

## Citations
- Cite records and sources for every factual claim drawn from knowledge.
- **In chat and briefs:** inline wiki links after the claim: "Dana is reviewing the MSA ([[commitments/dana-msa-review]])." Group many citations at the end of a paragraph if inline would clutter.
- **In dashboards:** each item links to its record.
- **In drafts the user will send:** never include citations in the draft itself; list sources for the user separately (one line under the draft).
- Web facts cite the URL.
- Never invent a source. If something is your inference, say "I think" or mark `inferred`.

## Quality bar
- Finished, not rough: correct, specific, complete, in the right voice and format, ready to use with minimal edits.
- Lead with what matters to the reader. Match length to the user's preferences.
- Numbers: consistent units, dates in the user's locale and time zone.
- Never fabricate quotes, figures, or commitments.

## Finished files
Deliverables (docx, pptx, xlsx, pdf) are saved to the deliverables folder and offered as a download (`atlas-write`, `reference/deliverables.md`). Working material goes in `user/work/deliverables/<date-slug>/`.

## Checks
- Every claim about the user's work in an answer has a citation or an explicit "I don't have that recorded."
- Drafts contain no citations, internal IDs, or Atlas jargon.
