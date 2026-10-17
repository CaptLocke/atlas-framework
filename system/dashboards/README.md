---
type: dashboards-readme
version: 1.0.0
---
# Dashboards

Dashboards are browsable pages Atlas keeps up to date. Each one is a **published Claude artifact**: a private, self-contained HTML page built from a template in this folder with the data embedded at render time. Dashboards are views only; every change happens in chat, where Atlas updates the underlying records and republishes.

The `atlas-dashboards` skill owns rendering and publishing. This folder holds what it renders from: one **template** (`<name>.html`) and one **data contract** (`<name>.contract.md`) per dashboard.

## The dashboards
| Dashboard | Template | Contract | Republished by | Page budget |
|---|---|---|---|---|
| Daily Brief | `daily-brief.html` | `daily-brief.contract.md` | `daily-brief` job; chat catch-up | 120 KB |
| Commitments | `commitments.html` | `commitments.contract.md` | `daily-brief`; `triage` (optional) | 300 KB |
| Projects | `projects.html` | `projects.contract.md` | `daily-brief`, `triage`, `weekly-review` | 250 KB |
| Goals (with accomplishments) | `goals.html` | `goals.contract.md` | `weekly-review`, `monthly`, `quarterly` | 200 KB |
| Week Ahead | `week-ahead.html` | `week-ahead.contract.md` | `daily-brief`, `weekly-review` | 150 KB |
| People | `people.html` | `people.contract.md` | `weekly-review` | 250 KB |
| Decisions & Risks | `decisions-risks.html` | `decisions-risks.contract.md` | `weekly-review` | 300 KB |
| Control Center | `control-center.html` | `control-center.contract.md` | `daily-brief`, `monthly` | 200 KB |
| About You | `about-you.html` | `about-you.contract.md` | `monthly`, `quarterly` | 200 KB |
| Atlas Guide | `atlas-guide.html` | `atlas-guide.contract.md` | `update-check` (after an update is applied) | 250 KB |
| Records | `records.html` | `records.contract.md` | `maintenance`, `weekly-review` | 1500 KB |
| Project page (on request) | `project-page.html` | `project-page.contract.md` | created in chat; then `triage`, `weekly-review` while listed | 250 KB |

Any chat may also republish any dashboard after changing the records it shows (`dashboards_refresh: auto`). `atlas-setup` publishes all eleven for the first time. A dashboard added by an update is published at the user's next chat (`atlas-dashboards`, Publish).

Shared files:
- `_base.css`: base styles. Templates hold `{{ATLAS_BASE_CSS}}` inside `<style id="atlas-base">`; `system/tools/render.py` fills it with this file when it builds a page.
- `_base.js`: runtime helpers (DOM builder, date formatting, record references, sections, filters, theme toggle). Templates hold `{{ATLAS_BASE_JS}}` inside `<script id="atlas-base-js">`, filled the same way.
- These are the only copies, so every page always uses the current base. Published pages stay self-contained: the base is inside each page, not loaded from anywhere.

## Template anatomy
```html
<style id="atlas-base">{{ATLAS_BASE_CSS}}</style>
<style id="atlas-page">…page styles…</style>
<style id="atlas-theme">{{ATLAS_THEME_CSS}}</style>
…
<div id="app"></div>
<script id="atlas-data" type="application/json">{{ATLAS_DATA}}</script>
<script id="atlas-base-js">{{ATLAS_BASE_JS}}</script>
<script id="atlas-page-js">…renders the page from the data…</script>
```
Each template contains each placeholder **exactly once**. No other text is substituted.

