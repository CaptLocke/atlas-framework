---
type: skill-reference
skill: atlas-health
---
# User health check

Run index-first. Open records only to confirm a finding. Thresholds are defaults; adjust if the user's work pattern clearly differs (e.g., a quarterly-cadence project).

| Check | How to detect | Auto-fix (logged) | Brought to the user |
|---|---|---|---|
| **Stale records** | Not closed and `updated` older than: project 30 days (`active`), commitment past due + 14 days (`open`/`slipped`), question 30 days (`open`), risk 60 days (`potential`/`active`), idea 90 days (`seed`/`exploring`), topic 90 days (`active`), goal past its `period` still `active` | Close only with evidence: a source shows completion (commitment → `done` with `completed_on`; question → `answered`). Goals are never closed here: a goal past its period goes to the user as a question (`atlas-review` §Guardrails). Ideas untouched 180 days → `archived: true`. Topics → `dormant`, no evidence needed and not reported (`system/schemas/topic.md`) | "These look finished or abandoned: close, keep, or archive?" (max 10, oldest first; never topics) |
| **No topics** | `setup.yaml: started` more than 30 days ago, at least 100 commitments, decisions, ideas, risks and questions in the indexes, and no `active` topic in `_index/topics.md` | Run `python3 -I system/tools/relations.py --out .atlas-tmp/relations.json` and weigh its `themes` as the intelligence sweep does (`atlas-insights` §A step 3b), creating the topics that meet `system/schemas/topic.md`'s bar | Only if none met the bar: known issue `topics-missing` (low), "Atlas hasn't grouped any of your work into topics yet"; it clears once one exists |
| **Orphans** | Records with no links and no sources (except `provenance: stated` with a journal/chat source) | Link to the obvious hub when one exists (same org/project mentioned in the body) | Remaining orphans: link, archive, or keep |
| **Duplicates** | Same email, or same full name and same organization (people), same domain (orgs), same/synonym title in overlapping context (projects, topics), near-identical commitments (same owner, counterparty, deliverable) | Merge clear cases (`merge_supersede`, `system/rules/knowledge.md`) | Ambiguous pairs as merge questions |
| **Broken links** | `[[id]]` that doesn't resolve (body and frontmatter) | Follow `superseded_by`; match alias/renamed title; fix | Unresolvable ones: list with the record they appear in |
| **Superseded chains** | A → B → C chains, or records linking to superseded records | Point links at the current record | none |
| **Unprocessed journal** | Journal sections with text but missing from `processed` | Process (`atlas-thoughts`/`atlas-capture`) | none |
| **Unprocessed inbox** | Files in `user/inbox/drop/`; `approvals.md` `approved` but not `executed`; `questions.md` open > 30 days | Process drops | Approved-but-not-executed actions (offer to do them now, in chat); old questions (answer or dismiss) |
| **Expired approvals / insights** | `pending` approvals > 14 days; `new` insights unseen > 30 days (days while away is active don't count); `pending` or `approved` approvals past their `Expires:` (away or not) | Mark `expired`; by age never while away is active | Count only ("3 approvals expired; nothing was done") |
| **Record currency** | From `validate.py --user` warnings: records whose Updates have run more than 8 lines past their top, people whose `last_contact` is behind their sources, superseded records still live. Fill rates: `cadence` on people with a recurring 1:1, `outcomes` on held events with a linked source, `relationship_status` on customer, prospect and partner organizations | The refresh, `normalize.py --derive` and the superseded rule already run in maintenance; nothing more here | One line in the report with the counts and fill rates ("Records current: 3 behind, 2 people's last contact late; outcomes on 88% of held meetings"); a question only if a count grew two months running |
| **Profile proposals** | `questions.md` kind `profile` still open | none (unless `profile_update: auto`: apply and notify) | "Here's what I've noticed about how you work: confirm or correct" (max 5) |
| **Guide drift** | Recent edits the user made to drafts (diff between draft and sent where visible), recurring corrections, house-voice terms changed on the company site, design system missing dark colors or fonts | none | Proposed voice/design updates as profile proposals |
| **Settings sanity** | Validation of `user/settings/*`; moments on whose jobs aren't in any routine; `status_updates.day` on a weekday no routine running `status-updates` is scheduled for ("Your status updates are set for Monday, but only your Friday routine drafts them"); jobs in routines for moments that are off; `status_updates.audiences` pointing to inactive people; exclusions for connectors no longer present; work hours inconsistent with schedules; `paused` items with `until` in the past; away `end` in the past but not cleared | Remove paused items whose `until` passed (resumed), clear an away block whose `end` passed and whose catch-up brief exists | Everything else as a suggested `atlas-settings` change |
| **Goal ranks** | Active goals with gaps or ties in `rank`, a `rank` on a goal that isn't active, or a mix of ranked and unranked active goals | Clear `rank` on goals that aren't active; renumber 1, 2, 3… keeping the user's order (gaps only; ties are never broken by Atlas) | Ties and unranked goals: "Where do these goals rank?" (one question) |
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
