# Releasing Atlas (maintainer checklist)

This file lives on the `maintainers` branch, not `main`, so it never ships to users (a repo created from the template copies only `main`). Get it, and the regression suite, into a checkout of `main` with:
```bash
git fetch origin maintainers && git checkout origin/maintainers -- docs/maintainers system/tests/regression
```
and don't commit them to `main`; `git restore --staged docs/maintainers system/tests/regression && rm -rf docs/maintainers system/tests/regression` removes them again.

This is the one place that says how an Atlas release is made. Other files (`system/tools/build-zip.md`, `system/tests/README.md`, `system/guide/whats-new.md`, `system/templates/bootstrap-stub.md`) point here instead of repeating steps. Work in the upstream repo (`CaptLocke/atlas-framework`), on a branch, through a pull request.

## Before 1.0.0 ships
- Atlas is still at **1.0.0**. Do not create any release tags (`v*`) until 1.0.0 is released: `update-check` installs whatever the highest tag is.
- Every change goes straight under `## 1.0.0` in `CHANGELOG.md`. There is no `## Unreleased` section yet.
- Testing is end to end: create a fresh repo from the template (e.g. `atlas-test` on the test account) and set it up. No update channel or pre-release tags are needed.

## While working (every pull request)
1. **Changelog.** Add lines to the version being built (`## 1.0.0` now; `## Unreleased` after 1.0.0 ships):
   - `### What's new`: one plain line per change the user will notice, written as what they can now say or do.
   - `### Action needed`: one plain line per thing **only the user can do** (Atlas can't do it for them), e.g. "Update your Atlas Project's instructions." Leave the heading out if there's nothing. `atlas-update` turns each line into a "Needs you" item that stays until it's done (see below).
   - `### Under the hood`: maintainer notes. Not shown to users.
2. **Bootstrap stub.** If the Project-instructions text in `system/templates/bootstrap-stub.md` changes, raise `bootstrap_version` in `system/manifest.yaml` and the `Atlas bootstrap <N>` marker in the stub and in `docs/setup/04-create-the-atlas-project.md`. That alone tells every user to update their instructions (no `Action needed` line required for it).
3. **Kernel.** If `system/kernel.md` changes in a way old Project instructions or sessions must notice, raise `kernel_version` in the manifest and the `atlas-kernel-<N>` marker in the kernel.
4. **Data shape.** If anything under `user/` must change shape, add a migration (`system/migrations/README.md`) and raise `manifest.yaml: data_version`. Non-additive or needs-input migrations make the release major.
5. **Dashboards.** If a template's shared code changed, run `python3 system/tests/dashboards/render.py --sync`.
6. **Checks** (all must pass):
   ```bash
   python3 system/tools/validate.py --all
   python3 -m unittest discover -s system/tests -t system/tests
   python3 system/tests/dashboards/render.py --check
   ```

## Cutting a release
1. **Pick the version** by semver against the last release: patch (fixes only), minor (additive), major (needs user input, non-additive migration, or breaking for extensions). Patch and minor install automatically by default; major waits for the user's yes.
2. **Set it** in `system/VERSION` and `system/manifest.yaml: version` (they must match).
3. **Changelog:** rename `## Unreleased` to `## <version> (YYYY-MM-DD)`; check every user-visible change has a What's new line and every user step has an Action needed line.
4. **Checks:** run the three commands above. The validator also confirms the changelog has a section for the version.
5. **Merge** the release pull request to `main`.
6. **Tag** the merge commit and push the tag: `git tag v<version> && git push origin v<version>`. This is what makes the release visible to every user's `update-check`. Never move or delete a pushed tag.
7. **Zip:** build `atlas-<version>.zip` (`system/tools/build-zip.md`) and attach it to a GitHub release for the tag, with the What's new and Action needed lines as the release notes.
8. **Confirm** on a test repo created from the previous release: say "update Atlas" in a chat and check that the update installs, What's new shows in the Atlas Guide, and any Action needed items appear in "Needs you".

## How user actions reach the user
- When `atlas-update` installs a release, it adds one open `action` entry to `user/inbox/questions.md` for each `Action needed` line in every installed release, and one for the Project instructions when `bootstrap_version` went up.
- The very next Daily Brief shows them at the top, under "Action needed", even when the update ran overnight. The Control Center lists them with any text to copy. In a chat, Atlas raises them at once and mentions them again, in one line, in later chats.
- An entry closes when it's done: Atlas sees it (current Project instructions are confirmed by the boot check, which also sets `atlas.yaml: bootstrap_confirmed`) or the user says it's done.
