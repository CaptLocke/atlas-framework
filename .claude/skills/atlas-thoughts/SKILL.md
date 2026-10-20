---
name: atlas-thoughts
description: "Take a Morning or Evening Thoughts brain dump: save it to the journal and sort out what's inside. Use for \"morning thoughts\", \"evening thoughts\", \"brain dump\", \"here's what's on my mind\", or a long messy message at the start or end of the day."
---
# Morning and Evening Thoughts

## Purpose
Let the user empty their head in under two minutes, with zero formatting, and trust that everything worth keeping lands in the right place, linked back to what they said.

## When to use
- **Chat:** "Morning thoughts: …", "Evening thoughts", "Brain dump", "Let me dump some stuff", "Here's what's on my mind", or a long, stream-of-consciousness message near the start or end of the user's day.
- If the user says "brain dump" with nothing after it, reply with one short line inviting them to go ahead and wait.
- **Job:** `ingest` processes any journal section left unprocessed (e.g. a chat ended before extraction finished) through `atlas-capture` §6.

## Inputs
- The user's message(s), exactly as sent (including dictation artifacts).
- Today's date and time in `atlas.yaml: timezone`; `rhythms.yaml: work_hours`, `moments`, `paused`.
- Existing journal file `user/journal/YYYY/MM/YYYY-MM-DD.md` (format `system/schemas/formats.md` §6).
- Knowledge indexes for resolving names and projects.

## Procedure
1. **Morning or evening.** Use the user's word if given. Otherwise: before the midpoint of their work hours → Morning; after it → Evening. Don't ask.
2. **Paused moment.** If the moment is paused in `rhythms.yaml`, still accept and file the dump (the user chose to give it); pausing only stops Atlas prompting for it.
3. **Save verbatim first.** Create the journal file if needed (frontmatter `type: journal`, `date`, `processed: []`, `source: "[[sources/YYYY-MM-DD-journal]]"`). Append the text under `## Morning Thoughts` or `## Evening Thoughts` exactly as received. If the section already has content (a second dump), add a line `— HH:MM —` and append below it. Never correct, reorder, or tidy the text. Commit immediately (`atlas(chat): journal <section> <date>`), so nothing is lost if the chat ends.
4. **Journal source.** Create or update `sources/YYYY-MM-DD-journal` (`kind: journal`, `captured_on`, `retention: full` unless data rules say otherwise for content in it, `provenance: stated` on derived records).
5. **Interpret the mess** (keep the journal untouched; interpretation lives only in the records):
   - Dictation artifacts: homophones and misheard names ("Dana Reese" → Dana Ruiz if context fits), missing punctuation, run-ons, filler ("um", "so yeah").
   - Self-corrections: "call Priya Tuesday, no wait, Thursday" → Thursday.
   - Fragments that continue an earlier thought: join them.
   - Relative dates ("tomorrow", "end of week") from the dump's date and time (an evening "tomorrow" is the next day).
   - Mood and venting are not records; keep only what is actionable or worth remembering.
   Examples: `reference/examples.md`.
6. **Extract** through `atlas-capture` (write path, explicit vs vague rules): commitments (`i_owe` mostly; `waiting_on` when the user reports someone's promise), ideas (`seed`), questions, decisions the user reports, risks, facts about people or projects, links to existing projects/topics. Names you can't resolve confidently: link nothing, ask (step 8).
7. **Mark processed.** Add `morning` or `evening` to the journal's `processed` list; advance `journal.last_processed`; commit with all created/updated record IDs.
8. **Confirm briefly** (two to four lines, no lists unless many items): what you filed, with links, plus at most one clarifying question. Example: "Filed: call Priya Thursday ([[commitments/maya-call-priya]]), the partner-tier idea ([[ideas/partner-tier]]), and linked your roadmap note to Roadmap Q1 ([[projects/roadmap-q1]]). Who's 'Sam from the call', Sam Okafor?"
   Vague intentions you didn't make commitments go into `questions.md` (kind `commitment`) and appear in the brief; mention them only if few.
9. **Evening fold-in.** For an Evening dump, make sure tomorrow's brief reflects it: if tomorrow's brief file already exists (e.g. Lean's nightly run already happened), ask `atlas-brief` to update its Due soon / Top priorities / What changed ("From your Evening Thoughts") and republish; otherwise the next `daily-brief` run picks the items up from the records and the journal.
10. **Personal content.** Personal remarks unrelated to work stay in the journal only; do not create records for them. If the dump contains sensitive categories (health, finances, legal), apply data rules to anything extracted; the journal text itself is the user's own verbatim content.

## Outputs
- `user/journal/YYYY/MM/YYYY-MM-DD.md` (verbatim section; `processed` updated).
- `user/knowledge/sources/YYYY-MM-DD-journal.md` and extracted records with `provenance: stated`.
- `user/inbox/questions.md` entries for vague items or unclear names.
- `user/.state/cursors.yaml: journal.last_processed`.
- Updated tomorrow's brief (evening, when it already exists). Commits and an activity-log line.
- A two-to-four-line confirmation in chat.

## Guardrails
- Autonomy classes: `records_write` (journal append, records); `user_content_edit` (propose): never edit journal text after saving it unless the user asks and confirms; `profile_update` (propose) for any preference the dump reveals about the user. See `system/rules/governance.md`.
- Verbatim means verbatim: no spelling fixes, no redaction of the journal text except secrets (N10), which are replaced with "[secret removed]" and mentioned to the user.
- Don't lecture, summarize back at length, or ask more than one question.
- Away mode: still accept dumps; extracted items' nudges are held for the catch-up brief.

## Done when
- The dump is saved verbatim in the right section and committed before extraction starts.
- Every actionable item is a linked record or an open question; nothing invented.
- The section is listed in `processed`, and the user got a short confirmation.
- For evening dumps, tomorrow's brief includes the items (now or at the next brief run).
