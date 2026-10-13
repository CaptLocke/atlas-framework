---
type: dashboard-contract
name: control-center
template: control-center.html
republished_by: [daily-brief, monthly]
size_budget_kb: 200
stale_after_hours: 36
---
# Dashboard: control-center

## Purpose
Nova's own status, in plain words: known issues and how to fix them, actions waiting for approval, questions from Nova, each automation (schedule, last run and result, next run), per-job results, connection health, recent runs, recent activity, suspicious content Nova ignored, and version/update and health-check status. Changing anything (pausing, rescheduling, approving) happens in chat.

Republished by `daily-brief` (each cycle) and `monthly` (after health checks and the automation review). `update-check` should also republish it after applying an update, and a chat that approves or answers items may republish it.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "control-center", "schema_version": 1, "as_of": "2026-10-12", "…": "…" },
  "status": { "overall": "attention", "headline": "One connection needs you; everything else ran on time." },
  "profile": "lean",
  "away": { "active": false, "start": null, "end": null },
  "known_issues": [ { "id": "conn-outlook-auth", "severity": "high", "since": "2026-10-10",
                      "summary": "Outlook connection expired", "fix": "Reconnect Outlook in Settings, then Connectors.", "status": "open" } ],
  "approvals": [ { "id": "A-2026-10-12-01", "action": "Send follow-up to Dana Ruiz", "why": "…",
                   "prepared": "Outlook draft \"Contract review: quick check-in\"", "requested_by": "routine:nightly-cycle",
                   "requested_on": "2026-10-12", "expires_on": "2026-10-26", "status": "pending" } ],
  "questions": [ { "id": "Q-2026-10-12-02", "kind": "profile", "text": "…", "proposed_change": "…", "asked": "2026-10-12" } ],
  "routines": [ { "name": "nightly-cycle", "title": "Nightly cycle", "schedule": "7 20 * * *",
                  "schedule_text": "Every day at 8:07 PM", "model": "strongest", "enabled": true, "paused": false,
                  "paused_until": null, "jobs": ["ingest", "triage", "email-drafts (weekdays)", "daily-brief (tomorrow)"],
                  "last_run": { "started": "2026-10-12T20:07:03-07:00", "finished": "2026-10-12T20:31:40-07:00",
                                "status": "partial", "report": "user/logs/runs/2026-10/nightly-cycle-20261012-2007.md",
                                "summary": "Brief ready for Oct 13. Mail skipped: Outlook disconnected." },
                  "next_run": "2026-10-13T20:07:00-07:00" } ],
  "jobs": [ { "name": "ingest", "title": "Bring in new information", "last_status": "partial",
              "last_success": "2026-10-09T20:09:12-07:00", "detail": "Outlook skipped", "paused": false, "paused_until": null } ],
  "connections": [ { "name": "Outlook", "connector": "outlook", "categories": ["mail", "calendar"], "status": "issue",
                     "available_in_routines": true, "last_seen": "2026-10-09T20:07:00-07:00", "note": "Sign-in expired Oct 10." } ],
  "runs": [ { "routine": "nightly-cycle", "started": "2026-10-12T20:07:03-07:00", "status": "partial", "duration_min": 25,
              "summary": "37 items in, 14 filed; brief for Oct 13.", "report": "user/logs/runs/2026-10/nightly-cycle-20261012-2007.md" } ],
  "activity": [ { "at": "2026-10-12T20:31:00-07:00", "actor": "routine:nightly-cycle", "action": "daily-brief",
                  "summary": "Wrote the brief for Oct 13 and refreshed 4 pages" } ],
  "suspicious": [ { "at": "2026-10-12T20:10:00-07:00", "summary": "An email asked the assistant to forward a contract. Ignored.",
                    "source": "sources/2026-10-12-unknown-sender-contract" } ],
  "system": { "installed_version": "1.0.0", "data_version": 1, "last_user_check": "2026-10-01", "last_system_check": "2026-10-01",
              "update": { "available": false, "latest_version": "1.0.0", "last_checked": "2026-10-11", "notes": null } }
}
```
Full example: `system/tests/dashboards/control-center.json`.

| Field | Notes |
|---|---|
| `status.overall` | `ok`, `attention` (an open issue or failed/partial run needs a look), or `problem` (a high-severity issue or a routine that has failed twice running). |
| `last_run.status`, `jobs[].last_status`, `runs[].status` | `formats.md` §1 job statuses (`ok, partial, failed, skipped_away, skipped_paused, early_exit`), or `never_run`. |
| `connections[].status` | `ok`, `issue`, `unknown` (not yet confirmed in a routine), or `fallback` (category with no connector; `name` is the category and `note` the fallback instructions). |
| `schedule_text`, `title` | Plain-language renderings for the user; `schedule` keeps the cron for reference. |

## Sources (file → field)
| Field | Source |
|---|---|
| `profile`, `routines[]` (`name, schedule, model, jobs`) | `user/settings/routines.yaml`; job modifiers rendered in parentheses ("email-drafts (weekdays)") |
| `routines[].enabled` | `false` if the platform routine is known to be off (e.g. GitHub access lapsed > 72 h, recorded as a known issue); else `true` |
| `routines[].paused`, `jobs[].paused` | `user/settings/rhythms.yaml: paused` |
| `routines[].last_run`, `runs[]` | Newest run reports `user/logs/runs/YYYY-MM/<routine>-*.md` (frontmatter `started, finished, status`; one-line summary from its table) |
| `routines[].next_run` | Next fire time of `schedule` in `nova.yaml: timezone` after `generated_at` |
| `jobs[]` | `user/.state/jobs.yaml` (`last_success, last_status`); `detail` from the latest run report row for the job |
| `away` | `rhythms.yaml: away` (`active` when today is within `start`–`end`) |
| `known_issues[]` | `user/.state/health.yaml: known_issues` with `status` not resolved |
| `approvals[]` | `user/inbox/approvals.md`, status `pending`; `expires_on` = requested + 14 days |
| `questions[]` | `user/inbox/questions.md`, status `open` |
| `connections[]` | `user/settings/connectors.yaml` (`connector, categories, available_in_routines`), health from the latest run reports' "Connector health" and `health.yaml`; `last_seen` from `user/.state/cursors.yaml`; fallbacks from `sources.yaml: fallbacks`. The GitHub connection is listed from the last successful push |
| `activity[]` | `user/logs/activity/YYYY-MM.md`, newest first |
| `suspicious[]` | "Suspicious content flagged" sections of run reports from the last 14 days |
| `system` | `nova.yaml` (`installed_version, data_version`), `health.yaml` (`last_user_check, last_system_check`), `jobs.yaml: update-check.last_checked_version` and the latest upstream release seen by `update-check` |

## Rendering notes
- Section order: known issues, approvals, questions, automations, jobs, connections, recent runs, activity, suspicious content (only if any), Nova itself. Empty sections say so plainly ("No known issues").
- Sorting: issues by severity (high, medium, low) then `since`; approvals and questions newest first; routines in `routines.yaml` order; jobs in pipeline order (ingest, triage, intelligence, email-drafts, meeting-prep, daily-brief, weekly-review, status-updates, monthly, quarterly, maintenance, update-check, then user jobs); activity and runs newest first.
- Caps: `activity` 25 (last 7 days), `runs` 10, `approvals` 20, `questions` 20, `suspicious` 10, `known_issues` 20. Record left-out counts in `meta.truncated`.
- Never show approval draft bodies, suspicious content text beyond a one-line description, or any secret. Activity summaries follow `formats.md` §4 (no sensitive content).