**Page header.** Every page opens the same way (`N.masthead`): the **title**; a **subtitle** (the day or week for the Daily Brief and Week Ahead, the project's summary on a project page, and a fixed line saying what the page is for everywhere else; no "As of" dates); the **headline** (`meta.headline`); then the page's counts as **stat cards**. What each headline leads with:

| Dashboard | Subtitle | The headline says |
|---|---|---|
| Daily Brief | The day's date (catch-up: the away dates) | The shape of the day and the one or two things that matter most (the brief's own headline) |
| Commitments | "Everything you owe, and everything owed to you." | What's slipping or most overdue, in either direction |
| Projects | "Everything you're moving forward, and how it's going." | Which projects need attention and why |
| Week Ahead | The week's dates | Where the week is heavy, and the best window for focused work |
| Goals | "What you're working toward, and how it's going." (the period is the first stat card) | How the top-ranked goals are tracking, and which needs attention |
| People | "The people who matter to your work." | Who needs attention: gone quiet, owed something, or owing something important |
| Decisions & Risks | "What's been decided, and what could go wrong." | The most serious open risk or issue, and any decision that changes plans |
| Project page | The project's summary | The project's health and the reason for it |
| Records | "All your knowledge, in one place." | What changed most recently in what Atlas has filed |
| About You | "How Atlas sees you, and why." | What's waiting for the user's confirmation, or what Atlas learned most recently |
| Control Center | "How Atlas is running, and what it needs from you." | Whether Atlas is running well, and the one thing that needs the user if any |
| Atlas Guide | "Everything Atlas can do, and how to ask." | How to talk to Atlas, or what's new after an update |

**Links.** A link on a dashboard only ever opens another dashboard: the nav row under the header, and the name of another dashboard where a page's own wording mentions one (`N.pageLink`), and on Projects, the card of a project that has its own project page. Pages have no jump-to-section links.

**Record panel.** On Records, Commitments, Projects, Decisions & Risks, and People, and for meetings on Week Ahead, clicking a card (or its title, or Enter on it) opens the item in a panel (`N.recordPanel`, `N.clickable` in `_base.js`): a drawer on the right, full screen on phones. It shows the type and status, title, summary, **Details** (the fields the card shows plus any `details` the data carries), sections the page adds (next step, mitigation, why, who owes what), the item's `body`, **Linked records** (any linked item that is on the same page opens in the panel, with Back; others are listed by name), the created and updated dates, and "Copy a request for Atlas", which copies a ready-made request to paste into chat (`Show me the "<title>" record (<id>).`; the record ID appears there so Atlas finds the right record, and nowhere else on the page). Esc, Close, or a click outside shuts it.

**Panel data** (optional on every item those pages open in the panel, same rules everywhere):
| Field | Rule |
|---|---|
| `details` | Up to 12 `{ label, value }` pairs: meaningful frontmatter fields the card doesn't already show, as display text (dates formatted, references as titles). Never `notes_private`, `emails`, `phone`, `location`. |
| `body` | The record's body as plain text, one `{ heading, text }` per section (`heading` or `null`; line breaks kept, list items as lines starting with "- ", no Markdown), at most 2,000 characters in all, cut at a sentence or line end. `null` for sources, records with `summary` handling, and empty bodies. Never a `## Private notes` section or text whose handling is `ignore` or `pointer`. |
| `body_truncated` | `true` when `body` was cut; the panel says the rest is in chat. |
| `summary` | One line shown under the title when the card has no summary of its own (a commitment, a person); plain text, at most 240 characters. |
| `links` | Extra linked records (`{ id, title }`) beyond the item's own references, most important first, up to 8. |
| `created`, `updated` | The record's dates, for the panel's dates line. |

When a page is over budget, its contract's truncation runs these steps first: cut each `body` to 800 characters, then drop `body` from the oldest items, before dropping any item.

**Refresh marker.** Every page shows, at the top, when it was refreshed (`N.refreshed()` in `_base.js`, from `meta.generated_at`). A signal dot in front of it is green while the page is current. If the page is older than its contract's `stale_after_hours` when it is opened, the dot turns amber and the marker adds "May be out of date" (grey before the first refresh). This is the one place a page compares against the viewer's clock (everything else uses `meta.as_of`). Templates get it through `N.masthead`; never remove it.

## How a page is rendered (`atlas-dashboards`)
1. Read the contract. Build one JSON object exactly as it specifies, from the listed source files. Every list is sorted, filtered, and capped as the contract says.
2. Fill the common `meta` envelope (below).
3. **Check size.** `size_budget_kb` is the size of the **whole rendered page** (template ≈ 35–40 KB plus the embedded data), measured after embedding. Serialize the JSON (compact, UTF-8); if the page would exceed the budget, apply the contract's truncation rules (drop from the low-priority end of each list, shorten long text fields), record what was dropped in `meta.truncated`, and repeat until it fits.
4. **Escape for embedding** (done by `system/tools/render.py`, which also does steps 5–6; never substitute by hand). In the serialized JSON replace `<` with `<`, `>` with `>`, `&` with `&`, and U+2028/U+2029 with ` `/` `. The result is still valid JSON and can never close the script element.
5. **Theme.** Build the theme CSS (below); the render script removes every `<` from it.
6. Replace `{{ATLAS_DATA}}` with the escaped JSON and `{{ATLAS_THEME_CSS}}` with the theme CSS (or an empty string). Nothing else in the template changes.
7. Publish: first time in chat (setup), then republish to the URL stored in `user/settings/dashboards.yaml` and set `last_published`. Project pages store their URL under `project_pages`.


