---
type: templates-index
version: 1.0.0
---
# Templates

Starter files for the user half. `atlas-setup` copies every template to its destination in `user/` at setup step 5 (steps: tactical §16 and `.claude/skills/atlas-setup/`); later steps fill them in. Templates are system-owned and replaced on update; the copies in `user/` belong to the user and are never overwritten by updates (only migrations change them).

**Copy rules**
- Copy only when the destination does not exist. Never overwrite a user file; if a destination exists (resumed or repeated setup), keep it and fill in missing keys only.
- Fill placeholders (`null`) during the step that owns them; leave the rest at their defaults.
- Commit each step's files together (`Atlas-Actor: setup`).
- Formats: settings `system/schemas/settings.md`; profile `system/schemas/profile.md`; inbox, state, logs, registry `system/schemas/formats.md`.

**Step 5 (attestation) copies every template below**, so a complete, valid `user/` exists before anything else happens: all settings (including the default `governance.yaml` and conservative `data-rules.yaml`), the profile starters, the inbox, state, and log starters, and the extensions registry. Nothing is ingested until the attestation in `atlas.yaml` is recorded at the same step. Later steps fill or adjust the copies; they never re-copy.

| Template | Destination | Filled or adjusted at (tactical §16) | Later maintained by |
|---|---|---|---|
| `state/setup.yaml` | `user/.state/setup.yaml` | after every step | `atlas-setup` |
| `state/cursors.yaml` | `user/.state/cursors.yaml` | 12 (first pass) | `ingest` |
| `state/jobs.yaml` | `user/.state/jobs.yaml` | 12 | every job |
| `state/triggers.yaml` | `user/.state/triggers.yaml` | 12 | jobs and chats that fire triggers |
| `state/health.yaml` | `user/.state/health.yaml` | 10–12 (smoke test, known issues) | `atlas-health`, `monthly` |
| `inbox/approvals.md` | `user/inbox/approvals.md` | as needed | jobs and chats (governance) |
| `inbox/insights.md` | `user/inbox/insights.md` | 12 | `intelligence` |
| `inbox/questions.md` | `user/inbox/questions.md` | as needed | all skills and jobs |
| `logs/README.md` | `user/logs/README.md` | (static) | — |
| `extensions/registry.yaml` | `user/extensions/registry.yaml` | (empty at setup) | `atlas-extend` |
| `settings/atlas.yaml` | `user/settings/atlas.yaml` | 5 (identity, versions, attestation); 9–10 (deliverables and drop folders) | `daily-brief` (`first_brief_delivered`), `atlas-update` |
| `settings/governance.yaml` | `user/settings/governance.yaml` | defaults kept; adjusted only if the user asks | `atlas-settings` (chat only, N6) |
| `settings/data-rules.yaml` | `user/settings/data-rules.yaml` | 9 (reviewed and adjusted with the user) | `atlas-settings` (chat only, N6), `atlas-memory` (exclusions) |
| `settings/connectors.yaml` | `user/settings/connectors.yaml` | 9 | `atlas-connectors` (chat only, N6) |
| `settings/sources.yaml` | `user/settings/sources.yaml` | 9 | `atlas-connectors`, `atlas-settings` |
| `settings/rhythms.yaml` | `user/settings/rhythms.yaml` | 10 (moments, work hours) | `atlas-settings`, `atlas-away` |
| `settings/routines.yaml` | `user/settings/routines.yaml` | 10: replaced by a copy of the chosen `system/routine-profiles/<profile>.yaml`, cron hours adjusted to `rhythms.yaml: work_hours`; `routine_id`s filled as routines are created | `atlas-settings` |
| `settings/dashboards.yaml` | `user/settings/dashboards.yaml` | 11 | `atlas-dashboards` |
| `profile/profile.md`, `working-style.md`, `communication-style.md`, `thinking-style.md`, `preferences.md` | `user/profile/` | 6 (interview), 7 (research) | proposals via `questions.md` |
| `profile/voice-personal.md`, `voice-house.md`, `design-system.md` | `user/profile/` | 7 (research), 8 (uploads); personal voice also from sent mail after 9 | refined from the user's edits |

**Placeholders set at step 5:** `atlas.yaml: installed_version` from `system/VERSION`, `data_version` from `system/manifest.yaml: data_version`, `timezone`, `repo`, `user_display_name`, `plan`, and `attestation` (with `reconfirm_due` = first business day of next quarter). `company` (website, email domains, fiscal year) is filled at steps 6–8; `deliverables_folder` and `drop_folder` are filled at steps 9–10; `first_brief_delivered` by the first `daily-brief`.

**Folders** (`user/knowledge/<type>/`, `user/journal/`, `user/work/`, `user/library/`, `user/inbox/drop/`, `user/logs/activity/`, `user/logs/runs/`, `user/extensions/<kind>/`, `user/profile/assets/`) ship in the template repo with `.gitkeep` files and need no template. `user/work/` subfolders (`briefs/`, `prep/`, `reviews/`, `status/`, `reports/`, `deliverables/`) are created by the jobs that first write to them.
