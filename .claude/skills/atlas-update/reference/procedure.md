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

## Verify the signature
```bash
python3 -I system/tools/release_check.py verify refs/atlas-upstream/v1.1.0 v1.1.0
```
It checks, with the installed `release_check.py` and the release keys inside it, that the tag is named `v1.1.0` and signed by Atlas's maker; it prints the release commit. If it fails, stop before changing anything: release the lock, delete the fetched ref (`git update-ref -d refs/atlas-upstream/v1.1.0`), record `update-check` as failed, and add a high-severity known issue `update-signature-failed` naming the version ("Atlas skipped an update that wasn't signed by its maker"). Never install an unverified release. (Installs from before 1.0.1 have no `release_check.py`; their first update to 1.0.1 or later brings it.)

## Replace owned paths
Use the **release's** `owned_paths` (read `system/manifest.yaml` from `refs/atlas-upstream/v1.1.0`; a release may add or remove an owned path). Write refs and paths out in full in each command, and run each line below as its own command: the hooks don't expand shell variables or `xargs`, and they read the removal list from its file, so the file must exist before `git rm` runs. In a routine they also accept only the release named in the lock's `version_to`. For each path P, in the order the release lists them (later paths can depend on earlier ones, such as new hooks):
```bash
# files present now but absent in the release → remove
git ls-files -- P | sort > /tmp/now.txt
git ls-tree -r --name-only refs/atlas-upstream/v1.1.0 -- P | sort > /tmp/rel.txt
comm -23 /tmp/now.txt /tmp/rel.txt > /tmp/gone.txt
git rm -q --pathspec-from-file=/tmp/gone.txt      # skip if /tmp/gone.txt is empty
# files added or changed in the release → take release version
git checkout refs/atlas-upstream/v1.1.0 -- P      # skip if P doesn't exist in the release
```
A path that was owned before but isn't in the release's list is removed only if it's not under `user/` (never remove user paths). Then:
```bash
git status --porcelain -- user/   # must be empty: abort and restore if not
git add -A -- <owned paths> && git commit -m "atlas(update): Atlas 1.0.0 → 1.1.0: system files" \
  -m "Atlas-Actor: update" -m "Atlas-Reason: apply release v1.1.0" -m "Atlas-Records: -"
```
Hooks allow these git checkouts and removals only while the update lock exists, and only from the signed release (in a chat also from a commit already in this repo's history; N5). In a routine the commit itself must match the release exactly for every owned path, and the release must not be older than the installed version. Any other way of writing owned paths is blocked. If a hook blocks something, stop and undo (below); never work around a hook.

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

## Undo on failure
Nothing from the update has been pushed until the final push, so a failure at any earlier step is undone by resetting to `origin/main` while the lock is still valid (the hooks allow this reset only under a valid update lock):
```bash
git reset --hard origin/main      # owned paths and user files back exactly as they were before the update
rm -f .atlas-tmp/update.lock
```
Then record the failure (`update-check` `last_status: failed`, a known issue with the step and a short error) and push that. If anything from the update did reach `origin`, don't try to restore from a routine: record a high-severity known issue `update-incomplete`; the next chat restores the previous version with the rollback procedure (`rollback.md`).