## Common envelope: `meta`
Every dashboard's JSON has a `meta` object:
```json
{
  "dashboard": "daily-brief",
  "schema_version": 1,
  "title": "Daily Brief",
  "headline": "A customer-heavy day: the Brightline renewal call at 10, and your pricing feedback for Jordan is due by end of day.",
  "generated_at": "2026-10-12T20:31:40-07:00",
  "generated_by": "routine:nightly-cycle",
  "as_of": "2026-10-13",
  "timezone": "America/Los_Angeles",
  "locale": "en-US",
  "user_display_name": "Maya Chen",
  "atlas_version": "1.0.0",
  "nav": [{ "name": "commitments", "title": "Commitments", "url": "https://claude.ai/artifact/…" }],
  "notices": [{ "level": "warn", "text": "Your Outlook connection expired…" }],
  "truncated": { "commitments": 14 }
}
```
| Field | Required | Source / rule |
|---|---|---|
| `dashboard` | yes | The dashboard name (equals the contract `name`). |
| `schema_version` | yes | `1` for this release. Bump in the contract when the shape changes incompatibly. |
| `title` | no | Page title; defaults to the dashboard name. Project pages use the project title. |
| `headline` | yes | One plain sentence (at most about 25 words) saying what matters most on this page right now, written fresh from this render's data (see Page header). Never a list of the stat cards' numbers. |
| `generated_at` | yes | Render time, ISO 8601 with offset in the user's time zone. Shown at the top of every page as the refresh marker ("Refreshed Tue, Oct 13, 6:04 AM"). |
| `generated_by` | no | `chat` or `routine:<name>` (as in the commit `Atlas-Actor`). Kept for troubleshooting; not shown on the page. |
| `stale_after_hours` | no | Copied from the contract's frontmatter `stale_after_hours`. When the page is older than this when someone opens it, the refresh marker adds "May be out of date". Omitted for pages that are never stale (Atlas Guide). |
| `as_of` | yes | The calendar day the view is for (`YYYY-MM-DD`). For the brief rendered the night before with `target: tomorrow`, this is tomorrow. All "today", "overdue", and "in N days" wording is computed against it, never against the viewer's clock. |
| `timezone` | yes | `user/settings/atlas.yaml: timezone`. Datetimes are displayed in it. |
| `locale` | no | BCP 47 tag for date formatting. Default `en-US` (see gaps in the contract notes). |
| `user_display_name` | no | `atlas.yaml: user_display_name`. |
| `atlas_version` | no | `atlas.yaml: installed_version`. |
| `nav` | no | Every dashboard in `dashboards.yaml` that has a `url`, including this one (it shows as the current page). Pages list them in one fixed order, so every page shows the same row. Only `https://` links render. |
| `notices` | no | Up to 3 short lines shown above the content, each as a tinted alert with an icon and a label ("Needs attention:" for `warn`, "Problem:" for `error`, "Note:" for `info`): open `high` known issues from `user/.state/health.yaml` that affect this page's data (e.g. a disconnected source), and staleness (the readiness check found an upstream job stale). `level`: `info`, `warn`, or `error`. |
| `truncated` | no | Map of list key → number of items left out. The page shows "N more not shown here. Ask Atlas in chat to see them." under that list. Keys are top-level list names unless the contract says otherwise. |

