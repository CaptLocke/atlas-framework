# Step 4: Create the Nova Project in Claude

**Time:** about 5 minutes · **You'll need:** the Claude desktop app, and your Nova's address from step 2 (for example `maya-chen/nova`)

A **Project** is a workspace in Claude. You'll make one called "Nova" and give it a short note that tells Claude, at the start of every chat, to open your Nova. All your Nova conversations will happen inside this Project.

---

## Create the Project

1. **In the Claude desktop app, click Projects** in the left-hand sidebar.

   ![The Claude app sidebar, with Projects near the top](images/claude-projects-sidebar.png)

2. **Click Create project** (or **New project**).

3. **Type `Nova` as the name.** You can leave the description empty.

4. **Click Create project.**

   ![The create project form in Claude, with the name "Nova" typed in](images/claude-new-project.png)

> **If it looks different:** if you don't see Projects in the sidebar, the sidebar may be collapsed. Click the sidebar icon at the top-left of the window to open it. On a narrow window, Projects may be under a menu (☰).

---

## Add the instructions

1. **Find the Project's instructions.** On the Project's page, look for **Instructions**, **Set project instructions**, or **Edit instructions** (often on the right-hand side). Click it.

2. **Copy the text in the box below.**
   - **Mac:** select the text and press **⌘ C**.
   - **Windows:** select the text and press **Ctrl C**.

   ```text
   This Project is my Nova. At the start of every conversation:
   1. Attach my GitHub repository YOUR-USERNAME/YOUR-REPO and sync it.
   2. Follow the CLAUDE.md file in that repository.
   Never ask me to commit, push, or merge.
   If you can't attach the repository, tell me in one sentence and give me the one step to fix it (usually: connect GitHub in Settings → Connectors, or give the Claude GitHub App access to this repository).
   If I say "Start Nova", do all of this again from the beginning.
   ```

3. **Paste it into the instructions box.**
   - **Mac:** **⌘ V**
   - **Windows:** **Ctrl V**

4. **Replace `YOUR-USERNAME/YOUR-REPO` with your Nova's address.** For example, if your GitHub username is `maya-chen` and you named the repository `nova`, the line becomes:

   ```text
   1. Attach my GitHub repository maya-chen/nova and sync it.
   ```

   Only change that one part. Keep the slash, and don't add spaces.

5. **Click Save.**

   ![The Nova Project page, with the instructions box open and the note pasted in](images/claude-project-instructions.png)

> **Don't worry about getting it perfect.** During setup, Nova shows you a ready-made copy of these instructions with your Nova's address already filled in. If anything differs, Nova will ask you to paste its version in place of this one.

---

## Start Nova

1. **Start a new chat inside the Nova Project.** On the Project's page, click in the message box (or click **New chat** while the Project is open). Make sure the chat is inside the Project: you'll see "Nova" above or beside the message box.

2. **Type this and send it:**

   ```text
   Set up Nova
   ```

   ![A new chat inside the Nova Project, with "Set up Nova" typed in the message box](images/claude-first-chat.png)

3. **Wait a moment.** The first time, Claude opens your Nova and gets ready, which can take up to a minute. Nova then greets you and starts setting things up with you.

> **If it looks different:**
> - **Claude says it can't find or attach the repository:** check the address you typed in the instructions (step 4 above), then see [Troubleshooting: Claude can't open my Nova](troubleshooting.md#claude-cant-open-my-nova).
> - **Claude answers like an ordinary chat and doesn't mention Nova:** type **`Start Nova`** and send it. See [Troubleshooting](troubleshooting.md#claude-doesnt-seem-to-follow-the-project-instructions).
> - **Claude asks permission to use a tool** (for example GitHub): click **Allow** (or **Always allow** for this Project).

---

**You're done with the setup steps.** From here, Nova guides you.

**Next:** [What happens next](05-what-happens-next.md)
