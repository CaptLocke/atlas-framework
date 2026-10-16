---
type: schema
name: _common
applies_to: every record in user/knowledge/
---
# Schema: common record fields

Every knowledge record is one markdown file at `user/knowledge/<folder>/<slug>.md`. Machine-readable field lists and enums live in `system/schemas/schema.yaml`; this file explains them.

## Identity
- **ID** = `<folder>/<slug>`, the file path under `user/knowledge/` without `.md` (e.g. `people/dana-ruiz`). The frontmatter `id` must equal the path.
- **Slug:** lowercase, words joined by `-`, ASCII only. People: `first-last` (add a disambiguator if needed: `dana-ruiz-acme`). Dated things (decisions, events, sources): `YYYY-MM-DD-short-title`.
- **Paths never change** once created. Renaming a person changes `title` and adds the old name to `aliases`, never the file name.
- **Links** use the ID in wiki form: `[[people/dana-ruiz]]`. Links in the body and in frontmatter use the same form.

## Fields
| Field | Required | Notes |
|---|---|---|
| `id` | yes | Equals the path. |
| `type` | yes | One of the 13 types or a registered user type. |
| `title` | yes | Human name of the thing. |
| `summary` | yes | One sentence; what someone needs to know at a glance. Used in indexes. |
| `status` | yes | Type-specific vocabulary (see each schema). |
| `created`, `updated` | yes | `YYYY-MM-DD`. `updated` changes on every meaningful edit. |
| `aliases` | no | Other names, emails, handles, abbreviations. Used for dedupe and search. |
| `links` | no | Map of link group → list of IDs. Groups: `people, organizations, projects, goals, commitments, decisions, events, risks, questions, ideas, topics, playbooks, related`. |
| `sources` | no* | List of source IDs this record's facts came from. *Required unless the user stated the fact directly in chat or journal (then link the journal source or set `provenance: stated`). |
| `supersedes` / `superseded_by` | no | IDs. Set when one record replaces another. |
| `provenance` | no | `stated` (user said it), `observed` (seen in a source), `researched` (web), `inferred` (Claude's conclusion). Default `observed`. If a key field (a person's role or title, an owner, a date) is your inference rather than something a source states, use `inferred` and say in the body what was inferred and from what. |
| `sensitivity` | no | Data-rule category the content falls under; default `normal`. |
| `archived` | no | `true` removes the record from default indexes (kept in `_index/archive.md`). Fully reversible. |

## Body
```markdown
<Free-form description and current state, written to be useful on its own.>

## Updates
- 2026-10-12: <what changed and why> ([[sources/2026-10-12-...]])
```
- The **Updates** section is append-only and newest last. Never delete history from it.
- Keep the top description current; move superseded facts into Updates rather than deleting them.

## Lifecycle
- **Create** only after checking indexes and aliases for an existing match (`system/rules/knowledge.md`).
- **Update** by editing fields, refreshing `updated`, and appending to Updates.
- **Supersede** when a record is replaced wholesale: new record sets `supersedes`, old sets `superseded_by` and keeps its content.
- **Archive** with `archived: true`.
- **Forget / purge** only through `atlas-memory` with approval (`system/rules/knowledge.md`).

## Minimal valid example
```markdown
---
id: decisions/2026-10-12-enterprise-tier-pricing
type: decision
title: Enterprise tier priced per seat
summary: Chose per-seat pricing for enterprise to match buyer procurement norms.
status: made
created: 2026-10-12
updated: 2026-10-12
aliases: []
links:
  projects: ["[[projects/enterprise-launch]]"]
  people: ["[[people/maya-chen]]"]
sources: ["[[sources/2026-10-12-pricing-sync]]"]
provenance: observed
decided_on: 2026-10-12
deciders: ["[[people/maya-chen]]"]
rationale: Buyers budget per seat; per-workspace pricing stalled two deals.
---
Enterprise pricing will be per seat with a 25-seat minimum.

## Updates
- 2026-10-12: Decided in pricing sync ([[sources/2026-10-12-pricing-sync]]).
```
