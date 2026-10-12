---
type: migrations-index
version: 1.0.0
---
# Migrations

A migration changes the shape of the user's data (`user/`) when a Nova release needs it. Updates replace only the system-owned paths (`system/manifest.yaml: owned_paths`); `user/` changes **only** through migrations. Each migration is a markdown spec that Claude executes, run by `nova-update` (tactical §13.2–13.3).

## Versions
- `system/manifest.yaml: data_version` is the data format this release expects. `user/settings/nova.yaml: data_version` is the format the user's data is in.
- `data_version` is an integer starting at **1** for Nova 1.0.0. A missing or `null` value in `nova.yaml` is treated as **0** (before the v1 baseline).
- Each migration moves data up by exactly one version (`from_data_version: N`, `to_data_version: N+1`). Several releases may share a data version; a release that doesn't change data shape ships no migration.
- `data_version` is raised only after a migration validates, and lowered only when its reverse step runs.

## Files
- Named `NNNN-<slug>.md`, four-digit, zero-padded, sequential from `0001` with no gaps (`0001-baseline.md`, `0002-…`). `NNNN` equals `to_data_version` padded (`0002` takes data from 1 to 2).
- Follow the migration outline in `system/guide/authoring.md`: frontmatter `type: migration`, `id`, `from_data_version`, `to_data_version`, `additive`, `needs_user_input`; sections Purpose, Affected paths, Transformation, Validation, Questions for the user, Reverse step.
- Optional helper scripts for bulk mechanical changes live in `system/tools/` (Python 3, stdlib + vendored YAML parser) and are named in the Transformation section. Claude runs them, then checks the result.

## Design rules
- **Additive by default.** Prefer new optional fields with defaults defined in the schema specs, so older files stay valid and older Nova versions ignore what they don't know. An additive migration may be a no-op on files (schema-only change) and still bumps `data_version`.
- **Non-additive changes** (renames, splits, moved folders, changed enums) set `additive: false`, must ship a reverse step, and make the release **major**.
- **Never lose content.** Transformations move, rename, or supersede; they never delete user content. Record IDs (paths) never change unless the migration rewrites every link to them in the same commit.
- **Safe defaults.** If a migration needs user input (`needs_user_input: true`), it applies a safe default, writes questions to `user/inbox/questions.md` (kind `migration`), and records which default it used; the answer is applied in a later chat. Needing user input makes the release major.
- **Idempotent.** Re-running a migration on already-migrated data changes nothing.
- **Scoped.** Touch only the paths listed under Affected paths; extensions' folders (`user/extensions/`, user-type knowledge folders) only when the migration says so explicitly.

## How `nova-update` runs migrations
1. After replacing the owned paths (under the update lock, with the rollback tag `pre-update-<old-version>` already created), compare `nova.yaml: data_version` (D) with `manifest.yaml: data_version` (M).
2. If D > M: stop; the release is older than the data (a rollback without reverse steps). Restore and report.
3. For each version from D to M−1, run the migration whose `from_data_version` equals it, in order:
   - Follow its Transformation for every affected file.
   - Run its Validation. If validation fails, stop: restore the owned paths and every migrated user file from the rollback tag with a forward revert commit, release the lock, record a known issue, and report (N13).
   - Set `nova.yaml: data_version` to its `to_data_version` and commit (`Nova-Actor: update`, `Nova-Reason: migration NNNN`).
4. Run full validation (`system/tools/validate.py`: schemas, links, settings, extension registry).
5. Ask any questions at the next chat; until answered, defaults apply.

## Validation (every migration)
- Every affected file parses and passes `system/tools/validate.py` for the new `data_version`.
- Record counts per folder are unchanged unless the migration says otherwise (and then match the stated change).
- No link points to a missing record.
- The migration's own checks (listed in its Validation section) pass.

## Reverse steps and rollback
User-initiated rollback ("go back to the previous version") restores the owned paths from the previous release with a forward revert commit. Additive migrations need nothing more: the older version ignores new fields, and `data_version` stays as it is. Non-additive migrations are undone by running their Reverse step, newest first, each lowering `data_version` by one. User content created since the update is kept.

## Index
| ID | From → to | Additive | Needs input | Summary |
|---|---|---|---|---|
| [0001](0001-baseline.md) | 0 → 1 | yes | no | Baseline: establishes the v1 data layout |
