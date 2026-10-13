---
type: guide
section: whats-new
title: What's new
order: 6
version: 1.0.0
generated_from: CHANGELOG.md
---
# What's new

This section is **generated, not written here.** Its content comes from the `### What's new` part of each release in `CHANGELOG.md` at the repository root.

## How it's produced
- When `atlas-update` applies a release, it reads the `### What's new` sections of every version newer than the one previously installed and adds them to the next Daily Brief ("Atlas was updated to version 1.1: here's what's new").
- `atlas-dashboards` renders this section of the Atlas Guide from `CHANGELOG.md`: the installed version (`user/settings/atlas.yaml: installed_version`) first, then earlier releases, newest first. Show the latest three releases expanded and older ones collapsed.
- Entries are written for users: plain language, one line each, and what they can now say or do. Any new example requests also belong in `features.md` or `requests.md`.
- If an update asked the user a question (a new setting, for example), the entry says so and points to it.
- Anything only the user can do (update their Project instructions, for example) is not left to this section: it comes from the release's `### Action needed` list (and from a higher `bootstrap_version`) and `atlas-update` turns each item into an open `action` entry in `user/inbox/questions.md`, shown at the top of the next Daily Brief and in the Control Center until it's done.

## Maintainer rules
- How to write the changelog and cut a release: `docs/maintainers/releasing.md` (the release checklist).
- Never edit this file to announce a release.
