---
name: nova-triage
description: "Review every open commitment against recent evidence and the user's goals\u2014catch missed ones, close finished ones, mark slipped ones, rank priorities, flag aging waiting-on items, and write a one-line insight and next step for each commitment and active project. Use when the triage job runs and in chat for \"what do I owe\", \"what am I waiting on\", \"what's slipping\", \"prioritize my week\", \"mark the Acme deck done\"."
---
# Triage

## Purpose
Keep the user's commitments honest and their priorities clear: nothing promised is lost, nothing finished stays open, and every open item says why it matters and what to do next.

## When to use
- **Job:** `triage` (`mode: full` default; `mode: light` on daytime runs).
- **Chat:** "What do I owe this week?", "What am I waiting on?", "What's slipping?", "Prioritize my week", "Start the renewal playbook for Brightline", "Save how we do renewals as a playbook" (`reference/playbooks.md`), "Rank my goals", "Make retention my top goal" (set `rank` per `system/schemas/goal.md` §Ranking, then a full priority pass), "I sent the deck to Jordan" (close with evidence), "Drop the vendor survey commitment".
- After `nova-thoughts` or a large manual capture, a light pass over the affected commitments.

## Inputs
- Commitments: `_index/commitments.md` filtered to `open` and `slipped`; open the records.
- Recent evidence since `jobs.yaml: triage.last_success` (chat: since the last triage or 7 days): Sources captured in that window, `mail.list_sent`, `tasks.list_recent` (completed tasks), the user's statements in chat and journal.
- Active goals (with `rank`) and projects; `people-map.md` (who is the manager, key stakeholders).
- Calendar for the next 14 days (events records) for due-date context.
- `rhythms.yaml: triggers` (each trigger's `enabled`, `deadline_approaching.days`), `away` (`end: null` = open-ended), `paused`; `user/.state/triggers.yaml`.
- Active playbook runs (projects linked to a playbook) and their step commitments: `reference/playbooks.md`.
- Signal guide: `reference/signals.md`. Learned rules: `user/profile/preferences.md` `## Triage rules` (how they're learned: `reference/learning.md`).

## Procedure
1. **Away/paused.** If the `triage` job is paused, stop. During away, run steps 2–8 (records stay accurate) but hold trigger actions in step 9 for the catch-up brief.
2. **Catch missed commitments.** Scan Sources captured in the window for explicit promises with no matching commitment (match by owner + counterparty + deliverable). Create them through `nova-capture` (explicit vs vague rules apply; vague → `questions.md`, kind `commitment`).
3. **Dedupe.** Commitments with the same owner, counterparty, and deliverable, and close or equal due dates, are duplicates: merge (`merge_supersede`) keeping the older record; add the newer source; set the other's `superseded_by`. Ambiguous → link with `related` and queue a question.
4. **Close with evidence.** For each open commitment, look for completion evidence (`reference/signals.md` § Completion): a sent message delivering it, a delivered file, a completed task, a source showing it done, the user's word. Found → `status: done`, `completed_on`, Updates line citing the evidence. Likely but uncertain → `questions.md` (kind `commitment`): "Did you send Acme the SOC report? I saw an email with an attachment on 10/12."
4a. **Apply triage rules** from `preferences.md ## Triage rules` to closing, dropping, and priority; name the rule where it changes an outcome.
5. **Drop or move.** If evidence shows it's no longer wanted (cancelled meeting, decision reversed) → `status: dropped` with reason; if a new date was agreed → update `due`, keep "was X, now Y" in Updates.
6. **Slipped.** Open items past `due` → `status: slipped` (this is the `commitment_overdue` condition; see step 9). A slipped item that gets done → `done`.
7. **Priority** (skip in `mode: light` except for new commitments). Set `priority` high/medium/low against goals first (weighted by each goal's `rank`), then urgency and people (`reference/signals.md` § Priority). Due-less items get a suggested date in `next_step`, not in `due`.
8. **Insight and next step.**
   - Every open or slipped commitment: `insight` (one line: why it matters or may slip, grounded in evidence) and `next_step` (one concrete action with a time). Refresh only when stale or circumstances changed.
   - **Aging waiting-on:** compute days waiting (since created, or since the last follow-up recorded in Updates). Aging = past due, or no movement for more than 5 business days, or due within 2 days with no sign of progress. Say so in `insight` and suggest the follow-up channel in `next_step` (person's `cadence`/habits if known).
   - **Playbook runs:** check steps out of order or skipped in practice, and finish runs whose steps are all closed (`reference/playbooks.md` §4–5).
   - Every `active` project: `insight` and `next_step` from its commitments, risks, decisions, questions, and target date; update `health` (`on_track | at_risk | off_track | unknown`) when evidence supports it, with an Updates line.
   - In `mode: light`: only for commitments created or changed in this run.
9. **Triggers** (`system/triggers.md`; check and record in `user/.state/triggers.yaml`, key = due date):
   - `deadline_approaching`: open `i_owe` commitments and deadline events due within `days` (default 3) → mark for the brief's "Due soon"; the day before, mark as top-of-brief and Work Board (via `priority: high`).
   - `commitment_overdue`: slipped items → flag for the brief. If `waiting_on`, triage does **not** draft in routines:
     1. Mark the commitment for follow-up (`next_step` says a follow-up is due).
     2. Add an `approvals.md` entry (`send_communication`, "send follow-up to <owner>", linking the commitment) **only if** no `pending` entry already links that commitment; `Prepared:` says "follow-up draft to be created by email-drafts".
     3. The draft itself is created only by the `nova-write` email-drafts procedure (`email-drafts` job, which runs after triage in every profile; on weekends or light runs, the next weekday run). In chat, triage calls that `nova-write` procedure directly.
     4. Shared marker: before any follow-up draft is created, the commitment's `## Updates` is checked for a line `follow-up draft created <date>`; if present since the commitment last changed, no new draft is made. `nova-write` writes that line when it drafts.
     Without a mail connector, `nova-write` puts the follow-up text in the approvals entry for the user to send.
   - During away: evaluate, set statuses, but do not create drafts or approvals and do not record the trigger as fired; the catch-up brief lists them and they fire on return.
10. **Write** all record changes with Updates lines; update `_index/commitments.md`, `_index/projects.md`, `hot.md`. Commit (`nova(routine:<name>): triage …` with `Nova-Records`) and log one activity line.
11. **Republish** with `nova-dashboards` every dashboard whose contract lists `triage` in `republished_by` and whose data changed: the Work Board, and project pages listed in `dashboards.yaml: project_pages` whose project's records changed in this run (`system/dashboards/project-page.contract.md`).
11a. **Feedback.** In chat, when the user drops something Nova created as never a promise, reopens something Nova closed, or overrides a priority, log a `feedback` line (`reference/learning.md` §1) with the fix.
12. **Report.** Run-report row: reviewed, created, closed, dropped, slipped, follow-up drafts, questions raised. In chat: answer the user's question (grouped lists, cited), then the one or two things that need them.

## Outputs
- Commitment and project records (`status`, `priority`, `insight`, `next_step`, `health`, `completed_on`, Updates).
- New commitments (via `nova-capture`), questions in `user/inbox/questions.md`, follow-up approvals in `user/inbox/approvals.md` (drafts themselves come from `nova-write`).
- Republished Work Board and project pages (`nova-dashboards`).
- `user/.state/triggers.yaml` entries; index lines; activity-log line; run-report row.
- Data the Work Board and brief read directly from records (no separate file).

## Guardrails
- Autonomy classes: `records_write`, `merge_supersede` (ambiguous → propose), `dashboards_refresh`, `external_read`; `drafts_create` only in chat via `nova-write`; sending a follow-up is `send_communication` (locked, approve) and never happens here; `tasks_manage` (propose) if the user asks to mirror commitments into a task tool. See `system/rules/governance.md`.
- Close only on evidence (`system/rules/knowledge.md` § Commitments); never close on absence of news.
- Never change `due` without evidence or the user's word.
- Insights and next steps are specific and short; no generic advice ("follow up soon"). No more than one line each.
- Respect `rhythms.yaml` trigger switches and away/paused (step 1, step 9).

## Done when
- No open commitment is past due without `status: slipped`.
- Every open/slipped commitment and every active project has a current `insight` and `next_step` (full mode).
- Every closed commitment cites its evidence in Updates.
- Every overdue `waiting_on` (not away) has exactly one pending approvals entry and is handed to the email-drafts procedure for its single follow-up draft (marker `follow-up draft created <date>`); the firing is recorded once in `triggers.yaml`.
- Dashboards listing `triage` (Work Board, changed project pages) are republished.
- Indexes and the run report reflect the changes; everything is committed.
