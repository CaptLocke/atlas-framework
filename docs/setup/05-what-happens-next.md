# What happens next

From here on, you just talk to Atlas. It asks questions, explains what it's doing, and every question has a sensible default you can accept or skip. You can stop at any time and come back later: open a new chat in the Atlas Project and say **"Continue setting up Atlas"**. Atlas picks up exactly where you left off.

**Time:** 30 to 45 minutes in total, in one sitting or several.

![Atlas's first reply: a welcome, and a question asking you to confirm you're permitted to store work information](images/atlas-welcome.png)

---

## 1. Your permission

Atlas explains, in plain words, that what it learns about your work will be kept in your private GitHub repository. It then asks you to confirm that you're **permitted to store work information from your employer there**. Atlas records your confirmation with the date. Nothing about your work is brought in until you've confirmed.

Atlas will ask you to confirm again each quarter, and if you change jobs or roles.

## 2. Sharing what you have

Atlas reads before it asks. In one message it asks for:
- **your company's website**;
- **your LinkedIn profile**, if you'd like (the easiest way: on your LinkedIn profile, click **More → Save to PDF**, then attach the file);
- **any documents you have handy**, all optional: a few emails or memos you've written, something your company published, a brand guide or slide template, an org chart, strategy or planning documents, recent reports.

Attach whatever you have and skip the rest. You can add more in any chat later.

## 3. Checking what Atlas learned

Atlas reads your material and looks up public information about your company (what it does, its customers, competitors, size, recent news), then shows you what it found, a short section at a time, so you can correct anything. After that it asks only what it still needs to know, usually who your manager and key people are, your current goals, and how you like to work and receive information. Every question has a default, and you can skip any of them.

## 4. Connecting your tools

Atlas helps you connect the tools where your work happens: email, calendar, meeting transcripts, chat (such as Slack or Teams), and your cloud drive. For each one, Atlas learns what it can do and how to use it safely. It also:
- creates a **Atlas Drop** folder in your cloud drive, where you can drop any file for Atlas to read;
- asks where to save finished documents (your **deliverables folder**);
- sets careful defaults for sensitive information, which you can change.

Atlas only reads your tools. It **never sends, shares, or deletes anything without asking you first**.

## 5. Choosing your automations

Atlas suggests an **automation profile** that fits your Claude plan (Lean, Standard, or Full) and explains what will run and when. You choose, and you can adjust times or turn things off. Atlas then sets up the automations so they run in the cloud, even when your computer is off. To do that, Atlas creates a cloud **environment** (a small behind-the-scenes workspace) called **Atlas routine**, with one setting in it: `ATLAS_CONTEXT` set to `routine`. Every automation uses it. It tells Atlas's safety checks that nobody is there to approve things, so automations can only prepare drafts and queue requests for you, never send, share, or delete. Your chats don't need anything like this.

This is the part where you may need to follow a few clicks. If Claude can't create the environment or the automations itself, Atlas shows you exactly what to click and what to copy and paste, one step at a time. The labels in your Claude app may differ a little (for example **Environments** may sit under **Claude Code** or **Routines** in Settings); Atlas tells you what to look for. At the end, Atlas runs one automation once as a test and checks it used the right environment.

## 6. Your dashboards

Atlas creates your dashboards: always-up-to-date pages such as your Daily Brief, Work Board, and the Atlas Guide (a handy reference for everything Atlas can do).

## 7. Your first brief

Atlas looks through your last couple of weeks of work, builds its first picture of your people, projects, and commitments, and prepares your first **Daily Brief**. It arrives by the next morning at the latest.

---

## After setup

- **Just ask.** "What did we decide about pricing?", "Prep me for my 2pm", "Draft a reply to Priya." Atlas uses what it knows without you having to say "check my notes."
- **Brain-dump.** Say "Morning thoughts" or "Evening thoughts" and type or dictate whatever's on your mind. Atlas sorts it.
- **Learn what Atlas can do.** Open the **Atlas Guide** dashboard, or ask "What can you do?"
- **Stay in control.** Ask "What did you do overnight?", "Pause the weekly review", or "I'm away from the 12th to the 20th."

Everything happens in chat. You'll never need to open GitHub, manage files, or save anything.

**Something not working?** See [Troubleshooting](troubleshooting.md), or tell Atlas "Report an issue".
