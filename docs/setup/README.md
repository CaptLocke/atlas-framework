# Set up Nova

Welcome! This guide gets you from nothing to a working Nova. You do **four short steps** yourself, then Nova takes over in conversation and does the rest with you.

You don't need to be technical. Every step is one small action, with a picture of what you should see. If something on your screen looks different, each step has a note for that.

**Total time:** about 20 minutes for the four steps below, then 30 to 45 minutes chatting with Nova. You can stop at any point and pick up where you left off.

---

## What you need

- **A Claude Pro plan or higher** (Pro, Max, Team, or Enterprise).
- **The Claude desktop app** on a Mac or a Windows PC. If you don't have it yet, download it from [claude.ai/download](https://claude.ai/download) and sign in.
- **An email address** you can open now, for a free GitHub account.
- **A phone** with an authenticator app (recommended, for extra account security in step 1).

That's all. Nova costs nothing beyond your Claude plan.

---

## Before you start: where your information lives

Nova keeps everything it learns about your work in a **private GitHub repository**. Think of it as a private folder in the cloud that only you can see. GitHub is a widely used service for storing files safely, with a full history of every change.

- **It's private.** Only you can open it. You'll choose "Private" in step 2, and Nova checks that it stays that way.
- **It's yours.** Everything is stored as plain, readable text. You can read it, download it, or take it elsewhere at any time.
- **You confirm permission first.** Because Nova will store information about your work, it will ask you to confirm that you're allowed to keep work information in your own private repository. If you're not sure, check with your manager or IT team before you continue. Nova brings nothing in until you've confirmed.

---

## The four steps

| Step | What you'll do | Time |
|---|---|---|
| [1. Create a free GitHub account](01-github-account.md) | Sign up and turn on two-factor authentication | 5 to 10 min |
| [2. Create your Nova](02-create-your-nova.md) | Make your own private copy of Nova | 2 to 3 min |
| [3. Connect GitHub to Claude](03-connect-github.md) | Let Claude open your Nova, and nothing else | 3 to 5 min |
| [4. Create the Nova Project in Claude](04-create-the-nova-project.md) | Make a "Nova" Project, paste a short note, say "Set up Nova" | 5 min |

Then: [What happens next](05-what-happens-next.md) (Nova guides you from here).

Stuck? See [Troubleshooting](troubleshooting.md).

---

## A few words that will come up

- **Repository** (or "repo"): the private storage space on GitHub where your Nova lives.
- **Template:** the original Nova that you copy to make your own. Your copy is completely separate; nobody else can see it.
- **Project:** a workspace inside the Claude app. You'll make one called "Nova" and have all your Nova chats there.
- **Connector:** a link between Claude and one of your tools, such as your email or calendar. Nova helps you set these up later.

---

## Maintainer TODO: screenshots to capture (G-2)

Capture these during the end-to-end setup run, on both macOS and Windows where marked. Save them in `docs/setup/images/` with exactly these names. Blur or crop any personal details (email addresses, usernames, avatars).

| File | Page | What it shows | Mac + Windows? |
|---|---|---|---|
| `github-signup.png` | 1 | GitHub sign-up page with the email field | Once (browser) |
| `github-verify-email.png` | 1 | The "enter the code we emailed you" screen | Once |
| `github-free-plan.png` | 1 | Choosing the Free plan (or the skip/continue option) | Once |
| `github-2fa-settings.png` | 1 | Settings → Password and authentication, with "Enable two-factor authentication" highlighted | Once |
| `github-2fa-qr.png` | 1 | The QR-code screen for the authenticator app | Once |
| `nova-template-page.png` | 2 | The Nova template page with the green "Use this template" button highlighted | Once |
| `use-template-menu.png` | 2 | The menu open, "Create a new repository" highlighted | Once |
| `create-repo-form.png` | 2 | The form: name `nova`, **Private** selected and circled | Once |
| `new-repo-created.png` | 2 | The new private repo, with the "Private" label next to its name circled | Once |
| `github-app-select-target.png` | 3 | The Claude GitHub App "select account" screen | Once |
| `github-app-only-select.png` | 3 | "Only select repositories" chosen, with the `nova` repo picked | Once |
| `github-app-installed.png` | 3 | The confirmation page after installing | Once |
| `claude-settings-mac.png` | 3 | Claude desktop app on macOS: where Settings is | Mac |
| `claude-settings-windows.png` | 3 | Claude desktop app on Windows: where Settings is | Windows |
| `claude-connectors-github.png` | 3 | Settings → Connectors with GitHub shown as connected | Mac + Windows |
| `claude-projects-sidebar.png` | 4 | Where "Projects" is in the Claude app sidebar | Mac + Windows |
| `claude-new-project.png` | 4 | The "create project" form with the name "Nova" | Once |
| `claude-project-instructions.png` | 4 | Where to add the Project's instructions, with the note pasted in | Once |
| `claude-first-chat.png` | 4 | A new chat inside the Nova Project with "Set up Nova" typed | Once |
| `nova-welcome.png` | 5 | Nova's first reply (welcome and the permission question) | Once |
| `github-change-visibility.png` | Troubleshooting | Repo Settings → Danger Zone → "Change visibility" | Once |
| `github-app-configure.png` | Troubleshooting | GitHub Settings → Applications → Claude → Configure, showing repository access | Once |

Also confirm every button label and menu path in these pages against the current GitHub and Claude app, and update the wording where it has changed.
