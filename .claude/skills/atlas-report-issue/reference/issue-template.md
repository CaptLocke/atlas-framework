---
type: skill-reference
skill: atlas-report-issue
---
# Issue report template

Plain text (it goes into an email body). Keep it under ~60 lines. Omit sections that don't apply. Everything below is after redaction (`redaction.md`).

```
Subject: Atlas issue: <one-line summary> (v<installed_version>)

WHAT HAPPENED (user's words, redacted)
<1–5 sentences>

EXPECTED
<1 sentence>

WHEN / HOW OFTEN
First noticed: <YYYY-MM-DD>. Happens: <once | every run | sometimes>.

ATLAS VERSION
Installed: <installed_version> (system/VERSION <version>), data version <data_version>
Last update: <YYYY-MM-DD or "none">  Last update check: <status>

SETUP
Claude plan: <plan>   Automation profile: <lean | standard | full | custom>
Routines: <name @ schedule in plain words; …>   Models: fast=<id>, strongest=<id>
Connected categories: <mail (Gmail), calendar (Google Calendar), files (Google Drive), …>
Available in routines: <per connector: yes | no | unknown>
Extensions installed: <count by kind, e.g. 1 job, 1 type>   Overrides: <component names or none>

RECENT RUNS (last 5)
<routine> <YYYY-MM-DD HH:MM> <ok|partial|failed> — <job rows that failed: job, status, short error>

ERRORS (redacted, most relevant first)
- <job or skill>: <error message with names/IDs replaced>

HEALTH
Last user check: <date>  Last system check: <date>
Smoke test <date>: repo_push=<pass|fail>, connectors=<…>, hooks=<…>, artifact_republish=<…>
Open known issues: <id: summary; …>

VALIDATOR (if relevant)
<summary counts and redacted error lines>

INDICATORS (only if the user agreed)
<period>: automation_success_rate=<n>, user_action_issues=<n>, corrections=<n>, …

WHAT ATLAS ALREADY TRIED
<retries, re-mapping, repair, rollback>

Sent by the user from their own Atlas. Personal and work details were removed before sending.
```

## Example (fictional, after redaction)
```
Subject: Atlas issue: Daily Brief missing today's meetings (v1.0.0)

WHAT HAPPENED
My brief this morning didn't list any of my meetings, but my calendar has [N=4] meetings today. Yesterday it was fine.

EXPECTED
Today's meetings with prep notes, as usual.

WHEN / HOW OFTEN
First noticed: 2026-10-14. Happens: every run since.

ATLAS VERSION
Installed: 1.0.0 (system/VERSION 1.0.0), data version 1
Last update: none  Last update check: ok

SETUP
Claude plan: pro   Automation profile: lean
Routines: nightly-cycle @ daily 8:07 PM; weekly @ Fri 2:07 PM; upkeep @ Sun 3:07 AM
Connected categories: mail (Outlook), calendar (Outlook), files (OneDrive)
Available in routines: Outlook yes, OneDrive unknown

RECENT RUNS (last 5)
nightly-cycle 2026-10-13 20:07 partial — meeting-prep: failed, "calendar.list_range: parameter 'startDateTime' not recognized"

ERRORS
- meeting-prep: calendar.list_range (tool list_events) returned "unknown parameter startDateTime"

HEALTH
Smoke test 2026-10-01: repo_push=pass, connectors=pass, hooks=pass, artifact_republish=pass
Open known issues: conn-outlook-drift: "Outlook tools changed; map update pending"

WHAT ATLAS ALREADY TRIED
Re-ran meeting-prep in chat (same error). Connector re-map is waiting for the user's confirmation.
```
