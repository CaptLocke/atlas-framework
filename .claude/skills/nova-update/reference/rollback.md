---
type: skill-reference
skill: nova-update
---
# User-initiated rollback and repair

## Rollback ("go back to the previous version")
Chat only; the user's request plus a one-line confirmation is enough (`updates_major`-level care: say exactly what happens first).

1. **Find the target.** The newest tag `pre-update-<X>` where `<X>` < installed version. That is the version to return to. If none exists (fresh install), say there's no earlier version to go back to.
2. **Explain:** "I'll put Nova's system back to version X. Your knowledge, settings, and anything you've done since the update stay as they are." Mention any feature they'd lose (from the newer CHANGELOG). Wait for yes.
3. **Rollback point for the rollback:** tag the current state `pre-update-<installed>` if that tag doesn't exist (so the newer version can be restored later), push it.
4. **Lock:** write `.nova-tmp/update.lock` (`version_from: <installed>`, `version_to: <X>`).
5. **Reverse migrations first (newest to oldest)**, while the newer migration specs are still present: for each migration applied since `<X>` (ids between X's `data_version` and the current one):
   - `additive: true` → nothing to do (older versions ignore new fields). Leave `data_version` unchanged.
   - `additive: false` → run its **Reverse step**, validate, then set `nova.yaml: data_version` to its `from_data_version`. If a non-additive migration has no reverse step, stop: release the lock, tell the user rollback isn't safe for this release, and offer `nova-report-issue`.
6. **Restore owned paths** from `pre-update-<X>` exactly (add, change, remove), as in `procedure.md` "Forward revert", in one commit (`Nova-Actor: update`, reason "user rollback to X").
7. Set `nova.yaml: installed_version: <X>`. If `data_version` is still higher than X's manifest (additive migrations kept), that is expected; note it in `health.yaml` known issues (severity `low`, status `open` until the next update) so validators and later updates know.
8. Validate, release the lock, push, log (`update · rolled back 1.1.0 → 1.0.0 at user request · commit <sha>`), republish Nova Guide and Control Center.
9. Ask whether to stay on X (pause automatic update checks) or let the next check reinstall the newer version.

## Repair (system files modified outside an update; chat only)
- Triggered by `nova-health` in a chat (owned paths differ from the baseline with changes not made by `Nova-Actor: update` commits). In a routine, health records a known issue and nothing is restored.
- Baseline: `refs/tags/v<installed>` from upstream; before the first real update (or if that tag doesn't exist upstream), `nova.yaml: installed_from_commit`, the template's starting commit, which is already in the repo (no fetch needed). If upstream is unreachable and no `installed_from_commit` exists, ask for the zip of that version.
- First, always: show what changed and offer to keep intentional edits (the user or a helper edited a skill) as a user extension with `nova-extend` (`overrides: <component>`); never silently discard them.
- Then restore from the baseline: take the update lock and make owned paths match it exactly, validate, release the lock, commit (`Nova-Actor: update`, reason "repair: restore system files to 1.0.0"), push.

## Data version ahead of the system
After a rollback over additive migrations, `nova.yaml: data_version` can exceed `manifest.data_version`. Updates then run only migrations with `from_data_version` ≥ the user's value; validators should accept extra optional fields. Never lower `data_version` without running a reverse step.
