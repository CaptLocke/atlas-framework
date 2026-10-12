---
type: tests-index
version: 1.0.0
---
# Tests

Nova's automated checks. All tests use Python 3 standard library `unittest` plus the vendored YAML parser (`system/tools/vendor/`); nothing needs installing. Run them from the repository root. They must all pass before a release (`system/tools/build-zip.md`) and after every update (`nova-update`, `nova-health`).

**Everything at once:**
```
python3 -m unittest discover -s system/tests -t system/tests
```

## Hook and validator tests

### What they cover
| Folder | Covers | Build plan |
|---|---|---|
| `hooks/` | `.claude/hooks/actions.py` (N1-N4), `paths.py` (N5, N6), `git.py` (N8, N10, N12), the upstream bypass and context detection in `context.py` | T-1 (H-1..H-6) |
| `validators/` | `system/tools/validate.py`: record frontmatter, settings files, registry, manifest, VERSION, skills, jobs, profiles, dashboard contracts, migrations, settings templates; plus a check that this repository itself validates | T-2 |

### How to run
```
python3 -m unittest discover -s system/tests/hooks -v        # hook tests
python3 -m unittest discover -s system/tests/validators -v   # validator tests
python3 system/tools/validate.py --all                       # validate this repo
```
`validate.py` options: `--system`, `--user`, `--all` (default), `--root DIR` (validate another checkout), `--quiet` (errors only), or a list of file paths. It exits 1 when there is any ERROR. Folders that have no files yet produce warnings; once a folder has files, every expected component (20 skills, 12 jobs, dashboard contracts, settings templates) must exist.

### How the hook tests work
Each test builds a throwaway git repo in a temp folder that looks like a **user's** Nova repo (origin set to a non-upstream URL, hooks, manifest and vendored parser copied in), then runs a hook script exactly as Claude Code does: one JSON object on stdin (`tool_name`, `tool_input`, `cwd`, ...), `CLAUDE_PROJECT_DIR` pointing at the temp repo, and `NOVA_CONTEXT` set to `chat`, `routine`, or left unset. A block is exit code 2 with the reason on stderr; "ask the user" is exit 0 with a JSON `permissionDecision: "ask"`.

Fake secrets in `hooks/test_git.py` are assembled at runtime so no committed file contains a secret-shaped string (the commit hook would flag it). Keep it that way in any new test or doc.

Cases covered include: send in routine (block), send in chat without a record (block), with a record (allow once; record consumed), expired or over-long record (block), record for another tool or action (block), security/financial tools (always block), unmapped tool with an unclear name (block in routine, ask in chat), Bash deletes under `user/` (block without a `destructive` record), owned-path writes with and without the update lock, governance files in routine (block) and chat (record with `governance_settings`), approval records and purge locks can't be created in routines, force push and history rewrites (block), the purge-lock exception (chat only), commits without `Nova-Actor`/`Nova-Reason` trailers (block), secrets in staged or same-command changes (block), the upstream bypass in all remote URL forms (allow everything), and a missing `NOVA_CONTEXT` treated as routine.

### Hook design notes and known limits
- **Upstream bypass:** every hook is a no-op when `git remote get-url origin` names the repo in `system/manifest.yaml: upstream` (https, ssh, scp-style, `.git` suffix and proxy URLs all compare by their last `owner/repo`, case-insensitively), or when the manifest is missing. This is how maintainers develop Nova. `git.py` blocks changing `origin` in user repos so the bypass can't be switched on from inside a session.
- **Fail closed:** hooks catch their own errors (Claude Code treats a crash as a non-blocking error). On an internal error they block in routines and for locked actions, and allow with a warning otherwise. `.claude/settings.json` also sets `"onFailure": "block"` so a hook that can't start or times out blocks the call (Claude Code v2.1.295+).
- **Risk classification** (`actions.py`): the `tool_risk` tag from `user/settings/connectors.yaml` plus name patterns from `system/connectors/README.md`, matched on whole name tokens with simple inflections (`send`, `sends`, `sending`; `design` is not `sign`). The riskiest wins. Two deliberate refinements: a name with `draft` and `reply`/`forward`/`respond` but no `send`/`post`/`publish` is a draft (`create_reply_draft`); money nouns (`payment`, `invoice`, `transfer`, ...) are security unless the name starts with a read verb (`list_payments` is a read).
- **Approval records:** must name the exact `tool`, an `action` matching the call's class, a non-empty `user_confirmation`, and expire within 2 minutes (update lock 30, purge lock 15; one minute of clock slack). A record that claims a longer life is rejected.
- **Exempt deletes:** `user/inbox/drop/` (staging copies removed after filing) and `user/knowledge/_index/` (regenerable) can be deleted without approval.
- **Shell analysis is pragmatic** (`.claude/hooks/shell.py`): it understands separators, `cd`, `VAR=` prefixes, wrappers (`sudo`, `env`, `timeout`...), `bash -c`/`eval`, redirections, heredocs, `tee`, `sed -i`, `cp`/`mv`/`install`/`rsync`/`ln`, `rm`/`unlink`/`shred`, `find -delete`, `touch`/`mkdir`/`chmod`, `dd of=`, `unzip`/`tar -x`, and `git rm/mv/checkout --/restore/clean -f`. It does **not** expand variables or command substitutions, reduces globs to their literal prefix, and cannot see writes made by interpreters (`python -c`, `node -e`, `awk` redirection inside its program). These are procedural guards backed by the rules and the health-check audits, not a sandbox.
- **Commit messages:** read from `-m`, `--message`, `-F <file>`, `-F -` with a heredoc, and `-m "$(cat <<EOF ...)"`. When the source can't be read (editor, `-C`, `--amend` without `-m`), the commit is allowed with a warning.
- **Secret scan:** added lines of `git diff --cached`; when the same command runs `git add` or `commit -a`, also unstaged changes and untracked files (text files up to 2 MB).
