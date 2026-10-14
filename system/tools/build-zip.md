---
type: tool-spec
name: build-zip
---
# Building a release zip

A release zip is the zip-delivery alternative to fetching from the upstream repo. When to build one, and every other release step, is in the release checklist, `docs/maintainers/releasing.md` on the upstream repo's `maintainers` branch; this file covers only the zip itself.

**Contents:** exactly the paths in `system/manifest.yaml: owned_paths`, taken from the release tag. Never anything under `user/`, never `.atlas-tmp/`.

**Name:** `atlas-<version>.zip` (e.g. `atlas-1.1.0.zip`), attached to the GitHub release for that tag.

**Build (from the release tag, after the checks in the release checklist pass):**
1. Create the zip from the owned paths only, preserving folder structure from the repo root.
2. Verify: unzip into an empty folder and confirm no `user/` path exists and `system/VERSION` matches the tag.

**Applying a zip:** the user attaches it in an Atlas chat and says "update Atlas from this"; `atlas-update` applies it with the same procedure as an upstream update (`atlas-update` §D).
