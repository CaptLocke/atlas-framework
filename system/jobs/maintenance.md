---
type: job
name: maintenance
model: fast
skills: [nova-health]
---
# Job: maintenance

## Purpose
Keep knowledge tidy with no user effort and confirm every automation runs in its routine environment: rebuild all indexes, repair links, merge obvious duplicates, sweep the journal and inbox for leftovers, and expire old approvals and insights.

## Runs when
- Lean and Standard: `upkeep` (Sunday 3:07), first job. Full: `upkeep` (daily 3:07), first job.
- Also run (index rebuild only) by `monthly` when stale.
- Modifiers: `when`. `mode: light` = expiry and sweeps only, no full index rebuild.

## Away and paused
Runs normally during away, except that expiry is paused (step 6). Paused per `system/jobs/README.md`.

## Readiness check
None beyond sync. Maintenance does not read connectors.

## Inputs
- All non-archived records in `user/knowledge/` (frontmatter first; bodies only when repairing).
- `user/inbox/` (approvals, insights, questions, `drop/`), `user/journal/`, `user/.state/cursors.yaml` (`journal`).

## Steps
1. **Validate.** Run `system/tools/validate.py` over `user/` if available; use its findings as the work list.
1a. **Routine environment check** (`nova-health`, the "Routine environment" row of `reference/system-health.md`): read the run reports from the last 8 days in `user/logs/runs/` (this run included) and find any routine run whose `nova_context` isn't `routine` (missing field counts). For each routine affected, add or update the high-severity known issue `routine-env-missing` in `user/.state/health.yaml` naming the routine; close an open one when that routine's runs since the issue opened all show `routine`.
2. **Index rebuild** (`nova-health`, maintenance mode): regenerate every `user/knowledge/_index/` file from the records (`system/schemas/formats.md` §5), including registered user types' folders, `hot.md`, `people-map.md`, and `archive.md`.
3. **Link repair:** fix links that point to a superseded record (point to the successor), to a renamed alias, or to a missing path when the intended target is unambiguous. Ambiguous broken links become a `questions.md` entry.
4. **Obvious dedupes** (`merge_supersede`): same email (people), same domain (organizations), identical commitments from the same source. Follow the merge procedure in `system/rules/knowledge.md`. Anything less than obvious becomes a question, never a merge.
5. **Journal sweep:** journal days with sections not in `processed` are left for the next `ingest` (check that the `journal` cursor will not skip them; move it back if it would). **Inbox sweep:** files lingering in `user/inbox/drop/` and open questions answered in a later chat are noted for ingest or closed.
6. **Expiry:** approvals `pending` for more than 14 days → `expired`; insights `new` for more than 30 days → `expired`. Add a dated status-history line; never delete entries. Away pauses the clock: while away is active (`system/jobs/README.md`), expire nothing; afterwards, extend each item's limit by the number of away days that fell after it was created (count from `away.start` to `away.end`, or to today for an open-ended away). If away has already been cleared, use the away period recorded in the catch-up brief (`user/work/briefs/*-catch-up.md`).
7. Commit (one commit for indexes, one for record fixes, one for inbox).

## Outputs
- Regenerated `user/knowledge/_index/*.md`; repaired and merged records with Updates lines.
- `user/inbox/approvals.md` and `insights.md` status changes; questions for ambiguous cases.

## Early exit
Never fully skipped on its scheduled run (the index rebuild is the safety net). In `light` mode, nothing to expire or sweep → `early_exit`.

## Guardrails
- No deletions: merges supersede, expiries change status, nothing is removed (`destructive` is locked).
- Never edit journal text or user-authored notes (`user_content_edit`).
- Indexes are regenerable; records are not. If a record looks corrupt, leave it and raise a known issue.

## Run report
Row: `maintenance | <status> | <i> indexes, <l> links fixed, <d> merged, <e> expired | validator: <pass/fail count>; routine env: <ok or routines without the marker>`.
