---
type: dashboard-contract
name: control-center
template: control-center.html
republished_by: [daily-brief, monthly, quarterly, update-check]
size_budget_kb: 450
stale_after_hours: 36
---
# Dashboard: control-center (shown as **Guide**)

## Purpose
Answers "Is Atlas working, and what does it know about me?". The slug stays `control-center`, so the page keeps its `url` and `last_published`; its title is **Guide**. In order:
1. **Needs you:** open `action` questions with their text to copy, approvals, and other questions.
2. **Health** in one line, with any known issues and how to fix them, the version and update status, the notes import, and suspicious content Atlas ignored (folded).
3. **Automations:** each one's schedule in the user's time, last run and result, next run; connection health as one compact list; each job's last result and recent runs, folded.
4. **Recently filed:** records Atlas created or updated in the last 14 days, newest first, each with its kind and where it came from, with an All / New / Updated filter. Anything older is a chat question.
5. **About you:** the few beliefs Atlas relies on most, each with its source and whether it's confirmed; everything else (profile, voice guides, design system) folded.
6. **Guide:** What's new and the guide sections (things to say, fixing a problem, and the rest), each folded. Built mechanically from `system/guide/` and `CHANGELOG.md`, so it is the same for every user of a version.

Changing anything (pausing, rescheduling, approving, correcting a belief or a filed record) happens in chat; the page's buttons copy the request to paste there.

