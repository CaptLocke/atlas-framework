# Setup troubleshooting

Find the problem that matches what you see. Each fix is a few steps. If none of these helps, you can still continue: open a chat in your Nova Project and describe what happened; Nova will help, and can draft an issue report to Nova's maker for you ("Report an issue").

---

## I can't find Use this template

1. **Check you're signed in to GitHub.** The button only appears when you're signed in. Look for your profile picture in the top-right corner; if you see **Sign in** instead, sign in and reload the page.
2. **Make the browser window wider.** On narrow windows the button can move or hide.
3. **Use the direct link instead:** [github.com/new?template_owner=CaptLocke&template_name=nova](https://github.com/new?template_owner=CaptLocke&template_name=nova). It opens the "Create a new repository" form with the Nova template already chosen. Continue from step 5 of [Step 2](02-create-your-nova.md).
4. **Don't use Fork.** A fork of a public repository is public, which isn't safe for your Nova.

---

## My repository is public by mistake

Fix this before you go any further. It takes a minute and nothing is lost.

1. **Open your repository on GitHub** (for example `github.com/maya-chen/nova`).
2. **Click Settings** in the row of tabs near the top of the repository page (it has a gear icon). If you don't see it, click the **⋯** menu at the end of the tabs.
3. **Scroll to the very bottom** of the General page, to the **Danger Zone**.
4. **Click Change visibility**, then **Change to private** (or **Make private**).
5. **Confirm** by following GitHub's prompts. It may ask you to type the repository name and your password or a phone code.

   ![Screenshot: Repo Settings, Danger Zone, "Change visibility"](images/github-change-visibility.png)

6. **Check** that the label next to your repository name now says **Private**.

> If you'd already added work information while it was public, tell Nova in your next chat ("my Nova was public for a while"). Nova will help you review what was there.

---

## Claude can't open my Nova

Claude says it can't find, attach, or access your repository. Work through these in order; most people are fixed by the first or second.

1. **Check the address in the Project instructions.** Open the Nova Project, open its instructions, and check the line `Attach my GitHub repository …`. It must be exactly your GitHub username, a slash, and the repository name (for example `maya-chen/nova`), with no spaces and no `https://github.com/` in front.
2. **Check GitHub is connected in Claude.** Settings → **Connectors** → **GitHub** should say **Connected**. If it shows **Connect**, click it and authorize. (Details: [Step 3, Part B](03-connect-github.md#part-b-check-github-is-connected-in-claude-in-the-desktop-app).)
3. **Check the Claude GitHub App can see your Nova repository.**
   1. On GitHub, click your profile picture → **Settings** → **Applications** (under "Integrations" in the left-hand list).
   2. Next to **Claude**, click **Configure**.
   3. Under **Repository access**, make sure **Only select repositories** is chosen and your Nova is listed. If it isn't, add it with **Select repositories**.
   4. Click **Save**.

   ![Screenshot: GitHub Settings, Applications, Claude, Configure, showing repository access](images/github-app-configure.png)

4. **Reinstall the app if Claude isn't listed.** Go to [github.com/apps/claude/installations/select_target](https://github.com/apps/claude/installations/select_target) and follow [Step 3, Part A](03-connect-github.md#part-a-give-claude-access-to-your-nova-repository-in-your-browser) again.
5. **Start a fresh chat** in the Nova Project and say **`Start Nova`**.

---

## Claude doesn't seem to follow the Project instructions

Claude answers like an ordinary chat, doesn't mention Nova, or doesn't know anything about your setup.

1. **Check you're inside the Nova Project.** The chat must be started from the Nova Project page (you'll see "Nova" near the message box). Chats started elsewhere don't get the instructions.
2. **Say `Start Nova`** and send it. This tells Claude to open your Nova from the beginning.
3. **Check the instructions were saved.** Open the Project's instructions and make sure the text from [Step 4](04-create-the-nova-project.md#add-the-instructions) is there, with your address filled in.
4. If it still doesn't work, see [Claude can't open my Nova](#claude-cant-open-my-nova) above.

---

## Nova asks me something I don't know the answer to

Every setup question can be skipped. Say **"skip"** or **"I'm not sure, use the default"**. You can change anything later by asking Nova.

## I need to stop part-way

Just close the app. Your progress is saved. Next time, open a chat in the Nova Project and say **"Continue setting up Nova"**.

## I'm not sure I'm allowed to store work information

Pause here and ask your manager or IT team before continuing. Nova doesn't bring in any work information until you've confirmed you're permitted to. When you're ready, open a chat in the Nova Project and say **"Continue setting up Nova"**.

## My company manages my GitHub or Claude account

Company-managed accounts may block installing apps or creating private repositories, or may have their own rules about storing work information. Check with your IT team; they may need to approve the Claude GitHub App or recommend a different setup.
