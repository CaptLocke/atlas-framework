---
type: templates-index
version: 1.0.0
---
# Templates

Starter files for the user half. `nova-setup` copies each template to its destination in `user/` at the setup step shown (steps: tactical §16 and `.claude/skills/nova-setup/`). Templates are system-owned and replaced on update; the copies in `user/` belong to the user and are never overwritten by updates (only migrations change them).

**Copy rules**
- Copy only when the destination does not exist. Never overwrite a user file; if a destination exists (resumed or repeated setup), keep it and fill in missing keys only.
- Fill placeholders (`null`) during the step that owns them; leave the rest at their defaults.
- Commit each step's files together (`Nova-Actor: setup`).
- Formats: settings `system/schemas/settings.md`; profile `system/schemas/profile.md`; inbox, state, logs, registry `system/schemas/formats.md`.

| Template | Destination | Copied at setup step | Filled by |
|---|---|---|---|
| `state/setup.yaml` | `user/.state/setup.yaml` | 5 (first thing setup writes) | `nova-setup` after every step |
| `state/cursors.yaml` | `user/.state/cursors.yaml` | 5 | `ingest` |
| `state/jobs.yaml` | `user/.state/jobs.yaml` | 5 | every job |
| `state/triggers.yaml` | `user/.state/triggers.yaml` | 5 | jobs and chats that fire triggers |
| `state/health.yaml` | `user/.state/health.yaml` | 5 | `nova-health`, `monthly` |
| `inbox/approvals.md` | `user/inbox/approvals.md` | 5 | jobs and chats (governance) |
| `inbox/insights.md` | `user/inbox/insights.md` | 5 | `intelligence` |
| `inbox/questions.md` | `user/inbox/questions.md` | 5 | all skills and jobs |
| `logs/README.md` | `user/logs/README.md` | 5 | (static) |
| `extensions/registry.yaml` | `user/extensions/registry.yaml` | 5 | `nova-extend` |
| `settings/nova.yaml` | `user/settings/nova.yaml` | 5 (attestation recorded here; nothing is ingested before it) | `nova-setup` (5, 9, 12), `nova-update` |
| `settings/governance.yaml` | `user/settings/governance.yaml` | 5 | `nova-settings` (chat only, N6) |
| `profile/profile.md` | `user/profile/profile.md` | 6 | interview (6), research (7) |
| `profile/working-style.md` | `user/profile/working-style.md` | 6 | interview |
| `profile/communication-style.md` | `user/profile/communication-style.md` | 6 | interview |
| `profile/thinking-style.md` | `user/profile/thinking-style.md` | 6 | interview |
| `profile/preferences.md` | `user/profile/preferences.md` | 6 | interview |
| `profile/voice-personal.md` | `user/profile/voice-personal.md` | 8 | uploads, sent mail (9), edits over time |
| `profile/voice-house.md` | `user/profile/voice-house.md` | 8 | research (7), uploads |
| `profile/design-system.md` | `user/profile/design-system.md` | 8 | brand guides, website research |
| `settings/connectors.yaml` | `user/settings/connectors.yaml` | 9 | `nova-connectors` |
| `settings/sources.yaml` | `user/settings/sources.yaml` | 9 | `nova-connectors`, `nova-settings` |
| `settings/data-rules.yaml` | `user/settings/data-rules.yaml` | 9 (conservative defaults; user may adjust) | `nova-settings` (chat only, N6) |
| `settings/rhythms.yaml` | `user/settings/rhythms.yaml` | 10 | `nova-setup`, `nova-settings`, `nova-away` |
| `settings/routines.yaml` | `user/settings/routines.yaml` | 10: replaced by a copy of the chosen `system/routine-profiles/<profile>.yaml`, cron hours adjusted to `rhythms.yaml: work_hours` | `nova-setup`, `nova-settings` |
| `settings/dashboards.yaml` | `user/settings/dashboards.yaml` | 11 | `nova-dashboards` |

**Placeholders set at step 5:** `nova.yaml: installed_version` from `system/VERSION`, `data_version` from `system/manifest.yaml: data_version`, `timezone`, `repo`, `user_display_name`, `plan`, and `attestation` (with `reconfirm_due` = first business day of next quarter). `deliverables_folder` and `drop_folder` are filled at steps 9–10; `first_brief_delivered` by the first `daily-brief`.

**Folders** (`user/knowledge/<type>/`, `user/journal/`, `user/work/`, `user/library/`, `user/inbox/drop/`, `user/logs/activity/`, `user/logs/runs/`, `user/extensions/<kind>/`, `user/profile/assets/`) ship in the template repo with `.gitkeep` files and need no template. `user/work/` subfolders (`briefs/`, `prep/`, `reviews/`, `status/`, `reports/`, `deliverables/`) are created by the jobs that first write to them.
