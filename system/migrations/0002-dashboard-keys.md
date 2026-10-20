---
type: migration
id: "0002"
from_data_version: 1
to_data_version: 2
additive: false
needs_user_input: true
---
# Migration 0002: New Dashboards

## Purpose
Atlas 2.0.0 replaces eleven dashboards with three: **Today** (slug `daily-brief`), **Work** (`commitments`) and **Guide** (`control-center`). Each keeps its existing slug, so its link and `last_published` carry over unchanged. This migration removes the eight retired pages from the user's settings, keeps their links so the user can find and delete the published pages, and points anything else that named a retired page at its replacement. It changes no records: every retired page was a view computed from records, so nothing it showed is lost.

The retired pages and where their content went:

| Retired slug | Now on |
|---|---|
| `projects`, `goals`, `decisions-risks`, `people` | Work |
| `week-ahead` | Today (the week strip and upcoming milestones) |
| `about-you`, `atlas-guide`, `records` | Guide (Records' "recently filed" only; looking a record up is a chat question) |

## Affected paths
- `user/settings/dashboards.yaml`: the eight retired keys are removed; `daily-brief`, `commitments`, `control-center`, `project_pages` and any user-dashboard keys stay as they are.
- `user/inbox/questions.md`: one `action` entry (below), and, only when a user dashboard extends a retired page, one `migration` question.
- `user/.state/health.yaml`: open known issues that name a retired page.
- `user/extensions/registry.yaml` and `user/extensions/dashboards/`: read only, to find user dashboards with `overrides:` set to a retired page. Nothing there is changed.

## Transformation
1. If `atlas.yaml: data_version` is already 2 or higher, stop (no-op).
2. **Keep the links.** Read `user/settings/dashboards.yaml`. For each retired key (`projects`, `goals`, `decisions-risks`, `week-ahead`, `people`, `about-you`, `atlas-guide`, `records`) whose `url` is set, note its display name and `url`. Keys with `url: null` were never published and are not listed.
3. **Queue the action.** Add one open `action` entry to `user/inbox/questions.md` (`system/schemas/formats.md` §questions.md) with `Action key: release-2.0.0-1`, the question set to the 2.0.0 changelog's first `Action needed` line word for word, and `Copy text` listing each noted page as `<display name>: <url>`, one per line. If no retired page was ever published, set the question but leave `Copy text` out. Update the `counts` block. Because the key is already open, `atlas-update` §B step 9 doesn't queue a second copy. If an open entry with that key already exists (a re-run), leave it as it is.
4. **Remove the keys.** Delete the eight retired keys from `dashboards.yaml`. Leave every other key, comment and value unchanged.
5. **Known issues.** In `user/.state/health.yaml`, close any open known issue that is only about a retired page, for example a failed republish of the People page (`status: resolved`, `summary` noting "page retired in 2.0.0"). One that is about the underlying data, such as a disconnected source, stays open.
6. **User dashboards that extend a retired page.** For each entry in `user/extensions/registry.yaml` with `kind: dashboard` and `overrides:` naming a retired slug, apply the safe default: the user's dashboard keeps working as a standalone page under its own key, and `overrides:` is left as it is; `atlas-health` reports the dangling override as low. Then queue one `migration` question: "Your <name> page replaced the <retired page>, which Atlas no longer has. Keep it as a page of its own, or remove it?" When no such extension exists, ask nothing.
7. Set `atlas.yaml: data_version: 2`. Commit (`Atlas-Actor: update`, `Atlas-Reason: migration 0002`, `Atlas-Records:` listing the changed paths).

## Validation
- `dashboards.yaml` parses, holds none of the eight retired keys, and still holds `daily-brief`, `commitments` and `control-center` with the `url` and `last_published` they had before (compare with the update lock's `base_commit`).
- `questions.md` holds exactly one open entry with `Action key: release-2.0.0-1`, whose `Copy text` names every retired page that had a `url`, and only those.
- No file under `user/knowledge/` changed (`git diff --stat` against `base_commit`).
- `system/tools/validate.py` reports no new errors.

## Questions for the user
Only when a user dashboard extends a retired page: keep it as a standalone page (the default) or remove it. Removing a published page is `destructive` and is done in a chat with the user's OK (`atlas-dashboards` §Project pages and user dashboards).

## Reverse step
Run before the system files go back to 1.x (`atlas-update/reference/rollback.md` step 4):
1. Re-add the eight retired keys to `dashboards.yaml`. Set each `url` from the `Copy text` of the `release-2.0.0-1` action entry where the page is listed, otherwise `null`; set every `last_published: null`, so the next routine or chat republishes them.
2. Mark the `release-2.0.0-1` action entry `dismissed` (`- **Done:** <date> · rolled back to <version>`), since the old pages are live again, and update the `counts` block. Leave any `migration` question from step 6 as it is.
3. Known issues closed by step 5 stay closed.
4. Set `atlas.yaml: data_version: 1`.
