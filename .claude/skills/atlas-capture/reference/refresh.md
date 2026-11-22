---
type: skill-reference
skill: atlas-capture
---
# Refreshing records

Filing appends: every source adds a dated `## Updates` line, and the top of a record stays the first pass. This is how the top is kept current (`system/schemas/_common.md` §Body). `maintenance` runs it (step 1b); a chat may run it for one record ("bring Dana's record up to date").

## 1. Which records
- Types: project, person, organization, topic, goal. Not archived, status not closed (`schema.yaml: closed_statuses`), not superseded, and never the user's own record (`relationship: self`), which the user's profile describes.
- **Due** when its `## Updates` has 3 or more lines dated after `refreshed` (after `created` if it was never refreshed), or, for a project, when `validate.py` warns about its `health` (an active project `on_track` past its `target` or with an active high-impact risk): a quiet project adds no Updates lines, so the warning is what brings it here.
- At most **25 a run**, the most lines behind first; the rest wait for the next run. The validator warns at more than 8 (`system/tools/validate.py`).

## 2. Rewriting the top
Read the record, its Updates, and the records it links that are still open. For a project, run §3's `target` and `health` step first, so the top is written from the reconciled fields. Then rewrite only the text above `## Updates`:
- **For a project:** what it is and why it matters, where it stands now (`health` and `target` after §3 has reconciled them, the last real change), what's open (its open commitments, risks and decisions, by link), and what's next.
- **For a person:** who they are to the user (role, team, organization), what they're working on with the user now, what's open either way, and how often they meet (`cadence`).
- **For an organization:** what they are to the employer, where the relationship stands, what's open, and who the user deals with there.
- **For a topic or goal:** what it covers, where it stands, and the records that carry it.

Rules:
- **Every fact cites its source** the way Updates lines do (`([[sources/...]])`), or the record that holds it (`[[commitments/...]]`). Nothing that isn't in the record, its Updates or a linked record; no researched or inferred lines unless the record already marks them so.
- **Nothing is lost.** A fact in the old top that no longer holds goes into Updates as a dated "was X, now Y" line before it leaves the top. A line in the old top with no source (often something the user said) stays as it is, or moves to Updates as a dated line "from the earlier summary" before it leaves. Updates is never edited.
- Short: 60 to 150 words for most records; more only for a large project. Write in the user's language, plainly. Keep every `##` section already above Updates (a project's scope or success criteria, the employer's sections in `organization.md` §Employer) and refresh only the text before the first of them; add no headings of your own.
- Refresh `summary` (one sentence) if it no longer says what the record is.
- Set `refreshed: <today>`; leave `updated` as it is, since a rewrite isn't new activity and the stale and stalled checks read `updated`. The "was X, now Y" and "from the earlier summary" lines above are the only Updates lines a refresh writes.
- Data rules still apply (N11): nothing a data rule restricts comes back into the top. `notes_private` is never copied into it.

## 3. Fields that follow from the records
While the record is open:
- **Organizations** with `kind: customer | prospect | partner`: set `relationship_status` from linked open projects, commitments and risks and the last dated Updates line ("renewal due 2027-01-31; two open risks"). Leave it if nothing supports a change.
- **Held events** (`status: held`) with a linked source and empty `outcomes`: fill `outcomes` from the decisions and commitments that cite that source (one short line each, linked), the same rule as filing (`system/rules/knowledge.md` write path step 6). Events are refreshed this way only, never rewritten.
- **Projects: `target` and `health` agree with the record** (ATL-132). A refresh that leaves the top saying one thing and the fields another gives a chat answer and a dated page different pictures.
  - **`target`:** the newest `made`, non-superseded decision linked to the project that sets or moves its date wins: if it is dated after the last change to `target` and names another date, set `target` to it, with a "was X, now Y" Updates line citing the decision. A different date in the Updates or the old top with no decision behind it doesn't move the field: add one `other` question to `user/inbox/questions.md` ("Orion's target says Dec 11, but the Nov 18 notes say Dec 20. Which holds?", `Proposed change:` the field, `Links:` the project and the source), unless one about it is open, and write the top with the field's date and the open question.
  - **`health`:** `off_track` when `target` has passed with the project still active, or an `active` linked risk has `impact: high`; `at_risk` when a linked open risk has `impact: high`, the newest estimate in the record or its sources puts the end after `target`, or work the top calls unscoped or unsized stands between now and `target`; `on_track` again when it was `at_risk` or `off_track` for evidence that no longer holds (the risk is resolved, a decision moved the target forward, the work is scoped); otherwise leave it. Change it only on that evidence, with a "was X, now Y" Updates line naming the evidence. The top says the same.
  - Goals keep `target` as text: compare it only by eye, and ask the same way when it plainly disagrees.
- `last_contact` and `cadence` are set by `normalize.py --derive`, not here.

## 4. Before compaction
`maintenance` compacts a source only after its records hold what it said (`system/schemas/source.md` §Compaction). For each source about to be compacted, read the records that cite it: if the source's key facts are in none of their tops or Updates, add one dated Updates line to the record they belong to, citing the source. Then compact.

## 5. Commit
One commit for the refresh (`Atlas-Reason: refresh records`), its `Atlas-Records` the records changed; count them from git (`system/jobs/README.md` step 4). Report the count and how many were left for the next run.
