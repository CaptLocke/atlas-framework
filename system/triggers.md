---
type: triggers
version: 1.0.0
---
# Event triggers

Triggers are conditions Nova checks every time it runs; they are not scheduled. On/off switches and parameters live in `user/settings/rhythms.yaml: triggers`. User triggers live in `user/extensions/triggers/` (same format) and are registered in `registry.yaml`.

**Fire once:** before acting, check `user/.state/triggers.yaml` for `(trigger, record, key)`; after acting, record it. **Away/paused:** during away mode, triggers are evaluated but their user-facing actions are held for the catch-up brief (record creation still happens).

| Trigger | Evaluated by | Condition | Key | Action |
|---|---|---|---|---|
| `new_project` | `ingest`, chat | Work with a clear outcome is discussed and no project record matches | project ID | Create the project record (`nova-capture`); add up to 3 questions (owner, goal, target date) to `questions.md` |
| `new_key_person` | `ingest`, chat | A person without a record appears in ≥3 sources within 14 days, or in a decision, commitment, or 1:1 | person ID | Create and link the person; if relationship is unclear, add a `relationship` question |
| `deadline_approaching` | `triage`, chat | Open commitment (`i_owe`) or deadline event due within `days` (default 3) | due date | Add to the next brief's "Due soon"; the day before, raise to the top of the brief and the Work Board |
| `key_meeting_upcoming` | `meeting-prep`, chat | A `one_on_one` event, or a meeting with external attendees or ≥1 linked open commitment/decision, within the next 24h | event start | Create a prep note (`nova-prep`) and link it in the brief |
| `commitment_overdue` | `triage`, chat | Open commitment past due (either direction; `waiting_on` items approaching their date are surfaced by triage's aging rules, not `deadline_approaching`) | due date | Set `status: slipped` (triage owns this); flag in the brief; if `waiting_on`, create a follow-up email draft (`nova-write`) and an approval entry |

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
Create a deal brief with `nova-prep` (topic: the deal) and link it in the next brief.
```
