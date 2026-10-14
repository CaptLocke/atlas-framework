---
type: skill-reference
skill: atlas-dashboards
---

> **Contracts govern.** `system/dashboards/README.md` and each `<name>.contract.md` define placeholders, theme tokens, truncation, and titles; where this file differs, they win.
# Rendering and publishing detail

## The eleven dashboards (and who refreshes them)
Each contract's `republished_by` lists the jobs that republish it; any chat may also republish a dashboard after changing what it shows. This table copies those lists; when they differ, the contract wins.
| Dashboard | Shows | `republished_by` |
|---|---|---|
| `daily-brief` | Today's brief (from `user/work/briefs/`) | daily-brief (and the chat catch-up) |
| `commitments` | Open commitments in two sections, I owe and Waiting on | daily-brief, triage |
| `projects` | Active, proposed, and paused projects with health and next step; a project with its own page opens it | daily-brief, triage, weekly-review |
| `week-ahead` | The next 7 days as a plan: outcomes, day load and free time, prep, watch-outs, each day | daily-brief, weekly-review |
| `goals` | Ranked goals with progress, evidence, linked projects, accomplishments | weekly-review, monthly, quarterly |
| `people` | Key relationships, last contact, open items each way, gone quiet | weekly-review |
| `decisions-risks` | Decision log with reasoning; risk and issue register | weekly-review |
| `records` | Every record, searchable, each opening in the record panel | maintenance, weekly-review |
| `about-you` | Profile, preferences, voice and design with provenance and confirmation status | monthly, quarterly |
| `control-center` | Actions, automations, approvals, questions, connections, known issues, updates | daily-brief, monthly |
| `atlas-guide` | What Atlas can do, how to ask, What's new (`system/guide/`) | update-check |
| `project-page` | One project in depth, made on request | triage, weekly-review (while listed) |

## Building data
- Read only the contract's listed sources, index-first (`_index/*.md`, `hot.md`), opening records only for fields the contract needs.
- IDs: include `id` for each record item. Pages never show it (titles only); it is used for search, the record panel's linked records, and troubleshooting.
- "Next run" times for the Control Center: compute from `routines.yaml` schedules in the user's time zone.
- Away: when `rhythms.yaml: away` is active, add an `info` line to `meta.notices` ("You're away until Oct 20; Atlas is filing quietly.").
- Exclude archived and superseded records unless the contract asks for history.

## Theme
Map `user/profile/design-system.md` to the `--brand-*` tokens in `system/dashboards/README.md` §Theming contract (accent, highlight, text on accent, heading and body fonts, optional background, surface, and text), for light and dark. Rules:
- Use only colors listed in the design system; if dark-mode colors are missing, derive them by keeping hue and adjusting lightness, and keep text contrast at WCAG AA (4.5:1) in both modes.
- Fonts must have web-safe fallbacks; never load fonts or scripts from external URLs.
- No company logo: pages show only the built-in Atlas mark, drawn in the highlight color. With no design system, the theme block stays empty and the default Atlas palette applies.

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
