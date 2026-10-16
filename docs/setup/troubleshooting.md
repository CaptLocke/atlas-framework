# Setup troubleshooting

Find the problem that matches what you see. Each fix is a few steps. If none of these helps, you can still continue: open a chat in your Atlas Project and describe what happened; Atlas will help, and can draft an issue report to Atlas's maker for you ("Report an issue").

---

## I can't find Use this template

1. **Check you're signed in to GitHub.** The button only appears when you're signed in. Look for your profile picture in the top-right corner; if you see **Sign in** instead, sign in and reload the page.
2. **Make the browser window wider.** On narrow windows the button can move or hide.
3. **Use the direct link instead:** [github.com/CaptLocke/atlas-framework/generate](https://github.com/CaptLocke/atlas-framework/generate). It opens the "Create a new repository" form with the Atlas template already chosen. Continue from step 5 of [Step 2](02-create-your-atlas.md).
4. **Don't use Fork.** A fork of a public repository is public, which isn't safe for your Atlas.

---

## My repository is public by mistake

Fix this before you go any further. It takes a minute and nothing is lost.

1. **Open your repository on GitHub** (for example `github.com/maya-chen/atlas`).
2. **Click Settings** in the row of tabs near the top of the repository page (it has a gear icon). If you don't see it, click the **⋯** menu at the end of the tabs.
3. **Scroll to the very bottom** of the General page, to the **Danger Zone**.
4. **Click Change visibility**, then **Change to private** (or **Make private**).
5. **Confirm** by following GitHub's prompts. It may ask you to type the repository name and your password or a phone code.

6. **Check** that the label next to your repository name now says **Private**.

> If you'd already added work information while it was public, tell Atlas in your next chat ("my Atlas was public for a while"). Atlas will help you review what was there.

---

## Claude can't open my Atlas

Claude says it can't find, attach, or access your repository. Work through these in order; most people are fixed by the first, second, or third.

1. **If your Claude account is through work, check the company setting.** Your company's Claude admin must turn on **unified chat and Cowork** in **Organization settings → Capabilities**. Without it, Claude can't open any GitHub repository from a chat, even when everything below is set up correctly. Ask your admin if you can't see Organization settings. (Details: [Step 3, Before you start](03-connect-github.md#before-you-start-is-your-claude-account-through-work).) After it's turned on, start a fresh chat in the Atlas Project.
2. **Check the address in the Project instructions.** Open the Atlas Project, open its instructions, and check the line `Attach my GitHub repository … with write (push) access …`. It must be exactly your GitHub username, a slash, and the repository name (for example `maya-chen/atlas`), with no spaces and no `https://github.com/` in front.
3. **Check GitHub is connected in Claude.** Settings → **Connectors** → **GitHub** should say **Connected**. If it shows **Connect**, click it and authorize. (Details: [Step 3, Part B](03-connect-github.md#part-b-check-github-is-connected-in-claude-in-the-desktop-app).)
4. **Check the Claude GitHub App can see your Atlas repository.**
   1. On GitHub, click your profile picture → **Settings** → **Applications** (under "Integrations" in the left-hand list).
   2. Next to **Claude**, click **Configure**.
   3. Under **Repository access**, make sure **Only select repositories** is chosen and your Atlas is listed. If it isn't, add it with **Select repositories**.
   4. Click **Save**.

5. **Reinstall the app if Claude isn't listed.** Go to [github.com/apps/claude/installations/select_target](https://github.com/apps/claude/installations/select_target) and follow [Step 3, Part A](03-connect-github.md#part-a-give-claude-access-to-your-atlas-repository-in-your-browser) again.
6. **Start a fresh chat** in the Atlas Project and say **`Start Atlas`**.

---

## Atlas can read my Atlas but can't save anything

Atlas says it can't save, or that your repository is attached **read-only**. Atlas checks this at the start of every chat and normally fixes it itself by re-attaching your repository with write access. If it still can't:

1. **Check the Project instructions** ask for write access. The first numbered line should end with **with write (push) access and sync it**. If yours doesn't, copy the text from [Step 4](04-create-the-atlas-project.md#add-the-instructions) again (or ask Atlas for it) and paste it in place of the old one.
2. **Check the Claude GitHub App can write to your Atlas.** On GitHub, click your profile picture → **Settings** → **Applications** → next to **Claude**, click **Configure**. If GitHub shows a banner asking you to **accept new permissions**, accept it. Make sure your Atlas is listed under **Repository access**.
3. **Start a fresh chat** in the Atlas Project and say **`Start Atlas`**.

---

## Claude doesn't seem to follow the Project instructions

Claude answers like an ordinary chat, doesn't mention Atlas, or doesn't know anything about your setup.

1. **Check you're inside the Atlas Project.** The chat must be started from the Atlas Project page (you'll see "Atlas" near the message box). Chats started elsewhere don't get the instructions.
2. **Say `Start Atlas`** and send it. This tells Claude to open your Atlas from the beginning.
3. **Check the instructions were saved.** Open the Project's instructions and make sure the text from [Step 4](04-create-the-atlas-project.md#add-the-instructions) is there, with your address filled in.
4. If it still doesn't work, see [Claude can't open my Atlas](#claude-cant-open-my-atlas) above.

---

## Atlas says an automation isn't using its routine environment

Atlas's automations run in the cloud in an **environment** (a small behind-the-scenes workspace) called **Atlas routine**, which has one setting: `ATLAS_CONTEXT` set to `routine`. That setting tells Atlas's safety checks that nobody is there to approve things. If an automation runs without it, Atlas notices, stops that run before it does anything, and tells you in your next chat. Your chats don't need this setting.

1. **Say "Fix my automation environment"** in a chat in the Atlas Project. Atlas fixes it for you where it can, or walks you through it one step at a time.
2. **Or do it yourself:**
   1. In the Claude desktop app, open **Routines** (it may be in the sidebar, or under a **Claude Code** section).
   2. Open the automation Atlas named (they're called **Atlas · …**, for example **Atlas · nightly-cycle**).
   3. Find its **Environment** setting and choose **Atlas routine**. Save.
3. **If there's no "Atlas routine" environment:** open **Settings** and look for **Environments** (or **Cloud environments**). Create one named **Atlas routine** and add one variable: name `ATLAS_CONTEXT` (capitals, with an underscore), value `routine` (lower case, no spaces or quotes). Save, then go back to step 2.

4. **Tell Atlas "Done"**. Atlas runs the automation once as a test and checks it used the right environment.

> **If it looks different:** these settings may be labeled differently, or sit under **Claude Code**, **Code**, or **Routines** in Settings. If you can't find them, tell Atlas: it will help, or draft an issue report.

---

## Atlas asks me something I don't know the answer to

Every setup question can be skipped. Say **"skip"** or **"I'm not sure, use the default"**. You can change anything later by asking Atlas.

## I need to stop part-way

Just close the app. Your progress is saved. Next time, open a chat in the Atlas Project and say **"Continue setting up Atlas"**.

## I'm not sure I'm allowed to store work information

Pause here and ask your manager or IT team before continuing. Atlas doesn't bring in any work information until you've confirmed you're permitted to. When you're ready, open a chat in the Atlas Project and say **"Continue setting up Atlas"**.

## My company manages my GitHub or Claude account

Company-managed accounts may block installing apps or creating private repositories, or may have their own rules about storing work information. Check with your IT team; they may need to approve the Claude GitHub App or recommend a different setup.

If your Claude account is through work (a Team or Enterprise plan), your Claude admin must also turn on **unified chat and Cowork** in **Organization settings → Capabilities**. Without it, Claude can't open your Atlas repository from a chat.