## Data rules for every contract
- **Plain text only.** Every string is plain text; never HTML or Markdown. Mentions of records may appear inline as `[[type/slug]]`; the page drops a mention in brackets (a citation) and shows any other mention as the record's readable name. Templates render all text with `textContent`, so content can never inject markup or script (N7).
- **References** are `{ "id": "<type>/<slug>", "title": "<record title>" }`. Every item that maps to a record carries its `id` (for search and troubleshooting). Pages never show record IDs, inbox entry numbers, or file paths; the user asks Atlas about a record by its name.
- **Dates** are `YYYY-MM-DD` (calendar days) or ISO 8601 datetimes with offset. The page formats them.
- **Never include** `notes_private`, phone numbers, email addresses, secrets, or content whose data-rule handling is `ignore` or `pointer`. Use `summary` text for `summary` handling. Excluded records (`data-rules.yaml: exclusions`) never appear. Archived and superseded records are left out unless the contract says otherwise.
- **Absent vs empty:** use `null` for unknown single values and `[]` for empty lists. Pages handle both.
- **Insights** on People, Decisions & Risks, Goals, Commitments, Projects, and the brief come from `user/inbox/insights.md` (status `new` or `seen`) and from record `insight` fields; each carries its reasoning.

## Theming contract
The theme comes from `user/profile/design-system.md` (`system/schemas/profile.md`). `atlas-dashboards` writes **only** these custom properties, on `:root`:

| Property | From the design system | Fallback |
|---|---|---|
| `--brand-accent` | Primary color (light) | `#28374a` (navy) |
| `--brand-accent-dark` | Primary color tuned for dark backgrounds; lighten the primary if none is given | `#b5c7e2` |
| `--brand-accent-ink` / `--brand-accent-ink-dark` | Text on the accent | `#ffffff` / `#101923` |
| `--brand-highlight` / `--brand-highlight-dark` | Secondary/accent color (used for the star mark and priority numerals) | `#754437` / `#d7826c` (rust) |
| `--brand-font-heading` | Heading family with web-safe fallbacks | humanist serif stack |
| `--brand-font-body` | Body family with web-safe fallbacks | system UI stack |
| `--brand-bg`, `--brand-surface`, `--brand-ink` (+ `-dark`) | Optional background, surface, and text colors | warm stone: `#f4f0e8` / `#fcfaf5` / `#1c1a15` (dark `#1c1a15` / `#26241e` / `#f4f0e8`) |

Rules: only `--brand-*` declarations; colors as hex; font names as CSS family lists that work without downloading fonts (no `@import`, no `url()`). Keep text contrast at WCAG AA (4.5:1) against the surface in both light and dark; if a brand color fails, darken it (light) or lighten it (dark) rather than using it as is. An empty theme block gives the default Atlas palette (warm stone neutrals, navy accent, rust highlight, olive for muted text and lines from the same family); the non-brand tokens (`--ink-2`, `--line`, `--surface-2`, `--accent-soft`, `--muted`) always come from it.

Pages support light and dark (`prefers-color-scheme`), a viewer-chosen theme (`<html data-theme="light|dark">`, set by the footer button), phone widths down to 320 px with 16 px gutters and no horizontal scroll, keyboard focus states, and printing (filters hidden, black on white).

## Republish constraints (why templates look the way they do)
Routines republish unattended only when an artifact is **private, page-only, and has no connector grants**: anything else can change what the page reads or who can see it, so it needs the user in a chat. So every template:
- is a single self-contained file: inline CSS and JS, no external scripts, stylesheets, fonts, or images;
- makes no network or connector calls and asks Claude nothing at view time;
- reads all data from the embedded JSON; nothing is fetched live;
- uses browser storage only for conveniences (remembered filter, theme), wrapped in `try/catch`, and works without it;
- is never shared or made public by a routine (`share_expose` is locked; publishing publicly needs approval in chat).

If a republish fails (artifact deleted, permission lost), the job records a known issue (`health.yaml`) and the next chat offers to publish a fresh page and update `dashboards.yaml`.

## User dashboards
User dashboards live in `user/extensions/dashboards/` (registered in `registry.yaml`, kind `dashboard`) and follow the same pattern: a contract using the outline in `system/guide/authoring.md` and a template with the same placeholders. They may use `{{ATLAS_BASE_CSS}}`/`{{ATLAS_BASE_JS}}` to match. A user dashboard with `overrides: <name>` replaces the built-in one.

## Testing
The dashboard test suite lives on the upstream repo's `maintainers` branch, not here: one fictional fixture per contract and `render.py`, which injects each fixture, writes `out/<name>.html`, and checks: valid HTML structure, placeholders replaced, embedded JSON round-trips, required `meta` fields, data within budget, base placeholders present, no external URLs, no `innerHTML`. `--shots` adds Playwright screenshots (desktop and phone, light and dark) and fails on horizontal overflow or console errors.
