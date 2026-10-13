---
type: job
name: intelligence
model: strongest
skills: [nova-insights]
---
# Job: intelligence

## Purpose
Look across what changed and what matters (goals, open risks, questions) for risks, gaps, patterns, cross-project connections, and opportunities. Write a small number of well-reasoned insights, each with a one-line reason and its sources, and create Risk, Question, or Idea records where warranted.

## Runs when
- Lean: `nightly-cycle`. Standard: `morning-cycle`. Full: `intelligence` routine (every 3 hours in work hours).
- Modifiers: `when`. `mode: light` limits the look to records changed since the last run (no wider sweep).

## Away and paused
Runs during away; new insights stay `new` in `user/inbox/insights.md` and are summarized in the catch-up brief, not nudged. Paused per `system/jobs/README.md`.

## Readiness check
If `ingest` has not succeeded in the last 24 hours and is not earlier in this routine, proceed and note the staleness in the run report.

## Inputs
- Records and sources created or updated since `jobs.yaml: intelligence.last_success` (from `updated` dates in `hot.md` and the type indexes; sources from `_index/sources.md`, since `hot.md` never lists them).
- Active goals, open risks, open questions, active projects (indexes first, then records as needed per `system/rules/retrieval.md`).
- `user/inbox/insights.md` (to avoid repeats) and engagement signals in `user/.state/health.yaml` (acted/dismissed by kind).
- `rhythms.yaml: insights` (`brief_max`, `engagement`, `suppressed_kinds`).

## Steps
1. Gather the change set. If it is empty, exit early.
2. Invoke `nova-insights` (routine mode) over the change set and its L3 neighborhood: look for risks, gaps (missing owners, dates, decisions without rationale), patterns (repeated themes across sources), connections (same issue in two projects), and opportunities.
3. Score each candidate 0–1 (relevance to goals × urgency × novelty). Drop candidates of a kind listed in `suppressed_kinds` and candidates that repeat an existing `new`, `seen`, or recently `dismissed` insight. Adapt volume to engagement when `engagement: adaptive`.
4. Append surviving insights to `user/inbox/insights.md` (newest first, format `system/schemas/formats.md` §3) with Why, Sources, Links, and a Suggested action.
5. Where an insight is a concrete risk, open question, or idea, create or update the record (`records_write`) and link it from the insight.
6. Commit.

## Outputs
- New entries in `user/inbox/insights.md` (status `new`).
- New or updated records in `user/knowledge/risks/`, `questions/`, `ideas/`, with links and index lines.

## Early exit
No records or sources changed since the last successful run → `early_exit`. No candidate scores high enough → `ok` with "0 new insights" (not an error).

## Guardrails
- Every insight cites at least one source or record; never invent evidence. Inferences are marked `provenance: inferred` on records.
- Insights are suggestions; acting on one (drafting, scheduling, contacting) is left to other jobs or the user.
- Quality over volume: noise erodes trust. The brief shows at most `brief_max`; the rest stay in the inbox.

## Run report
Row: `intelligence | <status> | <N> new insights, <r> records | <top score>`.
