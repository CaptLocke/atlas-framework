---
type: skill-reference
skill: atlas-update
---
# Update procedure: commands and edge cases

Commands are examples for the cloud session's shell. Use `<up>` for `https://github.com/<manifest.upstream>.git` (e.g. `https://github.com/CaptLocke/atlas-framework.git`). Every commit carries the trailers from `system/rules/sync.md` with `Atlas-Actor: update`.

## Check
```bash
git ls-remote --tags --refs <up> 'v*'          # list release tags
```
Parse `refs/tags/vMAJOR.MINOR.PATCH`; skip tags with a pre-release suffix. Compare semver numerically, not as strings (`1.10.0` > `1.9.0`). If the network can't reach GitHub with git, try the GitHub connector or the releases page via web fetch; if all fail, record `update-check` `last_status: failed` and a low-severity known issue after two consecutive failures.

## Rollback point and lock
```bash
git status --porcelain                          # must be empty (commit user work first)
git pull --rebase
git tag pre-update-1.0.0                        # if it doesn't already exist
git push origin pre-update-1.0.0
mkdir -p .atlas-tmp && printf '%s' '{"by":"atlas-update","version_from":"1.0.0","version_to":"1.1.0","created":"2026-10-18T03:09:00-07:00","expires":"2026-10-18T03:39:00-07:00"}' > .atlas-tmp/update.lock
```
If pushing the tag fails (permissions), stop before changing anything, release the lock, and record a known issue: without a remote rollback point the update doesn't proceed (N13).

## Fetch the release (upstream)
```bash
git fetch --depth=1 --no-tags <up> refs/tags/v1.1.0:refs/atlas-upstream/v1.1.0
```
The fetched history is unrelated to the user's (template copies don't share history); that's expected. The `refs/atlas-upstream/*` refs stay local and are never pushed.

## Replace owned paths
Use the **release's** `owned_paths` (read `system/manifest.yaml` from `refs/atlas-upstream/v1.1.0`; a release may add or remove an owned path). For each path P:
```bash
REL=refs/atlas-upstream/v1.1.0
# files present now but absent in the release → remove
git ls-files -- P | sort > /tmp/now.txt
git ls-tree -r --name-only $REL -- P | sort > /tmp/rel.txt
comm -23 /tmp/now.txt /tmp/rel.txt | xargs -r git rm -q --
# files added or changed in the release → take release version
git checkout $REL -- P          # skip if P doesn't exist in the release
```
A path that was owned before but isn't in the release's list is removed only if it's not under `user/` (never remove user paths). Then:
```bash
git status --porcelain -- user/   # must be empty: abort and restore if not
git add -A -- <owned paths> && git commit -m "atlas(update): Atlas 1.0.0 → 1.1.0: system files" \
  -m "Atlas-Actor: update" -m "Atlas-Reason: apply release v1.1.0" -m "Atlas-Records: -"
```
Hooks allow these writes and removals only while the update lock exists (N5). If a hook blocks something, stop and restore; never work around a hook.

## Migrations
- Pending = files in the **new** `system/migrations/` whose `from_data_version` ≥ the user's `data_version` and `to_data_version` ≤ the manifest's, sorted by `id`.
- For each: read Purpose, Affected paths, Transformation; apply it; run its Validation; set `atlas.yaml: data_version: <to>`; commit with `Atlas-Records` listing changed files. Optional helper scripts in `system/tools/` may be used for bulk mechanical changes (run with `python3 -I`).
- A migration that needs input applies its safe default now and queues its question (kind `migration`).
- A migration must never touch `governance.yaml`, `data-rules.yaml`, or `connectors.yaml` from a routine (hooks block it); if one needs to, it queues a question for the next chat instead.

## Validate
```bash
python3 system/tools/validate.py --all
```
Compare with the result before the update if available: pre-existing problems unrelated to the update are recorded as known issues for `atlas-health`, not treated as an update failure.

## Release the lock and finish
```bash
rm -f .atlas-tmp/update.lock      # .atlas-tmp is git-ignored; removing the lock is not a deletion of user data
git push origin HEAD:main
```

## Forward revert on failure
```bash
OLD=pre-update-1.0.0
# 1) owned paths back to the old release (both lists: old and new owned_paths)
for P in <owned paths>; do
  git ls-files -- P | sort > /tmp/now.txt
  git ls-tree -r --name-only $OLD -- P | sort > /tmp/old.txt
  comm -23 /tmp/now.txt /tmp/old.txt | xargs -r git rm -q --
  git checkout $OLD -- P 2>/dev/null || true
done
# 2) user files changed by this update's commits (Atlas-Actor: update after the tag)
git log $OLD..HEAD --grep='Atlas-Actor: update' --name-only --format= -- user/ | sort -u
# restore each listed file from $OLD (or remove it if it didn't exist at $OLD), then set
# atlas.yaml installed_version / data_version back to their values at $OLD
git commit -m "atlas(update): update to 1.1.0 failed; restored 1.0.0" -m "Atlas-Actor: update" \
  -m "Atlas-Reason: update failed at <step>: <short error>" -m "Atlas-Records: <restored user paths or ->"
```
Only user files changed by update commits are restored; user content created by chats or routines since the tag is kept.

## Zip specifics
```bash
mkdir -p .atlas-tmp/update && mv user/inbox/drop/atlas-1.1.0.zip .atlas-tmp/
python3 -I -m zipfile -e .atlas-tmp/atlas-1.1.0.zip .atlas-tmp/update/
```
Move the zip out of `user/inbox/drop/` before any commit so it never enters the repo.
Verify the top-level entries are a subset of the owned paths, `system/VERSION` matches `system/manifest.yaml: version`, and there's no `user/` entry. Use the extracted tree in place of `$REL` (copy each owned path over, removing files absent from the zip). Afterwards remove `.atlas-tmp/update/` and `.atlas-tmp/atlas-*.zip` (git-ignored transients).
