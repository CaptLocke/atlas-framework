---
type: migration
id: "0001"
from_data_version: 0
to_data_version: 1
additive: true
needs_user_input: false
---
# Migration 0001: baseline (v1 data layout)

## Purpose
Establish data version 1, the layout Atlas 1.0.0 expects. For a brand-new install created by `atlas-setup`, `atlas.yaml: data_version` is already 1 and this migration is skipped; if `data_version` is missing or `null` (treated as 0), it verifies the v1 layout, fills anything missing from `system/templates/`, and sets `data_version: 1`. It never changes existing user content.

## Affected paths
- `user/settings/atlas.yaml` (`data_version`; `installed_version` if missing).
- Missing starter files only: `user/.state/{cursors,jobs,triggers,health}.yaml`, `user/inbox/{approvals,insights,questions}.md`, `user/extensions/registry.yaml`, `user/logs/README.md`.
- Missing folders only: `user/knowledge/<folder>/` for the 13 types and `_index/`, `user/journal/`, `user/work/`, `user/library/`, `user/inbox/drop/`, `user/logs/activity/`, `user/logs/runs/`, `user/extensions/{skills,jobs,triggers,types,dashboards,playbooks}/`, `user/profile/assets/`.

## Transformation
1. If `user/settings/atlas.yaml` does not exist, stop: this is not an installed Atlas; `atlas-setup` creates it. (Not a failure.)
2. If `data_version` is already 1 or higher, stop (no-op).
3. Create each missing folder in Affected paths with a `.gitkeep`.
4. For each missing starter file, copy it from `system/templates/` (mapping in `system/templates/README.md`). Never overwrite an existing file. Do not create settings files other than `atlas.yaml`'s missing keys; setup owns those.
5. If `installed_version` is missing or `null`, set it to `system/VERSION`.
6. Set `data_version: 1`. Commit (`Atlas-Actor: update`, `Atlas-Reason: migration 0001 baseline`).

## Validation
- `user/settings/atlas.yaml` parses and has `data_version: 1`.
- Every folder and starter file listed in Affected paths exists.
- No pre-existing file under `user/` changed except `atlas.yaml` (check with `git diff --stat` against the rollback tag).
- `system/tools/validate.py` reports no new errors.

## Questions for the user
None.

## Reverse step
Not needed (additive). If a rollback ever requires it: set `atlas.yaml: data_version` back to its previous value (`null`); created starter files and folders are left in place, since they are empty and harmless.
