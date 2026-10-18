# Changelog

All notable changes to Atlas. Atlas follows semantic versioning:
- **Patch** (1.0.x): fixes only.
- **Minor** (1.x.0): additive features, new optional fields, additive migrations. Applied automatically by default.
- **Major** (x.0.0): a migration that needs user input, a non-additive data change, or a breaking change for extensions. Applied after the user says yes.

Each release's "What's new" section is shown to users in the Atlas Guide and their next Daily Brief. "Action needed" lists what only the user can do; each line becomes an "Action needed" item at the top of the next Daily Brief that stays until it's done. Maintainer notes for each release live on the upstream repo's `maintainers` branch (`docs/maintainers/under-the-hood.md`), as does the release checklist (`docs/maintainers/releasing.md`).

## 1.1.1 (2026-10-18)

### What's new
- Atlas follows one set of rules everywhere, so the same question gets the same answer on every page and in every brief:
  - Your Daily Brief page and the brief itself now pick the same items for what's due, who you're waiting on, drafts, and questions.
  - "Gone quiet", how long a piece of work takes, and how much free time you have are worked out the same way in your brief, insights, reviews, and pages.
  - Something due tomorrow goes to the top of your brief without changing its priority.
- At the end of each quarter, Atlas suggests how each goal went and waits for you to confirm before marking it achieved or missed.
- While you're away, Atlas's suggestions no longer expire before you're back, and the reminders that still matter are waiting in your catch-up brief (ones whose date passed while you were out are left out).
- Your overnight automations can read your mail, calendar, and files again, so drafts and overnight filing work as designed. They still can't send, share, or delete anything.
- Custom record types you've added (such as deals) now show up in Atlas's quick-reference lists, so answers and dedupe find them like built-in records.
- Clearer setup and help pages: the steps now use the same numbers Atlas uses, and they point to where automations and their settings really are in the Claude app.

### Action needed
- Turn your mail, calendar, and file connectors (for example Gmail, Google Calendar, and Google Drive) back on in each Atlas automation, so overnight filing and email drafts work again. Atlas still blocks every send, share, and delete in automations. Ask Atlas "update my automation connectors" and it walks you through it.

## 1.1.0 (2026-10-17)

### What's new
- Atlas keeps its quick-reference lists of your records up to date automatically, so answers and your Daily Brief no longer miss something you filed moments earlier.
- Chats start a little faster: Atlas loads less behind the scenes before your first reply, and its own files take up much less space.
- When an evening routine and a chat both log work at the same time, both entries are kept.

## 1.0.2 (2026-10-17)

### What's new
- Stronger safety checks for automatic runs. Atlas's overnight and scheduled work now runs only plain, checkable steps, so a misleading email, document or web page can't get it to send data out, delete your knowledge, change GitHub settings, or weaken its own safeguards. Nothing changes in how you use Atlas.

## 1.0.1 (2026-10-16)

### What's new
- Atlas no longer warns that it couldn't save to GitHub when everything was saved.
- Updates are checked before they install: Atlas installs a new version only if it was signed by Atlas's maker, and skips (and tells you about) any that isn't.
- Before anything is sent, shared, or deleted from a chat, Claude shows its own approval card with exactly what will happen. Setup now walks you through turning these cards on.

### Action needed
- In Settings → Connectors, set every tool that sends, replies, forwards, shares, or deletes to ✋ **Needs approval**, and remove those connectors from your Atlas routines (routines only draft). Ask Atlas "help me set up approval cards" and it walks you through it.
- Update each Atlas routine's instructions so it stops if it ever runs outside its "Atlas routine" environment. Ask Atlas "update my routine instructions" and it shows you exactly what to paste.

## 1.0.0 (2026-10-16)

### What's new
- First public release of Atlas.
- Choose which meetings Atlas shows: all-day events, tentatively accepted meetings, and invitations you haven't answered can each be included or skipped in your brief, Week Ahead, and meeting prep. Everything is included unless you change it, and deadlines on your calendar always show.
- Two new people categories, **prospect** and **board**, and clear definitions for every category so people are sorted the same way every time.
- **Rank your goals.** Tell Atlas which goal matters most, at setup, at the quarterly reset, or any time ("make retention my top goal"). Work tied to your top goals now rises higher in your priorities, and the Goals page lists them in your order.
- **A Week Ahead you can plan with.** It opens with this week's outcomes, a strip showing how full each day is and how much focus time is free, a check of whether that time covers the work you owe, the meetings that need preparing, and anything about the schedule worth fixing early. Select a day to see just that day; select a meeting to see its details and prep.
- **Commitments and Projects pages.** What you owe and what you're waiting on, in two clearly separate sections; and every project with its health, next step, and open commitments and risks.
- **New Records page**: browse and search everything Atlas has filed, by name, type, or status. Select a record to open it in full (details, notes, and linked records you can follow), with a button that copies a request for Atlas when you want to change it. The Commitments, Projects, Decisions & Risks, and People pages open their cards the same way, and so do meetings on the Week Ahead.
- **Atlas learns from your corrections.** When you keep dropping the same kind of "commitment", reranking the same kind of work, or dismissing the same kind of insight, Atlas suggests a rule and follows it once you agree. The monthly report shows what it learned.
- **Playbooks.** Atlas notices work you repeat and offers to save it as a playbook. When one starts, it sets up the checklist with dates, drafts the messages as each step comes due, and flags steps that are missed or out of order.
- **Insights come with the draft.** When an insight suggests messaging someone, the draft is already waiting in your mail.
- **Focus time for what you owe.** When something you owe is due soon and your calendar is filling up, Atlas offers to block time for it (a private hold, only after you say yes).
- **Templates for things you make often.** Atlas offers to turn a recurring deliverable into a template, so every edition is consistent and quicker.
- Atlas checks itself at the start of each chat (that your instructions are current, that it's up to date with your repository, and that it can save to it) and only speaks up if something's wrong, with the fix.
- Every dashboard opens the same way: a one-line headline on what matters most there right now, the key numbers as cards, and when the page was last refreshed, behind a green signal dot that turns amber, with "May be out of date", when a page is older than it should be.
- **Things only you can do come first.** When an update needs something from you, like new Project instructions, it appears at the top of your next Daily Brief under "Action needed" and stays there until it's done. The Control Center shows any text to copy.
- **Coming from another notes app?** Setup asks, then brings your notes in once, first thing after the permission check, so the rest of setup only asks about what your notes didn't cover: from an **Atlas Import** folder in your drive, or an export you attach, zipped or not. Atlas asks what to leave out once it can show you your folders. Notes about you shape your profile after you confirm; everything else becomes connected records with links back to the originals. Atlas never changes your old notes. Open to-dos from the last 60 days stay live. "Undo the import" takes it all back out.
