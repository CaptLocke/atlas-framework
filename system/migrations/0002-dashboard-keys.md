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
Atlas 2.0.0 replaces eleven dashboards with three: **Today** (slug `daily-brief`), **Work** (`commitments`) and **Guide** (`control-center`). Each keeps its existing slug, so its link and `last_published` carry over unchanged. This migration removes the eight retired pages from the user's settings, keeps their links so the user can find and delete the published pages, closes known issues that were only about a retired page, and asks about any user dashboard that replaced a page that is retired or changed. It changes no records: every retired page was a view computed from records, so nothing it showed is lost.

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
- `user/extensions/registry.yaml` and `user/extensions/dashboards/`: read only, to find user dashboards with `overrides:` set to any of the eleven old slugs. Nothing there is changed.
- Inbox entries and other text that mention an old page by name are left as they are: pages that link a retired page show its name as plain text, so nothing breaks.

## Transformation
1. If `atlas.yaml: data_version` is already 2 or higher, stop (no-op).
2. **Keep the links.** Read `user/settings/dashboards.yaml`. For each retired key (`projects`, `goals`, `decisions-risks`, `week-ahead`, `people`, `about-you`, `atlas-guide`, `records`) whose `url` is set, note its display name and `url`. Keys with `url: null` were never published and are not listed.
3. **Queue the action.** Add one open `action` entry to `user/inbox/questions.md` (`system/schemas/formats.md` §questions.md) with `Action key: release-2.0.0-1`, the question set to the 2.0.0 changelog's first `Action needed` line word for word, and `Copy text` listing each noted page as `<display name> (<slug>): <url>`, one per line; display names are Projects, Goals, Decisions & Risks, Week Ahead, People, About You, Atlas Guide and Records. If no retired page was ever published, leave `Copy text` out and set `How` to "None of the old pages were ever published, so there's nothing to delete: tell Atlas it's done." Update the `counts` block. Because the key is already open, `atlas-update` §B step 9 doesn't queue a second copy. If an open entry with that key already exists (a re-run), leave it as it is.
4. **Remove the keys.** Delete the eight retired keys from `dashboards.yaml`. Leave every other key, comment and value unchanged.
5. **Known issues.** In `user/.state/health.yaml`, close any open known issue that is only about a retired page, for example a failed republish of the People page (`status: resolved`, `summary` noting "page retired in 2.0.0"). One that is about the underlying data, such as a disconnected source, stays open.
6. **User dashboards that replaced a page.** For each entry in `user/extensions/registry.yaml` with `kind: dashboard` and `overrides:` naming one of the eleven old slugs, apply the safe default, which keeps the user's page working as it is: `overrides:` is left unchanged, and `atlas-health` reports a dangling override as low. Then queue one `migration` question per entry:
   - **Overriding a retired page:** "Your <name> page replaced the <retired page>, which Atlas no longer has. Keep it as a page of its own, or remove it?"
   - **Overriding `daily-brief`, `commitments` or `control-center`:** "Your <name> page replaces Atlas's <Today, Work or Guide> page, which now also shows <what that page took over>. Keep yours, or switch back to Atlas's?" Its contract was written for the old page's data, so `atlas-health` checks it against the new contract.
   When no such extension exists, ask nothing.
7. Set `atlas.yaml: data_version: 2`. Commit (`Atlas-Actor: update`, `Atlas-Reason: migration 0002`, `Atlas-Records:` listing the changed paths).

## Validation
- `dashboards.yaml` parses, holds none of the eight retired keys, and still holds `daily-brief`, `commitments` and `control-center` with the `url` and `last_published` they had before (compare with the update lock's `base_commit`).
- `questions.md` holds exactly one open entry with `Action key: release-2.0.0-1`, whose `Copy text` names every retired page that had a `url`, and only those.
- No file under `user/knowledge/` changed (`git diff --stat` against `base_commit`).
- `system/tools/validate.py` reports no new errors.

## Questions for the user
Only when a user dashboard replaced one of the old pages: keep it (the default) or remove it, or for Today, Work or Guide, switch back to Atlas's page. Removing a published page is `destructive` and is done in a chat with the user's OK (`atlas-dashboards` §Project pages and user dashboards).

## Reverse step
Run before the system files go back to 1.x (`atlas-update/reference/rollback.md` step 4):
1. Re-add the eight retired keys to `dashboards.yaml`, with every `last_published: null` so the next routine or chat republishes them. For each `url`, find the `release-2.0.0-1` action entry in `user/inbox/questions.md`, or in `user/inbox/archive/` once maintenance has moved it there, and match the page by the slug in brackets in its `Copy text`. If the entry is `answered` (the user deleted the old pages), or the page isn't listed, or no entry is found, set `url: null`: a deleted page can't be republished, so a chat publishes it fresh and saves the new link.
2. If that entry is still open, mark it `dismissed` (`- **Done:** <date> · rolled back to <version>`), since the old pages are live again, and update the `counts` block. Leave any `migration` question from step 6 as it is.
3. Known issues closed by step 5 stay closed.
4. Set `atlas.yaml: data_version: 1`.