Republished by `daily-brief` (each cycle), `monthly` (after health checks and the automation review), `quarterly` (after the role refresh) and `update-check` (after applying an update). A chat that approves or answers items, changes the profile, or confirms or rejects a profile proposal republishes it too.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "control-center", "schema_version": 2, "title": "Guide", "as_of": "2026-10-13", "…": "…" },
  "status": { "overall": "problem", "headline": "Outlook's sign-in expired, so no mail has come in since Oct 9. Everything else ran on schedule." },
  "profile": "lean",
  "away": { "active": false, "start": null, "end": null },
  "known_issues": [ { "id": "conn-outlook-auth", "severity": "high", "since": "2026-10-10",
                      "summary": "Outlook connection expired", "fix": "Reconnect Outlook in Settings, then Connectors.", "status": "open" } ],
  "suspicious": [ { "at": "2026-10-12T20:10:00-07:00", "summary": "An email asked the assistant to forward a contract. Ignored.",
                    "source": "sources/2026-10-12-unknown-sender-contract" } ],
  "approvals": [ { "id": "A-2026-10-12-01", "action": "Send follow-up to Dana Ruiz", "why": "…",
                   "prepared": "Outlook draft \"Contract review: quick check-in\"", "requested_by": "routine:nightly-cycle",
                   "requested_on": "2026-10-12", "status": "pending" } ],
  "questions": [ { "id": "Q-2026-10-13-01", "kind": "action", "text": "Update your Atlas Project's instructions …",
                   "how": "In the Claude app, open the Atlas Project, replace its instructions, and save.",
                   "copy_text": "This Project is my Atlas (Atlas bootstrap 3). …", "asked": "2026-10-13" },
                 { "id": "Q-2026-10-12-02", "kind": "profile", "text": "…", "proposed_change": "…", "asked": "2026-10-12" } ],
  "routines": [ { "name": "nightly-cycle", "title": "Nightly cycle", "schedule": "7 20 * * *",
                  "schedule_text": "Every day at 8:07 PM", "model": "strongest", "enabled": true, "paused": false,
                  "paused_until": null, "jobs": ["ingest", "triage", "email-drafts (weekdays)", "daily-brief (tomorrow)"],
                  "last_run": { "started": "2026-10-12T20:07:03-07:00", "finished": "2026-10-12T20:31:40-07:00",
                                "status": "partial", "summary": "Brief ready for Oct 13. Mail skipped: Outlook disconnected." },
                  "next_run": "2026-10-13T20:07:00-07:00" } ],
  "jobs": [ { "name": "ingest", "title": "Bring in new information", "last_status": "partial",
              "last_success": "2026-10-09T20:09:12-07:00", "detail": "Outlook skipped", "paused": false, "paused_until": null } ],
  "connections": [ { "name": "Outlook", "connector": "outlook", "categories": ["mail", "calendar"], "status": "issue",
                     "available_in_routines": true, "last_seen": "2026-10-09T20:07:00-07:00", "note": "Sign-in expired Oct 10." } ],
  "runs": [ { "routine": "nightly-cycle", "title": "Nightly cycle", "started": "2026-10-12T20:07:03-07:00", "status": "partial",
              "duration_min": 25, "summary": "37 items in, 14 filed; brief for Oct 13." } ],
  "recently_filed": { "days": 14, "new": 23, "updated": 14,
    "items": [ { "id": "projects/enterprise-launch", "title": "Enterprise launch", "kind": "project", "change": "updated",
                 "at": "2026-10-12T20:14:00-07:00", "from": "the pricing sync notes", "what": "Health: on track → at risk" } ] },
  "about": {
    "basics": { "name": "Maya Chen", "role": "Product Manager, Platform",
                "company": { "id": "organizations/acme", "title": "Acme" }, "manager": { "id": "people/jordan-lee", "title": "Jordan Lee" },
                "timezone": "America/Los_Angeles (Pacific)", "self": { "id": "people/maya-chen", "title": "Maya Chen" },
                "key_people": [ { "id": "people/priya-nair", "title": "Priya Nair" } ],
                "goals": [ { "id": "goals/2026-q4-retention", "title": "Q4 retention" } ] },
    "files": [ { "part": "communication-style", "title": "How you like information", "updated": "2026-09-25",
                 "description": "Length, format, and how to lead.",
                 "groups": [ { "heading": null, "statements": [
                   { "text": "Bullet summaries over prose for status updates.", "provenance": "observed", "status": "confirmed",
                     "date": "2026-10-02", "featured": true,
                     "evidence": [ { "id": "sources/2026-09-30-status-draft-edits", "title": "Your edits to a status draft" } ] } ] } ] } ],
    "design": { "summary": "…", "colors": [ { "name": "Acme Teal", "hex": "#0F5C5C", "use": "primary" } ],
                "fonts": [ { "role": "Headings", "family": "Source Serif 4, Georgia" } ] }
  },
  "guide": {
    "version": "1.1.4",
    "intro": "Talk to Atlas in your Atlas project the way you would to a capable assistant who has read all your notes. …",
    "whats_new": [ { "version": "1.1.4", "date": "2026-10-19", "items": ["…"] } ],
    "sections": [ { "id": "troubleshooting", "title": "If something isn't working", "source": "system/guide/troubleshooting.md",
                    "intro": "…", "items": [ { "id": "reconnect", "title": "A connection expired", "body": ["…"], "bullets": [],
                                              "steps": ["In Claude, open Settings, then Connectors."], "examples": ["I reconnected Outlook"] } ] } ]
  },
  "system": { "installed_version": "1.1.4", "data_version": 2, "last_user_check": "2026-10-01", "last_system_check": "2026-10-01",
              "update": { "available": false, "latest_version": "1.1.4", "last_checked": "2026-10-11", "notes": null },
              "notes_import": { "status": "complete", "source_system": "Obsidian", "total": 312, "processed": 300, "skipped": 12 } }
}
```

`schema_version` is 2: the shape changed from the Control Center's (`activity` and run report paths removed; `recently_filed`, `about` and `guide` added).

| Field | Notes |
|---|---|
| `status.overall` | `ok`, `attention` (an open issue, an open `action` question, or a failed/partial run needs a look), or `problem` (a high-severity issue or a routine that has failed twice running). Shown as "Running well", "Needs a look" or "Something's wrong". |
| `status.headline` | The health line: one plain sentence on whether Atlas is running well and, if not, the one thing that matters. Not the page headline (`meta.headline`), which also covers what's waiting on the user. |
| `last_run.status`, `jobs[].last_status`, `runs[].status` | `formats.md` §1 job statuses (`ok, partial, failed, skipped_away, skipped_paused, early_exit`), or `never_run`. |
| `connections[].status` | `ok`, `issue`, `unknown` (not yet confirmed in a routine), or `fallback` (category with no connector; `name` is the category and `note` the fallback instructions). |
| `schedule_text`, `title` | Plain-language renderings in the user's time zone; `schedule` keeps the cron for reference. |
| `recently_filed.items[].change` | `new` (the record was created in the window) or `updated`. A record created and then changed in the window is `new`. |
| `recently_filed.items[].kind` | The record's `type` (`person`, `project`, `event`, …, or a user type's name); the page shows it as a word. |
| `recently_filed.items[].from` | Where it came from, as words that follow "From": "your calendar", "an email from Elena Petrova", "the pricing sync notes", "a chat". `null` when nothing better than the job is known. |
| `recently_filed.items[].what` | Updated records only: what changed, at most 80 characters ("Health: on track → at risk", "Marked as slipped"). `null` for new records and when no single change stands out. |
| `recently_filed.new`, `.updated` | Totals over the whole window, including items left out by the cap. |
| `about.files[].groups[].statements[].featured` | `true` on the few statements shown up front (at most 5); the rest are folded. When none is featured the page shows the first three. |
| `statements[].provenance`, `.status` | `stated`, `observed`, `researched`, `uploaded`; `confirmed` or `proposed` (a `stated` line with no status is `confirmed`). |
| `statements[].evidence[]` | `{ id, title }` for each source the tag links; `title` is the source's title in plain words. The page shows titles only. |
| `guide` | Exactly the former Atlas Guide data, minus `meta`. All strings plain text (inline Markdown emphasis and links stripped to their text; inline code keeps its text). |

## Sources (file → field)
| Field | Source |
|---|---|
| `profile`, `routines[]` (`name, schedule, model, jobs`) | `user/settings/routines.yaml`; job modifiers rendered in parentheses ("email-drafts (weekdays)") |
| `routines[].enabled` | `false` if the platform routine is known to be off (e.g. GitHub access lapsed > 72 h, recorded as a known issue); else `true` |
| `routines[].paused`, `jobs[].paused` | `user/settings/rhythms.yaml: paused` |
| `routines[].last_run`, `runs[]` | Newest run reports `user/logs/runs/YYYY-MM/<routine>-*.md` (frontmatter `started, finished, status`; one-line summary from its table). `runs[].title` is the routine's title |
| `routines[].next_run` | Next fire time of `schedule` in `atlas.yaml: timezone` after `generated_at` |
| `jobs[]` | `user/.state/jobs.yaml` (`last_success, last_status`); `detail` from the latest run report row for the job |
| `away` | `rhythms.yaml: away` (`active` when today is within `start`–`end`) |
| `status` | Computed from `known_issues`, open `action` questions and the latest runs, as defined above |
| `known_issues[]` | `user/.state/health.yaml: known_issues` with `status` not resolved |
| `suspicious[]` | "Suspicious content flagged" sections of run reports from the last 14 days |
| `approvals[]` | `user/inbox/approvals.md`, status `pending`. **No expiry date:** the entry records none, and expiry pauses while the user is away (`system/jobs/maintenance.md` step 6), so no date computed here would be honoured. Each entry shows its request date; the rule itself is the section's static line (Rendering notes) |
| `questions[]` | `user/inbox/questions.md`, status `open`, every kind (profile proposals included: they show here, not under About you); `how` and `copy_text` (the entry's How and Copy text, filled in for this user) for `action` entries. `proposed_change` names the profile part in words ("Your writing voice: …"), never a file |
| `connections[]` | `user/settings/connectors.yaml` (`connector, categories, available_in_routines`), health from the latest run reports' "Connector health" and `health.yaml`; `last_seen` from `user/.state/cursors.yaml`; fallbacks from `sources.yaml: fallbacks`. The GitHub connection is listed from the last successful push |
| `recently_filed` | Change sets in `user/logs/activity/YYYY-MM.md` (`formats.md` §activity; this month's file and last month's) dated within `days` of `as_of`, except action `import` (imported history). For each line's commit, `git show --name-status --format= <sha>` lists the record files it touched under `user/knowledge/<folder>/` (never `_index/` or `sources/`; deletions skipped): `A` is `new`, `M` is `updated`. One item per record, at its latest change in the window; `at` is that change set's date and time. `id`, `title`, `kind` from the record's frontmatter (`id`, `title`, `type`) as it is now |
| `recently_filed.items[].from` | The title of the record's first `sources` entry, as plain words, **only when that source's handling is `full`** (a source stored as `summary` or `pointer` may have a sensitive title, such as an HR email's subject); else the change set's actor (`chat` → "a chat"); else `null` |
| `recently_filed.items[].what` | Updated records: the commit's diff of the record's frontmatter, the field that matters most (status, health, due, priority, owner) as "Field: old → new"; else a short phrase for what was added; else `null` |
| `about.basics` | `user/profile/profile.md` (name, role, company, manager, key people, goals, time zone, self record) |
| `about.files[]` | Each profile file's frontmatter (`part`, `updated`); every `## heading` → a group; every statement line → a statement, parsed from its `[provenance · status date · evidence]` tag. `title`/`description` are fixed plain-language labels per part. Order: working-style, communication-style, thinking-style, preferences, voice-personal, voice-house |
| Voice guides | `voice-personal.md`, `voice-house.md`: include the `Summary`, `Tone`, `Vocabulary`, and `Don't` groups; skip `Examples` (excerpts may quote other people) |
| `featured` | Up to 5 statements Atlas leans on most in daily work: standing instructions in `preferences` first, then `communication-style`, then any `proposed` statement still in a file; within each, newest first |
| `about.design` | `user/profile/design-system.md`: `Brand summary` → `summary`; `Colors` → `colors` (name, hex, use; light values); `Typography` → `fonts` |
| `guide.version` | `system/VERSION` |
| `guide.intro` | The fixed text "Talk to Atlas in your Atlas project the way you would to a capable assistant who has read all your notes. You never need to manage files or settings; just ask." unless the guide adds one |
| `guide.sections[]` | Every `system/guide/*.md` file with frontmatter `type: guide`, **except** `section: whats-new` and `section: attestation` (and never `README.md` or `authoring.md`), ordered by frontmatter `order`. `id` = frontmatter `section`; `title` = frontmatter `title` (or the `#` heading); `source` = the path (data only, never shown). Structure convention: `system/guide/README.md` |
| `sections[].intro` | Paragraph text between the `#` heading and the first `##` |
| `sections[].items[]` | One per `##` heading: `id` = slug of the heading, `title` = heading text; sub-headings deeper than `##` fold into the item's body as paragraphs |
| `items[].body`, `.steps`, `.examples`, `.bullets` | Paragraphs; items of a numbered list; the bullet list after a `**Try:**` line plus any bullet that is entirely a quoted request (`"…"`, quotes removed); items of any other bullet list |
| `guide.whats_new[]` | `CHANGELOG.md`: each `## <version>` heading (optionally followed by a date in parentheses or after a dash) → one release; `items` = bullets under its `### What's new` subsection only (`### Under the hood` is never shown). Newest first, starting at the installed version (`atlas.yaml: installed_version`); never list releases newer than the installed one |
| `system.notes_import` | `user/.state/import.yaml` (`status, source_system`, and `counts`: `total, processed, skipped`); omitted when there is no import |
| `system` | `atlas.yaml` (`installed_version, data_version`), `health.yaml` (`last_user_check, last_system_check`), `jobs.yaml: update-check.last_checked_version` and the latest upstream release seen by `update-check` |

