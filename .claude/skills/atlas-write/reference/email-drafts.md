# Email drafts (job mode) and voice learning

Used by the `email-drafts` job, and by `atlas-triage` in chat. This is the **only** procedure that creates follow-up drafts. Fictional examples.

## Which threads get a reply draft
Draft when all are true:
- The latest message in the thread is to the user (To, or a direct question in CC), from a person (not automated), and the user hasn't replied since (check `mail.list_sent` / thread).
- It asks for something: a question, a decision, a document, a time, a confirmation.
- It isn't excluded by data rules, isn't from a sender the user's preferences say to leave alone, and isn't pointer-only content.
- No Atlas draft already exists for the thread (the Source's Updates has no "reply draft created" line) and the user hasn't answered (`mail.list_sent`).
Skip: FYIs, threads the user is likely to handle in a meeting today (note that in the brief instead), sensitive topics flagged by data rules (list them in the brief as "needs your reply" without drafting), anything requiring facts Atlas doesn't have (draft with a clearly marked placeholder only if the rest is useful).
Cap: ~10 drafts per run, highest priority first (manager, customers, items tied to goals or commitments).

## Follow-ups for overdue waiting_on
Candidates: `waiting_on` commitments with `status: slipped` (marked by `atlas-triage`, `commitment_overdue`).
1. **Marker check:** if the commitment's `## Updates` has a line `follow-up draft created <date>` since the commitment last changed (new due date, owner reply), skip it.
2. Draft 3–5 sentences, friendly, specific (what, when it was due, why it matters now, an easy next step). Reply in the original thread when there is one.
3. Append to the commitment's Updates: `- <date>: follow-up draft created <date> (draft id …)`.
4. Approvals: if a `pending` entry already links this commitment (triage usually adds it), update its `Prepared:` line with the draft; otherwise add one (`send_communication`). Never two pending entries for one commitment.
5. No mail connector: put the text in the approvals entry's `Prepared:` line instead and still write the marker.

## Draft quality
- Voice per `system/rules/writing.md`; reply in the thread's language and register.
- Answer the actual ask first; propose concrete times or options; keep commitments realistic (never promise dates the user hasn't agreed to; use "[confirm date]").
- No citations, IDs, or Atlas jargon in the draft body.

## Recording drafts (for the brief and idempotency)
For each draft created (`system/jobs/email-drafts.md`):
- Reply drafts: append `reply draft created (draft id …)` to the thread Source's `## Updates`. Follow-ups: append `follow-up draft created <date> (draft id …)` to the commitment's Updates (the shared marker with `atlas-triage`). These lines are the marker that prevents a second draft.
- List the draft in the run report (recipient and subject only, no content), e.g. `- Dana Ruiz · "MSA redlines: quick check-in" · follow-up · [[commitments/dana-msa-redlines]]`.
- `atlas-brief` reads drafts from run reports (and chat activity) since the last brief for "Drafts ready to review".

## Voice learning from sent mail
During ingest, when a sent message matches an Atlas draft (same thread, similar content):
- Compare draft and sent text: length change, removed/added greeting or sign-off, words replaced, structure changes.
- Record the observation as an Updates line on the thread's Source: `- 2026-10-12: Sent version differs from Atlas draft: ~50% shorter, greeting removed.` (no message text). Later runs count these lines by text search.
- When a pattern is clear (≥3 similar observations in 60 days, and no open or dismissed proposal for the same change), propose it in `user/inbox/questions.md`:
```markdown
## Q-2026-10-12-02 · open · profile
- **Question:** You shortened my last 4 drafts by about half. Should I default to shorter emails?
- **Proposed change:** voice-personal.md: "Keep emails under ~120 words" [observed · proposed]
- **Asked:** 2026-10-12
```
- Sent text is evidence, never stored verbatim beyond what data rules allow.
