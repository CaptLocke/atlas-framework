---
type: guide
section: automations
title: Automations
order: 3
version: 1.0.0
---
# Automations

Atlas's background work runs in the cloud on a schedule, whether or not your computer is on. Each automation does one job. Together they bring in new information, keep your commitments in order, draft what you'd otherwise write yourself, and have your brief ready each morning. Times are in your own time zone. They're set a few minutes past the hour on purpose, because runs on the exact hour can start late. Claude keeps the schedules in UTC, so when your clocks change Atlas notices and asks to move your automations back to their usual times ("re-time my automations").

How much runs, and how often, depends on your **automation profile**. Atlas suggests one that fits your Claude plan, since automations use your plan's allowance. You can switch at any time ("Switch me to the Standard profile"), move any time ("Move my weekly review to Thursday"), or turn things off.

## Lean profile (suggested for Claude Pro)
One main run each evening, so everything is ready the next morning.
- **Every evening, around 8:07 pm:** bring in the day's information, triage commitments, look for insights, draft email replies and follow-ups (weekdays), prepare for tomorrow's meetings, run the monthly or quarterly check-in if one is due, and write tomorrow's Daily Brief.
- **Fridays, around 2:07 pm:** weekly review and status-update drafts.
- **Sundays, around 3:07 am:** tidy-up and check for Atlas updates.
- **First chat of each day:** if nothing's been brought in for more than 3 hours, Atlas quickly checks your email and calendar and updates your brief with anything new.

## Standard profile (suggested for Claude Max 5x)
A full morning run plus refreshes through the working day.
- **Every morning, around 5:07 am:** bring in information, triage, insights, email drafts (weekdays), meeting prep for today, monthly or quarterly check-in if due, and today's Daily Brief.
- **Weekdays at about 10:07 am, 1:07 pm and 4:07 pm:** bring in new information and quickly catch any new commitments.
- **Every evening, around 8:07 pm:** bring in information, triage, email drafts (weekdays), and prep for tomorrow's meetings.
- **Fridays, around 2:07 pm:** weekly review and status-update drafts.
- **Sundays, around 3:07 am:** tidy-up and update check.

## Full profile (suggested for Claude Max 20x)
Close to real time during your working hours.
- **Every hour during work hours:** bring in new information.
- **Every 4 hours outside work hours:** bring in new information.
- **Every 3 hours during work hours:** look for insights.
- **Every 2 hours during work hours:** triage commitments and draft replies and follow-ups.
- **Daily at about 6:07 am and 11:07 am:** meeting prep.
- **Daily at about 6:37 am:** monthly or quarterly check-in if due, then the Daily Brief.
- **Fridays, around 2:07 pm:** weekly review and status-update drafts.
- **Daily at about 3:07 am:** tidy-up (update check on Sundays).

Work hours default to 8:00 am to 6:00 pm on weekdays. Change them any time: "My work hours are 7 to 4."

## Bringing in information
Reads what's new since last time from your connected email, calendar, meeting transcripts, chat, files, and your Atlas Drop folder, plus any Morning or Evening Thoughts. Skips noise, applies your data rules, and files what matters as connected records with their sources. Instructions hidden inside emails or documents are treated as information, never followed, and flagged to you if they look suspicious.

## Commitment triage
Reviews every open commitment: catches new ones, closes ones that are clearly done (with evidence), re-prioritizes against your goals, flags anything slipping or aging, and adds a short insight and a suggested next step to each.

## Insights
Looks across everything for risks, gaps, patterns, connections, and opportunities, ranks them by what matters to your goals, and explains each one with its sources.

## Email drafts
Drafts replies to emails that need one from you, and polite follow-ups for things you're waiting on that are overdue, in the right voice. They're left as **drafts** in your email for you to review and send. Atlas never sends them.

## Meeting prep
For each meaningful upcoming meeting (1:1s, external meetings, anything with open items), a short prep note: who's coming, your history with them, open items each way, and a suggested agenda and questions.

## Daily Brief
Pulls everything above into your morning brief and refreshes your dashboards.

## Weekly review
Wins, decisions made, commitments kept and slipped, stalled projects, things you've been waiting on too long, people to reconnect with, and a preview of next week with suggested priorities. It also adds your wins to your running accomplishments list.

## Status updates
Drafts updates for your manager and stakeholders, in the right voice, ready for you to review and send.

## Monthly check-in
Runs once at the start of each month: progress on each goal, a tidy-up of your knowledge (duplicates, stale items, things to confirm about you), a check of Atlas itself (failing automations, expired connections, updates), and an automation review showing what was useful, what was ignored, and suggested changes.

## Quarterly check-in
Runs once at the start of each quarter: a look back at last quarter's goals and help setting new ones, a quick "has anything changed?" about your role and tools (including re-confirming your permission to store work information), and a ready-made summary of your accomplishments for self-reviews and 1:1s.

## Tidy-up
Rebuilds Atlas's catalogs, repairs links, merges obvious duplicates, and sweeps up anything unprocessed.

## Update check
On Sundays, checks for a new version of Atlas and applies it (small updates automatically, bigger ones after you say yes).

## Things Atlas reacts to
Besides schedules, Atlas watches for these moments every time it runs, including whenever you chat. All are on by default; turn any off ("Stop creating project records automatically").
- **A new project comes up:** Atlas creates it and asks the few questions that matter (owner, goal, target date).
- **A new important person appears:** Atlas adds them and links them; it asks how you know them if that's unclear.
- **A deadline is getting close (3 days by default):** it appears in your brief, then moves to the top the day before.
- **A 1:1 or key meeting is within 24 hours:** a prep note is made.
- **A commitment becomes overdue:** it's flagged; if you're waiting on someone, a polite follow-up draft is prepared for your approval.
- **Something you owe needs time your calendar doesn't have:** Atlas offers to block focus time for it (a private hold, only after you say yes).
- **Work starts that matches one of your playbooks:** Atlas offers to start the playbook, or starts it if you've set that playbook to start on its own, with the checklist dated and the first messages drafted.

How quickly Atlas reacts depends on your profile: within a day on Lean, within a few hours on Standard and Full, and immediately when you're chatting.

## When you're away or have paused something
In away mode, Atlas keeps bringing in and filing information and keeps tidying up, but pauses your brief, email drafts, status updates, meeting prep, and reminders, and holds anything waiting for approval. A catch-up brief is ready on your first day back. Anything you've paused stays paused until the date you chose, or until you say "resume".

## Your own automations
Describe what you want and when: "Every Monday morning, pull last week's pipeline numbers from the CRM and summarize the changes." Atlas builds it, shows you, and adds it to your schedule once you agree.
