---
name: nova-status-update
description: "Draft status updates for the user's manager and stakeholders from what actually happened in the period\u2014projects, decisions, commitments kept and slipped, risks, asks\u2014in the right voice, saved for review and optionally as an email draft, never sent without approval. Use when the status-updates job runs and for \"draft my weekly update\", \"write a status for Jordan\", \"update the Acme team on Atlas\", \"what should I tell my boss this week\"."
---
# Status updates

## Purpose
Remove the weekly status-writing chore: an accurate, audience-shaped update is waiting for review, built from records rather than memory.

## When to use
- **Job:** `status-updates` (usually Friday, after `weekly-review`).
- **Chat:** "Draft my weekly update for Jordan", "Status for the Atlas steering group", "Update Acme on the integration", "What should I tell my boss this week?"

## Inputs
- Audiences: `rhythms.yaml: moments.status_updates` (`on`, `audiences` as person IDs, `day`); in chat, whoever the user names (a person, a group, or a project's stakeholders).
- For each audience: the person record (relationship, role, organization, what they care about, preferred format), their linked projects and goals, and the previous update to them (latest `user/work/status/*-<audience-slug>.md`).
- Period: since that previous update, else the last 7 days (or what the user says).
- Records changed in the period for the audience's scope: projects (status, health, insight, next_step), decisions made, commitments done/slipped/new/due next, risks opened/changed/resolved, questions needing the audience, goal progress (`current`, accomplishments), the latest Weekly Review (`user/work/reviews/`) if it exists.
- Voice: `system/rules/writing.md`; `user/profile/voice-personal.md` / `voice-house.md`; `communication-style.md`.
- Template and examples: `reference/template.md`. If the user has an `active` template in `user/work/templates/` for this audience, it takes precedence.

## Procedure
1. **Away/paused.** If away is active or `status-updates` / the `status_updates` moment is paused, stop (job records the skip). Chat requests always work.
2. **Per audience** (job: every configured audience; skip if a draft for this ISO week exists and nothing relevant changed since, per `system/jobs/status-updates.md`):
   1. **Scope:** the projects, goals, and topics this audience cares about (linked to them, owned by them, or their organization's). For the user's manager: everything material the user owns.
   2. **Gather** the period's facts (Inputs), retrieving through L3. Prefer outcomes over activity.
   3. **Select:** what changed, what was decided, what's at risk, what the user needs from them, what's next. Drop items the audience doesn't care about. Never include items protected by data rules beyond what the rule allows, `notes_private`, or anything the user marked not to share with this person (`preferences.md`).
   4. **Voice:** manager and internal stakeholders → personal; customers, partners, external or official groups → house; unclear → personal (`system/rules/writing.md`). Match the audience's preferred length and format (bullets vs prose, numbers-first) from their record and past updates.
   5. **Write** using the template: one-line headline (overall state), highlights, decisions, risks/issues with mitigation, asks (explicit, with dates), next period. Keep to what fits in one screen. No citations or record IDs in the update text.
   6. **Check:** every statement traces to a record; numbers and dates correct; no promises the user hasn't made; tone fits.
   7. **Save** `user/work/status/YYYY-MM-DD-<audience-slug>.md` with frontmatter `type: status`, `date`, `audience`, `period_start`, `period_end`, `voice`, `sources` (records used), and the update body; append a `## Sources (for you)` list after the body, outside what would be sent.
   8. **Email draft (optional):** if the audience has an email, a mail connector with `mail.create_draft` exists, and `drafts_create` is `auto` (unless the audience's record or `preferences.md` names another channel), create a draft via `nova-write` (`mail.create_draft`); add an `approvals.md` entry (`send_communication`) in routines. Otherwise the file is the draft (e.g. for Slack or a doc), and the brief says where it is.
3. **Commit and log**; run-report row (audiences drafted, skipped, drafts created). The brief lists them under "Drafts ready to review".
4. **In chat:** show the update, the voice used, and offer: edit, shorten, create the email draft, or send (approval path in `nova-write` §4).

## Outputs
- `user/work/status/YYYY-MM-DD-<audience-slug>.md` per audience.
- Optional email drafts in the user's mail tool; `approvals.md` entries in routines.
- Activity-log line; run-report row (and "Drafts created" lines per `nova-write` `reference/email-drafts.md`).

## Guardrails
- Autonomy classes: `read`, `records_write` (status files), `drafts_create` (auto); sending is `send_communication` 🔒, posting to a channel is `send_communication` 🔒, sharing a doc is `share_expose` 🔒: all chat-only with approval (`system/rules/governance.md`). Never sent from a routine.
- Facts only from records; label anything inferred; never inflate progress or hide a slipped commitment the audience is owed.
- Data rules and per-person preferences on what to share apply to every audience.
- Away/paused respected (step 1).

## Done when
- Each configured audience has a saved update for the period (or a logged reason it was skipped).
- Each update is in the right voice, within one screen, with explicit asks and a next-period line, and has no citations in the sendable text.
- Any email draft exists only as a draft, with an approval entry when created by a routine.
