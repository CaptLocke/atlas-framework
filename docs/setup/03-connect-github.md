# Step 3: Connect GitHub to Claude

**Time:** 3 to 5 minutes · **You'll need:** to be signed in to GitHub, and the Claude desktop app

Claude needs permission to open your Nova. You'll give that permission to **only your Nova repository**, nothing else on your GitHub account. This step has two parts: install the Claude app on GitHub, then make sure GitHub is connected inside Claude.

---

## Part A: Give Claude access to your Nova repository (in your browser)

1. **Open this link:** **[github.com/apps/claude/installations/select_target](https://github.com/apps/claude/installations/select_target)**

2. **Choose your personal account** (your username) from the list.

   ![Screenshot: The Claude GitHub App "select account" screen](images/github-app-select-target.png)

3. **Choose Only select repositories.** Don't choose "All repositories".

4. **Click the Select repositories drop-down and pick your Nova** (for example `nova`).

   ![Screenshot: "Only select repositories" chosen, with the nova repo picked](images/github-app-only-select.png)

5. **Click Install** (or **Install & Authorize**). If GitHub asks for your password or a code from your phone, enter it.

6. **If you're taken to a Claude page that asks you to sign in or authorize**, sign in with the same account you use in the Claude app and click **Authorize**.

   ![Screenshot: The confirmation page after installing](images/github-app-installed.png)

> **If it looks different:**
> - **The page says Claude is already installed** and shows a **Configure** button: click **Configure**, scroll to **Repository access**, choose **Only select repositories**, make sure your Nova is in the list, and click **Save**.
> - **You see "Install & Request" instead of "Install"**: you picked an organization account rather than your personal one. Go back and choose your own username.

---

## Part B: Check GitHub is connected in Claude (in the desktop app)

1. **Open the Claude desktop app.**
   - **Mac:** click Claude in the Dock, or open it from your Applications folder.
   - **Windows:** click the Start menu and type **Claude**, then open it.

2. **Open Settings.**
   - **Mac:** click **Claude** in the menu bar at the very top of the screen, then **Settings…** (or press **⌘ ,**). You can also click your name or initials at the bottom-left of the Claude window and choose **Settings**.

     ![Screenshot: Claude desktop app on macOS: where Settings is](images/claude-settings-mac.png)

   - **Windows:** click your name or initials at the bottom-left of the Claude window and choose **Settings** (or press **Ctrl ,**).

     ![Screenshot: Claude desktop app on Windows: where Settings is](images/claude-settings-windows.png)

3. **Click Connectors** in the Settings list.

4. **Find GitHub.**
   - If it says **Connected** (or shows a tick), you're done.
   - If it shows **Connect**, click it and follow the prompts. Sign in to GitHub if asked, and click **Authorize**.

   ![Screenshot: Settings, Connectors, with GitHub shown as connected](images/claude-connectors-github.png)

> **If it looks different:**
> - **No "Connectors" in Settings?** Look for **Integrations** or **Connected apps** instead; it's the same thing.
> - **GitHub isn't in the list?** Click **Browse connectors** (or **Add connector**) and search for **GitHub**.
> - **You're asked which repositories to allow:** choose **Only select repositories** and pick your Nova, as in Part A.

---

That's the last thing you need to do on GitHub. You won't need to visit it again for day-to-day use.

**Next:** [Step 4: Create the Nova Project in Claude](04-create-the-nova-project.md)
