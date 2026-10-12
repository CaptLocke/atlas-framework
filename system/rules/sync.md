---
type: rule
name: sync
---
# Rule: sync (invisible git)

## Applies to
Every session that changes files in the repo.

## The rule
The user never sees or manages git. Pull at the start, commit and push after each logical change set, resolve conflicts yourself, and never rewrite history (N8; sole exception: purge).

## Procedure
| Moment | Action |
|---|---|
| Session start | `git pull --rebase` on `main` |
| After each logical change set (a filed input, a job, a settings change, a deliverable) | `git add -A`, `git commit` with trailers (below), `git pull --rebase`, `git push origin HEAD:main` |
| Conflict during rebase | Resolve (below), `git rebase --continue`, push |
| Push rejected or network/auth failure | Keep working; retry after the next change set; if it still fails at the end of the session or run, record a known issue in `user/.state/health.yaml` and tell the user in one line with the fix (usually: reconnect GitHub) |

## Commit messages
```
nova(<actor>): <short summary>

Nova-Actor: chat | routine:<routine-name> | update | setup
Nova-Reason: <why, one line>
Nova-Records: <record IDs or paths touched, comma-separated; may be "-" for settings/logs only>
```
Hooks reject commits without `Nova-Actor` and `Nova-Reason` (N12). Commit messages never contain sensitive content.

## Conflict resolution
- **Records:** merge both sides. Frontmatter: take the side with the later `updated` per field; union list fields (aliases, links, sources). Body: keep both sides' content; `## Updates` is the union in date order.
- **Indexes:** take either side, then rebuild the affected index file from records.
- **Logs, journals, inbox files:** union of entries, ordered by date/ID.
- **Settings:** take the side from a `chat` commit over a routine commit; if both are chats, take the later and add a `questions.md` entry if values differ meaningfully.
- **System-owned paths:** take `origin` (only updates change them).

## Undo
Revert with a **forward commit** (`git revert` or restoring file contents from an earlier commit and committing). Never `reset --hard` pushed commits or force-push.

## Never
- Force-push, `rebase -i` on pushed commits, `filter-branch`/`filter-repo` (except the purge procedure), deleting branches with unmerged work.
- Commit `.nova-tmp/` or secrets.
- Ask the user to run git commands.
