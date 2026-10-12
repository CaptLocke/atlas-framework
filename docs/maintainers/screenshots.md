# Setup guide screenshots (maintainer task G-2)

Not user-facing, so don't link it from `docs/setup/`.

Capture these during the end-to-end setup run (build plan §6), on both macOS and Windows where marked. Save them in `docs/setup/images/` with exactly these names; the setup pages already reference them, with alt text that reads well until the images exist. Blur or crop personal details (email addresses, usernames, avatars, repository names other than `nova`).

| File | Page | What it shows | Mac + Windows? |
|---|---|---|---|
| `github-signup.png` | 01 | GitHub sign-up page with the email field | Once (browser) |
| `github-verify-email.png` | 01 | The "enter the code we emailed you" screen | Once |
| `github-free-plan.png` | 01 | Choosing the Free plan (or the skip option) | Once |
| `github-2fa-settings.png` | 01 | Settings → Password and authentication, "Enable two-factor authentication" highlighted | Once |
| `github-2fa-qr.png` | 01 | The QR-code screen for the authenticator app | Once |
| `nova-template-page.png` | 02 | Nova template page, green "Use this template" button highlighted | Once |
| `use-template-menu.png` | 02 | Menu open, "Create a new repository" highlighted | Once |
| `create-repo-form.png` | 02 | Form: name `nova`, **Private** selected and circled | Once |
| `new-repo-created.png` | 02 | New repo with the "Private" label circled | Once |
| `github-app-select-target.png` | 03 | Claude GitHub App "select account" screen | Once |
| `github-app-only-select.png` | 03 | "Only select repositories" with the `nova` repo picked | Once |
| `github-app-installed.png` | 03 | Confirmation after installing | Once |
| `claude-settings-mac.png` | 03 | Claude desktop app on macOS: where Settings is | Mac |
| `claude-settings-windows.png` | 03 | Claude desktop app on Windows: where Settings is | Windows |
| `claude-connectors-github.png` | 03 | Settings → Connectors with GitHub connected | Mac + Windows |
| `claude-projects-sidebar.png` | 04 | Where "Projects" is in the sidebar | Mac + Windows |
| `claude-new-project.png` | 04 | Create-project form with the name "Nova" | Once |
| `claude-project-instructions.png` | 04 | Project instructions with the stub pasted | Once |
| `claude-first-chat.png` | 04 | New chat in the Nova Project with "Set up Nova" typed | Once |
| `nova-welcome.png` | 05 | Nova's first reply (welcome + permission question) | Once |
| `claude-environment-nova-routine.png` | troubleshooting (and Nova's step-10 walkthrough) | Cloud environment "Nova routine" with `NOVA_CONTEXT=routine`, and where a routine selects its environment | Mac + Windows |
| `github-change-visibility.png` | troubleshooting | Repo Settings → Danger Zone → "Change visibility" | Once |
| `github-app-configure.png` | troubleshooting | GitHub Settings → Applications → Claude → Configure, repository access | Once |

## Also verify during the run
Every button label and menu path in `docs/setup/` and `system/guide/troubleshooting.md` is unverified, especially:
- the cloud environment settings (where they live, how a variable is added, how a routine is tied to an environment);
- the Routines screen (where it lives, the Environment setting on a routine, "Run now");
- Settings → Connectors in the desktop app.

Replace the hedged wording ("look for…", "If it looks different") with the confirmed labels, but keep one "if it looks different" note per step.
