# Releasing Atlas (maintainer checklist)

This file lives on the `maintainers` branch, not `main`, so it never ships to users (a repo created from the template copies only `main`). Get it, and the test suites, into a checkout of `main` with:
```bash
git fetch origin maintainers && git checkout origin/maintainers -- docs/maintainers system/tests
```
and don't commit them to `main`; `git restore --staged docs/maintainers system/tests && rm -rf docs/maintainers system/tests` removes them again.

This is the one place that says how an Atlas release is made. Other files (`system/tools/build-zip.md`, `system/tests/README.md`, `system/guide/whats-new.md`, `system/templates/bootstrap-stub.md`) point here instead of repeating steps. Work in the upstream repo (`CaptLocke/atlas-framework`), on a branch, through a pull request.

## Versions and testing
- `v1.0.0` is the first tag. Every change after it goes under `## Unreleased` in `CHANGELOG.md` until the next release.
- **Test a release before tagging it** with a signed pre-release tag on the release branch's last commit (`v1.0.1-rc.1`, then `-rc.2`, …). In a chat on the test account's Atlas, say "update to v1.0.1-rc.1". Atlas never installs pre-releases on its own, so users don't see them.
- New installs are tested end to end too: create a fresh repo from the template on the test account and set it up.

## While working (every pull request)
1. **Changelog.** Add lines to the version being built (`## 1.0.0` now; `## Unreleased` after 1.0.0 ships):
   - `### What's new`: one plain line per change the user will notice, written as what they can now say or do.
   - `### Action needed`: one plain line per thing **only the user can do** (Atlas can't do it for them), e.g. "Update your Atlas Project's instructions." Leave the heading out if there's nothing. `atlas-update` turns each line into a "Needs you" item that stays until it's done (see below).
   - Maintainer notes go in `docs/maintainers/under-the-hood.md` on this branch (since 1.1.0), not in `CHANGELOG.md`, so users' copies stay short. Add them in the companion pull request to `maintainers`.
2. **Bootstrap stub.** If the Project-instructions text in `system/templates/bootstrap-stub.md` changes, raise `bootstrap_version` in `system/manifest.yaml` and the `Atlas bootstrap <N>` marker in the stub and in `docs/setup/04-create-the-atlas-project.md`. That alone tells every user to update their instructions (no `Action needed` line required for it).
3. **Kernel.** If `system/kernel.md` changes in a way old Project instructions or sessions must notice, raise `kernel_version` in the manifest and the `atlas-kernel-<N>` marker in the kernel.
4. **Data shape.** If anything under `user/` must change shape, add a migration (`system/migrations/README.md`) and raise `manifest.yaml: data_version`. Non-additive or needs-input migrations make the release major.
5. **Dashboards.** `_base.css` and `_base.js` are the only copies of the shared page code (since 1.1.0 `render.py` puts them into each page), so there's nothing to sync. `render.py --check` confirms every template still holds the base placeholders.
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
   Then run the **regression suite** on the release candidate (`system/tests/regression/README.md`, from this branch) and fill in its scorecard. A release needs two passing runs; the README's "Pass criteria" and "Releasing: two runs, and when to stop" set the bar and when to stop rerunning.
5. **Merge** the release pull request to `main`.
6. **Tag** the merge commit, signed, on your own machine (the signing key never leaves it). Claude prepares everything up to this step and hands you the command:
   ```bash
   git fetch origin && git checkout origin/main
   git tag -s v<version> -m "Atlas <version>"
   git verify-tag v<version> && git push origin v<version>
   ```
   This is what makes the release visible to every user's `update-check`. Never move or delete a pushed tag. Never push an unsigned `v*` tag: from 1.0.1, Atlas refuses releases it can't verify.
7. **Zip:** none. The zip update path is removed in 1.0.1, so releases ship as signed tags only.
8. **Confirm** on a test repo created from the previous release (no previous release exists for 1.0.0; the first check is 1.0.0 → 1.0.1): say "update Atlas" in a chat and check that the update installs, What's new shows in the Atlas Guide, and any Action needed items appear in "Needs you".

## How user actions reach the user
- When `atlas-update` installs a release, it adds one open `action` entry to `user/inbox/questions.md` for each `Action needed` line in every installed release, and one for the Project instructions when `bootstrap_version` went up.
- The very next Daily Brief shows them at the top, under "Action needed", even when the update ran overnight. The Control Center lists them with any text to copy. In a chat, Atlas raises them at once and mentions them again, in one line, in later chats.
- An entry closes when it's done: Atlas sees it (current Project instructions are confirmed by the boot check, which also sets `atlas.yaml: bootstrap_confirmed`) or the user says it's done.

## Signing key (one-time setup)
Releases are signed with an SSH key that lives only on your machine. A backup key is kept offline so a lost or broken key never strands users.
1. **Create the key.** With a hardware security key: `ssh-keygen -t ed25519-sk -C "atlas-release" -f ~/.ssh/atlas_release`. Without one (or if your `ssh-keygen` refuses `-sk`): `ssh-keygen -t ed25519 -C "atlas-release" -f ~/.ssh/atlas_release`, and set a strong passphrase.
2. **Tell git to use it:**
   ```bash
   git config --global gpg.format ssh
   git config --global user.signingkey ~/.ssh/atlas_release.pub
   ```
3. **Let git verify your own tags:**
   ```bash
   mkdir -p ~/.config/git
   echo "$(git config user.email) $(cat ~/.ssh/atlas_release.pub)" >> ~/.config/git/allowed_signers
   git config --global gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers
   ```
4. **Create the backup key** the same way (`-f ~/.ssh/atlas_release_backup`) and add its `.pub` line to `allowed_signers` as in step 3. Keep `atlas_release_backup.pub`, but move the private file (`atlas_release_backup`, no extension) somewhere offline, such as a password manager or a USB drive, and delete it from the machine. It's used only to replace the main key.
5. **Add both public keys to GitHub** as *signing* keys (your account's SSH and GPG keys settings), so GitHub shows Atlas tags as Verified.
6. **From 1.0.1**, both public keys ship in `SIGNERS` inside `system/tools/release_check.py`, and every Atlas checks each update against them before installing it (`atlas-update` runs `release_check.py verify`; the paths hook refuses unverified release refs). Replacing a key means a release, signed by a key users already trust, that updates `SIGNERS`.
