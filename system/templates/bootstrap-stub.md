---
type: template
name: bootstrap-stub
destination: the user's "Nova" Project instructions in the Claude app (pasted by the user; never stored in user/)
---
# Bootstrap stub (canonical)

The setup guide (`docs/setup/04-create-the-nova-project.md`) and `nova-setup` both use exactly this text. `nova-setup` shows it with the user's repository filled in, ready to copy, so the user never writes it themselves. `Nova bootstrap <N>` must equal `system/manifest.yaml: bootstrap_version`; bump both whenever this text changes, so the kernel's boot check (§2 step 0) can tell users their instructions are out of date.

```text
This Project is my Nova (Nova bootstrap 2). At the start of every conversation:
1. Attach my GitHub repository YOUR-USERNAME/YOUR-REPO with write (push) access and sync it.
2. Follow the CLAUDE.md file in that repository.
Never ask me to commit, push, or merge.
If you can't attach the repository, tell me in one sentence and give me the one step to fix it (usually: connect GitHub in Settings → Connectors, or give the Claude GitHub App access to this repository; if my Claude account is through work, my admin must turn on unified chat and Cowork in Organization settings → Capabilities).
If I say "Start Nova", do all of this again from the beginning.
```
