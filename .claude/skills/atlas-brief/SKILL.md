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
3. **Set the window.** "What changed" covers from the previous brief's creation to now. For `target: tomorrow`, Today = tomorrow's calendar; Due from you is counted from tomorrow.
4. **Build sections** in this order (template: `reference/template.md`). Omit a section that's empty, except Top priorities.
   0. **Action needed** (only if any): every open `action` question in `user/inbox/questions.md` (things only the user can do, such as updating their Project instructions after an update), oldest first, never capped. One line each with what to do; when the entry has `Copy text`, say "the text to copy is on the Guide page, or ask me in chat". It stays in every brief until the entry is closed.
   1. **Today:** meaningful events shown by the meeting filter (`rhythms.yaml: meetings`; all-day, tentative, and unanswered events may be set to skip), in time order, each with a one-line why-it-matters and a link to its prep note (`prep` field) or "no prep needed". Flag conflicts and back-to-backs.
   2. **Due from you:** `i_owe` items that are slipped, past due or due today, and today's deadline events: overdue first, most days late first, then due today, then priority. These are the items of the Today page's Due from you card, which groups them by person; today's deadline events show there as Your day pills instead. Each shows how late it is or "due today", and `next_step`. Then one bold line for what's due tomorrow, the `deadline_approaching` warning ("**Tomorrow:** pricing feedback to Jordan"), since the brief has no This week strip to show it. Items due later than tomorrow aren't listed: they're on the Today page's This week and on Work.
   3. **Waiting on:** open `waiting_on` items that are overdue or due within 7 days, soonest first, with who and when (overdue ones show days late), plus any waiting 7+ days without a due date; note if a follow-up draft is ready.
   4. **What changed:** never imported history (`.claude/skills/atlas-capture/reference/import.md` §10). At most 5 bullets, flagged content not among them (step 10): decisions made (naming a decider only from the record's `deciders`, and "relayed by" when `relayed_by` is set), projects whose health changed, new risks, new commitments to the user, notable replies. Include a "From your Evening Thoughts" line group if last night's journal produced items; each item it names links its own record (the idea, the commitment, the person), not only the journal. Add "What's new in Atlas" (one line) if `atlas.yaml: installed_version` changed since the last brief.
   5. **Top priorities:** up to 5 items, chosen and ordered by `atlas-triage/reference/signals.md` §Top priorities (candidates, order and how many are there, not here). Each with a one-line reason tied to a goal or person, and its slot from §E ("11:30 AM focus"; "won't fit today: send a date at 4:15 PM").
   6. **Insights:** up to `brief_max` of the highest-scoring `new` insights not shown before; each with its one-line why and link, and "Draft ready in <where>" when its entry has a `Draft:` line. Then mark them `seen` (via `atlas-insights` lifecycle).
   7. **Drafts ready to review:** each draft created since the last brief, with recipient, subject, why, and where it is (e.g. "in your Outlook drafts"). Then the latest `email-drafts` run report's **Still unsent**, oldest first, each with its age counted to the brief's date ("4 days in your drafts") and, when stale or its named date has passed since, "the 10/16 date in it has passed: update or delete it"; at most 3, then "+N more".
   8. **Awaiting your approval:** pending approvals with ID, action, and why; note any expiring within 3 days.
   9. **Questions from Atlas:** first, if any, one **Looks done (N)** line: every open `commitment` question with an `Evidence:` line, each as the item, linked to its commitment, and its evidence in a few words, ending "Say which are done, or all"; at most 5, then "+N more in Questions". It sits outside the cap of 3. Then up to 3 open questions other than `action` and Looks done ones (vague commitments to confirm, relationships, profile proposals): first those raised since the last brief, then the oldest. Each links the record or source it's about. "+N more in Questions" if needed.
   10. **Needs attention** (only if any): first, one line per source flagged as suspicious since the last brief (the run reports' "Suspicious content flagged"), saying who it came from, when, what it asked for and that Atlas ignored it, with no link (nothing links to a flagged source, `atlas-capture` §8); then high-severity known issues from `health.yaml` with their one-step fix. Never capped: flagged content goes here, never in What changed.
   Also compute **Today's week data** for the 7 days from the target date (§D), and **place** the priorities (§E) before writing Top priorities. Under Today, one line on the time between meetings: "3.5 h between meetings; all 5 due today are placed" (or which aren't).
5. **Two-minute check.** Target ≤ ~350 words. Caps: Due from you 5 (the Tomorrow line apart), Waiting on 5, What changed 5, priorities 5, Questions 3; overflow becomes "+N more on the Work page". Every item links each record it names, in that item, not only the record behind it: a health line links each project it names as well as the risk, a roll-up links each record as well as its source (`system/rules/writing.md`). Lead with what needs the user.
6. **Write** `user/work/briefs/YYYY-MM-DD.md` (target date) with frontmatter `type: brief`, `date`, `generated` (timestamp), `window_start`, `sources` (records cited). If the file exists (re-run), regenerate it but keep any "Since last night" section.
7. **Republish** with `atlas-dashboards` every dashboard whose contract lists `daily-brief` in `republished_by`: always Today, with the week data from §D.
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
3. Republish Today. The page has no "Since last night" section: the new items appear in its own sections (Schedule, Due from you, Needs you). Tell the user in one line only if something is urgent.

### D. Today's week data
Used by A for the Today page's This week and Coming up sections. Field definitions: `system/dashboards/daily-brief.contract.md`. The range is always the 7 days from the target date. From event records (events hidden by the meeting filter still count as busy), `rhythms.yaml: work_hours` and open commitments:
1. **Days** (`week.days[]`): for each day, whether it's a work day, the number of meetings, meeting hours, free hours inside work hours, and what's due: commitments due that day in either direction (I owe first), and deadline and milestone events, at most 5 per day.
2. **Totals:** `week.work_hours_per_day` and the week's `free_hours`. With no calendar connected, `week` is `null` and the section is hidden.
3. **Coming up** (`milestones[]`): deadline and milestone events from tomorrow to 60 days out, soonest first, at most 8, each with its project (the event's first linked project) and a one-line note.
4. **Schedule extras** for today's events: `project` (the event's first linked project), and `prep.todo` (what to prepare, or when `meeting-prep` will write the note) where there's no prep summary.
Pass it all to `atlas-dashboards` with the Today republish.

### E. Placement
Which open window each priority goes in is a rule, run by a tool, so the same day always gives the same plan; only the wording is the brief's. Used by A for Top priorities and the Today page's timeline.
1. **Input** (`system/tools/placement.py` names every field): the target date and `atlas.yaml: timezone`; `rhythms.yaml: work_hours` and `focus.shortest_window` (missing = 30); the target date's events that block time: meetings shown by the meeting filter and the user's holds (all-day events never block); the Top priorities in rank order, each commitment line with its `effort`, `due` and `status`, each project line with its open `i_owe` commitments; every other open `i_owe` commitment due on the target date. In chat for `today`, also `now` (the current time), so windows already past aren't offered.
2. **Run** `python3 -I system/tools/placement.py <file>` with the input written to `.atlas-tmp/placement.json`. It prints the windows and each item's slot. Don't adjust its result; if it fails, leave slots out and say so in the run report.
3. **Words:** a `window` slot is "<window start> focus", as the page calls a window with something placed in it (one with nothing placed is free time); `wont_fit` is "won't fit today: send a date at <date_at>" (or "won't fit today" with no window); `none` says nothing. An unsized item (`sized: false`) adds "(size unknown)", and triage sets its `effort` next run. Times 12-hour with AM or PM (`system/rules/writing.md`).
4. **To the page:** `day`, `windows` and each priority's `slot`, with the items' titles (`system/dashboards/daily-brief.contract.md`).

## Outputs
- `user/work/briefs/YYYY-MM-DD.md`, `user/work/briefs/YYYY-MM-DD-catch-up.md`.
- Insight status updates in `user/inbox/insights.md` (`seen`).
- Today (and any other `daily-brief`-listed dashboard) republished, with its week data (§D); activity-log line; run-report row (brief date, sections, dashboards republished).
- In chat: the brief, readable in two minutes.

## Guardrails
- Autonomy classes: `read`, `records_write` (brief files, insight statuses), `dashboards_refresh`. Clearing away after its end date completes the user's instruction and is not a `behavior_settings` change. See `system/rules/governance.md`.
- The brief proposes; it never acts. Sending, accepting invites, or approving anything happens only in chat through the approval procedure.
- Data rules: pointer-only items appear as "a confidential document from Legal arrived" with no content.
- Never invent priorities without a reason; never list an item without a link.
- Away/paused: no brief while away (catch-up on return); respect a paused `daily_brief` moment.

## Done when
- The brief file exists for the target date with all non-empty sections, every item linked, and fits the caps.
- Top priorities follow `atlas-triage/reference/signals.md` §Top priorities, each citing a goal or a person as the reason.
- Insights shown are marked `seen`; pending approvals and drafts are all listed.
- The Today page shows the new brief; the change is committed and logged.
