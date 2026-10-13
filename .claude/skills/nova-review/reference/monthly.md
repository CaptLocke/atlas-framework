---
type: skill-reference
skill: nova-review
---
# Monthly report

Period: the previous calendar month (`YYYY-MM`), produced on the first run on or after the month's first business day (the `monthly` job decides when).

## File format
```markdown
---
type: report
date: 2026-11-02
period: 2026-10
sources: ["[[goals/...]]", "..."]
---
# October 2026 · monthly report

<3–4 line summary: goals at a glance, anything needing the user>

## Goal progress
## Your knowledge          (from nova-health, user mode)
## Nova's health           (from nova-health, system mode)
## Automation review
## What Nova learned
## Needs you
```
Sections whose moment is off say "Turned off in your settings."

## Goal progress
For each `active` goal (sorted by period end):
- **Progress:** `current` vs `target` with date; trend since last month.
- **Evidence for:** accomplishments, done projects, decisions advancing it (cited).
- **Evidence against:** slipped commitments, `at_risk`/`off_track` projects, active risks linked to it.
- **Needs attention:** one line.
Update `current` only when a source states a new measured value (record update, cited). Status changes (`achieved`, `missed`, `dropped`) are questions for the user.

## Automation review
Per routine and job, from run reports for the month:
| Job | Runs | OK | Avg duration | Items | Used vs ignored | Suggestion |
|---|---|---|---|---|---|---|
| ingest | 31 | 31 | 6 min | 1,140 in / 402 filed | n/a | none |
| email-drafts | 22 | 22 | 3 min | 61 drafts | 38 sent after edits, 23 untouched | Draft only for threads older than 1 day? |
Signals for "used vs ignored":
- Drafts: drafts later seen as sent (`mail.list_sent` evidence) vs left untouched or deleted by the user.
- Insights: `acted`/`dismissed`/`expired` counts by kind (`insights.md` and that month's `user/inbox/archive/<YYYY-MM>-insights.md`); trend vs last month.
- Approvals: approved/rejected/expired (`approvals.md` and the month's archive file).
- Prep notes and status drafts: referenced or edited in chat, sent status updates.
- Briefs: the user's chat activity on brief days (no tracking beyond the repo).
Suggestions (each a one-line proposal with reason): turn off or reduce something ignored; change a schedule to when the user actually works; switch profile if runs are long/heavy for the plan (R2) or if the user wants fresher information; fix a recurring failure. Queue each in `approvals.md` as a `behavior_settings` proposal (or `questions.md` when it's a choice), never applied by this skill.

## What Nova learned
Run the learning pass (`.claude/skills/nova-triage/reference/learning.md` §2) over the last 60 days. Report rules confirmed this month, proposals queued (max 3, as `questions.md` entries), and `feedback` counts by signal against last month, in one short table. If nothing reached a pattern: "Nothing new learned this month."

## Success indicators
Compute per `reference/indicators.md`; write `health.yaml: indicators` for the month; show a small table with last month's values for comparison and a one-line reading ("Corrections are down from 6 to 3.").

## Needs you
The combined list (max ~7) from all sections, each also present as a `questions.md` or `approvals.md` entry so it can be handled in any chat.
