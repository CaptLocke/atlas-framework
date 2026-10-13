---
type: skill-reference
skill: nova-review
---
# Success indicators (computed locally)

Strategy §3 indicators, computed by the monthly automation review from files in the user's repo only. Stored in `user/.state/health.yaml: indicators` (format: `system/schemas/formats.md` §1) and shown in the monthly report. **Nothing is sent anywhere.** They leave the repo only if the user chooses to include them in an issue report.

| Field | Definition | Computed from |
|---|---|---|
| `period` | The month, `YYYY-MM` | |
| `time_to_first_brief_hours` | Hours from setup start to the first Daily Brief. Fixed after setup; repeat the value each month | `setup.yaml: started` (date; use the first `setup` commit time if available) → `nova.yaml: first_brief_delivered` (use the brief file's commit time if available) |
| `cited_answer_share` | Share of chat answers about the user's work that included at least one citation | Activity-log `recall` lines if `nova-recall` logs them (`cited`/`uncited`); otherwise a sample: up to 20 chat answers visible from this month's chat-written outputs. If no reliable data, `null` and say "not measured" |
| `auto_commitments` | Commitments created in the period from connected sources | Commitment records with `created` in period whose sources are connector kinds (`email`, `meeting`, `message`, `doc`, `data`) |
| `manual_commitments` | Commitments created in the period from the user directly | `created` in period with `provenance: stated` or sources of kind `manual`/`journal` |
| `automation_success_rate` | Jobs completed without failure ÷ jobs run | Run reports in period: job rows `ok`, `skipped_away`, `skipped_paused`, `early_exit` count as success; `partial` counts as half; `failed` as failure |
| `user_action_issues` | Problems that needed the user to act | `health.yaml: known_issues` opened in the period whose fix requires the user (reconnect, permission, choose) |
| `corrections` | Times the user corrected or reversed Nova | Activity-log lines in period for corrections and undo (`nova-memory` correct/forget, forward reverts at the user's request, rejected approvals, profile proposals rejected, and `feedback` lines) |
| `active_weeks` | ISO weeks in the period with at least one user interaction | Commits with `Nova-Actor: chat` or journal entries, grouped by ISO week. Also report rolling counts for the last 3, 6, and 12 months in the report (not stored) |

## Reading them
- Lower `time_to_first_brief_hours` is better (target < 24).
- `cited_answer_share` should be high (≥ 0.8) when knowledge exists.
- A rising `auto_commitments` share means capture is working.
- `automation_success_rate` should be ≥ 0.95; below that, the system health section explains why.
- `corrections` should fall over time; a rise points at a specific skill or source (name it).
- `active_weeks` falling suggests Nova isn't earning its place: offer to simplify (fewer insights, fewer drafts, a lighter profile).

Write values as numbers (shares as 0–1 with two decimals). Unknown → `null`, never a guess.
