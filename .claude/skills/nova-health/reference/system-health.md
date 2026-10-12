---
type: skill-reference
skill: nova-health
---
# System health check, smoke test, and audits

## Checks
| Check | How | Auto-fix | Known issue / to the user |
|---|---|---|---|
| **Run failures** | Run reports since `last_system_check` with `status: failed|partial`; `## Errors`; `jobs.yaml` `last_status: failed` | Re-run a failed idempotent job once if in a chat or the same routine allows it | Repeated failure (≥3 runs, same error): issue + report suggestion |
| **Missed runs** | For each routine in `routines.yaml`, expected runs from its schedule vs run reports. No run for >2× interval (daily: >48h) | none | "Your nightly routine hasn't run since Oct 9. GitHub access may have lapsed, which turns routines off after 3 days. Fix: reconnect GitHub (Settings → Connectors → GitHub), then turn the routine back on in Routines." |
| **Connector auth** | Auth/permission errors in run reports' `## Connector health`; a read probe failing in chat | none | "Your Outlook connection expired. Reconnect it in Settings → Connectors." (one issue per connector, id `conn-<name>-auth`) |
| **Connector drift** | Tools in the session vs `connectors.yaml`: missing connector, new connector, `tool_fingerprint` changed, `mcp_prefix` mismatch | Chat: run `nova-connectors` (confirmation needed). Routine: none | Routine: issue "Your connections changed; I'll update my map next chat" |
| **Routine availability** | Run reports show a connector's tools used or "not available" while `available_in_routines: unknown` | Chat: update via `nova-connectors` | none |
| **Hooks present** | `.claude/settings.json` exists, parses, registers PreToolUse matchers for MCP tools, file writes, and shell; each referenced script exists under `.claude/hooks/`; `python3` available | Chat: missing/changed files → `nova-update` repair; routine: known issue only | High-severity issue if hooks can't be restored |
| **Routine environment** | Run reports since `last_system_check` (maintenance: the last 8 days): every routine run's frontmatter has `nova_context: routine` (case-insensitive). A missing field or any other value means that routine ran outside the "Nova routine" environment, so the safety hooks treated it as a chat (it stayed safe by instruction only). Chats need no marker; don't check them | none (attaching a routine to an environment happens in the user's routine settings; in chat, offer to walk them through it) | High-severity issue `routine-env-missing` per routine (`routine: <name>`): "Your nightly automation ran without its 'Nova routine' environment. It still only made drafts, but the safety checks weren't guarding it. Fix: open the routine's settings and choose the 'Nova routine' environment (`nova-setup/reference/automations.md` §3)." Close it when that routine's later runs all show `routine` |
| **Validation** | `python3 system/tools/validate.py --all` | Fix record/settings errors with one obvious fix (missing `updated`, index line mismatch, enum case) | Remaining errors, grouped |
| **System files unmodified** | Baseline: `refs/tags/v<installed_version>` fetched from `manifest.upstream` (see `nova-update/reference/procedure.md`); if that tag doesn't exist upstream or `nova.yaml: installed_from_commit` is set (no real update yet), use `installed_from_commit` (the template's starting commit). Diff each owned path against the baseline; changes made by `Nova-Actor: update` commits are expected | Chat only: `nova-update` repair, which first offers to keep intentional edits as an extension. Routine: no fix | Routine: known issue `system-files-modified` ("I'll restore Nova's system files next time we chat"). Upstream unreachable: low issue, retry next check |
| **Extensions** | Each registry entry: file exists; `requires_nova` range satisfied by `installed_version`; for `overrides`, the overridden system component changed since the entry's `created` (diff the component between the release it was created under and now, or check CHANGELOG); duplicate overrides (newer wins, flag); instructions conflicting with governance | none | "Your 'deals' record type expects Nova ≥2.0; you're on 1.4" with a suggested fix (`nova-extend` update or rollback) |
| **Repo size** | `git count-objects -vH` (size-pack), record counts per type, index line counts | none | Medium at >500 MB or an index >2,000 lines: suggest archiving old sources and splitting indexes by year (R15); high at >1 GB |
| **Attestation due** | `nova.yaml: attestation.reconfirm_due` ≤ today | none | Issue `attestation-due` (medium); in chat, offer the re-confirmation now (`nova-review` quarterly role refresh procedure) |
| **GitHub connection** | Push succeeded this session/run; repository visibility `private` and no collaborators, where the GitHub connector/API allows checking (N9) | none | Public repo or collaborators: high issue; tell the user immediately with the fix (make private / remove collaborator; Nova never does it itself) |
| **Updates** | Installed vs latest release tag | Minor/patch: let `update-check` handle | "Update available: 1.2.0" on the Control Center |

