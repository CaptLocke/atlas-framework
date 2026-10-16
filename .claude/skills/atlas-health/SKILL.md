---
name: atlas-health
description: "Keep Atlas healthy with little or no effort from the user: tidy the knowledge (stale, orphaned, duplicate, broken, unprocessed, expired items), check the system (failed runs, connections, hooks, routine environment, validation, unmodified system files, extensions, repo size, attestation, GitHub), smoke-test the platform features Atlas depends on, audit that every locked action was approved, fix what's clear, and bring only real decisions to the user. Use for the `maintenance` and `monthly` jobs, after updates, and when the user says \"run a health check\", \"is everything working?\", \"why didn't my brief arrive?\", \"clean up my knowledge\"."
---
# Health

## Purpose
Atlas maintains itself. Clear problems are fixed automatically and logged; ambiguous ones become short questions; problems Atlas can't fix become a known issue with a plain-language fix, and, when it's a product problem, a suggested issue report. Results feed the monthly report, the Control Center, and `user/.state/health.yaml`.

## When to use
| Mode | Invoked by | Scope |
|---|---|---|
| **Maintenance** | `maintenance` job (upkeep routine) | Routine-environment check, index rebuild, link repair, obvious dedupes, journal/inbox sweep, expiries |
| **User health check** | `monthly` job (when `moments.user_health_check` is on); chat on request | The user half: `reference/user-health.md` |
| **System health check** | `monthly` job (when `moments.system_health_check` is on); `atlas-update` after each update; chat on request | The system half, smoke test, audits: `reference/system-health.md` |
| **Quick check** | Chat: "is everything working?", "why didn't X run?" | Known issues + latest run reports + targeted checks for the question |

## Inputs
- `user/knowledge/` (records, `_index/`), `user/journal/`, `user/inbox/`, `user/profile/`, `user/settings/`, `user/extensions/registry.yaml`.
- `user/logs/activity/`, `user/logs/runs/`, `user/.state/{jobs,health,triggers,cursors,setup}.yaml`.
- `system/manifest.yaml`, `system/VERSION`, `.claude/settings.json`, `.claude/hooks/`, `python3 system/tools/validate.py --all`.
- Connector tools in the session, `user/settings/connectors.yaml`, `user/settings/dashboards.yaml`, `user/settings/atlas.yaml`.

