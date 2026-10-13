---
type: skill-reference
skill: nova-health
---
# User health check

Run index-first. Open records only to confirm a finding. Thresholds are defaults; adjust if the user's work pattern clearly differs (e.g., a quarterly-cadence project).

| Check | How to detect | Auto-fix (logged) | Brought to the user |
|---|---|---|---|
| **Stale records** | Not closed and `updated` older than: project 30 days (`active`), commitment past due + 14 days (`open`/`slipped`), question 30 days (`open`), risk 60 days (`potential`/`active`), idea 90 days (`seed`/`exploring`), goal past its `period` still `active` | Close only with evidence: a source shows completion (commitment → `done` with `completed_on`; question → `answered`). Ideas untouched 180 days → `archived: true` | "These look finished or abandoned: close, keep, or archive?" (max 10, oldest first) |
| **Orphans** | Records with no links and no sources (except `provenance: stated` with a journal/chat source) | Link to the obvious hub when one exists (same org/project mentioned in the body) | Remaining orphans: link, archive, or keep |
| **Duplicates** | Same email (people), same domain (orgs), same/synonym title in overlapping context (projects, topics), near-identical commitments (same owner, counterparty, deliverable) | Merge clear cases (`merge_supersede`, `system/rules/knowledge.md`) | Ambiguous pairs as merge questions |
| **Broken links** | `[[id]]` that doesn't resolve (body and frontmatter) | Follow `superseded_by`; match alias/renamed title; fix | Unresolvable ones: list with the record they appear in |
| **Superseded chains** | A → B → C chains, or records linking to superseded records | Point links at the current record | none |
| **Unprocessed journal** | Journal sections with text but missing from `processed` | Process (`nova-thoughts`/`nova-capture`) | none |
| **Unprocessed inbox** | Files in `user/inbox/drop/`; `approvals.md` `approved` but not `executed`; `questions.md` open > 30 days | Process drops | Approved-but-not-executed actions (offer to do them now, in chat); old questions (answer or dismiss) |
| **Expired approvals / insights** | `pending` approvals > 14 days; `new` insights unseen > 30 days (days while away is active don't count) | Mark `expired`, never while away is active | Count only ("3 approvals expired; nothing was done") |
| **Profile proposals** | `questions.md` kind `profile` still open | none (unless `profile_update: auto`: apply and notify) | "Here's what I've noticed about how you work: confirm or correct" (max 5) |
| **Guide drift** | Recent edits the user made to drafts (diff between draft and sent where visible), recurring corrections, house-voice terms changed on the company site, design system missing dark colors or fonts | none | Proposed voice/design updates as profile proposals |
| **Settings sanity** | Validation of `user/settings/*`; moments on whose jobs aren't in any routine; jobs in routines for moments that are off; `status_updates.audiences` pointing to inactive people; exclusions for connectors no longer present; work hours inconsistent with schedules; `paused` items with `until` in the past; away `end` in the past but not cleared | Remove paused items whose `until` passed (resumed), clear an away block whose `end` passed and whose catch-up brief exists | Everything else as a suggested `nova-settings` change |
| **Goal ranks** | Active goals with gaps or ties in `rank`, a `rank` on a goal that isn't active, or a mix of ranked and unranked active goals | Clear `rank` on goals that aren't active; renumber 1, 2, 3… keeping the user's order (gaps only; ties are never broken by Nova) | Ties and unranked goals: "Where do these goals rank?" (one question) |
| **Profile currency** | `profile.md` role/manager/goals disagree with records (e.g., manager person `inactive`, goals all closed) | none | Role refresh questions (handled at the quarterly role refresh if it's near) |

## Output (monthly report section "Your knowledge")
```markdown
## Your knowledge
- Tidied automatically: 2 duplicates merged (Dana Ruiz, Acme Corp), 7 links fixed, 3 finished commitments closed.
- Needs you (3):
  1. Is "Vendor shortlist" still active? No updates since Aug 30. ([[projects/vendor-shortlist]]) Close / keep / archive
  2. Same person? "J. Lee" and "Jordan Lee" ([[people/j-lee]], [[people/jordan-lee]])
  3. I've noticed you shorten my email drafts by about half. Default to shorter emails?
```
Every "needs you" item also exists as a `questions.md` entry so the user can answer in any chat.
