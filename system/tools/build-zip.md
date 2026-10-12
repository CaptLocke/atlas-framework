---
type: tool-spec
name: build-zip
---
# Building a release zip

A release zip is the zip-delivery alternative to fetching from the upstream repo.

**Contents:** exactly the paths in `system/manifest.yaml: owned_paths`, taken from the release tag. Never anything under `user/`, never `.nova-tmp/`.

**Name:** `nova-<version>.zip` (e.g. `nova-1.0.0.zip`), attached to the GitHub release for that tag.

**Steps (maintainer, or Claude in the upstream repo):**
1. Check out the release tag.
2. Run `python3 system/tools/validate.py --system` and the tests in `system/tests/` (all must pass).
3. Create the zip from the owned paths only, preserving folder structure from the repo root.
4. Verify: unzip into an empty folder and confirm no `user/` path exists and `system/VERSION` matches the tag.
5. Attach to the GitHub release.

**Applying a zip:** the user attaches it in a Nova chat and says "update Nova from this"; `nova-update` applies it with the same procedure as an upstream update (tactical §13.2).
