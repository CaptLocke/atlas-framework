---
type: skill-reference
skill: atlas-report-issue
---
# Redaction rules

Goal: the maintainer can understand and reproduce the technical problem; nobody can learn who the user is, where they work, or what they work on.

## Replace (consistent numbering within one report)
| What | Replace with | Example |
|---|---|---|
| People's names (including the user), nicknames, initials | `[PERSON-n]` | "Dana Ruiz" → `[PERSON-1]` |
| Email addresses | `[EMAIL-n]` | `dana@acme.example` → `[EMAIL-1]` |
| Phone numbers, street addresses | `[PHONE]`, `[ADDRESS]` | |
| Employer, customer, partner, vendor, and team names; email domains | `[ORG-n]` | "Acme" → `[ORG-1]` |
| Record titles, IDs, and slugs (`people/dana-ruiz`, `projects/orion-migration`) | Keep the type, replace the slug: `people/[RECORD-n]` | `[[projects/orion-migration]]` → `projects/[RECORD-2]` |
| Project, product, and codenames | `[PROJECT-n]` | |
| Message, email, document, transcript, journal, brief, or draft content (any quoted text from the user's work) | `[CONTENT REMOVED]` | |
| Meeting and event titles, calendar series names | `[EVENT-n]` | |
| File and folder names from the user's drive (except "Atlas Drop", "Atlas Deliverables") | `[FILE-n]`, `[FOLDER-n]` | |
| URLs that contain IDs, paths, or names (mail permalinks, doc links, dashboard links) | `[LINK]` | |
| GitHub owner/repo name, usernames | `[REPO]`, `[USER]` | |
| Channel names, labels, mailbox folders | `[CHANNEL-n]`, `[LABEL-n]` | |
| Exact counts that reveal content ("4 meetings with the board") | Keep numbers, drop context: "[N=4] meetings" | |
| IDs from connectors (message IDs, event IDs, folder IDs) | `[ID]` | |

## Keep
- Atlas version, data version, plan, profile, routine names (`nightly-cycle`), job and skill names, schedules in plain words, model IDs.
- Connector **product** names and categories (Gmail, Outlook, Slack), tool names and operation names (`calendar.list_range`, `list_events`), parameter names, error types and messages (after replacing anything above inside them).
- Dates and times of runs; statuses; durations; counts without context.
- Health check results, smoke-test results, validator rule names.

## Never include
- Secrets of any kind (tokens, keys, passwords, cookies). If an error line contains one, drop the line entirely.
- `notes_private`, data-rule categories' content (confidential, PII, PHI, financial, legal privileged), profile content, voice or design guides.
- Attachments or files from the repo.

## Final pass
Read the finished report top to bottom asking: "Could someone tell who this user is, where they work, or what they're working on?" Remove anything that could. Error messages quoting content are the most common leak: rewrite them as "[tool] failed with [error type] on [ID]".
