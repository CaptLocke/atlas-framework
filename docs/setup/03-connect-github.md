# Step 3: Connect GitHub to Claude

**Time:** 3 to 5 minutes · **You'll need:** to be signed in to GitHub, and the Claude desktop app

Claude needs permission to open your Atlas. You'll give that permission to **only your Atlas repository**, nothing else on your GitHub account. This step has two parts: install the Claude app on GitHub, then make sure GitHub is connected inside Claude.

---

## Before you start: is your Claude account through work?

If you use Claude through your company (a Team or Enterprise plan), your company's Claude admin must turn on one setting before Atlas can open your repository:

- **Organization settings → Capabilities → unified chat and Cowork** must be **on**.

If you're the admin, turn it on there yourself. If you're not, send your admin this sentence: *"Please turn on unified chat and Cowork in Organization settings → Capabilities in Claude."* You can carry on with Part A and Part B while you wait. Atlas just won't be able to open your repository until the setting is on.

If you pay for Claude yourself (Pro or Max), skip this and go to Part A.

---

## Part A: Give Claude access to your Atlas repository (in your browser)

1. **Open this link:** **[github.com/apps/claude/installations/select_target](https://github.com/apps/claude/installations/select_target)**

2. **Choose your personal account** (your username) from the list.

3. **Choose Only select repositories.** Don't choose "All repositories".

4. **Click the Select repositories drop-down and pick your Atlas** (for example `atlas`).

5. **Click Install** (or **Install & Authorize**). If GitHub asks for your password or a code from your phone, enter it.

6. **If you're taken to a Claude page that asks you to sign in or authorize**, sign in with the same account you use in the Claude app and click **Authorize**.

> **If it looks different:**
> - **The page says Claude is already installed** and shows a **Configure** button: click **Configure**, scroll to **Repository access**, choose **Only select repositories**, make sure your Atlas is in the list, and click **Save**.
> - **You see "Install & Request" instead of "Install"**: you picked an organization account rather than your personal one. Go back and choose your own username.

---

## Part B: Check GitHub is connected in Claude (in the desktop app)

1. **Open the Claude desktop app.**
   - **Mac:** click Claude in the Dock, or open it from your Applications folder.
   - **Windows:** click the Start menu and type **Claude**, then open it.

2. **Open Settings.**
   - **Mac:** click **Claude** in the menu bar at the very top of the screen, then **Settings…** (or press **⌘ ,**). You can also click your name or initials at the bottom-left of the Claude window and choose **Settings**.

   - **Windows:** click your name or initials at the bottom-left of the Claude window and choose **Settings** (or press **Ctrl ,**).

3. **Click Connectors** in the Settings list.

4. **Find GitHub.**
   - If it says **Connected** (or shows a tick), you're done.
   - If it shows **Connect**, click it and follow the prompts. Sign in to GitHub if asked, and click **Authorize**.

> **If it looks different:**
> - **No "Connectors" in Settings?** Look for **Integrations** or **Connected apps** instead; it's the same thing.
> - **GitHub isn't in the list?** Click **Browse connectors** (or **Add connector**) and search for **GitHub**.
> - **You're asked which repositories to allow:** choose **Only select repositories** and pick your Atlas, as in Part A.

---

That's all you need to do on GitHub for setup. You won't need it for day-to-day use; if something ever needs fixing there (for example, GitHub asks you to accept new permissions for the Claude app), Atlas tells you and walks you through it.

**Next:** [Step 4: Create the Atlas Project in Claude](04-create-the-atlas-project.md)
