---
type: skill-reference
skill: atlas-setup
---
# Steps 1–4: before Atlas runs, and getting unstuck

Steps 1–4 are done by the user with the setup guide in `docs/setup/` (macOS and Windows). This file is what Atlas says when the user is partly through them, comes back stuck, or needs the bootstrap stub again. Keep every answer to one action at a time; wait for "done" before giving the next.

## The bootstrap stub
The canonical text is `system/templates/bootstrap-stub.md`; use it exactly, replacing `YOUR-USERNAME/YOUR-REPO` with the user's `<owner>/<repo>` from `git remote get-url origin` (e.g. `https://github.com/maya-chen/atlas.git` → `maya-chen/atlas`). Show it in one copy block. Never paraphrase it here or anywhere else.

How to present it:
> Here's the text for your Atlas project. Copy all of it, then in Claude open your **Atlas** project → **Project instructions** (sometimes shown as "Set custom instructions" or a pencil icon), paste it in, and save. After that, every new chat in that project starts as Atlas.

If the user doesn't know their repo name (they're in a chat without the repo attached, so this skill isn't running): the setup guide explains it as their GitHub username, a slash, and the name they gave the repository (`docs/setup/04-create-the-atlas-project.md`, "Replace YOUR-USERNAME/YOUR-REPO"). If they've forgotten either, they can find it on github.com under their profile picture → **Your repositories**, shown as `their-username/repo-name`.

## Quiet checks on the first run of setup
| Step | Check | If it fails |
|---|---|---|
| 2. Repo | Repository is private (GitHub connector/API if available; otherwise ask "Does your repository page show a **Private** label next to its name?") | Walk them to **Settings → General → Danger Zone → Change visibility → Make private**. Explain: this keeps their work information visible only to them. N9. |
| 3. Connect | Committing and pushing `setup.yaml` to `main` succeeds | See "Claude can't save to your repository" below |
| 4. Project | You're in a project chat with the stub (ask once: "Did you paste the Atlas text into your project's instructions?") | Give the stub again |

## "I'm stuck at step N"
Ask what they see on screen if the fix below doesn't match. Screens change; describe the goal ("we're looking for the button that creates a copy of Atlas") as well as the click.

### Step 1: accounts
- **No GitHub account yet:** go to github.com → **Sign up**; the free plan is all Atlas needs. Use any email; pick a username they don't mind seeing in links.
- **Verification email didn't arrive:** check spam/promotions; the GitHub sign-up page has "Resend".
- **Two-factor prompt:** recommended; an authenticator app or a passkey, as the setup guide describes. It protects their knowledge.
- **Which Claude plan?** Pro or higher. If they're on Free, Atlas can't run automatic routines; they need to upgrade first.

### Step 2: repository from the template
- **Can't find "Use this template":** on the Atlas page (link in the guide), it's the green button near the top right, next to "Code". On narrow windows it may be under a "…" menu. Choose **Create a new repository**.
- **Naming:** any name works; suggest `atlas`. Owner: their own account.
- **Visibility:** choose **Private**. If they already made it public, change it (table above) before going further.
- **"Include all branches":** leave unticked.
- **Made it under an organization by mistake:** fine if it's private and they control it; otherwise create a new one under their own account and delete nothing yet; Atlas will use whichever they name in the stub.

### Step 3: connecting GitHub to Claude
- Goal: Claude's GitHub app is installed with access to **only** their Atlas repository.
- In Claude: **Settings → Connectors** (or **Integrations**) → **GitHub** → **Connect**; on GitHub choose **Only select repositories** → pick their Atlas repo → **Install / Authorize**.
- **"Claude can't save to your repository"** (push fails): the app was installed with read-only access or on other repos. Fix: github.com → **Settings → Applications → Installed GitHub Apps → Claude → Configure** → ensure their Atlas repo is selected and access includes writing contents. Then say "try again".
- **Pushes land on a branch named `claude/...` instead of `main`:** routines push to a `claude/` branch unless their prompt says otherwise, and the Atlas routine prompt says to push to `main`, so check that the routine's instructions were pasted in full. A GitHub branch rule on `main` can also block pushes; the user can remove it in the repository's settings. Note it (`setup.yaml: notes`) and continue; routine pushes are checked during testing.
- **Repository not in the list:** reopen the app configuration and add it.

### Step 4: the Atlas project
- **Create the project:** in Claude, **Projects → New project** → name it **Atlas** → paste the stub into the project instructions → save → start a new chat in it and say **Set up Atlas**.
- **Claude can't attach the repository at all** (the chat says access to the repository isn't enabled, it has no way to add a repository, or cloning fails with an invalid GitHub token): ask once whether their Claude account is through work (a Team or Enterprise plan). If it is, the usual cause is an organization setting: their Claude admin must turn on **unified chat and Cowork** in **Organization settings → Capabilities**. Give them that in one sentence, plus a line they can send their admin ("Please turn on unified chat and Cowork in Organization settings → Capabilities in Claude."). Once it's on, they start a fresh chat in the Atlas Project. If it's a personal account, or the setting is already on, continue with the GitHub checks below and in the setup guide's troubleshooting ("Claude can't open my Atlas").
- **Atlas is attached read-only** (pushing is refused): re-attach with write access yourself first. If that fails, check the user's Project instructions contain "with write (push) access"; if they have an older copy, give them the stub again. Otherwise the Claude GitHub App needs write access or has pending permissions to accept (setup guide troubleshooting, "Atlas can read my Atlas but can't save anything").
- **The chat doesn't seem to know about Atlas** (no greeting about setup, or it asks what Atlas is): the repo wasn't attached. Check the stub is pasted exactly; in the chat, use the attach/add-repository option and pick their repo; or say "attach my Atlas repository <owner>/<repo>". If it still fails, the GitHub connection (step 3) is the usual cause.
- **Where do I type?** Any new chat inside the Atlas project.

## Resuming later
Tell the user: "Any time, open a new chat in your Atlas project and say *continue setup*. I'll pick up right here." Record where they stopped in `setup.yaml: notes`.
