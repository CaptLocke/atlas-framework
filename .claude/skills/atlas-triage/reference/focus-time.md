---
type: skill-reference
skill: atlas-triage
---
# Protecting time for what the user owes (`focus_time_needed`)

Triage knows what the user owes, when it's due, and roughly how big it is (`effort`). This connects that to the calendar, so a week full of meetings doesn't quietly eat the time a commitment needs.

## 1. Effort (triage step 7)
For each open `i_owe` commitment without an `effort`, estimate one from what the work is, and record it as inferred (Updates line: "effort estimated: half_day"):
- `quick`: a reply, a short review, a decision.
- `hour`: a written answer, feedback on a document, a small analysis.
- `half_day`: a memo, a deck, a plan, a substantial review.
- `day`: a large document, a model, several connected pieces.

If the user states a size ("that'll take me a couple of hours"), use theirs. Users can also say "the deck is a full day".

## 2. When the trigger fires
The condition is in `system/triggers.md` (`focus_time_needed`). Read the calendar from now to the due date with `calendar.list_range`.
- **Busy:** every event counts, including ones the meeting filter hides (tentative, unanswered, all-day) and the user's own holds.
- **Free:** only time inside `rhythms.yaml: work_hours` on work days counts, and `working-style.md` / `preferences.md` are respected ("no focus time on Friday afternoons", "mornings are best for writing").
- **Needed:** `hour` = 1 h, `half_day` = 4 h, `day` = 8 h. A `day` may be split into two blocks on different days.

Skip it when:
- The user already has a focus or hold event that names the work.
- An Atlas focus block for this commitment exists (marker below).
- The commitment's Updates show the user declined a block for this due date.

## 3. The proposal
- **Pick a slot.** Choose the gap that leaves a buffer before the due time: prefer the earliest gap that fits whole, starting at least 30 minutes after the previous meeting. On the due date, don't use the last two hours before the due time unless that's the only option.
- **In chat:** "Pricing feedback for Jordan is due Thursday and your calendar is nearly full. Block Wed 9:00–11:00 to write it?" On yes, go to §4.
- **In a routine:** add one `approvals.md` entry:
```markdown
## A-2026-10-13-02 · pending
- **Action:** own_calendar_manage: create focus block "Focus: pricing feedback for Jordan", Wed Oct 14 9:00–11:00
- **Why:** Due Thu Oct 15 ([[commitments/send-pricing-feedback]]); about 2 hours of work and only 2.5 free hours before then
- **Prepared:** calendar hold, no attendees, on your calendar only
- **Requested by:** routine:nightly-cycle · 2026-10-13
- **Status history:** pending 2026-10-13
```
  The brief lists it under "Needs you" with the slot. An entry whose slot has already passed is marked `expired` the next time triage runs; triage may then propose a new slot once.
- **No slot fits:** don't propose an overlapping block. Add one line to the brief's Due section instead: "No free 2-hour slot before Thursday. The Wednesday 2:00 vendor sync (tentative) is the easiest to move." Prefer, in order, meetings the user hasn't accepted, recurring meetings they organize, and large meetings where they're optional.

## 4. Creating the block (chat only, after the user's yes)
`calendar.create_event` on the user's own calendar, **with no attendees** (`own_calendar_manage`, propose; the yes is the confirmation):
- Title "Focus: <commitment title>"; description "Held by Atlas for [[commitments/<slug>]]", with no other content.
- Shown as busy, with no reminders beyond the user's defaults.

Then append to the commitment `- <date>: focus block created for <slot> (event id …)` (the marker), and mark the approvals entry `approved`, then `executed`. If the user says no, append `focus block declined for due <date>` so Atlas doesn't ask again for that date.

Adding attendees, or moving or cancelling someone else's meeting, is never part of this. Those are `send_communication` and need the user to do it or approve it explicitly.

## 5. Afterwards
- **Done early:** if the commitment is done before the block, mention it in the brief ("Your Wed 9:00 focus block is free now"). Deleting the event is the user's call, or `destructive` with approval.
- **Due date moves:** if the due date moves, the trigger key changes, so Atlas re-evaluates. An existing block that still fits stays.
