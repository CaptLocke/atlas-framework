---
type: job
name: status-updates
model: strongest
skills: [nova-status-update]
---
# Job: status-updates

## Purpose
Draft the week's status updates for the user's manager and stakeholders, in the right voice, grounded in projects, decisions, and commitments, ready to review and send.

## Runs when
- All profiles: `weekly` routine, after `weekly-review`.
- Audiences and day come from `rhythms.yaml: moments.status_updates` (`enabled`, `audiences`, `day`, default `fri`). The job checks `day` itself: on any other weekday (run date in the user's time zone) it exits early, leaves `jobs.yaml: status-updates.last_status` unchanged, and notes "not the status day (<day>)" in the run report. It drafts at most once per audience per ISO week.
- Modifiers: `when`. `target` and `mode` are ignored.

## Away and paused
During away (run date within away, `system/jobs/README.md`), exit with `skipped_away`. If the moment or the job is paused, exit with `skipped_paused`.

## Readiness check
- `moments.status_updates.enabled` must be true; if false, exit early (`early_exit`) with a run-report note.
- Today must be `moments.status_updates.day` (see Runs when).
- `audiences` must list at least one person. If empty, exit early and add one `setup` question ("Who should I draft weekly updates for?") to `user/inbox/questions.md` if none is open.
- If `weekly-review` hasn't run this week, proceed from records and note it.

## Inputs
- This week's review (`user/work/reviews/YYYY-Www.md`) when present; projects, decisions, risks, and commitments relevant to each audience (linked to the audience person, their team, or projects they sponsor).
- Each audience's person record (relationship, preferences noted there), previous status updates to that audience in `user/work/status/`.
- Voice guides (`system/rules/writing.md`: personal voice for the user's manager and internal updates, house voice for external or official ones), `communication-style.md`, `preferences.md`.

## Steps
1. For each audience, skip if a status draft for this ISO week exists and nothing relevant changed since.
2. Invoke `nova-status-update` for that audience: what moved, decisions, risks and asks, next week; finished and ready to send, no citations in the draft; list sources separately in the file.
3. Write `user/work/status/YYYY-MM-DD-<audience-slug>.md` (`type: status`, `date`, `sources`).
4. If a mail connector with `mail.create_draft` is available and `drafts_create` is `auto`, also create an email draft to that audience and add a pending `send_communication` entry to `user/inbox/approvals.md` pointing to it.
5. Commit.

## Outputs
- `user/work/status/YYYY-MM-DD-<audience-slug>.md` per audience.
- Email drafts in the user's mail tool (never sent) and approval entries.

## Early exit
Not enabled, not the status day (`last_status` unchanged), no audiences, or every audience already has an up-to-date draft this week → early exit.

## Guardrails
- Never send (`send_communication` locked). Never post to messaging tools; a post is also a send.
- Only include information appropriate for that audience; apply data rules and `preferences.md` instructions.

## Run report
Row: `status-updates | <status> | <N> drafts | audiences: <names>`. Adds approvals queued.
