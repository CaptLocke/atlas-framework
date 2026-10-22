---
name: atlas-insights
description: "Spot risks, gaps, quiet people, patterns and contradictions, score them against goals, and manage insights. Use for the intelligence job and \"what am I missing?\", \"any risks I should know about?\", \"connect the dots on…\", \"dismiss that insight\"."
---
# Insights

## Purpose
Surface the few things the user would want to know but hasn't noticed, each with a one-line reason and its sources, and keep volume matched to what the user actually finds useful.

## When to use
- **Job:** `intelligence` (after ingest and triage).
- **Chat, exploration:** "What am I missing on Orion?", "Any patterns in customer complaints this month?", "Connect the dots on churn", "What should I worry about this week?". For plain factual exploration ("what do we know about churn") `atlas-recall` answers first and hands off here for patterns.
- **Chat, lifecycle:** "That's not useful", "dismiss", "good catch, make that a risk", "tell me more about the import bug insight".
- **Other skills:** `atlas-brief` (marks shown insights `seen`), `atlas-recall` (marks presented insights `seen`), `atlas-review` (engagement for the automation review).

## Inputs
- Changes since `jobs.yaml: intelligence.last_success` (records updated, sources captured, activity log).
- `_index/hot.md`; active goals; open risks, questions, decisions (`proposed`), projects; people records (`last_contact`, `cadence`, relationship).
- `user/inbox/insights.md` and, for windows longer than 14 days, `user/inbox/archive/*-insights.md` (existing insights and their status histories, for novelty and engagement).
- `rhythms.yaml: insights` (`brief_max`, `engagement: adaptive | fixed`, `suppressed_kinds`); `health.yaml` engagement summary if present.
- Detection and scoring guide: `reference/insight-kinds.md`.

## Procedure

### A. Generate (job or "what am I missing")
1. **Paused/away.** If `intelligence` is paused, stop. During away, generate normally (they wait for the catch-up brief) but don't nudge.
2. **Early exit.** Nothing changed since the last run and no date-driven checks are due (quiet people, approaching targets) → exit (`early_exit`).
3. **Look** across the changed records and their neighborhoods (imported history is context, never a change: `.claude/skills/atlas-capture/reference/import.md` §10) (`system/rules/retrieval.md` L3) for each kind in `reference/insight-kinds.md`, skipping every kind listed in `rhythms.yaml: insights.suppressed_kinds`: risks, gaps, quiet people, patterns, connections, contradictions, opportunities, goal drift.
   **Topics** (every run, `mode: light` included): for each theme the change set touches that no topic covers, search for it and its variants as `atlas-recall` §D does. If it meets `system/schemas/topic.md` §Capture guidance, create the topic through `atlas-capture` (`provenance: inferred`, a `scope` line) and link its records both ways. No insight for this: topics are Atlas's own structure.
4. **Ground** every candidate in at least one record or source; write the reasoning in one line. Drop candidates you can't cite.
5. **Score** each: `score = goal_relevance × urgency × novelty` (each 0–1; rubric in the reference). Novelty is low when `insights.md` already holds the same insight (same links and gist) in the last 30 days in any status; a dismissed insight returns only if something material changed (say what).
6. **Apply insight rules** from `user/profile/preferences.md ## Insight rules` (drop or raise matching candidates), then **adapt volume** (if `engagement: adaptive`): compute engagement per kind from status histories over the last 60 days (acted, dismissed, expired-unseen). Lower the kind's effective score by its dismiss/expire rate and raise it by its act rate; never suppress `risk` kinds with high impact entirely. With `fixed`, skip this step.
7. **Keep** candidates with adjusted score ≥ 0.4, at most ~10 per run (most runs produce 0–5). The brief later shows the top `brief_max`.
8. **Write** each to `user/inbox/insights.md` (format `system/schemas/formats.md` §3; newest first): ID `I-YYYY-MM-DD-NN`, `new`, score; Insight, Why it matters, Sources, Links, Suggested action, Status history; plus a `- **Kind:** <kind>` line for engagement tracking. Links cover every record the insight names or puts at risk: the risk or issue, each affected project, and the goal it threatens. The Insight names the dates at stake. When facts from different sources combine into a risk none of them shows alone (a customer requirement meeting a blocked dependency), make that its own insight naming both facts; don't fold it into a broader one.
9. **Create records when warranted** (through `atlas-capture`, `provenance: inferred`, sources = the evidence):
   - A pattern or concern likely to cause harm → `risk` (`status: potential`, or `active` if already happening), with likelihood/impact.
   - An important gap that needs an answer → `question`.
   - An opportunity worth keeping → `idea` (`status: seed`).
   - Recurring work (the same kind of work at least 3 times in 12 months) → a draft playbook plus an `opportunity` insight proposing it (`.claude/skills/atlas-triage/reference/playbooks.md` §1).
   - A recurring deliverable (the same kind of output at least 3 times in 6 months) → a draft template plus an `opportunity` insight proposing it (`.claude/skills/atlas-write/SKILL.md` §7).
   Link the insight entry to the new record.
