---
type: job
name: status-updates
model: strongest
speaks: always
skills: [atlas-status-update, atlas-write]
---
# Job: status-updates

## Purpose
Draft the week's status updates for the user's manager and stakeholders, in the right voice, grounded in projects, decisions, and commitments, ready to review and send. Also draft each scheduled template's edition that comes due before the next run (`system/schemas/formats.md` §Deliverable templates, On a schedule).

## Runs when
- All profiles: `weekly` routine, after `weekly-review`.
- Audiences and day come from `rhythms.yaml: moments.status_updates` (`enabled`, `audiences`, `day`, default `fri`). The job checks `day` itself: on any other weekday (run date in the user's time zone) it skips steps 1–5 (exiting early if no scheduled template is due), leaves `jobs.yaml: status-updates.last_status` unchanged, and notes "not the status day (<day>)" in the run report. It drafts at most once per audience per ISO week.
- Modifiers: `when`. `target` and `mode` are ignored.
- **Scheduled templates** run on every weekly run, whatever the status day and whether or not status updates are on: an edition due on or before the next run's date is drafted on this one, so it's never late and never more than a week early. The day and enabled checks below are for status updates only (steps 1–5).

## Away and paused
During away (run date within away, `system/jobs/README.md`), exit with `skipped_away`. If the job is paused, exit with `skipped_paused`. If only the `status_updates` moment is paused or off, skip steps 1–5 and still run step 6: scheduled templates are the user's own request, not part of the moment.

## Readiness check
For status updates (steps 1–5); scheduled templates (step 6) need only an `active` template with `schedule` and `next_due`.
- `moments.status_updates.enabled` must be true; if false, skip steps 1–5 with a run-report note (`early_exit` if step 6 has nothing due either).
- Today must be `moments.status_updates.day` (see Runs when).
- `audiences` must list at least one person. If empty, skip steps 1–5 and add one `setup` question ("Who should I draft weekly updates for?") to `user/inbox/questions.md` if none is open.
- If `weekly-review` hasn't run this week, proceed from records and note it.

## Inputs
- This week's review (`user/work/reviews/YYYY-Www.md`) when present; projects, decisions, risks, and commitments relevant to each audience (linked to the audience person, their team, or projects they sponsor).
- Each audience's person record (relationship, preferences noted there), previous status updates to that audience in `user/work/status/`.
- Voice guides (`system/rules/writing.md`: personal voice for the user's manager and internal updates, house voice for external or official ones), `communication-style.md`, `preferences.md`.

## Steps
1. For each audience, skip if a status draft for this ISO week exists and nothing relevant changed since.
2. Invoke `atlas-status-update` for that audience: what moved, decisions, risks and asks, next week; finished and ready to send, no citations in the draft; list sources separately in the file.
3. Write `user/work/status/YYYY-MM-DD-<audience-slug>.md` (`type: status`, `date`, `sources`).
4. If a mail connector with `mail.create_draft` is available and `drafts_create` is `auto`, also create an email draft to that audience and add a pending `send_communication` entry to `user/inbox/approvals.md` pointing to it (`Proposal kind: send_communication · status update`).
5. Commit.
6. **Scheduled templates.** For each `active` template in `user/work/templates/` with a `schedule`, while its `next_due` is on or before the next weekly run's date (today + 7 days), one edition at a time:
   1. If `drafted_for` equals `next_due`, or an edition for that date is already in the deliverables folder or `user/work/deliverables/` (a run that stopped before its commit), don't draft it again: go to step 4.
   2. Invoke `atlas-write` with the template, as an edition for `next_due`, its files named for that date. A fact the sources don't give is marked `[needed]`, never guessed.
   3. Hand it over at each class's autonomy level (`system/rules/governance.md`), as step 4 does: a doc, deck or sheet is saved to the deliverables folder (`atlas-write` §5) only if `deliverables_save` is `auto`; an email or message is a draft in the user's tool only if `drafts_create` is `auto`, with a pending `send_communication` approvals entry when it has recipients. At `propose`, queue a pending approvals entry for that class instead; otherwise, or with no drive connector in this routine, keep the working files. Either way, say where it is in the next brief (`atlas-write` §5 step 7).
   4. Set `drafted_for` to that `next_due`, move `next_due` to the next date the `schedule` gives, and commit (`Atlas-Reason: scheduled edition of <template> for <date>`). Words that no longer give a date: leave `next_due`, add one `questions.md` entry asking when it's next due, and stop for this template.

## Outputs
- `user/work/status/YYYY-MM-DD-<audience-slug>.md` per audience.
- Email drafts in the user's mail tool (never sent) and approval entries.
- Scheduled editions: files in the deliverables folder (and their `user/work/deliverables/` working files and `kind: deliverable` sources), or drafts; the template's `drafted_for` and `next_due`.

## Early exit
Not enabled, not the status day (`last_status` unchanged), no audiences, or every audience already has an up-to-date draft this week, **and** no scheduled template is due → early exit. With a template due, the status-update half is skipped (noted in the run report) and the job runs step 6.

## Guardrails
- Never send (`send_communication` locked). Never post to messaging tools; a post is also a send. A scheduled edition is never shared (`share_expose`) and never overwrites an earlier file (`atlas-write` §5).
- Only include information appropriate for that audience; apply data rules and `preferences.md` instructions.

## Run report
Row: `status-updates | <status> | <N> drafts | audiences: <names> | <M> scheduled editions`. Adds approvals queued and each edition's template and due date.
