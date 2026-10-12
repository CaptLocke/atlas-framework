---
type: skill-reference
skill: nova-review
---
# Quarterly moments

Period: the previous calendar quarter (`YYYY-Qn`), produced on the first run on or after the quarter's first business day (the `quarterly` job decides when). In chat, the user can run any of these on demand.

## Quarterly report (`user/work/reports/YYYY-Qn.md`, `type: report`)
```markdown
# Q3 2026 · quarterly reset
## Goals: how last quarter went
## Draft goals for Q4
## Role refresh
## Permission re-confirmation
## Needs you
```

### Goals: how last quarter went
Per goal of the period: outcome (achieved / partly / missed / dropped), the evidence (accomplishments, decisions, metrics), and the main reason in one line. Propose status updates as questions; don't set them.

### Draft goals for the new quarter
- Sources: unfinished goals worth carrying over, plans the user stated (journal, chats), manager or company priorities recorded in decisions/sources, projects starting.
- Create each as a goal record: `status: draft`, `horizon: quarter`, `period: YYYY-Qn`, `metric`, `target`, links to projects. Max 5.
- Ask the user to confirm, edit, drop, or import their official goals (e.g., "paste your OKRs and I'll set them up"). Only on confirmation set `status: active`; update `profile.md` current goals (profile line `[stated · confirmed <date>]`).

### Role refresh
Ask (one at a time in chat; as `questions.md` entries kind `profile` in routines), skipping anything clearly unchanged:
1. Is your role still <role>? Any change in title or responsibilities?
2. Is <manager> still your manager?
3. Any changes to your team or the people you work with most?
4. What are your top priorities this quarter?
5. Any new tools you use (and want connected), or tools you stopped using?
6. Anything changing at <company> I should know (reorg, strategy, products)?
Also propose changes Nova noticed in records (e.g., a new frequent collaborator; the manager's person record shows `inactive`). Confirmed changes update `profile.md`, person records (`relationship`), and connectors (`nova-connectors`) as needed.

### Permission re-confirmation (attestation)
- Show the statement from `nova.yaml: attestation.statement` and ask the user to confirm it still holds for their current employer and role.
- **Same employer and role, confirmed in chat:** set `recorded_on: <today>`, `nova_version: <installed>`, `reconfirm_due:` first business day of the next quarter. Commit (`Nova-Actor: chat`), log.
- **Employer or role changed:** a new attestation is required. Update `employer` (link to the new organization record, created via `nova-capture`) and `role`, have the user re-affirm the statement, then record as above. Until recorded, don't ingest from sources belonging to the new employer (pause `ingest` with `nova-away` if all sources are the new employer's) and tell the user why. Offer to archive, minimize, or export knowledge from the previous employer (`nova-memory`); never decide that for them.
- **User declines or is unsure:** pause `ingest` (until resolved), keep everything already stored, record a high-severity known issue `attestation-declined`, and offer minimize/export/forget options (`nova-memory`).
- **In a routine:** never record; add a `setup`-kind question to `questions.md` and a medium known issue `attestation-due` when `reconfirm_due` has passed.

## Performance review pack (`user/work/reports/YYYY-Qn-performance.md`, `type: performance`)
```markdown
# Q3 2026 · performance review pack
## Summary                 (3–4 sentences in the user's personal voice)
## Accomplishments by goal (from accomplishments.md and goal records)
## Key decisions and outcomes
## Impact                  (metrics, deliverables, customers/people helped)
## Recognition             (thanks and praise received, quoted briefly only if the data rules allow)
## Challenges and learning
## Talking points          (for the self-review or 1:1, 5 bullets max)
## Evidence                (sources and records, grouped by section)
```
Rules: outcomes over activity; every claim traceable in Evidence; no `notes_private`, no confidential content beyond what data rules allow; no exaggeration. Offer to turn it into a document in the user's format (`nova-write`, deliverables folder).