10. **Project insight.** If an insight is the most important thing about an active project, update that project's `insight` (and `next_step` if the suggested action is better than triage's), with an Updates line.
11. **Expire** entries `new` for more than 30 days (never seen) → `expired`. Days while away is active don't count: expiry pauses during away and resumes afterwards (`system/jobs/README.md` §Common job protocol), so nothing expires while the user is out.
12. **Commit and log**; run-report row: candidates, kept, records created, by kind.

### B. Exploration (chat)
1. Retrieve broadly around the subject (recall procedure D), then look for the kinds above within that scope, plus timelines, recurring causes, and who keeps appearing.
2. Answer as analysis: 2–5 findings, each with reasoning and citations, then what is uncertain and what data would settle it.
3. Offer to keep anything useful: as an insight entry (status `acted` if the user takes it up), or a risk/question/idea record. A theme that meets the topic bar gets its topic without asking (`atlas-recall` §D step 4).

### C. Lifecycle
| Event | Status change |
|---|---|
| Shown in a published brief, in chat, or opened from a dashboard discussion | `new` → `seen` |
| User acts on it, asks to turn it into a record, or the suggested action happens (evidence) | → `acted` |
| User says it's wrong, not useful, or dismisses it | → `dismissed` (ask briefly why only if it helps tune: "wrong" vs "not now"); "wrong" or "not useful" also logs an `insight_noise` feedback line, and "that was useful" an `insight_useful` one (`.claude/skills/atlas-triage/reference/learning.md` §1) |
| `new` for 30 days without being seen | → `expired` |
Append to Status history with the date (and "(brief)" / "(chat)" where useful). Never delete entries. "Stop suggesting X" from the user: map X to an insight kind (e.g. "stop telling me who's gone quiet" → `quiet_person`), confirm in one line, and ask `atlas-settings` to add it to `rhythms.yaml: insights.suppressed_kinds` (`behavior_settings`). Mark matching `new` entries `dismissed`. "Start suggesting X again" removes it the same way.

## Outputs
- `user/inbox/insights.md` entries and status updates.
- New `risk`, `question`, `idea` records (via `atlas-capture`); project `insight`/`next_step` updates.
- Activity-log line; run-report row. In chat: findings with reasoning and citations.

## Guardrails
- Autonomy classes: `read`, `records_write` (insights, inferred records, project insight fields); `behavior_settings` for volume preferences (propose). See `system/rules/governance.md`.
- Every insight has a reason and at least one source; inferences are labeled `inferred` and phrased as such ("likely", "may").
- No insights about the user's personality, health, or protected attributes; nothing from `notes_private` is ever surfaced; pointer-only content can't support an insight beyond "a confidential item exists".
- Quiet-people insights concern working relationships only, phrased neutrally ("no contact in 5 weeks; your cadence is biweekly").
- Insights never trigger actions; suggested actions are offers.
- Few where attention is scarce: the brief shows at most `brief_max`. Kinds in `suppressed_kinds` are never generated, in jobs or in unprompted chat suggestions (an explicit user question about that kind is still answered).

## Done when
- Each new entry has kind, score, reason, sources, links, a suggested action, and status `new`.
- No duplicate of an insight from the last 30 days was written unless materially changed (and says what changed).
- Records created from insights link back to their evidence.
- Statuses reflect what the user saw, acted on, or dismissed; stale `new` entries are expired.
