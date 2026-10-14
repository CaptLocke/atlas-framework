---
type: skill-reference
skill: atlas-dashboards
---

> **Contracts govern.** `system/dashboards/README.md` and each `<name>.contract.md` define placeholders, theme tokens, truncation, and titles; where this file differs, they win.
# Rendering and publishing detail

## The eleven dashboards (and who usually refreshes them)
The contract's `republished_by` is authoritative; this is the usual pattern.
| Dashboard | Shows | Typical republishers |
|---|---|---|
| `daily-brief` | Today's brief (sections from `user/work/briefs/`) | daily-brief, chat catch-up |
| `commitments` | Open commitments, split into Waiting on and I owe; filters all / overdue / high priority | triage, daily-brief |
| `projects` | Active, proposed, and paused projects with health, next step, and their open commitments and risks | daily-brief, triage, weekly-review |
| `goals` | Goals with progress, linked projects, evidence, accomplishments | weekly-review, monthly |
| `week-ahead` | Next 7 days: meetings with prep status, deadlines, commitments due, focus time | daily-brief, meeting-prep |
| `people` | Key relationships, last contact, open items each way, gone quiet | weekly-review, daily-brief |
| `decisions-risks` | Decision log with reasoning; risk/issue register | intelligence, weekly-review |
| `control-center` | Routines and jobs (status, last/next run), activity, approvals, questions, connection health, known issues | every routine's last job, settings/away/update/health changes |
| `about-you` | Profile, preferences, voice and design guides with provenance and confirmation status | monthly, after profile changes |
| `atlas-guide` | Features, example requests, automations, controls, troubleshooting, What's new (`system/guide/`) | update, setup |
| `records` | Every record, searchable by name, type, and status; links between records | maintenance, weekly-review |
| `project-page` | One project: state, next step, commitments, decisions, risks, people, timeline | on request; triage, weekly-review while listed |

## Building data
- Read only the contract's listed sources, index-first (`_index/*.md`, `hot.md`), opening records only for fields the contract needs.
- IDs: include `id` for each record item; the template turns it into a link label/anchor per its rendering notes.
- "Next run" times for the Control Center: compute from `routines.yaml` schedules in the user's time zone.
- Away: if `rhythms.yaml: away` is active, set the contract's away banner field (if the contract defines one).
- Exclude archived and superseded records unless the contract asks for history.

## Theme
Map `user/profile/design-system.md` to the template's theme tokens (the contract's rendering notes name them; typically primary, secondary, accent, text, background, surface, and chart colors for light and dark, plus heading and body font stacks). Rules:
- Use only colors listed in the design system; if dark-mode colors are missing, derive them by keeping hue and adjusting lightness, and check text contrast stays readable (aim for WCAG AA, 4.5:1 for body text).
- Fonts must have web-safe fallbacks; never load fonts or scripts from external URLs unless the template already does.
- Logo: embed only if small (under ~20 KB) and the contract allows it; otherwise use the company name in text.

## Size budget
- Budget = contract `size_budget_kb` for the whole HTML file.
- Measure after embedding. Trim in this order unless the contract says otherwise: drop closed/old items beyond the contract's window → cap list lengths (keep highest priority, soonest due, most recent) → shorten summaries to one line → drop optional sections. Record truncation exactly as the contract specifies (`meta.truncated`: list name → number of items left out; see `system/dashboards/README.md`).

## Publishing rules (so routines can republish unattended)
- **Private:** never public, never shared with anyone.
- **Page-only:** a single self-contained HTML file; no extra published files, no uploaded assets.
- **No grants:** no connector access, no live data, no runtime capabilities; everything the page shows is embedded at render time.
- Same title on every republish (the template's title, e.g. "Commitments"), so the user recognizes it.
- Publishing a new page is done in chat (setup or recovery); republishing an existing URL is allowed in routines.
- Use whatever artifact publishing tool the session provides; publish the rendered file from `.atlas-tmp/dashboards/`.

## dashboards.yaml upkeep
```yaml
dashboards:
  commitments: { url: "https://…", last_published: 2026-10-12 }
  deals-board: { url: "https://…", last_published: 2026-10-20 }   # user dashboard (extension name)
project_pages:
  projects/orion-migration: "https://…"
```
Update `last_published` on every successful (re)publish. Commit with the job or chat change set.