## Smoke test (platform dependencies)
Record in `health.yaml: smoke_test` `{ last_run: <date>, results: { repo_push, connectors, hooks, artifact_republish } }` with `pass | fail | skipped`.
| Dependency | Probe | Pass when |
|---|---|---|
| `repo_push` | Commit the updated `health.yaml` and push to `main` | Push accepted on `main` (not a `claude/` branch) |
| `connectors` | One read-only call (1 item) per mapped connector's required read operation | Every connector returns without auth error (list failures by name) |
| `hooks` | `git push --force --dry-run origin HEAD:main` (no effect even if allowed) | The hook blocks it. If it isn't blocked, the hook didn't fire: high issue |
| `artifact_republish` | Republish the Control Center to its stored URL (`nova-dashboards`) | Same URL, publish succeeded (in a routine this tests unattended republish) |
A failed smoke-test item creates a known issue with a fix; if the fix is outside the user's control (platform change), suggest `nova-report-issue`.

## Audits
1. **Locked actions approved.** For the period, find activity-log lines whose action is a locked class (`send_communication`, `share_expose`, `destructive`, `governance_settings`). Each must: say `(approved)`, have actor `chat` (or `setup` during setup), and match an `approvals.md` entry or a chat commit whose `Nova-Reason` quotes or references the user's confirmation. Any miss → high issue, told to the user.
2. **No locked action in routines.** No activity line or commit with actor `routine:*` performs a locked class; no routine commit changes `governance.yaml`, `data-rules.yaml`, or `connectors.yaml`. Look hardest at runs flagged `routine-env-missing`: the hooks didn't treat them as routines.
3. **Governance files only in chat.** `git log --format='%H %(trailers:key=Nova-Actor,valueonly)' -- user/settings/governance.yaml user/settings/data-rules.yaml user/settings/connectors.yaml` shows only `chat` (or `setup`).
4. **Trailers present.** Commits in the period all carry `Nova-Actor` and `Nova-Reason` (N12).
5. **Data rules (N11), sampling.** Pick up to 10 recent sources; check excluded senders/channels/series don't appear, and `pointer`/`summary` handling matches categories. Fix over-stored content by reducing it to the allowed handling (a records change, logged), and tell the user.
6. **Suspicious content (N7).** Run reports' "Suspicious content flagged" entries since the last check: confirm no action followed; list them for the user if they look targeted.
7. **No secrets (N10).** Quick pattern scan of files changed in the period (keys, tokens, passwords in URLs). If found: high issue; tell the user; removing it from history needs a purge (`nova-memory`) with their confirmation, and they should rotate the secret.

## Output (monthly report section "Nova's health")
```markdown
## Nova's health
- Automations: 30 of 31 runs succeeded. One nightly run failed on Oct 9 (calendar timeout); it caught up the next night.
- Connections: all working. Slack added new tools; I'll update my map next time we chat.
- Safety checks: every send and delete this month had your approval. No settings changed outside our chats. Every automation ran in its routine environment.
- Platform check: saving, connections, safety guards, and dashboard refresh all working.
- Needs you: none.
```
