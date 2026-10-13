---
type: tool-spec
name: build-zip
---
# Building a release zip

A release zip is the zip-delivery alternative to fetching from the upstream repo. When to build one, and every other release step, is in `docs/maintainers/releasing.md`; this file covers only the zip itself.

**Contents:** exactly the paths in `system/manifest.yaml: owned_paths`, taken from the release tag. Never anything under `user/`, never `.nova-tmp/`.

**Name:** `nova-<version>.zip` (e.g. `nova-1.1.0.zip`), attached to the GitHub release for that tag.

**Build (from the release tag, after the checks in the release checklist pass):**
1. Create the zip from the owned paths only, preserving folder structure from the repo root.
2. Verify: unzip into an empty folder and confirm no `user/` path exists and `system/VERSION` matches the tag.

**Applying a zip:** the user attaches it in a Nova chat and says "update Nova from this"; `nova-update` applies it with the same procedure as an upstream update (tactical §13.2).
