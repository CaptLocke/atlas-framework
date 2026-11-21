---
type: skill-reference
skill: atlas-capture
---
# Refreshing records

Filing appends: every source adds a dated `## Updates` line, and the top of a record stays the first pass. This is how the top is kept current (`system/schemas/_common.md` §Body). `maintenance` runs it (step 1b); a chat may run it for one record ("bring Dana's record up to date").

## 1. Which records
- Types: project, person, organization, topic, goal. Not archived, status not closed (`schema.yaml: closed_statuses`), not superseded.
- **Due** when its `## Updates` has 3 or more lines dated after `refreshed` (after `created` if it was never refreshed).
- At most **25 a run**, the most lines behind first; the rest wait for the next run. The validator warns at more than 8 (`system/tools/validate.py`).

## 2. Rewriting the top
Read the record, its Updates, and the records it links that are still open. Then rewrite only the text above `## Updates`:
- **For a project:** what it is and why it matters, where it stands now (`health`, the last real change), what's open (its open commitments, risks and decisions, by link), and what's next.
- **For a person:** who they are to the user (role, team, organization), what they're working on with the user now, what's open either way, and how often they meet (`cadence`).
- **For an organization:** what they are to the employer, where the relationship stands, what's open, and who the user deals with there.
- **For a topic or goal:** what it covers, where it stands, and the records that carry it.

Rules:
- **Every fact cites its source** the way Updates lines do (`([[sources/...]])`), or the record that holds it (`[[commitments/...]]`). Nothing that isn't in the record, its Updates or a linked record; no researched or inferred lines unless the record already marks them so.
- **Nothing is lost.** A fact in the old top that no longer holds goes into Updates as a dated "was X, now Y" line before it leaves the top. Updates is never edited.
- Short: 60 to 150 words for most records; more only for a large project. Write in the user's language, plainly, with no headings unless the schema gives them (the employer's sections, `organization.md` §Employer, are kept as they are).
- Refresh `summary` (one sentence) if it no longer says what the record is.
- Set `refreshed: <today>` and `updated`. A refresh adds no Updates line of its own.
- Data rules still apply (N11): nothing a data rule restricts comes back into the top. `notes_private` is never copied into it.

## 3. Fields that follow from the records
While the record is open:
- **Organizations** with `kind: customer | prospect | partner`: set `relationship_status` from linked open projects, commitments and risks and the last dated Updates line ("renewal due 2027-01-31; two open risks"). Leave it if nothing supports a change.
- **Held events** (`status: held`) with a linked source and empty `outcomes`: fill `outcomes` from the decisions and commitments that cite that source (one short line each, linked), the same rule as filing (`system/rules/knowledge.md` write path step 6). Events are refreshed this way only, never rewritten.
- `last_contact` and `cadence` are set by `normalize.py --derive`, not here.

## 4. Before compaction
`maintenance` compacts a source only after its records hold what it said (`system/schemas/source.md` §Compaction). For each source about to be compacted, read the records that cite it: if the source's key facts are in none of their tops or Updates, add one dated Updates line to the record they belong to, citing the source. Then compact.

## 5. Commit
One commit for the refresh (`Atlas-Reason: refresh records`), its `Atlas-Records` the records changed; count them from git (`system/jobs/README.md` step 4). Report the count and how many were left for the next run.
