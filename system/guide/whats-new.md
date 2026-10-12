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
- When `nova-update` applies a release, it reads the `### What's new` sections of every version newer than the one previously installed and adds them to the next Daily Brief ("Nova was updated to version 1.1: here's what's new").
- `nova-dashboards` renders this section of the Nova Guide from `CHANGELOG.md`: the installed version (`user/settings/nova.yaml: installed_version`) first, then earlier releases, newest first. Show the latest three releases expanded and older ones collapsed.
- Entries are written for users: plain language, one line each, and what they can now say or do. Any new example requests also belong in `features.md` or `requests.md`.
- If an update asked the user a question (a new setting, for example), the entry says so and points to it.

## Maintainer rules
- Every release adds a `## <version>` section with a `### What's new` list to `CHANGELOG.md`. Technical notes go under a separate `### Under the hood` heading, which is not shown to users.
- Never edit this file to announce a release.
