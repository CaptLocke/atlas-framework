---
type: job
name: intelligence
model: strongest
skills: [atlas-insights]
---
# Job: intelligence

## Purpose
Look across what changed and what matters (goals, open risks, questions) for risks, gaps, patterns, cross-project connections, collisions ahead, decisions whose reason no longer holds, and opportunities. Once a week, also look at what *didn't* change: the blind spots, and the relationships between records nothing links yet. Write a small number of well-reasoned insights, each with a one-line reason and its sources, and create Risk, Question, or Idea records where warranted.

## Runs when
- Lean: `nightly-cycle`. Standard: `morning-cycle`. Full: `intelligence` routine (every 3 hours in work hours).
- **Weekly sweep:** the first run that finds `jobs.yaml: intelligence.last_sweep` missing or at least 7 days old also runs the sweep (`atlas-insights` §A step 3b). No routine or schedule changes: on every profile the job decides for itself, as `monthly` does with `period_done`.
- Modifiers: `when`. `mode: light` limits the look to records changed since the last run (no sweep, which waits for the next full run; the topic search in `atlas-insights` §A step 3 still runs).

## Away and paused
Runs during away; new insights stay `new` in `user/inbox/insights.md` and are summarized in the catch-up brief, not nudged. Paused per `system/jobs/README.md`.

## Readiness check
If `ingest` has not succeeded in the last 24 hours and is not earlier in this routine, proceed and note the staleness in the run report.

## Inputs
- Records and sources created or updated since `jobs.yaml: intelligence.last_success` (from `updated` dates in `hot.md` and the type indexes; sources from `_index/sources.md`, since `hot.md` never lists them).
- Active goals, open risks, open questions, active projects (indexes first, then records as needed per `system/rules/retrieval.md`).
- `user/inbox/insights.md` (to avoid repeats) and engagement signals in `user/.state/health.yaml` (acted/dismissed by kind).
- `rhythms.yaml: insights` (`brief_max`, `engagement`, `suppressed_kinds`).
- `jobs.yaml: intelligence.last_sweep`. On a sweep run: the indexes of every active goal and project, open risk and question, and `proposed` or `made` decision, changed or not; calendar events and dated records in the next 28 days; and `python3 -I system/tools/relations.py --out .atlas-tmp/relations.json` (candidate relationships from links and source dates).

## Steps
1. Gather the change set, and check whether the sweep is due. If the change set is empty and no sweep is due, exit early.
2. Invoke `atlas-insights` (routine mode) over the change set and its L3 neighborhood: look for risks, gaps (missing owners, dates, decisions without rationale), patterns (repeated themes across sources), connections (same issue in two projects), collisions the changed dates cause, decisions a new fact undercuts, and opportunities. On a sweep run, also the sweep (`atlas-insights` §A step 3b): blind spots, the 28-day look-ahead, and the relationship candidates. Create a topic for any theme that has reached `system/schemas/topic.md`'s bar without one (`atlas-insights` §A step 3).
3. Score each candidate 0–1 (relevance to goals × urgency × novelty). Drop candidates of a kind listed in `suppressed_kinds` and candidates that repeat an existing `new`, `seen`, or recently `dismissed` insight. Adapt volume to engagement when `engagement: adaptive`.
4. Append surviving insights to `user/inbox/insights.md` (newest first, format `system/schemas/formats.md` §3) with Why, Sources, Links, and a Suggested action.
5. Where an insight is a concrete risk, open question, or idea, create or update the record (`records_write`) and link it from the insight.
6. On a sweep run, set `jobs.yaml: intelligence.last_sweep` to today, even if it found nothing.
7. Commit.

## Outputs
- New entries in `user/inbox/insights.md` (status `new`).
- New or updated records in `user/knowledge/risks/`, `questions/`, `ideas/`, `topics/`, with links and index lines.
- `jobs.yaml: intelligence.last_sweep` on a sweep run.

## Early exit
No records or sources changed since the last successful run and no sweep due → `early_exit`. No candidate scores high enough → `ok` with "0 new insights" (not an error).

## Guardrails
- Every insight cites at least one source or record; never invent evidence. A relationship insight says what moved together or what followed what, with the counts, and never that one caused the other. Inferences are marked `provenance: inferred` on records.
- Insights are suggestions; acting on one (drafting, scheduling, contacting) is left to other jobs or the user.
- Quality over volume: noise erodes trust. The brief shows at most `brief_max`; the rest stay in the inbox. A sweep doesn't raise the cap: its candidates compete on score with everything else.
- Frugal: the sweep reads indexes and `relations.py`'s output first, and opens a record only for a candidate it is weighing.

## Run report
Row: `intelligence | <status> | <N> new insights, <r> records, <t> topics[, sweep] | <top score>`.
