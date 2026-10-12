---
type: guide
section: attestation
title: Permission to store work information
order: 7
version: 1.0.0
used_by: [nova-setup, nova-review, nova-settings]
---
# Permission to store work information

The exact text Nova shows when it asks the user to confirm they may store work information in their private repository, and how the answer is recorded. Used by `nova-setup` (setup step 5), `nova-review` (quarterly role refresh), and whenever the user says their employer or role has changed. Show the explanation and statement **verbatim** (fill in the bracketed values); adapt only the surrounding conversation.

## Explanation shown first
> Before I bring in anything about your work, one important check.
>
> Everything I learn (emails, meetings, documents, notes, and what I work out from them) will be stored in **your private GitHub repository, [owner/repo]**. Only you can see it. It isn't shared with your employer, with Nova's maker, or with anyone else, and I'll never make it public or add anyone to it. I keep sensitive material to a minimum: by default I keep only pointers or summaries of confidential, health, and legally privileged material, and you can tighten that further at any time.
>
> Some employers don't allow work information to be stored outside company systems, even privately. Only you can know whether yours does. If you're not sure, it's worth checking your company's policy, or asking your manager or IT team, before we go on.
>
> If you're permitted, please confirm the statement below. I'll record it with today's date, and I'll ask you to confirm it again once a quarter, and whenever you change jobs or roles.

## The statement
> **I confirm I am permitted to store work information from my employer in this private GitHub repository.**
>
> Employer: [employer name] · Role: [role]

Ask for a clear yes in the user's own words ("Yes, I confirm"). If the user works for themselves, their own business is the employer; the statement is the same.

## If the user says no or isn't sure
> No problem. I won't bring in or store anything about your work until you've confirmed. Your setup is saved, so when you're ready, just say "I'm ready to confirm" or "Continue setting up Nova".

Record nothing in `attestation`. Mark setup step 5 incomplete in `user/.state/setup.yaml` and stop before any ingestion.

## How it's recorded
On a clear yes, write `user/settings/nova.yaml: attestation` (format: `system/schemas/settings.md`):
- `statement`: the statement above, exactly, without the employer/role line.
- `employer`: link to the employer's organization record; `role`: the role as stated.
- `recorded_on`: today; `nova_version`: the installed version.
- `reconfirm_due`: the first business day of the next quarter.

Log it in the activity log. Confirm back to the user in one line: "Thanks, recorded on [date]. I'll check in again at the start of next quarter."

## Re-confirmation (quarterly)
Asked during the quarterly role refresh (`nova-review`), on or after `reconfirm_due`:
> A quick quarterly check: are you still permitted to store work information from [employer] in your private GitHub repository? Has anything changed about your role or your employer's policy?

- **Still yes:** update `recorded_on`, `nova_version`, and `reconfirm_due`; keep the statement.
- **No longer permitted:** stop ingestion immediately (pause all `ingest` work via `rhythms.yaml: paused`), and offer the user's options: keep less (minimize to pointers and summaries), export, forget, or permanently erase. Each follows its normal approval.

## Re-confirmation (job or role change)
When the user says they've changed employer or role, or the quarterly role refresh finds it:
> Congratulations on the change. Because your employer or role has changed, I need a fresh confirmation before I bring in anything new. Are you permitted to store work information from [new employer] in your private GitHub repository?

Then show **The statement** again with the new employer and role. Until confirmed, ingestion is paused. What's already stored from the previous employer stays untouched until the user decides; offer to archive it, minimize it, export it, or erase it.
