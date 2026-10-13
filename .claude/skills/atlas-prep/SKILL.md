---
name: atlas-prep
description: "Prepare the user for a meeting, a person, a topic, or a deal\u2014who's involved, history, open items in both directions, related decisions, risks and questions, a suggested agenda, and the questions to ask\u2014and save it as a prep note linked from the event. Use when the meeting-prep job runs, when the key-meeting trigger fires, and for \"prep me for\u2026\", \"brief me on Dana before my call\", \"get me ready for the board meeting\", \"what should I raise in my 1:1 with Jordan\", \"what do I need to know about the Acme deal\"."
---
# Prep

## Purpose
Walk into every important conversation already knowing the history, the open items both ways, and what to ask, in a note readable in two minutes.

## When to use
- **Job:** `meeting-prep` (next ~24h, or `target: tomorrow`).
- **Trigger:** `key_meeting_upcoming` (`system/triggers.md`), from the job or in chat.
- **Chat:** "Prep me for my 2pm", "Get me ready for the board meeting", "What should I bring to my 1:1 with Jordan?", "Brief me on Dana Ruiz", "What do I need to know about the Acme deal before the call?".
- **User triggers** that ask for a deal or topic brief (e.g. a `deals` extension).

## Inputs
- The event (record and/or `calendar.read_item`): title, time, attendees, description, attachments, series.
- Attendee people records and their organizations; `people-map.md`.
- Retrieval L1–L3 (`system/rules/retrieval.md`) around attendees, linked projects, and the meeting's subject; L4 for the last thread or transcript with them when wording matters.
- Previous instances in the series (events with the same `series`) and their prep notes and outcomes.
- Active goals; `user/profile/communication-style.md` (format preferences).
- Templates: `reference/templates.md`.

## Procedure

### A. Which meetings get prep (job)
1. **Away/paused.** If away is active or `meeting-prep` is paused, stop (job records the skip). In chat, prep on request always works.
2. List events for the target window. Prep a meeting when it meets `key_meeting_upcoming` (a `one_on_one`, external attendees, or ≥1 linked open commitment or decision) or is one the user asked to always prep (`preferences.md`, e.g. "always prep board and steering meetings"). Skip holds, focus blocks, personal items, all-hands, declined events, events hidden by the meeting filter (`rhythms.yaml: meetings`, unless the user asks for that meeting by name), and meetings that already have a current prep note (re-prep only if attendees, time, or linked items changed since).
3. For each `key_meeting_upcoming` match, check `user/.state/triggers.yaml` (key = event start); record the firing after the note exists.

### B. Build a meeting prep note
1. **Purpose in one line:** why this meeting exists and what a good outcome is for the user (from the description, series history, linked projects, goals).
2. **Attendees:** for each person who matters (cap ~6; group the rest): role and organization, relationship to the user, last interaction (date + what), anything notable (preferences, recent changes). Never include `notes_private`.
3. **Open items both directions:** `i_owe` to attendees and `waiting_on` from attendees, with due dates and status; flag slipped ones and suggest how to address them in the meeting.
4. **Context:** related decisions (recent and pending), active risks and issues, open questions, project health, key numbers (from records or `data` sources), last meeting's outcomes in the series.
5. **Suggested agenda:** 3–5 items in a sensible order, time-boxed if the meeting is ≥45 minutes; build on the user's own goals and the items above.
6. **Questions to ask:** 3–5 specific questions that close gaps or move commitments ("Can you confirm the redlines by Friday?"); likely questions the user will be asked, with short answers drawn from records.
7. **Watch-outs:** sensitivities, conflicting facts, things not to commit to without checking.
8. **Keep it to one screen** (~250–400 words; board or customer reviews may be longer, with a summary at the top). Cite records inline.
9. **Write** `user/work/prep/YYYY-MM-DD-<event-slug>.md` (frontmatter `type: prep`, `date`, `event`, `sources`).
10. **Link:** set the event record's `prep` field to the note path (create the event record first if missing, via `atlas-capture`); add an Updates line. The brief's Today section links it.
11. Commit and log; run-report row (notes created, events skipped and why).

### C. 1:1s
Use the 1:1 template: the other person's open items and yours, wins and progress to mention, decisions you need from them (or they need from you), feedback or career topics if the profile says the user uses 1:1s for that, items carried over from the last 1:1's outcomes, and the person's cadence (is this overdue?). For a 1:1 with the user's manager, include a short status they can give in 60 seconds (from `atlas-status-update` material if recent).

### D. Person, topic, or deal prep (chat or user triggers)
- **Person:** who they are, relationship history (timeline of key interactions), open items both ways, what they care about (from records), how they prefer to communicate, upcoming touchpoints, suggested talking points.
- **Topic / deal:** current state, history and decisions, people and organizations involved, numbers, risks and open questions, what's next, suggested position or questions.
- Save to `user/work/prep/YYYY-MM-DD-<person-or-topic-slug>.md` (same frontmatter, `subject:` instead of `event:`) when the user wants to keep it or a trigger requested it; otherwise answer in chat.

### E. In chat
Present the note (or its top section for long ones) and offer follow-ups: "Want a draft agenda to send to Dana?" (→ `atlas-write`, draft only; sending needs approval), "Want focus time before it?" (→ `own_calendar_manage`, propose).

## Outputs
- `user/work/prep/YYYY-MM-DD-<slug>.md`.
- Event record `prep` field and Updates line; new event/person records only through `atlas-capture`.
- `user/.state/triggers.yaml` entries for `key_meeting_upcoming`.
- Activity-log line; run-report row; the note in chat when asked.

## Guardrails
- Autonomy classes: `read`, `external_read`, `records_write` (prep notes, event `prep` field). Sending an agenda or editing a calendar invite is `send_communication` 🔒 / `own_calendar_manage` (propose); never done here without the user (`system/rules/governance.md`).
- Data rules: pointer-only items appear as "a confidential document exists" with no content; `notes_private` never appears in prep notes.
- Never invent attendee facts, figures, or prior commitments; label inferences.
- Away: the job doesn't prep; triggers are held for the catch-up brief. Respect a paused `meeting-prep`.

## Done when
- Every qualifying meeting in the window has a current prep note, linked from its event record.
- Each note has purpose, attendees with last interaction, open items both ways, a suggested agenda, and questions, all cited.
- Trigger firings are recorded once; skipped meetings are explained in the run report.
