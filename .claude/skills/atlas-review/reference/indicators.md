---
type: skill-reference
skill: atlas-review
---
# Success indicators (computed locally)

Atlas's success indicators, computed by the monthly automation review from files in the user's repo only. Stored in `user/.state/health.yaml: indicators` (format: `system/schemas/formats.md` §1) and shown in the monthly report. **Nothing is sent anywhere.** They leave the repo only if the user chooses to include them in an issue report.

| Field | Definition | Computed from |
|---|---|---|
| `period` | The month, `YYYY-MM` | |
| `time_to_first_brief_hours` | Hours from setup start to the first Daily Brief. Fixed after setup; repeat the value each month | `setup.yaml: started` (date; use the first `setup` commit time if available) → `atlas.yaml: first_brief_delivered` (use the brief file's commit time if available) |
| `cited_answer_share` | Share of chat answers about the user's work that included at least one citation | Activity-log `recall` lines if `atlas-recall` logs them (`cited`/`uncited`); otherwise a sample: up to 20 chat answers visible from this month's chat-written outputs. If no reliable data, `null` and say "not measured" |
| `auto_commitments` | Commitments created in the period from connected sources | Commitment records with `created` in period whose sources are connector kinds (`email`, `meeting`, `message`, `doc`, `data`) |
| `manual_commitments` | Commitments created in the period from the user directly | `created` in period with `provenance: stated` or sources of kind `manual`/`journal` |
| `automation_success_rate` | Jobs completed without failure ÷ jobs run | Run reports in period: job rows `ok`, `skipped_away`, `skipped_paused`, `early_exit` count as success; `partial` counts as half; `failed` as failure |
| `user_action_issues` | Problems that needed the user to act | `health.yaml: known_issues` opened in the period whose fix requires the user (reconnect, permission, choose) |
| `corrections` | Times the user corrected or reversed Atlas | Activity-log lines in period for corrections and undo (`atlas-memory` correct/forget, forward reverts at the user's request, rejected approvals, profile proposals rejected, and `feedback` lines) |
| `active_weeks` | ISO weeks in the period with at least one user interaction | Commits with `Atlas-Actor: chat` or journal entries, grouped by ISO week. Also report rolling counts for the last 3, 6, and 12 months in the report (not stored) |
| `work_days` | Work days in the period that count: weekdays in `rhythms.yaml: work_hours.days`, less days away (`away`, and the run reports' `skipped_away`) and the first 7 days after `setup.yaml: started` | Settings, run reports, setup state |
| `brief_days` | Of `work_days`, days the user opened the brief | Today's `views` rows (`ArtifactData` list on Today's URL from `dashboards.yaml`; `atlas-dashboards` `reference/live.md` §1), plus days the brief was shown in a chat (a chat commit for the day's brief, `atlas-brief` step 8). Today not live, or its rows unreadable: `null` |
| `brief_acted_days` | Of `brief_days`, days the user acted on something the brief listed | Activity-log lines that day, from a chat or a request applied from a page, that change a record or approval the day's brief (`user/work/briefs/<date>.md`) links |
| `late_captures` | Commitments filed late or missed | Commitments `created` in the period more than a day after their source's date, plus `missed_commitment` feedback lines (`atlas-triage` `reference/learning.md` §1) |
| `slips` | `i_owe` commitments that became `slipped` in the period, by cause: `{ unwarned, wrong_close, user }` | `unwarned`: no `deadline_approaching` `fired_on` before its `due` in `user/.state/triggers.yaml`, and absent from the day-before brief. `wrong_close`: `wrong_close` feedback lines on commitments. `user`: slipped after an on-time warning. A capture miss is in `late_captures`, not here |
| `hand_fixes` | Records the user had to fix | `atlas-memory` correction lines on records, plus commits in the period changing `user/knowledge/` without `Atlas-Actor` (edits made outside Atlas) |
| `repeat_corrections` | Corrections made again | `feedback` and correction lines in the period whose signal and dimension (or record) already appeared earlier in the same period |

## Reading them
- Lower `time_to_first_brief_hours` is better (target < 24).
- `cited_answer_share` should be high (≥ 0.8) when knowledge exists.
- A rising `auto_commitments` share means capture is working.
- `automation_success_rate` should be ≥ 0.95; below that, the system health section explains why.
- `corrections` should fall over time; a rise points at a specific skill or source (name it).
- `active_weeks` falling suggests Atlas isn't earning its place: offer to simplify (fewer insights, fewer drafts, a lighter profile).
- **Against the success measures:**
  - The brief is working at `brief_days` ≥ 8 per 10 `work_days`, and failing below 5. `brief_acted_days` should be at least half of `brief_days`.
  - `late_captures`, `slips.unwarned`, `slips.wrong_close` and `repeat_corrections` should be 0.
  - `hand_fixes` above 1 is failing.
  - `slips.user` isn't Atlas's failure, but a rising count says the priorities are off: name the pattern.
  - Say which bar each field meets, in one line each.

Write values as numbers (shares as 0–1 with two decimals). Unknown → `null`, never a guess.