## Procedure
### 1. Maintenance (fast, mechanical)
0. **Routine environment:** run the "Routine environment" check from `reference/system-health.md` over the last 8 days of run reports (any routine run without `atlas_context: routine` → known issue `routine-env-missing` naming the routine).
1. **Rebuild indexes** from records (`system/schemas/formats.md` §5): every `_index/<folder>.md` for system and registered user types, `hot.md`, `people-map.md`, `archive.md`.
2. **Repair links:** for each `[[id]]` that doesn't resolve, fix it when the target is clear (renamed alias, superseded → follow `superseded_by`, merged duplicate); otherwise leave it and list it for the user health check.
3. **Obvious dedupes** per `system/rules/knowledge.md` (same email; same domain; same full name + same org): merge (`merge_supersede`) only clear cases; ambiguous → `user/inbox/questions.md`.
4. **Sweep:** journal days with unprocessed sections (`processed` missing a section that has text) and files left in `user/inbox/drop/` → process with `atlas-capture` (or leave for `ingest` if it runs next in the same routine).
5. **Expire** (skip entirely while away is active; away time doesn't count toward expiry): approvals pending over 14 days → `expired`; insights `new` and unseen over 30 days → `expired`; answered/dismissed questions older than 90 days stay (history). Record each status change in the entry's status history.
6. Commit; add counts to the run report (indexes rebuilt, links fixed, merges, items expired).

### 2. User health check
Follow `reference/user-health.md`: stale records, orphans, duplicates, broken links, unprocessed journal/inbox, profile proposals, guide drift, settings sanity, expired approvals/insights. Auto-fix the clear cases (table in the reference); bring the rest to the user as a short list in the monthly report and as `questions.md` entries. Set `health.yaml: last_user_check`.

### 3. System health check
Follow `reference/system-health.md`:
1. **Runs:** failures and partial runs in run reports since the last check; routines that missed expected runs (a routine silent for more than twice its interval, or 72h for daily ones, likely turned off by the platform).
2. **Connectors:** auth errors in run reports; each mapped connector present in the session; `tool_fingerprint` drift; unmapped connectors → re-map via `atlas-connectors` (chat) or a known issue (routine).
3. **Hooks present:** `.claude/settings.json` registers the PreToolUse hooks; hook scripts exist.
3a. **Routine environment:** every routine run report since the last check has `atlas_context: routine`; otherwise a high-severity `routine-env-missing` issue per routine, with the fix (attach it to the "Atlas routine" environment). Each also has `release_check` of `clean`, `restored` or `skipped`; otherwise a high-severity `routine-release-check` issue (fix: paste the setup script, `atlas-setup` `reference/automations.md` §3). A `restored` run means a chat had changed system files: tell the user in one line and look at what changed (the repair commit, `Atlas-Actor: release-check`, shows it).
4. **Validation:** `python3 system/tools/validate.py --all`; fix data errors that have one obvious fix; list the rest.
5. **System files unmodified** vs the release tag `v<installed_version>`, or, until such a tag exists upstream, vs `atlas.yaml: installed_from_commit` (the template's starting commit); differences not made by update commits → in chat, `atlas-update` repair (§D), which first offers to keep intentional edits as an extension; in a routine, record a known issue only and stop there. **Uncommitted** edits to owned paths, or unexpected new files in `.claude/hooks/` (the hooks block every send, share and delete while they exist), are simpler: show the user what changed, then restore with `git checkout HEAD -- <each owned path>` (e.g. `git checkout HEAD -- .claude system CLAUDE.md`), which only puts back committed content (allowed in chats and routines; the source must be written as `HEAD`). New files in `.claude/hooks/` can't be removed by Atlas: ask the user to delete them on GitHub or in a session without hooks.
6. **Extensions:** `requires_atlas` satisfied; overridden components unchanged since the extension was created or last confirmed; conflicts (two overrides of one component, governance conflicts) flagged.
7. **Repo size** and growth; record and index sizes.
8. **Attestation due:** `atlas.yaml: attestation.reconfirm_due` reached → known issue and a quarterly-style re-confirmation question (`atlas-review` role refresh handles it in chat).
9. **GitHub connection:** push works; repository still private and without collaborators (N9) where the session can check.
10. **Updates:** installed vs latest release.
11. **Smoke test** of platform dependencies (repo push, connector read, hooks fire, artifact republish) → `health.yaml: smoke_test`.
12. **Audits:** every locked action in the activity log has an approval entry and a matching user confirmation; no routine performed a locked action; governance files changed only in chat commits; data-rule spot checks (N11) and suspicious-content follow-ups (N7).
Set `health.yaml: last_system_check`.

### 4. Record results
- Update `user/.state/health.yaml: known_issues`: add new issues (`id`, `severity: high|medium|low`, `since`, `summary`, `fix`, `status: open`), close fixed ones (`status: resolved`), never duplicate an open issue (same `id`).
- Write the user-facing summary into the caller's output (monthly report section, run report, or chat). Each problem: what happened, what it affects, how to fix it (one action).
- Republish the Control Center (`atlas-dashboards`).

### 5. Can't fix it?
If a problem persists after the available fix (e.g., a job fails three runs in a row with the same error, an update failed twice, a platform feature fails the smoke test), say so plainly and suggest `atlas-report-issue` ("Want me to draft a short report to Atlas's maker? I'll remove anything personal first."). In routines, add the suggestion to the known issue's `fix`.

## Outputs
- Rebuilt indexes, repaired links, merged clear duplicates, processed sweep items, expired inbox entries.
- `user/.state/health.yaml` (`last_user_check`, `last_system_check`, `known_issues`, `smoke_test`); `questions.md` entries for decisions.
- Sections for the monthly report (`user/work/reports/YYYY-MM.md`) or the run report; one-line chat summaries.
- Activity-log lines for every fix; Control Center republished.

## Guardrails
- Governance: `system/rules/governance.md`. Classes touched: `read`, `records_write`, `merge_supersede` (clear cases only; ambiguous always proposed), `archive` (only records the user agreed to, or per auto rules in the reference), `external_read` (read-only probes), `dashboards_refresh`. Never `destructive`: health checks never delete records, files, events, or messages; deletion suggestions go to the user.
- System-file restore is chat-only and goes through `atlas-update` (update lock, N5); routines only record a known issue. Connector map changes go through `atlas-connectors` (N6, chat only).
- Profile changes are proposals unless `profile_update: auto`.
- Never edit journal text or user-authored notes (`user_content_edit`); only the `processed` field.
- Audits report; they never "fix" history (N8). An unapproved locked action is a high-severity known issue told to the user.
- Never write secrets into health files or reports; error text is summarized without personal content.

## Done when
- Indexes match records; every link resolves or is listed for the user.
- `health.yaml` has today's check date(s), an up-to-date `known_issues` list, and (system check) a `smoke_test` result for all four dependencies.
- Every problem found is fixed, queued as a question, or recorded as a known issue with a fix; unfixable product problems carry a report suggestion.
