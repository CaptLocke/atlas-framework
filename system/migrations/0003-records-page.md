---
type: migration
id: "0003"
from_data_version: 2
to_data_version: 3
additive: false
needs_user_input: false
---
# Migration 0003: Records page, project pages retired

## Purpose
Atlas 3.0.0 adds **Records** (slug `records`): every record Atlas keeps and how they link, as a web you can zoom into. It retires **project pages**: one project in depth is now Records zoomed to that project, or Work's Projects tab. A project page's update history and sources become chat questions.

Removing `project_pages` from `dashboards.yaml` is a non-additive change, so 3.0.0 is a major release. The published project pages themselves are not deleted: they stop updating, and the user can delete them in Claude (deleting is `destructive`, never done by a migration).

## Affected paths
- `user/settings/dashboards.yaml`: `project_pages` is removed; `records: { url: null, last_published: null }` is added under `dashboards`. Every other key, comment and value stays.
- `user/inbox/questions.md`: one `action` entry (always; its text depends on whether there were links).
- `user/.state/health.yaml`: open known issues that are only about a project page.
- Each live project page's `requests` (through `ArtifactData`, before its link goes): worked as `atlas-dashboards` `reference/live.md` §5 says, so no press made there is lost.
- `user/extensions/registry.yaml`: read only, to find a user dashboard with `overrides: project-page`. Nothing there is changed.

## Transformation
1. If `atlas.yaml: data_version` is already 3 or higher, stop (no-op).
2. **Keep the links.** Read `user/settings/dashboards.yaml`. For each `project_pages` entry, note the project ID (the key), the project's title (its record's, or the ID when there's none), the link (the value when it's a plain link, or its `url`), and whether it was live.
3. **Work the live pages' queues.** For each entry that was live, work its `requests` now (`live.md` §5, in this context: a routine leaves what it can't do for a chat as usual). A press still `queued` or `needs_chat` afterwards is named in the action entry's `How` ("Your Enterprise launch page had a Mark done waiting: say it in chat if you still want it"). This needs the page reachable; if it isn't, say so in the action entry the same way and carry on.
4. **Queue the action.** If an open entry with `Action key: release-3.0.0-1` already exists, leave it. Otherwise add one open `action` entry to `user/inbox/questions.md` (`system/schemas/formats.md` §questions.md) with that key and the question set to the 3.0.0 changelog's first `Action needed` line word for word. **With links:** `How:` "In Claude, open each page below and delete it, or keep it as a snapshot: none of them update any more." plus any line from step 3, and `Copy text` with one line per page: `<title> [<project ID>] <link>`, with ` (live)` after a live one. **Without links:** `How:` "You had no project pages, so there's nothing to delete: tell Atlas it's done." Update the `counts` block.
5. **User dashboards that replaced a project page.** For a registry entry with `kind: dashboard` and `overrides: project-page`, change nothing: it no longer replaces anything and keeps working as a page of its own. Add one line to the action entry's `How` naming it.
6. **Change the keys.** Delete `project_pages` from `dashboards.yaml`. Add `records: { url: null, last_published: null }` under `dashboards` if it isn't there. Leave everything else unchanged.
7. **Known issues.** In `user/.state/health.yaml`, close any open known issue that is only about a project page (`status: resolved`, `summary` noting "project pages retired in 3.0.0").
8. Set `atlas.yaml: data_version: 3`. Commit (`Atlas-Actor: update`, `Atlas-Reason: migration 0003`, `Atlas-Records:` listing the changed paths).
9. **Publish Records** at the next chat (`atlas-dashboards` §Publish: published, then switched over to live in the same chat), with one line telling the user what it is. A routine leaves it for the chat, without a known issue.

## Validation
- `dashboards.yaml` parses, has no `project_pages`, has `records` under `dashboards`, and still holds every other key with the `url`, `last_published` and `live` it had before (compare with the update lock's `base_commit`).
- `questions.md` holds exactly one open entry with `Action key: release-3.0.0-1`; when `project_pages` had links, its `Copy text` names every one of them, with its project ID, and only those.
- No file under `user/knowledge/` changed (`git diff --stat` against `base_commit`).
- `system/tools/validate.py` reports no new errors.

## Questions for the user
None. The action entry asks the user to delete the old pages if they want; keeping them changes nothing.

## Reverse step
Run before the system files go back to 2.x (`atlas-update/reference/rollback.md` step 4):
1. Re-add `project_pages` to `dashboards.yaml` from the `release-3.0.0-1` action entry's `Copy text` (in `user/inbox/questions.md`, or in `user/inbox/archive/` once closed): each line's `[<project ID>]` as the key and its link as the value, or `{ url: <link>, live: true }` for a line marked `(live)`. A page the user has deleted since then can't come back, so leave its line out if the user says so. With no links, add `project_pages: {}`.
2. Remove `records` from `dashboards` (its published page, if any, stays; 2.x doesn't know it).
3. If the action entry is still open, mark it `dismissed` (`- **Done:** <date> · rolled back to <version>`) and update the `counts` block.
4. Set `atlas.yaml: data_version: 2`.
