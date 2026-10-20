---
type: skill-reference
skill: atlas-triage
---
# Playbooks: from recurring work to a checklist Atlas runs

A playbook is a record (`system/schemas/playbook.md`). Running one adds no new machinery: each run is a small project whose steps are commitments, so triage tracks them, the brief and Work show them, `email-drafts` pre-drafts the messages, and slipped steps are flagged like any other slipped work.

## 1. Proposing a playbook from recurring work (`intelligence`)
1. **Look for repeats.** Atlas looks for the same kind of work done at least **3 times in 12 months**: projects or clusters of commitments with similar titles, the same kind of counterparty (customer, new hire, vendor), and a similar sequence of steps. Examples are three renewals that each went quote → call → contract, or two onboardings and one in progress.
2. **Check it's new.** The work must have no active or draft playbook already, and the user must not have dismissed a proposal for it in the last 90 days.
3. **Draft the record.** Create the playbook through `atlas-capture`:
   - `status: draft`, `provenance: inferred`, `sources` = the past runs.
   - `trigger`, `anchor`, and the common `steps`. Each step gets a typical `when` (the median offset seen) and `draft: email | message` where the step was a message to the same role each time.
   - Keep only steps that appeared in most runs; note the rest in the body as "sometimes".
4. **Propose it.** Write an `opportunity` insight: "You've run renewals 3 times with the same 5 steps. Save it as a playbook so I can run the checklist next time?" Link it to the draft.
5. **On confirmation.** On the user's yes (they may edit steps first), set `status: active` with an Updates line (`provenance: stated` for their edits). Then ask once whether runs should start automatically (`auto_start`). If they decline the proposal, set `status: retired`, which keeps it from being proposed again.

Users can also create one directly ("save how we do month-end close as a playbook"), or edit one ("add a step: send the welcome pack").

## 2. Starting a run (`playbook_start` trigger, or "start the renewal playbook for Brightline")
1. **Resolve the subject and anchor date.** The subject is the organization, person, or project the run is about; the anchor is its renewal date, start date, and so on. Missing anchor → ask (chat) or a question (routine); don't guess dates.
2. **Create the run project** (`records_write`):
   - Title: "<Playbook title>: <subject>", for example "Renewal: Brightline".
   - `scale: task_group`, `status: active`, `target` = anchor.
   - Links to the playbook, the subject, and the goal the work serves, if any.
3. **Create one `i_owe` commitment per step:**
   - `title` = the step.
   - `due` = anchor + `when`, or `null` if the step has no offset.
   - `origin: "[[playbooks/<slug>]]"`, `counterparty` = the person the `to` role resolves to for this subject (the customer champion, the user's manager), or the user's own person record.
   - Linked to the run project.
   - A step whose date has already passed gets `status: open` with `insight: "Step date passed before the run started"`, never `slipped`. The user decides whether it still applies.
4. **Tell the user** in the brief or chat, in one line: "Started your Renewal playbook for Brightline: 5 steps, first due Oct 20 ([[projects/renewal-brightline]])."

## 3. Pre-drafting the right messages (`email-drafts`)
For each open step commitment whose playbook step has a `draft`, due within `rhythms.yaml: triggers.deadline_approaching.days` (default 3), with no `step draft created` marker in its Updates:
- Draft the message with `atlas-write`, grounded in the run's subject records, to the resolved recipient, through the same channels as insight drafts (`system/jobs/email-drafts.md` step 4a).
- Append `- <date>: step draft created (draft id …)` to the commitment. The brief shows the step with "Draft ready".
- Never send. Sending is `send_communication` (approval in chat).

## 4. Flagging missed steps (`triage`)
In every full triage pass, for each active run project:
- **Slipped steps** are flagged as usual (`commitment_overdue`).
- **Out of order:** a later step was done while an earlier one is still open → the earlier step's `insight` says so ("Contract went out before the quote was confirmed"), and the run's `next_step` points at it.
- **Skipped in practice:** evidence shows the run moved past a step with no sign it happened (the call was held but the quote was never sent) → a question in `questions.md` (kind `commitment`): "Did the Brightline quote go out?"
- **Run health:** set the project's `health` from its steps (any slipped step → `at_risk`; two or more → `off_track`).

## 5. Finishing a run
When every step is `done` or `dropped`, or the user says the run is over:
- Set the project to `done`, and set the playbook's `last_used`.
- If steps were dropped, added, or moved in 2 of the last 3 runs, propose updating the playbook (a `profile`-style question with the exact change). This is the same learning rule as `reference/learning.md`: patterns are proposed, and only the user's yes changes the playbook.
