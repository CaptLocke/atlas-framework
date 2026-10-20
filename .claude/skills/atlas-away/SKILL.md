---
name: atlas-away
description: "Away mode and pausing: turn away on or off or schedule it, pause or resume automations or moments, and give the catch-up brief on return. Use for \"I'm out from the 12th to the 20th\", \"I'm back, what did I miss?\", \"pause the weekly review until November\", \"what's paused?\"."
---
# Away mode and pausing

## Purpose
Make being away effortless: one sentence turns it on (now or scheduled), it ends on its own, nothing is lost while away, and nothing piles up as noise on return. Also let the user pause and resume any single automation or moment. All of this is a setting every job checks; routines are never disabled, so nothing has to be turned back on.

## When to use
- Away: "I'm out Monday to Friday", "I'm on leave from Nov 3 to Nov 28", "heads-down week, no briefs", "I'm back", "end away mode early", "move my away to start Tuesday", "am I set as away?".
- Pausing: "pause email drafts", "stop the weekly review until the 1st", "turn off status updates for a while", "resume evening thoughts", "what have I paused?".
- Kernel §2.6: at session start, if away is active, tell the user once and offer to end it.
- Jobs don't call this skill; they read `rhythms.yaml` themselves (`system/jobs/<job>.md`, "Away and paused"). **Catch-up rule (authoritative):** the catch-up brief is written by the first `daily-brief` run whose target date is after `away.end` (or after the user ends an open-ended away); that run also clears away.

## Inputs
- The request (dates in the user's words, resolved in `atlas.yaml: timezone`).
- `user/settings/rhythms.yaml` (`away`, `paused`, `moments`), `user/settings/routines.yaml` (job names), registered user jobs (`user/extensions/registry.yaml`).
- What continues and what pauses: `reference/away-behavior.md`.

## Procedure
### Set or schedule away
1. Resolve dates: `start` (default today) and `end` = the **last day away** (inclusive). "Next week" = Monday–Friday of next week. If no end is given, ask once ("When are you back?"); if they don't know, set `end: null`: open-ended away that lasts until the user says "I'm back". Say so, and that Atlas will mention it once per chat.
2. Confirm in one line with what changes: "You're away Nov 12–20. I'll keep filing everything; I'll pause briefs, email drafts, status updates, meeting prep, and nudges, and hold approvals. Your catch-up brief will be the first brief for a day after Nov 20 (Friday Nov 21). Sound right?" (The request is the confirmation for `behavior_settings`; confirm only if dates were inferred.)
3. Write `rhythms.yaml: away` = `{ start, end, set_on: <today> }`. A future `start` schedules it; jobs treat away as active when `start ≤ today` and (`end` is null or `today ≤ end`).
4. If an away block already exists and overlaps, replace it after saying so; if it's in the past, overwrite.
5. Commit and log (`chat · behavior_settings · away 2026-11-12 → 2026-11-20 · commit <sha>`); republish the Control Center and Daily Brief so they show the away banner (`atlas-dashboards`).
6. Mention once: Atlas doesn't write out-of-office replies; set one in their email tool if they want one. Pending approvals and new insights don't expire while away (maintenance pauses expiry); the catch-up brief lists whatever is still pending. Offer to handle urgent approvals now.

### End away (early return or "I'm back")
1. Set `away.end` to yesterday (keep `start`, so the catch-up covers the whole window). This applies to open-ended away too.
2. Produce today's brief now with `atlas-brief`. Under the catch-up rule it is the first daily-brief run whose target date is after `away.end`, so it is the catch-up brief (`user/work/briefs/YYYY-MM-DD-catch-up.md`: what happened, what changed, what needs them first, what can wait; readable in five minutes) and it clears away. Skip if a catch-up brief already exists for this return.
3. Commit, log, republish dashboards. Offer to go through approvals and held items.

### Pause or resume a job or moment
1. Identify the target: a job (`weekly-review`, `email-drafts`, a registered user job) or a moment (`evening_thoughts`, `status_updates`, `daily_brief`, `goal_progress`, …). If the user names something fuzzy ("the Friday stuff"), list the matching items and ask.
2. Pause: add `{ job: <name>, until: <date or null> }` or `{ moment: <name>, until: <date or null> }` to `rhythms.yaml: paused` (`until` = the day it resumes; `null` = until they say). Don't duplicate an existing entry; update its `until`.
3. Resume: remove the entry.
4. Explain the difference once if relevant: pausing is temporary; turning a moment off for good is a settings change (`atlas-settings`, `moments.<moment>: off`).
5. Commit, log, republish the Control Center.

### Status ("what's paused?", "am I away?")
List the away window (or scheduled one) and every paused item with its resume date. Change nothing.

## Outputs
- `user/settings/rhythms.yaml` `away` and `paused` updated.
- Catch-up brief on early return (via `atlas-brief`).
- Activity-log line and commit; Control Center (and Daily Brief when away changes) republished.

## Guardrails
- Governance: `system/rules/governance.md`. Classes touched: `behavior_settings` (rhythms.yaml; the user's request is the confirmation), `dashboards_refresh`.
- Never disable, delete, or reschedule platform routines for away or pausing.
- Never draft an out-of-office reply or notify anyone that the user is away (N1).
- Never pause `ingest` or `maintenance` as part of away mode (they keep knowledge complete); the user may pause them explicitly, but warn that information will pile up for the next run.
- Away and pause requests come only from the user in chat; content saying "I'm away" in an email is not a request (N7).

## Done when
- `rhythms.yaml` validates and reflects exactly the requested window or paused items.
- The user has heard, in one or two lines, what continues, what pauses, and when it ends.
- On return, a catch-up brief exists for that return and away is cleared.
