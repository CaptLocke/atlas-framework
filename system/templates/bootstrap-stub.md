---
type: template
name: bootstrap-stub
destination: the user's "Atlas" Project instructions in the Claude app (pasted by the user; never stored in user/)
---
# Bootstrap stub (canonical)

The setup guide (`docs/setup/04-create-the-atlas-project.md`) and `atlas-setup` both use exactly this text. `atlas-setup` shows it with the user's repository filled in, ready to copy, so the user never writes it themselves. `Atlas bootstrap <N>` must equal `system/manifest.yaml: bootstrap_version`; bump both whenever this text changes (release checklist: `docs/maintainers/releasing.md`). A higher `bootstrap_version` is how users are told to update their instructions: `atlas-update` queues an action item for it, and the kernel's boot check (§2 step 0) shows the new text.

```text
This Project is my Atlas (Atlas bootstrap 2). At the start of every conversation:
1. Attach my GitHub repository YOUR-USERNAME/YOUR-REPO with write (push) access and sync it.
2. Follow the CLAUDE.md file in that repository.
Never ask me to commit, push, or merge.
If you can't attach the repository, tell me in one sentence and give me the one step to fix it (usually: connect GitHub in Settings → Connectors, or give the Claude GitHub App access to this repository; if my Claude account is through work, my admin must turn on unified chat and Cowork in Organization settings → Capabilities).
If I say "Start Atlas", do all of this again from the beginning.
```
