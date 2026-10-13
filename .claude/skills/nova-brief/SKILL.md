---
name: nova-brief
description: "Assemble the Daily Brief (today's or tomorrow's) and the catch-up brief after away mode, add the \"Since last night\" section after the morning catch-up, and republish the Daily Brief dashboard. Use for \"what's my day look like\", \"brief me\", \"what's on today\", \"what do I need to know\", \"rebuild my brief\", and when the daily-brief job runs."
---
# Daily Brief

## Purpose
Give the user a two-minute, trustworthy picture of where they stand: what's on, what's due or slipping, what they're waiting on, what changed, what matters most, and what needs their decision. After time away, give them a five-minute catch-up instead of an inbox mountain.

## When to use
- **Job:** `daily-brief` (with `target: today | tomorrow`), after ingest, triage, intelligence, email-drafts, and meeting-prep.
- **Chat:** "Brief me", "What's on today?", "What's my day look like?", "Rebuild today's brief"; and kernel §2 step 3 (add "Since last night" after a quick catch-up ingest).
- **Return from away:** the first `daily-brief` run whose target date is after `rhythms.yaml: away.end`, or, for open-ended away (`end: null`), after the user ends it (`nova-away`) → catch-up brief.

## Inputs
- Target date: `today` or `tomorrow` in `nova.yaml: timezone` (job modifier or the user's words; default `today` in chat).
- `user/.state/jobs.yaml` (readiness and staleness), `user/.state/health.yaml` (known issues), `user/.state/triggers.yaml`.
- Events for the target date (event records; `calendar.list_range` if records may be stale) and their `prep` notes in `user/work/prep/`.
- Commitments (index + records): open, slipped, due soon; `insight`/`next_step`; priorities from triage.
- Goals (active) for ranking.
- Changes since the last brief: activity log, run reports, records updated, journal (Evening Thoughts), approvals, questions.
- `user/inbox/insights.md` (`new`, highest score), `rhythms.yaml: insights.brief_max` (default 3).
- Drafts created since the last brief: run reports and activity log (email-drafts, status-updates, triage follow-ups).
- `user/inbox/approvals.md` (`pending`), `user/inbox/questions.md` (`open`; `action` entries lead the brief).
- `user/profile/communication-style.md` (numbers-first vs narrative, length).

## Procedure

### A. Daily Brief
1. **Away/paused check.** If the target date falls within away (including open-ended away, `end: null`), or `daily_brief` / `daily-brief` is paused, stop (the job records `skipped_away` / `skipped_paused`). If the target date is after `away.end` (or the user has just ended an open-ended away) and no catch-up brief exists for this return, do B first.
2. **Readiness.** Check `jobs.yaml`: if `ingest` or `triage` hasn't succeeded since the last brief, either run them (job context, per the job spec) or proceed and add one line under Today: "Based on information up to <time>."
3. **Set the window.** "What changed" covers from the previous brief's creation to now. For `target: tomorrow`, Today = tomorrow's calendar; Due soon is counted from tomorrow.
4. **Build sections** in this order (template: `reference/template.md`). Omit a section that's empty, except Top priorities.
   0. **Action needed** (only if any): every open `action` question in `user/inbox/questions.md` (things only the user can do, such as updating their Project instructions after an update), oldest first, never capped. One line each with what to do; when the entry has `Copy text`, say "the text to copy is on the Control Center, or ask me in chat". It stays in every brief until the entry is closed.
   1. **Today:** meaningful events shown by the meeting filter (`rhythms.yaml: meetings`; all-day, tentative, and unanswered events may be set to skip), in time order, each with a one-line why-it-matters and a link to its prep note (`prep` field) or "no prep needed". Flag conflicts and back-to-backs.
   2. **Due soon / slipping:** `i_owe` items slipped or due within the `deadline_approaching` window (default 3 days), and deadline events. Items due tomorrow (the trigger's escalation) go first and in bold. Each shows due date and `next_step`.
   3. **Waiting on:** aging `waiting_on` items (oldest first, with days waiting) and any overdue; note if a follow-up draft is ready.
   4. **What changed:** at most 5 bullets: decisions made, projects whose health changed, new risks, new commitments to the user, notable replies. Include a "From your Evening Thoughts" line group if last night's journal produced items. Add "What's new in Nova" (one line) if `nova.yaml: installed_version` changed since the last brief.
   5. **Top priorities:** 3–5 items ranked against active goals first, then urgency (triage `priority`, due dates, who's waiting). Each with a one-line reason tied to a goal or person.
   6. **Insights:** up to `brief_max` of the highest-scoring `new` insights not shown before; each with its one-line why and link, and "Draft ready in <where>" when its entry has a `Draft:` line. Then mark them `seen` (via `nova-insights` lifecycle).
   7. **Drafts ready to review:** each draft with recipient, subject, why, and where it is (e.g. "in your Outlook drafts").
   8. **Awaiting your approval:** pending approvals with ID, action, and why; note any expiring within 3 days.
   9. **Questions from Nova:** up to 3 open questions other than `action` ones (vague commitments to confirm, relationships, profile proposals), oldest first; "+N more" if needed.
   10. **Needs attention** (only if any): high-severity known issues from `health.yaml` with their one-step fix.
   Also compute the **focus suggestions** for the Week Ahead dashboard (`system/dashboards/week-ahead.contract.md`, `focus[]`): for the 7 days from the target date, find free gaps of ≥ 90 minutes inside `rhythms.yaml: work_hours` on work days (from event records, counting events hidden by the meeting filter as busy); match each to the highest-priority `i_owe` work due within the week that isn't already scheduled; at most 1 per day and 4 per week; respect `working-style.md` and `preferences.md` (e.g. no Friday afternoons). Each has `start`, `end`, `label`, and a one-line `reason`. Pass them to `nova-dashboards` with the republish; also produce the one-line Week Ahead `headline`. They are suggestions only (putting a hold on the calendar is `own_calendar_manage`, propose, in chat).
5. **Two-minute check.** Target ≤ ~350 words. Caps: Due soon 5, Waiting on 5, What changed 5, priorities 5, Questions 3; overflow becomes "+N more on the Work Board". Every item links to its record (`system/rules/writing.md`). Lead with what needs the user.
6. **Write** `user/work/briefs/YYYY-MM-DD.md` (target date) with frontmatter `type: brief`, `date`, `generated` (timestamp), `window_start`, `sources` (records cited). If the file exists (re-run), regenerate it but keep any "Since last night" section.
7. **Republish** with `nova-dashboards` every dashboard whose contract lists `daily-brief` in `republished_by` (always the Daily Brief; Week Ahead with the focus suggestions above).
8. **Commit and log** (`nova(routine:<name>): daily brief for <date>` or `nova(chat): …`).
9. **In chat**, present the brief itself (not a summary of it) in the user's preferred format, then offer the obvious next action ("Want me to send the follow-up to Dana?").

### B. Catch-up brief (after away)
1. Window = `away.start` to now. Write `user/work/briefs/YYYY-MM-DD-catch-up.md` (`type: brief`, `kind: catch-up`, `window_start`, `window_end`).
2. Sections (template: `reference/catch-up-template.md`), readable in five minutes:
   - **Needs you first:** open `action` questions (first, uncapped), approvals still pending from the away period (their 14-day expiry was paused during away, so none lapsed while the user was out), slipped `i_owe` items, deadlines in the next 3 days, held trigger actions (follow-ups for overdue `waiting_on`, new-project questions), decisions waiting on the user.
   - **What happened:** by project or person: decisions made, commitments made to/by the user, meetings held with outcomes. Max ~10 bullets; group the rest.
   - **What changed:** project health changes, new risks and issues, status changes, new people.
   - **Can wait:** FYIs, ideas, insights still `new` from the away period (lower-scoring ones; the top ones go to the normal brief's Insights), noise-adjacent items worth knowing.
3. Also produce the target date's normal Daily Brief (A) with a link to the catch-up brief at the top.
4. Clear `rhythms.yaml: away` (`start`, `end`, `set_on` to null) as `system/jobs/daily-brief.md` directs; this completes the user's own instruction, so no confirmation is needed (`nova-away`). In chat on an early return, `nova-away` clears it and calls this mode.
5. Republish, commit, log.

### C. "Since last night" (after the morning quick catch-up)
1. Input: the items `nova-capture` filed in the quick catch-up ingest.
2. Append `## Since last night` to today's brief file (create a minimal brief with Today and this section if none exists) with ≤5 bullets: new replies, new commitments, changed or new events today, anything urgent. Link each item.
3. Republish the Daily Brief dashboard. Tell the user in one line only if something is urgent.

## Outputs
- `user/work/briefs/YYYY-MM-DD.md`, `user/work/briefs/YYYY-MM-DD-catch-up.md`.
- Insight status updates in `user/inbox/insights.md` (`seen`).
- Daily Brief (and other `daily-brief`-listed) dashboards republished, including Week Ahead `focus[]` suggestions; activity-log line; run-report row (brief date, sections, dashboards republished).
- In chat: the brief, readable in two minutes.

## Guardrails
- Autonomy classes: `read`, `records_write` (brief files, insight statuses), `dashboards_refresh`. Clearing away after its end date completes the user's instruction and is not a `behavior_settings` change. See `system/rules/governance.md`.
- The brief proposes; it never acts. Sending, accepting invites, or approving anything happens only in chat through the approval procedure.
- Data rules: pointer-only items appear as "a confidential document from Legal arrived" with no content.
- Never invent priorities without a reason; never list an item without a link.
- Away/paused: no brief while away (catch-up on return); respect a paused `daily_brief` moment.

## Done when
- The brief file exists for the target date with all non-empty sections, every item linked, and fits the caps.
- Top priorities each cite a goal, a person, or a deadline as the reason.
- Insights shown are marked `seen`; pending approvals and drafts are all listed.
- The Daily Brief dashboard shows the new brief; the change is committed and logged.
