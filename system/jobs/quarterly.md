---
type: job
name: quarterly
model: strongest
skills: [nova-review]
---
# Job: quarterly

## Purpose
Run the quarterly moments once per quarter: Reset Goals (retrospective on last quarter's goals and preparation for new ones), Role Refresh (has anything changed, plus attestation re-confirmation), and the Performance Review pack.

## Runs when
- Lean: `nightly-cycle`. Standard: `morning-cycle`. Full: `morning-brief`. It rides along in a daily routine and decides for itself whether to do anything.
- **Period logic.** Let Q be the current calendar quarter (`YYYY-Qn`; Q1 = Jan–Mar) and B the first business day of Q (first Monday–Friday date; holidays ignored). Run when the run date is on or after B and `jobs.yaml: quarterly.period_done` is not Q. Otherwise exit early, cheaply.
- The run in quarter Q reviews the **previous quarter** (Q−1) and prepares Q.
- Modifiers: `when`. `target` and `mode` are ignored.

## Away and paused
During away, exit with `skipped_away` and leave `period_done` unchanged; the first run after away catches up. Each moment is skipped individually when its moment (`reset_goals`, `role_refresh`, `performance_review`) is off or paused. If the whole job is paused, exit with `skipped_paused`.

## Readiness check
Period check above. If `monthly` is due in the same run and hasn't run yet, it runs first (routines list `monthly` before `quarterly`); otherwise proceed.

## Inputs
- Goals for Q−1 and Q, their `accomplishments`, linked projects and decisions; weekly reviews and monthly reports for Q−1.
- `user/profile/profile.md` (role, manager, team, responsibilities), `user/settings/nova.yaml: attestation`.

## Steps
1. **Reset Goals** (`nova-review`, quarterly mode): retrospective on each Q−1 goal (evidence, outcome). Where evidence is clear, set status `achieved` or `missed` with an Updates line (`records_write`); otherwise ask. Draft candidate goals for Q as `status: draft` records and add a question asking the user to confirm, change, or import their Q goals.
2. **Role Refresh** (`nova-review`): prepare short questions about changes to role, manager, team, priorities, tools, and company context in `user/inbox/questions.md` (`profile` kind). Add a `setup` question asking the user to re-confirm the attestation; the re-confirmation itself, and a new `reconfirm_due`, are recorded only in chat.
3. **Performance Review** (`nova-review`): a ready-made record of Q−1 accomplishments, decisions, and impact with citations, for self-reviews and 1:1s.
4. Write `user/work/reports/<Q−1>.md` (reset + role refresh, `type: report`) and `user/work/reports/<Q−1>-performance.md` (`type: performance`), each with `date` and `sources`.
5. Republish every dashboard whose contract (`system/dashboards/*.contract.md`) lists `quarterly` in `republished_by`. Set `jobs.yaml: quarterly.period_done` to Q. Commit.

## Outputs
- `user/work/reports/YYYY-Qn.md` and `user/work/reports/YYYY-Qn-performance.md` (the reviewed quarter).
- Goal status updates and draft goals; questions in `user/inbox/questions.md`.

## Early exit
Period not due or already done → `early_exit`. All three moments off → set `period_done` and `early_exit`.

## Guardrails
- New goals are drafts until the user confirms. Profile changes are proposals (`profile_update`). The attestation is changed only in chat with the user's explicit words.
- The performance pack states only evidenced accomplishments; nothing is inflated or invented.

## Run report
Row: `quarterly | <status> | reports <Q−1>; <q> questions | moments run`.
