---
type: triggers
version: 1.0.0
---
# Event triggers

Triggers are conditions Atlas checks every time it runs; they are not scheduled. On/off switches and parameters live in `user/settings/rhythms.yaml: triggers`. User triggers live in `user/extensions/triggers/` (same format) and are registered in `registry.yaml`.

**Imported history** (records whose every source is `kind: import`; `.claude/skills/atlas-capture/reference/import.md` §10) never fires `new_project`, `new_key_person`, or `playbook_start`; live items it brought in are ordinary open work for the date-driven triggers.

**Fire once:** before acting, check `user/.state/triggers.yaml` for `(trigger, record, key)`; after acting, record it. **Away/paused:** during away mode, triggers are evaluated and recorded as held (`held: true`, `system/schemas/formats.md` §triggers.yaml), and their user-facing actions wait for the catch-up brief (record creation still happens). A held entry does not count as fired.

| Trigger | Evaluated by | Condition | Key | Action |
|---|---|---|---|---|
| `new_project` | `ingest`, chat | Work with a clear outcome is discussed and no project record matches | project ID | Create the project record (`atlas-capture`); add up to 3 questions (owner, goal, target date) to `questions.md` |
| `new_key_person` | `ingest`, chat | A person without a record appears in ≥3 sources within 14 days, or in a decision, commitment, or 1:1 | person ID | Create and link the person with a `relationship` chosen per `system/schemas/person.md` §Relationships; if it's unclear, set `other` and add a `relationship` question |
| `deadline_approaching` | `triage`, chat | Open commitment (`i_owe`) or deadline event due within `days` (default 3) | due date | Add to the next brief's "Due soon"; the day before, raise to the top of the brief and the Commitments page |
| `key_meeting_upcoming` | `meeting-prep`, chat | A `one_on_one` event, or a meeting with external attendees or ≥1 linked open commitment/decision, within the next 24h, and shown by the meeting filter (`rhythms.yaml: meetings`) | event start | Create a prep note (`atlas-prep`) and link it in the brief |
| `commitment_overdue` | `triage`, chat | Open commitment past due (either direction; `waiting_on` items approaching their date are surfaced by triage's aging rules, not `deadline_approaching`) | due date | Set `status: slipped` (triage owns this); flag in the brief; if `waiting_on`, create a follow-up email draft (`atlas-write`) and an approval entry |
| `playbook_start` | `ingest`, `triage`, chat | New work matches the `trigger` of an `active` playbook (a renewal date 60 days out, a new hire's start date), and no open run of that playbook exists for the same subject | playbook ID + subject ID + anchor date | `auto_start: true`: start the run. Otherwise ask: in chat directly, in routines as a `questions.md` entry (kind `other`): "Start your Renewal playbook for Brightline (5 steps, first due Oct 20)?" (`.claude/skills/atlas-triage/reference/playbooks.md` §2) |
| `focus_time_needed` | `triage`, chat | An open `i_owe` commitment with `effort` of `hour` or more, due within `deadline_approaching.days` (default 3), with no Atlas focus block for it yet, and too little free time before it: the largest free gap inside `rhythms.yaml: work_hours` before the due date is under 2 × the effort (every calendar event counts as busy, including ones the meeting filter hides) | commitment ID + due date | Propose a focus block in the best free gap (`.claude/skills/atlas-triage/reference/focus-time.md`): in chat ask directly; in routines add an `approvals.md` entry (`own_calendar_manage`). If no gap fits, say so in the brief and name the meeting most worth moving |

## User trigger format (`user/extensions/triggers/<name>.md`)
```markdown
---
type: trigger
name: deal_to_negotiation
evaluated_by: [ingest, triage]
default: on
---
## Condition
A record of type `deal` changes `status` to `negotiation`.
## Key
deal ID + date of the status change
## Action
Create a deal brief with `atlas-prep` (topic: the deal) and link it in the next brief.
```
