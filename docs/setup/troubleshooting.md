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

   ![Repository settings, Danger Zone, with the "Change visibility" button](images/github-change-visibility.png)

6. **Check** that the label next to your repository name now says **Private**.

> If you'd already added work information while it was public, tell Nova in your next chat ("my Nova was public for a while"). Nova will help you review what was there.

---

## Claude can't open my Nova

Claude says it can't find, attach, or access your repository. Work through these in order; most people are fixed by the first, second, or third.

1. **If your Claude account is through work, check the company setting.** Your company's Claude admin must turn on **unified chat and Cowork** in **Organization settings → Capabilities**. Without it, Claude can't open any GitHub repository from a chat, even when everything below is set up correctly. Ask your admin if you can't see Organization settings. (Details: [Step 3, Before you start](03-connect-github.md#before-you-start-is-your-claude-account-through-work).) After it's turned on, start a fresh chat in the Nova Project.
2. **Check the address in the Project instructions.** Open the Nova Project, open its instructions, and check the line `Attach my GitHub repository …`. It must be exactly your GitHub username, a slash, and the repository name (for example `maya-chen/nova`), with no spaces and no `https://github.com/` in front.
3. **Check GitHub is connected in Claude.** Settings → **Connectors** → **GitHub** should say **Connected**. If it shows **Connect**, click it and authorize. (Details: [Step 3, Part B](03-connect-github.md#part-b-check-github-is-connected-in-claude-in-the-desktop-app).)
4. **Check the Claude GitHub App can see your Nova repository.**
   1. On GitHub, click your profile picture → **Settings** → **Applications** (under "Integrations" in the left-hand list).
   2. Next to **Claude**, click **Configure**.
   3. Under **Repository access**, make sure **Only select repositories** is chosen and your Nova is listed. If it isn't, add it with **Select repositories**.
   4. Click **Save**.

   ![GitHub settings for the Claude app, with Repository access showing your Nova repository selected](images/github-app-configure.png)

5. **Reinstall the app if Claude isn't listed.** Go to [github.com/apps/claude/installations/select_target](https://github.com/apps/claude/installations/select_target) and follow [Step 3, Part A](03-connect-github.md#part-a-give-claude-access-to-your-nova-repository-in-your-browser) again.
6. **Start a fresh chat** in the Nova Project and say **`Start Nova`**.

---

## Claude doesn't seem to follow the Project instructions

Claude answers like an ordinary chat, doesn't mention Nova, or doesn't know anything about your setup.

1. **Check you're inside the Nova Project.** The chat must be started from the Nova Project page (you'll see "Nova" near the message box). Chats started elsewhere don't get the instructions.
2. **Say `Start Nova`** and send it. This tells Claude to open your Nova from the beginning.
3. **Check the instructions were saved.** Open the Project's instructions and make sure the text from [Step 4](04-create-the-nova-project.md#add-the-instructions) is there, with your address filled in.
4. If it still doesn't work, see [Claude can't open my Nova](#claude-cant-open-my-nova) above.

---

## Nova says an automation isn't using its routine environment

Nova's automations run in the cloud in an **environment** (a small behind-the-scenes workspace) called **Nova routine**, which has one setting: `NOVA_CONTEXT` set to `routine`. That setting tells Nova's safety checks that nobody is there to approve things. If an automation runs without it, Nova notices, keeps that run to drafts only, and tells you in your next chat. Your chats don't need this setting.

1. **Say "Fix my automation environment"** in a chat in the Nova Project. Nova fixes it for you where it can, or walks you through it one step at a time.
2. **Or do it yourself:**
   1. In the Claude desktop app, open **Routines** (it may be in the sidebar, or under a **Claude Code** section).
   2. Open the automation Nova named (they're called **Nova · …**, for example **Nova · nightly-cycle**).
   3. Find its **Environment** setting and choose **Nova routine**. Save.
3. **If there's no "Nova routine" environment:** open **Settings** and look for **Environments** (or **Cloud environments**). Create one named **Nova routine** and add one variable: name `NOVA_CONTEXT` (capitals, with an underscore), value `routine` (lower case, no spaces or quotes). Save, then go back to step 2.
   ![The environment settings, with an environment named "Nova routine" and the variable NOVA_CONTEXT set to routine](images/claude-environment-nova-routine.png)

4. **Tell Nova "Done"**. Nova runs the automation once as a test and checks it used the right environment.

> **If it looks different:** these settings may be labeled differently, or sit under **Claude Code**, **Code**, or **Routines** in Settings. If you can't find them, tell Nova: it will help, or draft an issue report.

---

## Nova asks me something I don't know the answer to

Every setup question can be skipped. Say **"skip"** or **"I'm not sure, use the default"**. You can change anything later by asking Nova.

## I need to stop part-way

Just close the app. Your progress is saved. Next time, open a chat in the Nova Project and say **"Continue setting up Nova"**.

## I'm not sure I'm allowed to store work information

Pause here and ask your manager or IT team before continuing. Nova doesn't bring in any work information until you've confirmed you're permitted to. When you're ready, open a chat in the Nova Project and say **"Continue setting up Nova"**.

## My company manages my GitHub or Claude account

Company-managed accounts may block installing apps or creating private repositories, or may have their own rules about storing work information. Check with your IT team; they may need to approve the Claude GitHub App or recommend a different setup.

If your Claude account is through work (a Team or Enterprise plan), your Claude admin must also turn on **unified chat and Cowork** in **Organization settings → Capabilities**. Without it, Claude can't open your Nova repository from a chat.
