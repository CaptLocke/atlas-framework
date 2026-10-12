---
type: rule
name: knowledge
---
# Rule: knowledge

## Applies to
Every write to `user/knowledge/`, `user/journal/`, `user/profile/`, and indexes.

## The rule
Preserve and connect. Each fact lives in exactly one record, is linked to related records, and traces to a source. Change by superseding and appending, never by silent overwrite. Record formats: `system/schemas/`.

## Write path
For every input (chat statement, journal entry, connector item, file):
1. **Exclusions first.** If the input matches an exclusion in `data-rules.yaml`, stop.
2. **Classify.** What does it contain? (people, organizations, projects, decisions, commitments, events, risks, questions, ideas, topics, playbooks, facts about existing records). Most inputs contain several things or nothing worth keeping; noise (newsletters, notifications, automated messages, pleasantries) is skipped.
3. **Sensitivity.** Classify against data-rule categories; choose handling (`ignore | pointer | summary | full`). When unsure, choose the more conservative option.
4. **Source.** Create or update the Source record for the input (one per thread, meeting, document, drop, journal day).
5. **Resolve.** For each thing, find an existing record: search the type index and `people-map.md` by title, aliases, emails, domains; then text-search `user/knowledge/`. Match on strong signals (same email, same domain + name, same project name in the same context). If a match is plausible but uncertain, link to the existing record and add a note rather than creating a duplicate; queue an ambiguous merge in `questions.md` if needed.
6. **Write.**
   - New record: create with all required fields, `provenance`, `sources`, and links.
   - Existing record: update fields, set `updated`, append a dated line to `## Updates` citing the source. If a fact changes, keep the old value in Updates ("was X, now Y").
   - Replacement: new record with `supersedes`; old record gets `superseded_by` (content kept).
7. **Link both ways where it helps.** At minimum, the new or changed record links to its related records. Add reciprocal links on people, projects, and topics so they act as hubs.
8. **Index.** Update the affected lines in `_index/` (`formats.md` §5).
9. **Log and commit** per `system/rules/sync.md`.

## Commitments
- Record **explicit** promises only: a clear actor, a clear deliverable or action, and either a date or clear expectation. Direction: `i_owe` when the user promised; `waiting_on` when someone promised the user.
- Vague intentions become `questions` or a "confirm?" line in the next brief.
- Close (`done`) only on evidence: a sent message, delivered file, the user's word, or a source showing completion. `slipped` is set by triage when past due and open.

## Decisions
Capture who decided, when, and why. If the why is missing, set `rationale: unknown`.

## Dedupe
- People: same email → same person. Same full name + same organization → same person. Nicknames and initials go in `aliases`.
- Organizations: same domain → same organization.
- Projects/topics: same name or clear synonym in overlapping context → same record; otherwise create and link via `related`.
- Clear duplicates are merged (`merge_supersede`): keep the older path, move content and links into it, set the other's `superseded_by`, update links pointing to the duplicate.

## Archive, forget, purge
- **Archive:** `archived: true`; reversible; nothing removed.
- **Forget** (destructive, approval required, chat only, via `nova-memory`): delete the record file and its index lines; remove links to it from other records (replace with plain text where context matters); add `record: <id>` (and source-level exclusions if appropriate) to `data-rules.yaml` exclusions after confirming the governance change; tell the user plainly that a copy remains in Nova's version history, and that "permanently erase" removes it there too.
- **Purge** ("permanently erase"; destructive, explicit confirmation, chat only, via `nova-memory` with the purge lock): remove the content from all history for the named paths, then force-push. Log that a purge happened and which paths, never the content. Tell the user GitHub may retain cached copies for a period.

## Profile
Profile lines follow `system/schemas/profile.md`. New observations are written as `proposed` questions in `user/inbox/questions.md`, never directly into the profile, unless `profile_update: auto`.

## Journal
Write the user's Morning/Evening Thoughts verbatim; never edit them afterwards without `user_content_edit` approval. Extraction is recorded in the journal's `processed` field.

## Checks
- Every record passes `system/tools/validate.py`.
- No orphan records (no links and no sources) except user-stated ones.
- No two non-superseded records share an email (people) or domain (organizations).
