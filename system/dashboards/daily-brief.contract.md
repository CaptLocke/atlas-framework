---
type: dashboard-contract
name: daily-brief
template: daily-brief.html
republished_by: [daily-brief]
size_budget_kb: 340
stale_after_hours: 36
---
# Dashboard: daily-brief (the Today page)

## Purpose
**Today** answers one question: what needs me today, and what's coming this week? Readable in two minutes, in this order: what needs the user (anything only they can do, approvals, questions, drafts ready to review), the top three priorities with why, today's schedule (meetings with prep status, plus today's deadlines and milestones), what is due or slipping (what the user owes beside what they're waiting on), up to three insights, then **This week** (a seven-day strip of meeting load against work hours, free hours, and what's due each day, milestones marked) and **Coming up** (milestones and deadlines in the next 60 days).

The page keeps the slug `daily-brief`, so its `url` and `last_published` carry over; its title is **Today**. It is the page view of the written **Daily Brief**, `user/work/briefs/YYYY-MM-DD.md`; the brief file and this page are built in the same step and must agree on everything they both show. The week strip and Coming up come from the same run's planning data (`atlas-brief` §D) and have no counterpart in the brief file.

Also republished by any chat that runs the morning catch-up (kernel §2.3); what it brings in shows up in the page's own sections (a new commitment under Due and slipping, a moved meeting under Schedule), not as a separate list. After away mode it renders the catch-up brief (`brief.kind: "catch-up"`, title "Catch-up Brief"), which adds a "While you were away" section.

## Data (JSON shape embedded in the page)
Envelope: `meta` as in `system/dashboards/README.md`; `meta.title` = `"Today"`; `meta.as_of` = the brief's date (tomorrow when built with `target: tomorrow`).

```json
{
  "meta": { "dashboard": "daily-brief", "schema_version": 1, "title": "Today", "as_of": "2026-10-13", "…": "…" },
  "brief": { "date": "2026-10-13", "kind": "daily", "path": "user/work/briefs/2026-10-13.md",
             "headline": "A customer-heavy day: …", "away": null },
  "actions": [ { "id": "Q-2026-10-13-01", "text": "Update your Atlas Project's instructions (Atlas was updated to 1.1.0).",
                 "how": "In the Claude app, open the Atlas Project, replace its instructions, and save.", "copy_text": true } ],
  "priorities": [ { "text": "Send pricing feedback to Jordan", "why": "Due today; Thursday's decision depends on it.",
                    "ref": { "id": "commitments/send-pricing-feedback", "title": "Send pricing feedback to Jordan" },
                    "slot": { "kind": "window", "start": "11:30", "at": "11:30", "minutes": 30, "sized": true } } ],
  "day": { "start": "08:00", "end": "18:00", "work_day": true, "open_minutes": 210, "due_today": 3, "due_today_placed": 3,
           "windows": [ { "start": "11:30", "end": "12:30", "minutes": 60, "left": 0,
                          "items": [ { "id": "commitments/send-pricing-feedback", "title": "Send pricing feedback to Jordan", "rank": 1, "at": "11:30", "minutes": 30, "sized": true } ] } ] },
  "today": [ { "id": "events/2026-10-13-brightline-renewal-call", "title": "Brightline renewal call", "kind": "meeting",
               "start": "2026-10-13T10:00:00-07:00", "end": "2026-10-13T10:45:00-07:00", "all_day": false,
               "location": "Zoom", "attendees": [ { "id": "people/sam-okafor", "title": "Sam Okafor" } ], "project": null,
               "prep": { "status": "ready", "path": "user/work/prep/2026-10-13-brightline-renewal-call.md",
                         "summary": "Lead with the import fix date.", "todo": null } } ],
  "due": [ { "id": "commitments/send-pricing-feedback", "title": "Send pricing feedback to Jordan", "direction": "i_owe",
             "status": "open", "due": "2026-10-13", "priority": "high",
             "counterparty": { "id": "people/jordan-lee", "title": "Jordan Lee" }, "next_step": "…" } ],
  "waiting_on": [ { "id": "commitments/dana-msa-review", "title": "Dana reviews the enterprise MSA", "direction": "waiting_on",
                    "status": "slipped", "due": "2026-10-07", "since": "2026-09-30",
                    "counterparty": { "id": "people/dana-ruiz", "title": "Dana Ruiz" }, "next_step": "…" } ],
  "insights": [ { "id": "I-2026-10-12-03", "text": "…", "why": "…", "suggested_action": "…",
                  "draft": { "to": "Sam Okafor", "where": "Outlook drafts" },
                  "refs": [ { "id": "risks/onboarding-import-failures", "title": "Onboarding import failures" } ] } ],
  "drafts": [ { "title": "Contract review: quick check-in", "to": "Dana Ruiz", "where": "Outlook drafts", "why": "…",
                "ref": { "id": "commitments/dana-msa-review", "title": "…" },
                "approval": { "id": "A-2026-10-12-01", "action": "Send follow-up to Dana Ruiz" } } ],
  "approvals": [ { "id": "A-2026-10-12-01", "action": "Send follow-up to Dana Ruiz", "why": "…", "requested_on": "2026-10-12" } ],
  "questions": [ { "id": "Q-2026-10-12-02", "kind": "profile", "text": "…" } ],
  "week": {
    "range": { "start": "2026-10-13", "end": "2026-10-19" },
    "work_hours_per_day": 10,
    "free_hours": 22,
    "days": [ { "date": "2026-10-15", "work_day": true, "meetings": 3, "meeting_hours": 4, "free_hours": 2,
                "due": [ { "id": "events/2026-10-15-enterprise-pricing-signoff", "title": "Enterprise pricing sign-off",
                           "kind": "deadline", "direction": "i_owe", "status": "open", "counterparty": null },
                         { "id": "commitments/review-q4-roadmap-draft", "title": "Review the Q4 roadmap draft", "kind": null,
                           "direction": "i_owe", "status": "open",
                           "counterparty": { "id": "people/priya-nair", "title": "Priya Nair" } } ] } ]
  },
  "milestones": [ { "id": "events/2026-11-09-globex-pilot-starts", "title": "Globex pilot starts", "kind": "milestone",
                    "date": "2026-11-09", "project": { "id": "projects/enterprise-launch", "title": "Enterprise launch" },
                    "note": "Needs Dana's MSA review first." } ]
}
```

| Field | Notes |
|---|---|
| `brief.kind` | `daily` or `catch-up`. For `catch-up`, `brief.away` = `{ "start", "end" }` and `while_away` holds the "While you were away" summary lines (`[{ "text" }]`): the catch-up brief file's "What happened" bullets, most important first. Daily briefs omit it. |
| `brief.headline` | One sentence summarizing the day, in the user's communication style. |
| `today[].kind` | `meeting`, `one_on_one`, `occurrence`, `deadline` or `milestone`. Deadlines and milestones are usually all-day and carry no prep. |
| `today[].project` | The event's first linked project as a ref, or `null`. |
| `prep.status` | `ready` (prep note exists), `planned` (meeting-prep will create one before the meeting), `none` (meaningful meeting without prep), `not_needed`. `prep.todo` is one line on what to prepare, for `planned` or `none`; shown when there is no `summary`. |
| `due[].status`, `waiting_on[].status` | `open` or `slipped`. |
| `day` | Optional (`null` or missing hides the windows): the placement from `system/tools/placement.py` (`atlas-brief` §E) with each window's items carrying their title and, for a priority, its `rank`. `start`/`end` are the work day in the user's time zone, `HH:MM`. A window's items are commitments due that day as well as priorities. |
| `priorities[].slot` | Optional: the priority's slot from the same run: `{ kind: "window", start, at, minutes, sized }`, `{ kind: "wont_fit", date_at, minutes, sized }` (`date_at` `null` when the day has no window), or `{ kind: "none" }`. `sized: false` means the item had no `effort` and counts as 30 minutes. |
| `counts` | Optional `{ overdue, due_today }`: totals over every open commitment in both directions, before caps, for the stat tiles. Without it the page counts only the items it shows. |
| `drafts[].where` | Plain words for where the draft is ("Outlook drafts"). Never the draft body. |
| `drafts[].approval` | `{ id, action }` of the `pending` approval that sends this draft, else `null`. On a live page, the draft's Approve approves that entry; without one it copies a request for chat. |
| `actions[]` | Things only the user can do. `how` is optional; `copy_text` is `true` when the entry has text to copy (shown on the Guide page, never on this one). |
| `insights[].draft` | `{ to, where }` when the insight's suggested action already has a draft (its `Draft:` line in `insights.md`), else `null`. Never the draft body. |
| `week` | The seven days from `meta.as_of` (`range.start` = `as_of`), always 7 entries in `days`. `null` when there is no calendar data; the page then leaves out This week. |
| `week.work_hours_per_day` | Length of the work day in hours, from `rhythms.yaml: work_hours`; the scale for each day's meeting bar. |
| `week.free_hours` | Sum of the days' `free_hours`. |
| `week.days[].meetings`, `meeting_hours` | Count and hours of the day's meetings (all-day items excluded). |
| `week.days[].free_hours` | Time that can hold focused work: gaps of at least 60 minutes inside work hours, after meetings (hidden ones included) and holds. `0` on non-work days (`work_day: false`). |
| `week.days[].due[]` | What falls due that day: commitments in either direction (`kind: null`), and deadline and milestone events (`kind: "deadline" | "milestone"`, `id` is the event). A milestone carries no `direction` or `counterparty`; a deadline has `direction: "i_owe"`. |
| `milestones[]` | Deadline and milestone events from tomorrow through `as_of` + 60 days. `kind`: `milestone` or `deadline`; `date` is the event's day; `project` a ref or `null`; `note` one line on why it matters or what it depends on, or `null`. |

## Sources (file → field)
| Field | Source |
|---|---|
| `brief.*`, `priorities`, `while_away` (catch-up briefs only) | The brief file `user/work/briefs/<as_of>.md` (or `-catch-up.md`) written by `atlas-brief` in the same run; `priorities[].ref` and `[[…]]` mentions are the record IDs cited there |
| `today[]` | Event records (`user/knowledge/events/`) with `start` on `as_of`, `status: scheduled`, and shown by the meeting filter (`rhythms.yaml: meetings`, rule in `system/schemas/settings.md`; deadline and milestone events always show): `id, title, kind, start, end, all_day, location, attendees` (→ person refs), `project` (first `links.projects` entry); `prep.path` = event `prep`; `prep.summary` = first line of the prep note's suggested agenda; `prep.todo` as in `atlas-brief` §D step 4 |
| `due[]` | Commitments, `direction: i_owe`, `status: open|slipped`, `due` ≤ `as_of` + `rhythms.yaml: triggers.deadline_approaching.days` (default 3): `id, title, direction, status, due, priority, counterparty, next_step` |
| `waiting_on[]` | The brief's Waiting on items (`atlas-brief` §A step 4.3): commitments, `direction: waiting_on`, `status: open|slipped`, that are overdue or due within 7 days, plus any waiting 7+ days with no `due`; `since` = `created`. Here `counterparty` is the person who owes it (the record's `owner`), so the page can say "From Dana" |
| `counts` | Open commitments in both directions (`commitments/`): `overdue` = slipped or past `due`; `due_today` = `due` on the target date, not slipped |
| `insights[]` | `user/inbox/insights.md`, status `new`, highest `score` first, max `rhythms.yaml: insights.brief_max` (default 3): heading ID, Insight, Why it matters, Suggested action, Links |
| `drafts[]` | Drafts created since the previous brief, from run reports and the activity log (`email-drafts`, `status-updates`, triage follow-ups), the same list the brief file shows first (the brief's Still unsent lines stay in the brief file): titles, recipients, reasons, where each draft is; `approval` from `user/inbox/approvals.md`, the `pending` entry whose action sends it |
| `approvals[]` | `user/inbox/approvals.md`, status `pending` |
| `actions[]` | `user/inbox/questions.md`, kind `action`, status `open`, oldest first: heading ID, Question, How, whether Copy text exists |
| `questions[]` | `user/inbox/questions.md`, status `open`, kind not `action`, in the brief's order (`atlas-brief` §A step 4.9): Looks done entries (those with an `Evidence:` line) first, then those raised since the previous brief, then the oldest |
| `week.days[].meetings`, `meeting_hours` | Event records with `start` that day, `status: scheduled`, `kind` not `deadline` or `milestone`, shown by the meeting filter |
| `week.days[].free_hours`, `week.free_hours` | `atlas-brief` §D step 2, from event records (hidden meetings still count as busy) and `rhythms.yaml: work_hours` |
| `week.days[].work_day`, `week.work_hours_per_day` | `rhythms.yaml: work_hours` (`days`, `start`, `end`) |
| `week.days[].due[]` | Commitments (`open|slipped`) with `due` that day, both directions; deadline and milestone events (`kind: deadline | milestone`) that day |
| `milestones[]` | Event records, `kind: milestone | deadline`, `status: scheduled`, `start` from `as_of` + 1 through `as_of` + 60: `id, title, kind`, `date` = day of `start`, `project` = first `links.projects` entry, `note` from the event's `insight` |
| `meta.notices` | `user/.state/health.yaml` open high-severity issues affecting ingestion; staleness found by the job's readiness check (`user/.state/jobs.yaml`) |

## Rendering notes
- Order on the page: while you were away (catch-up only); then two columns, stacked on a phone. **Left:** **your day** (all-day items and deadlines as pills, meetings already over in one "Earlier" strip, then a proportional timeline at 1.6px a minute with hourly ticks, the now line in ember and each meeting as a block; overlapping meetings share the width), the **brief** for the chosen block (when, where and with whom, project, prep, what you owe the people in it and what they owe you, and a prompt to copy), and **needs you** (only-you actions, approvals, drafts and questions as one list card; "Nothing needs you right now" when empty). **Right:** **top priorities** as the night card (numbered: they are ranked; only #1 takes ember), **overdue** (the count with its split, "1 you owe · 2 they owe you", an age bar of 1 day, 2–6 days and 7+ days, then people oldest first, five before "All N people"), **due soon** (what you owe that isn't late), **waiting on** grouped by person with one nudge each, and a line linking the Guide. Below both: worth knowing (if any), this week (when `week` is set), coming up. The brief file's "What changed" and "Since last night" sections are not shown on the page.
- **Open windows** (when `day.windows` is set) sit in the timeline as dashed ember-tint blocks, "Open · <first item>", with one ember dot counting the priorities placed there and the window's length; choosing one opens its brief: what's placed there, each with its priority number, start time and size, and the time left over. The Your day kicker says how much is open and whether everything due today was placed. Top priorities each carry their slot as a pill ("11:30 window"; "Won't fit · date at 4:15" in amber); choosing a priority opens the brief of its window.
- **The now line and the Earlier strip use the viewer's clock**, and only on the brief's own day (`brief.date`); on any other day there is no now line and every meeting is ahead. Times are placed in `meta.timezone`. The block chosen first is the meeting under way, else the next one; choosing another opens its brief, and a live refresh keeps the choice.
- No stat tiles: the overdue card carries the count and split, and every section is on the first screens.
- Actions copy a request for chat (`system/dashboards/README.md` §Actions copy a request for chat): "Approve" and "Decline" on approvals, "Answer in chat" on questions, "Approve" and "Change it" on drafts (Atlas sends a draft only from a chat, once the user confirms; the page never sends), "Mark done" and "Nudge <name>" on due items, "Do this" and "Not useful" on insights. On a live page, those that change something queue a request instead (README §Live pages): Approve, Decline, I've done this, a draft's Approve (when the draft has an approval), Mark done, Nudge and Not useful. Nudge on a person in Overdue or Waiting on targets their oldest item and asks for one follow-up covering all of them.
- **This week:** one tile per day: day and date (today outlined), a meeting bar against `work_hours_per_day` (amber over 60%), meeting and free hours, and what's due as short pins: due from the user (deadlines and `i_owe`) tinted red, milestones marked with a diamond, waiting-on items plain. Days off (`work_day: false`) carry no tile of their own: each run of them, such as a weekend, is one thin, empty dashed tile, so the work days get the width; what falls due on them is still read out to screen readers and shows in Coming up and Due soon. On phones the strip scrolls sideways inside its own box. Under it, a legend and one line with `week.free_hours`.
- **Coming up:** date with "in N days", title, deadline or project, and the note.
- Sorting: `priorities` in rank order (3 items, up to 5, fewer when fewer qualify; `atlas-triage/reference/signals.md` §Top priorities); `today` by `start`, all-day items last; `due` as in the brief (`atlas-brief` §A step 4.2): items due tomorrow first, then slipped, then by `due`, then priority; `waiting_on` slipped first, then by `due` (nulls last); `week.days[].due` deadlines and milestones first, then `i_owe`, then `waiting_on`; `milestones` by `date`.
- Caps (then `meta.truncated`): `today` 15, `due` 5, `waiting_on` 5, `drafts` 8, `approvals` 5, `questions` 3 plus up to 5 Looks done, `while_away` 8 (catch-up), `milestones` 8, 5 items per day in `week.days[].due` (key `week.<date>`; the tile shows "+N more"). `actions` is never capped. `due`, `waiting_on` and `questions` use the brief file's caps (`atlas-brief` §A step 5), so the page and the file list the same items; `meta.truncated` carries the "+N more" count.
- Text limits: `headline` 200 characters, `why`/`next_step`/`summary`/`todo` 240, `milestones[].note` 200.

## Size budget and truncation
The page is about 225 KB before data (the template, the base and the embedded fonts) and typically 10 to 20 KB of data, so 280 KB leaves room for a long catch-up. If a render would exceed it, cut in this order until it fits, recording each in `meta.truncated`: `while_away` (to 4), `drafts` (to 3), `milestones` (to 4), `week.days[].due` (to 3 per day), then shorten `why`, `next_step` and `note` text to 120 characters. Never drop `actions`, `priorities`, `today`, `due` or `waiting_on` below their caps.