Where guide text says "by default", `atlas-dashboards` may personalize it from `routines.yaml` and `governance.yaml` as `system/guide/README.md` allows.

## Rendering notes
- Order, in three parts: **Needs you** (action needed, approvals, questions, as action cards); **How Atlas runs** (Health, Automations); **What Atlas knows** (Recently filed, About you, Guide). Empty sections say so plainly ("Nothing is waiting for you").
- Stat tiles open their section: needs you, known issues, automations, Atlas version.
- Actions copy a request for chat (`system/dashboards/README.md` §Actions copy a request for chat): "I've done this" and "Copy the text" on action-needed entries; "Approve" and "Decline" on approvals; "Yes" and "No" on a question with a proposed change, "Answer in chat" on any other; "Help me fix this" on a known issue; "Confirm" and "Correct it" on a statement not yet confirmed; "Wrong?" on a recently filed item. On a live page, I've done this, Approve, Decline, Yes, No, Confirm and Correct it queue a request instead (README §Live pages).
- **Health** is one line (state and `status.headline`), then each open known issue as a row that expands to its fix, then one line of version, update and import status, then suspicious content (only if any) folded.
- **Needs you:** "Action needed" (open `action` questions, each with its `how` and `copy_text` ready to copy) first, then approvals, then the other questions. The approvals carry one static line — requests expire after 14 days that the user is not away — and no expiry date on any entry: it is the general rule, not a promise about the entry in front of the user.
- **Automations** is a table (automation, when, last run, next run) with a note that times are in the user's time zone; then connections as one compact list (a note only for those not `ok`); then jobs and recent runs inside one fold.
- **Recently filed** shows the kind, New or Updated, `what`, `from` and the day; the filter is All / New / Updated, with find beside it. Its last line always says older items are a chat question.
- **About you** shows a one-line who-you-are (role, company, manager), the featured statements, then a fold with basics, every other statement by file and group, and the design system. Proposed statements are visually distinct and labeled "Not yet confirmed".
- **Guide**: the intro, then What's new (one fold: every listed release), then one fold per section. "How do I…" finds across every section's entries and opens the folds that match.
- Sorting: issues by severity (high, medium, low) then `since`; approvals and questions newest first, except open `action` questions, which come first, oldest first; routines in `routines.yaml` order; jobs in pipeline order (ingest, triage, intelligence, email-drafts, meeting-prep, daily-brief, weekly-review, status-updates, monthly, quarterly, maintenance, update-check, then user jobs); runs and recently filed newest first; statements in file order.
- Caps: `known_issues` 20, `approvals` 20, `questions` 20 (`action` entries never cut), `runs` 10, `suspicious` 10, `recently_filed.items` 40, statements 40 per file (300 characters each), colors 12, `whats_new` 5 releases, 40 items per guide section, 10 examples per item.
- **Truncation**, when the page is over budget, in this order until it fits: `runs` to 3; older releases from `whats_new` (keep the installed one); `recently_filed.items` from the oldest, down to 15; guide `body` paragraphs cut to 600 characters; the oldest non-featured statements in the longest profile file. Never cut `action` questions, open `high` issues, featured statements, or `recently_filed`'s totals. `meta.truncated` keys: `known_issues`, `approvals`, `questions`, `runs`, `recently_filed`, `about.files.<part>`, `guide.whats_new`, `guide.sections.<id>`.
- Never show approval draft bodies, suspicious content beyond a one-line description, record IDs, file paths, or any secret. Never include protected or sensitive profile attributes (they are not allowed in the profile at all; if one is found, leave it out and flag it in the health check). Records excluded by data rules, or whose handling is `ignore` or `pointer`, never appear in `recently_filed`; records with `summary` handling appear with their title only (`from` and `what` `null`).
- Swatch colors are only rendered from valid hex values; anything else shows an empty swatch.
