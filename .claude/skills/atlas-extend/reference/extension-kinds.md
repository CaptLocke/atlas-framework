---
type: skill-reference
skill: atlas-extend
---
# Extension kinds: layout, required content, wiring

All paths are relative to `user/extensions/` (the registry `path`). Outlines: `system/guide/authoring.md`. Names: lowercase-hyphen, must not equal a system component name unless `overrides` is set to it.

## skill
- **Path:** `skills/<name>/SKILL.md` (+ `skills/<name>/reference/*.md` if long).
- **Content:** the skill outline with frontmatter `name: <name>` (no `atlas-` prefix, to avoid colliding with system skills) and a `description` with trigger phrases.
- **Wiring:** none beyond the registry; the kernel lists registered skills at session start and reads `SKILL.md` on demand.
- **Override example:** `overrides: atlas-status-update` replaces the system skill for this user (warn: they won't get its updates).

## job
- **Path:** `jobs/<name>.md`, the job outline (frontmatter `type: job`, `name`, `model: fast|strongest`, `skills: [...]`), with Away and paused, Readiness check, Early exit, Guardrails, Run report sections.
- **Wiring:** add to a routine's `jobs` list (`{ job: <name>, when: … }` modifiers allowed) in `routines.yaml`, or create a routine (next kind). Set `profile: custom` if a profile routine was edited. A job used only on demand needs no routine.
- **Rules:** idempotent; uses cursors in `user/.state/cursors.yaml` with key `<category>:<connector>:<job name>` for its own incremental reads; outputs to `user/work/<job name>/YYYY-MM-DD.md` or into the brief/dashboards via their existing inputs.

## routine
- **Path:** none (routines live in `user/settings/routines.yaml`); registry `path: null`, `description` says which jobs it runs.
- **Wiring:** add `{ name, schedule, model, routine_id: null, jobs }` to `routines.yaml`; create the platform routine with the thin-pointer prompt in the "Atlas routine" environment (`ATLAS_CONTEXT=routine`; `.claude/skills/atlas-setup/reference/automations.md` §3–§5, including the test run that must report `atlas_context: routine`); store `routine_id`.
- **Rules:** schedule minutes off the hour; at least hourly spacing; mention plan usage impact.

## trigger
- **Path:** `triggers/<name>.md` in the user trigger format of `system/triggers.md` (frontmatter `type: trigger`, `name`, `evaluated_by`, `default`; sections Condition, Key, Action).
- **Wiring:** add `<name>: on` (or `{ enabled: true, <param>: … }`) under `rhythms.yaml: triggers`. Fire-once via `user/.state/triggers.yaml`.
- **Rules:** `evaluated_by` lists existing jobs (and `chat`); the action calls an existing skill or job; actions that would send/share/delete become drafts + approval entries.

## type
- **Path:** `types/<type>.md`, the schema outline (frontmatter `type: schema`, `name: <type>`, `folder: user/knowledge/<folder>/`), plus machine-readable `fields`, `required`, and `enums` (including `status`) in the frontmatter in the same shape as a type entry in `system/schemas/schema.yaml`, so the validator can check records, and `closed_statuses` (the `status` values that mean finished), which the indexes and the Records page use. List the most identifying fields first: Records shows the first three on each card.
- **Wiring:** create `user/knowledge/<folder>/` (with `.gitkeep`), register the type, then run `python3 -I system/tools/index.py` to create its index; other records link to records of the new type under `related` (the common link groups in `schema.yaml` are fixed); ingest and capture classify into the type once registered.
- **Example (fictional):** `types/deal.md` with `folder: user/knowledge/deals/`, fields `account` (ID), `stage` (enum: discovery, proposal, negotiation, closed_won, closed_lost), `value` (number), `close_date` (date); `status` enum `open, won, lost`.

## dashboard
- **Path:** `dashboards/<name>.html` (self-contained template, light/dark, phone width; start from the closest system template's structure) and `dashboards/<name>.contract.md` (dashboard contract outline: `name`, `template`, `republished_by`, `size_budget_kb`; Data, Sources, Rendering notes).
- **Wiring:** `atlas-dashboards` publishes it privately in chat and adds `<name>` to `dashboards.yaml`; add the jobs that should republish it to `republished_by`.

## playbook
- **Path:** `playbooks/<slug>.md`, the runnable procedure (frontmatter `type: playbook-extension`, `name`, `record: "[[playbooks/<slug>]]"`, `automatable: true|false`; sections Purpose, When, Steps, Outputs, Guardrails).
- **Wiring:** create or update the knowledge record `user/knowledge/playbooks/<slug>.md` (playbook schema) so recall finds it, linking to the extension file; if it should run on a schedule or event, also create a job or trigger that runs it.
- **Note:** a playbook record alone already runs as a checklist with pre-drafted messages and missed-step flags (`.claude/skills/atlas-triage/reference/playbooks.md`); no extension needed for that. Use an extension only when a playbook needs work a checklist can't do (pulling data, building a document on a schedule).

## Registry entry (example, fictional)
```yaml
extensions:
  - name: deals
    kind: type
    path: types/deal.md
    overrides: null
    requires_atlas: ">=1.0"
    created: 2026-10-20
    description: "Sales deals with stage, value, and close date."
  - name: pipeline-summary
    kind: job
    path: jobs/pipeline-summary.md
    overrides: null
    requires_atlas: ">=1.0"
    created: 2026-10-20
    description: "Mondays: summarize last week's CRM pipeline changes into the brief."
```
