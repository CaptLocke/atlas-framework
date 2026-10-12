---
type: guide
section: troubleshooting
title: If something isn't working
order: 5
version: 1.0.0
---
# If something isn't working

Most problems have a one-step fix. Nova usually spots them first and tells you in chat, in your brief, or on the Control Center with what happened and how to fix it. If you're not sure, ask: "Is everything working?"

## Nova doesn't seem to know my setup
Claude answers like an ordinary chat, or says it can't open your Nova.
1. Make sure you started the chat inside the **Nova** Project.
2. Say **"Start Nova"**.
3. If Claude says it can't attach your repository, follow **Reconnect GitHub** below.

## Reconnect GitHub
Nova lives in your private GitHub repository. If Claude loses access, chats can't open your Nova and automations stop running.
1. In the Claude desktop app, open **Settings → Connectors**. If **GitHub** shows **Connect**, click it and authorize.
2. In your browser, go to GitHub → your profile picture → **Settings → Applications**. Next to **Claude**, click **Configure**. Under **Repository access**, make sure your Nova repository is selected, then click **Save**.
3. If Claude isn't listed there, reinstall it: open github.com/apps/claude/installations/select_target, choose your account, choose **Only select repositories**, pick your Nova, and click **Install**.
4. Start a new chat in the Nova Project and say **"Start Nova"**. Nova checks everything and catches up on what it missed.

## My automations stopped running
If Claude can't reach GitHub, scheduled runs are skipped. After about 3 days (72 hours) without access, the platform turns the automations off, and they stay off until they're turned back on.
1. **Reconnect GitHub** (above).
2. Open a chat in the Nova Project and say **"Check my automations"**. Nova shows which are off and turns them back on for you where it can.
3. If Nova asks you to do it yourself: in the Claude desktop app, open **Routines** in the sidebar, open each Nova routine that shows as off, and switch it back on.

Nothing is lost. Nova picks up from where it stopped and catches up on everything that arrived in the meantime.

## Reconnect a tool (email, calendar, chat, drive…)
Connections to your tools sometimes expire. Nova tells you which one, for example "Your calendar connection expired."
1. In the Claude desktop app, open **Settings → Connectors**.
2. Find the tool and click **Connect** (or **Reconnect**), then sign in.
3. Tell Nova: **"I've reconnected my calendar."** Nova checks the connection, re-learns anything that changed, and catches up.

If a tool can't be connected at all, Nova uses a fallback, such as forwarding items to your connected inbox or dropping files into your Nova Drop folder, and says so.

## My Daily Brief didn't arrive
1. Ask **"Where's my brief?"** Nova checks the last run and tells you what happened.
2. Common causes:
   - **Away mode is on.** The brief is paused while you're away. Say "I'm back" to end it.
   - **GitHub access lapsed**, so the evening run was skipped. See **My automations stopped running**.
   - **A tool connection expired.** The brief may be missing that tool's items. See **Reconnect a tool**.
   - **Your Claude plan's usage limit was reached** before the run. Nova may suggest a lighter automation profile.
3. Ask **"Make my brief now."** Nova builds it on the spot.

## The brief or a dashboard looks out of date
Say **"Refresh my dashboards."** If the problem keeps happening, Nova checks why in its next health check, or you can report it.

## Nova got something wrong
- **A wrong fact:** "That's wrong: the launch moved to November 9." Nova corrects it everywhere it's linked and keeps the history.
- **A wrong action:** "Undo what you did to the Globex record this morning."
- **Too much noise:** "Stop suggesting ideas in the brief" or "Fewer insights, please."

## Nova seems to be using a lot of my Claude allowance
Ask **"How much are my automations using?"** Nova can switch you to a lighter profile, run less often, or skip sources you don't need.

## Report an issue
If something keeps going wrong, or Nova suggests it, tell Nova: **"Report an issue: my brief didn't include today's meetings."** Nova gathers what Nova's maker needs (version, what happened, recent errors), removes anything personal or sensitive, and drafts an email for you to review and send. If no email tool is connected, it gives you the text to copy. Fixes arrive through normal updates.
