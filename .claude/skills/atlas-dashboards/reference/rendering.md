---
type: skill-reference
skill: atlas-dashboards
---

> **Contracts govern.** `system/dashboards/README.md` and each `<name>.contract.md` define placeholders, theme tokens, truncation, and titles; where this file differs, they win.
# Rendering and publishing detail

## The three dashboards (and who refreshes them)
Each contract's `republished_by` lists the jobs that republish it; any chat may also republish a dashboard after changing what it shows. This table copies those lists; when they differ, the contract wins.
| Dashboard | Shows | `republished_by` |
|---|---|---|
| `daily-brief` (Today) | Today's brief (from `user/work/briefs/`), then this week: the day strip with meeting load and free hours, and upcoming milestones | daily-brief (and the chat catch-up) |
| `commitments` (Work) | Commitments (I owe, then Waiting on), projects with health and next step, ranked goals, decisions and risks, and the people with something open | daily-brief, triage, weekly-review, monthly, quarterly |
| `control-center` (Guide) | Health, what's waiting on the user, automations, what Atlas filed in the last 14 days, About you, and the guide content (`system/guide/`) | daily-brief, monthly, quarterly, update-check |
| `project-page` | One project in depth, made on request | triage, weekly-review (while listed) |

## Building data
- **Today's week data** comes from `atlas-brief` §D; this skill only embeds it.
- **Work** carries no per-person lists: the page works out what each person owes and is owed from `commitments`. People are limited to current activity (something open, a meeting in the next 7 days, or gone quiet); decisions to the last 30 days plus any still proposed; risks to open ones. `commitments.contract.md` has the rest.
- **Guide's Recently filed** comes from the activity log (`user/logs/activity/`) for the last 14 days, imports left out. For each line's commit, `git show --name-status --format= <sha> -- user/knowledge/` (leaving out `_index/` and `sources/`) gives the records: added files are `new`, modified ones `updated`. `from` is the title of the record's first source; `what` is the main field that changed. Beliefs for About you are marked `featured` (preferences first, then communication style, then proposed; at most 5), and the guide content goes in the same page's data (`control-center.contract.md`).

- Read only the contract's listed sources, index-first (`_index/*.md`, `hot.md`), opening records only for fields the contract needs.
- IDs: include `id` for each record item. Pages never show it (titles only); it is used for search, the record panel's linked records, and troubleshooting.
- "Next run" times on Guide: compute from `routines.yaml` schedules in the user's time zone.
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
