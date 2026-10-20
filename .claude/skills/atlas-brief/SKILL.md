---
name: atlas-brief
description: "Build the Daily Brief or the catch-up brief and refresh the Today page. Use for \"brief me\", \"what does my day look like\", \"what's on today\", \"what do I need to know\", and the daily-brief job."
---
# Daily Brief

## Purpose
Give the user a two-minute, trustworthy picture of where they stand: what's on, what's due or slipping, what they're waiting on, what changed, what matters most, and what needs their decision. After time away, give them a five-minute catch-up instead of an inbox mountain.

## When to use
- **Job:** `daily-brief` (with `target: today | tomorrow`), after ingest, triage, intelligence, email-drafts, and meeting-prep.
- **Chat:** "Brief me", "What's on today?", "What's my day look like?", "Rebuild today's brief"; and kernel §2 step 3 (add "Since last night" after a quick catch-up ingest).
- **Return from away:** the first `daily-brief` run whose target date is after `rhythms.yaml: away.end`, or, for open-ended away (`end: null`), after the user ends it (`atlas-away`) → catch-up brief.

## Inputs
- Target date: `today` or `tomorrow` in `atlas.yaml: timezone` (job modifier or the user's words; default `today` in chat).
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
   2. **Due soon / slipping:** `i_owe` items slipped or due within the `deadline_approaching` window (default 3 days), and deadline events. Items due tomorrow (the trigger's escalation) go first and in bold, then slipped items, then the rest by due date, then priority (the same order as the Daily Brief page). Each shows due date and `next_step`.
   3. **Waiting on:** open `waiting_on` items that are overdue or due within 7 days, soonest first, with who and when (overdue ones show days late), plus any waiting 7+ days without a due date; note if a follow-up draft is ready.
   4. **What changed:** never imported history (`.claude/skills/atlas-capture/reference/import.md` §10). At most 5 bullets: decisions made, projects whose health changed, new risks, new commitments to the user, notable replies. Include a "From your Evening Thoughts" line group if last night's journal produced items. Add "What's new in Atlas" (one line) if `atlas.yaml: installed_version` changed since the last brief.
   5. **Top priorities:** 3–5 items ranked against active goals first, then urgency (triage `priority`, due dates, who's waiting). Each with a one-line reason tied to a goal or person.
   6. **Insights:** up to `brief_max` of the highest-scoring `new` insights not shown before; each with its one-line why and link, and "Draft ready in <where>" when its entry has a `Draft:` line. Then mark them `seen` (via `atlas-insights` lifecycle).
   7. **Drafts ready to review:** each draft with recipient, subject, why, and where it is (e.g. "in your Outlook drafts").
   8. **Awaiting your approval:** pending approvals with ID, action, and why; note any expiring within 3 days.
   9. **Questions from Atlas:** up to 3 open questions other than `action` ones (vague commitments to confirm, relationships, profile proposals): first those raised since the last brief, then the oldest. Each links the record or source it's about. "+N more in Questions" if needed.
   10. **Needs attention** (only if any): high-severity known issues from `health.yaml` with their one-step fix.
   Also compute the **Week Ahead planning data** for the 7 days from the target date (§D).
5. **Two-minute check.** Target ≤ ~350 words. Caps: Due soon 5, Waiting on 5, What changed 5, priorities 5, Questions 3; overflow becomes "+N more on the Commitments page". Every item links to its record (`system/rules/writing.md`). Lead with what needs the user.
6. **Write** `user/work/briefs/YYYY-MM-DD.md` (target date) with frontmatter `type: brief`, `date`, `generated` (timestamp), `window_start`, `sources` (records cited). If the file exists (re-run), regenerate it but keep any "Since last night" section.
7. **Republish** with `atlas-dashboards` every dashboard whose contract lists `daily-brief` in `republished_by` (always the Daily Brief; Week Ahead with the planning data from §D).
8. **Commit and log** (`atlas(routine:<name>): daily brief for <date>` or `atlas(chat): …`).
9. **In chat**, present the brief itself (not a summary of it) in the user's preferred format, then offer the obvious next action ("Want me to send the follow-up to Dana?").

### B. Catch-up brief (after away)
1. Window = `away.start` to now. Write `user/work/briefs/YYYY-MM-DD-catch-up.md` (`type: brief`, `kind: catch-up`, `window_start`, `window_end`).
2. Sections (template: `reference/catch-up-template.md`), readable in five minutes:
   - **Needs you first:** open `action` questions (first, uncapped), approvals still pending from the away period (their 14-day expiry was paused during away, so none lapsed while the user was out), slipped `i_owe` items, deadlines in the next 3 days, held trigger actions (follow-ups for overdue `waiting_on`, new-project questions), decisions waiting on the user.
   - **What happened:** by project or person: decisions made, commitments made to/by the user, meetings held with outcomes. Max ~10 bullets; group the rest.
   - **What changed:** project health changes, new risks and issues, status changes, new people.
   - **Can wait:** FYIs, ideas, insights still `new` from the away period (lower-scoring ones; the top ones go to the normal brief's Insights), noise-adjacent items worth knowing.
3. **Held triggers.** In `user/.state/triggers.yaml`, take the `held: true` entries: list under Needs you first those whose condition still holds today (an overdue item that's still open counts), leave out a `deadline_approaching` or `key_meeting_upcoming` whose date has passed, then remove every `held` entry. The next triage and email-drafts runs act on the conditions that are still true, as normal triggers (`system/schemas/formats.md` §triggers.yaml).
4. Also produce the target date's normal Daily Brief (A) with a link to the catch-up brief at the top.
5. Clear `rhythms.yaml: away` (`start`, `end`, `set_on` to null) as `system/jobs/daily-brief.md` directs; this completes the user's own instruction, so no confirmation is needed (`atlas-away`). In chat on an early return, `atlas-away` clears it and calls this mode.
6. Republish, commit, log.

### C. "Since last night" (after the morning quick catch-up)
1. Input: the items `atlas-capture` filed in the quick catch-up ingest.
2. Append `## Since last night` to today's brief file (create a minimal brief with Today and this section if none exists) with ≤5 bullets: new replies, new commitments, changed or new events today, anything urgent. Link each item.
3. Republish the Daily Brief dashboard. The page has no "Since last night" section: the new items appear in its own sections (Today, Due and slipping, Waiting on others, Needs you). Tell the user in one line only if something is urgent.

### D. Week Ahead planning data
Used by A and by `atlas-review`'s weekly review. The range is set by `system/dashboards/week-ahead.contract.md` (Purpose, "Which seven days"): next Monday to Sunday once this week's weekly review has run, otherwise the 7 days from the target date. Field definitions: `system/dashboards/week-ahead.contract.md`. From event records (events hidden by the meeting filter still count as busy), `rhythms.yaml: work_hours`, open commitments with `effort`, `working-style.md`, and `preferences.md`:
1. **Focus suggestions** (`focus[]`): free gaps of at least 60 minutes (the same gaps `free_hours` counts) inside work hours on work days, each matched to the highest-priority `i_owe` work due within the week that isn't already scheduled; at most 1 per day and 4 per week; respect working style and preferences (e.g. no Friday afternoons). Each has `start`, `end`, `label`, and a one-line `reason`. A focus block awaiting approval (`focus_time_needed`) is shown as the suggestion for its slot. Suggestions only: putting a hold on the calendar is `own_calendar_manage` (propose, in chat).
2. **Time:** each day's `free_hours`; the week's `summary.focus_hours`, `work_due_hours`, and `unsized`.
3. **Watch-outs** (`watchouts[]`): overloaded days, no-break stretches, double bookings, unprotected deadlines.
4. **Meetings:** `note` (one line on why it matters or what to raise; from the event's `insight` or the prep note), `project` (the event's first linked project), `prep.summary` (first line of the prep note's suggested agenda) and `prep.todo` (what to prepare, or when `meeting-prep` will write the note).
5. **Outcomes:** from the weekly review whose "next week" contains the range's first day, with `status` refreshed from the linked records; before the first weekly review, propose up to 3 (contract, Sources).
6. **Headline** (`meta.headline`): one line on the shape of the week.
Pass all of it to `atlas-dashboards` with the Week Ahead republish.

## Outputs
- `user/work/briefs/YYYY-MM-DD.md`, `user/work/briefs/YYYY-MM-DD-catch-up.md`.
- Insight status updates in `user/inbox/insights.md` (`seen`).
- Daily Brief (and other `daily-brief`-listed) dashboards republished, including the Week Ahead planning data (§D); activity-log line; run-report row (brief date, sections, dashboards republished).
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
