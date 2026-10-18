---
type: rule
name: sync
---
# Rule: sync (invisible git)

## Applies to
Every session that changes files in the repo.

## The rule
**The GitHub repo is the only source of truth.** Read Atlas files only from the clone of the user's repo attached to this session, save every change there, and push it to `origin/main`. Never read or write Atlas files anywhere else: not in folders on the user's computer (even if a copy of the repo is connected as a local folder), not in Claude Project knowledge, not in uploads. If you notice another copy, ignore it and tell the user once that Atlas only uses the GitHub repo.

The user never sees or manages git. Pull at the start, commit and push after each logical change set, resolve conflicts yourself, and never rewrite history (N8; sole exception: purge).

## Procedure
| Moment | Action |
|---|---|
| Session start | `git pull --rebase` on `main`, then `git push --dry-run origin HEAD:main` to confirm write access (in routines the `SessionStart` hook does both and reports the result; if it reports a failure, retry before reading or writing Atlas files. Repo hooks don't load in Cowork chats, so in a chat Atlas runs both itself: kernel §2 step 1). **Read-only attachment** (the dry run is refused): re-attach the repository with write (push) access and clone it again; if that is refused too, tell the user in one line to give the Claude GitHub App write access to the repository (GitHub → Settings → Applications → Claude → Configure → Repository permissions) and start a new chat |
| Before acting on a new request in a long chat (last pull > 15 minutes ago) | `git pull --rebase`, so routine runs made meanwhile are included |
| After each logical change set (a filed input, a job, a settings change, a deliverable) | `git add -A`, `git commit` with trailers (below), `git pull --rebase`, `git push origin HEAD:main` |
| Conflict during rebase | Resolve (below), `git rebase --continue`, push |
| Push rejected or network/auth failure | Keep working; retry after the next change set; if it still fails at the end of the session or run, record a known issue in `user/.state/health.yaml` and tell the user in one line with the fix (usually: reconnect GitHub) |
| End of every turn | Nothing uncommitted and nothing unpushed. In routines the `Stop` hook enforces this: a turn can't end with unsaved changes, and after repeated push failures it records a `sync-push-failing` known issue and warns. Repo hooks don't load in Cowork chats, so in a chat Atlas checks this itself before every reply that followed a change (`git status --porcelain` empty and nothing ahead of `origin/main`), and saves first if not |

## Commit messages
```
atlas(<actor>): <short summary>

Atlas-Actor: chat | routine:<routine-name> | update | setup
Atlas-Reason: <why, one line>
Atlas-Records: <record IDs or paths touched, comma-separated; may be "-" for settings/logs only>
```
Hooks reject commits without `Atlas-Actor` and `Atlas-Reason` (N12). Commit messages never contain sensitive content.

## Conflict resolution
- **Records:** merge both sides. Frontmatter: take the side with the later `updated` per field; union list fields (aliases, links, sources). Body: keep both sides' content; `## Updates` is the union in date order.
- **Indexes:** take either side, then run `python3 -I system/tools/index.py` once the rebase is done.
- **Logs, journals, inbox files:** union of entries, ordered by date/ID. Activity logs merge this way on their own (`.gitattributes`); the others are merged by hand.
- **Settings:** take the side from a `chat` commit over a routine commit; if both are chats, take the later and add a `questions.md` entry if values differ meaningfully.
- **System-owned paths:** take `origin` (only updates change them).

## Undo
Revert with a **forward commit** (`git revert` or restoring file contents from an earlier commit and committing). Never `reset --hard` pushed commits or force-push.

## Never
- Force-push, `rebase -i` on pushed commits, `filter-branch`/`filter-repo` (except the purge procedure), deleting branches with unmerged work.
- Commit `.atlas-tmp/` or secrets.
- Ask the user to run git commands.
