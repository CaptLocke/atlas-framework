---
type: dashboards-readme
version: 1.0.0
---
# Dashboards

Dashboards are browsable pages Nova keeps up to date. Each one is a **published Claude artifact**: a private, self-contained HTML page built from a template in this folder with the data embedded at render time. Dashboards are views only; every change happens in chat, where Nova updates the underlying records and republishes.

The `nova-dashboards` skill owns rendering and publishing. This folder holds what it renders from: one **template** (`<name>.html`) and one **data contract** (`<name>.contract.md`) per dashboard.

## The dashboards
| Dashboard | Template | Contract | Republished by | Page budget |
|---|---|---|---|---|
| Daily Brief | `daily-brief.html` | `daily-brief.contract.md` | `daily-brief` job; chat catch-up | 120 KB |
| Work Board | `work-board.html` | `work-board.contract.md` | `daily-brief`; `triage` (optional) | 300 KB |
| Goals (with accomplishments) | `goals.html` | `goals.contract.md` | `weekly-review`, `monthly`, `quarterly` | 200 KB |
| Week Ahead | `week-ahead.html` | `week-ahead.contract.md` | `daily-brief`, `weekly-review` | 150 KB |
| People | `people.html` | `people.contract.md` | `weekly-review` | 250 KB |
| Decisions & Risks | `decisions-risks.html` | `decisions-risks.contract.md` | `weekly-review` | 300 KB |
| Control Center | `control-center.html` | `control-center.contract.md` | `daily-brief`, `monthly` | 200 KB |
| About You | `about-you.html` | `about-you.contract.md` | `monthly`, `quarterly` | 200 KB |
| Nova Guide | `nova-guide.html` | `nova-guide.contract.md` | `update-check` (after an update is applied) | 250 KB |
| Project page (on request) | `project-page.html` | `project-page.contract.md` | created in chat; then `triage`, `weekly-review` while listed | 250 KB |

Any chat may also republish any dashboard after changing the records it shows (`dashboards_refresh: auto`). `nova-setup` publishes all nine for the first time.

Shared files:
- `_base.css`: canonical base styles. **Every template inlines it verbatim** inside `<style id="nova-base">`.
- `_base.js`: canonical runtime helpers (DOM builder, date formatting, record IDs, sections, filters, theme toggle). **Every template inlines it verbatim** inside `<script id="nova-base-js">`.
- After editing either file, run `python3 system/tests/dashboards/render.py --sync`, then `render.py --check`. Templates must never drift from the canonical copies.

## Template anatomy
```html
<style id="nova-base">…_base.css…</style>
<style id="nova-page">…page styles…</style>
<style id="nova-theme">{{NOVA_THEME_CSS}}</style>
…
<div id="app"></div>
<script id="nova-data" type="application/json">{{NOVA_DATA}}</script>
<script id="nova-base-js">…_base.js…</script>
<script id="nova-page-js">…renders the page from the data…</script>
```
Each template contains each placeholder **exactly once**. No other text is substituted.

## How a page is rendered (`nova-dashboards`)
1. Read the contract. Build one JSON object exactly as it specifies, from the listed source files. Every list is sorted, filtered, and capped as the contract says.
2. Fill the common `meta` envelope (below).
3. **Check size.** `size_budget_kb` is the size of the **whole rendered page** (template ≈ 35–40 KB plus the embedded data), measured after embedding. Serialize the JSON (compact, UTF-8); if the page would exceed the budget, apply the contract's truncation rules (drop from the low-priority end of each list, shorten long text fields), record what was dropped in `meta.truncated`, and repeat until it fits.
4. **Escape for embedding.** In the serialized JSON replace `<` with `<`, `>` with `>`, `&` with `&`, and U+2028/U+2029 with ` `/` `. The result is still valid JSON and can never close the script element.
5. **Theme.** Build the theme CSS (below). Remove any `</` sequence from it.
6. Replace `{{NOVA_DATA}}` with the escaped JSON and `{{NOVA_THEME_CSS}}` with the theme CSS (or an empty string). Nothing else in the template changes.
7. Publish: first time in chat (setup), then republish to the URL stored in `user/settings/dashboards.yaml` and set `last_published`. Project pages store their URL under `project_pages`.

`system/tests/dashboards/render.py` implements steps 4 to 6 exactly; use it as the reference.

## Common envelope: `meta`
Every dashboard's JSON has a `meta` object:
```json
{
  "dashboard": "daily-brief",
  "schema_version": 1,
  "title": "Daily Brief",
  "generated_at": "2026-10-12T20:31:40-07:00",
  "generated_by": "routine:nightly-cycle",
  "as_of": "2026-10-13",
  "timezone": "America/Los_Angeles",
  "locale": "en-US",
  "user_display_name": "Maya Chen",
  "nova_version": "1.0.0",
  "record_base_url": null,
  "nav": [{ "name": "work-board", "title": "Work Board", "url": "https://claude.ai/artifact/…" }],
  "notices": [{ "level": "warn", "text": "Your Outlook connection expired…" }],
  "truncated": { "commitments": 14 }
}
```
| Field | Required | Source / rule |
|---|---|---|
| `dashboard` | yes | The dashboard name (equals the contract `name`). |
| `schema_version` | yes | `1` for this release. Bump in the contract when the shape changes incompatibly. |
| `title` | no | Page title; defaults to the dashboard name. Project pages use the project title. |
| `generated_at` | yes | Render time, ISO 8601 with offset in the user's time zone. Shown in the footer. |
| `generated_by` | no | `chat` or `routine:<name>` (as in the commit `Nova-Actor`). |
| `as_of` | yes | The calendar day the view is for (`YYYY-MM-DD`). For the brief rendered the night before with `target: tomorrow`, this is tomorrow. All "today", "overdue", and "in N days" wording is computed against it, never against the viewer's clock. |
| `timezone` | yes | `user/settings/nova.yaml: timezone`. Datetimes are displayed in it. |
| `locale` | no | BCP 47 tag for date formatting. Default `en-US` (see gaps in the contract notes). |
| `user_display_name` | no | `nova.yaml: user_display_name`. |
| `nova_version` | no | `nova.yaml: installed_version`. |
| `record_base_url` | no | `null` by default. If set (e.g. `https://github.com/<repo>/blob/main/user/knowledge/`, from `nova.yaml: repo`), record IDs become links to the record file. Leave `null` unless the user asks; the ID text alone is enough to ask Nova. |
| `nav` | no | Links to the other dashboards, from `dashboards.yaml` entries that have a `url`. Only `https://` links render. |
| `notices` | no | Up to 3 short lines shown above the content: open `high` known issues from `user/.state/health.yaml` that affect this page's data (e.g. a disconnected source), and staleness (the readiness check found an upstream job stale). `level`: `info`, `warn`, or `error`. |
| `truncated` | no | Map of list key → number of items left out. The page shows "N more not shown here. Ask Nova in chat to see them." under that list. Keys are top-level list names unless the contract says otherwise. |

## Data rules for every contract
- **Plain text only.** Every string is plain text; never HTML or Markdown. Mentions of records may appear inline as `[[type/slug]]`; the page renders them as record IDs. Templates render all text with `textContent`, so content can never inject markup or script (N7).
- **References** are `{ "id": "<type>/<slug>", "title": "<record title>" }`. Every item that maps to a record carries its `id`, and the page shows the ID next to the title so the user can ask Nova about it.
- **Dates** are `YYYY-MM-DD` (calendar days) or ISO 8601 datetimes with offset. The page formats them.
- **Never include** `notes_private`, phone numbers, email addresses, secrets, or content whose data-rule handling is `ignore` or `pointer`. Use `summary` text for `summary` handling. Excluded records (`data-rules.yaml: exclusions`) never appear. Archived and superseded records are left out unless the contract says otherwise.
- **Absent vs empty:** use `null` for unknown single values and `[]` for empty lists. Pages handle both.
- **Insights** on People, Decisions & Risks, Goals, Work Board, and the brief come from `user/inbox/insights.md` (status `new` or `seen`) and from record `insight` fields; each carries its reasoning.

## Theming contract
The theme comes from `user/profile/design-system.md` (`system/schemas/profile.md`). `nova-dashboards` writes **only** these custom properties, on `:root`:

| Property | From the design system | Fallback |
|---|---|---|
| `--brand-accent` | Primary color (light) | `#2b5a8a` |
| `--brand-accent-dark` | Primary color tuned for dark backgrounds; lighten the primary if none is given | `#8eb5e3` |
| `--brand-accent-ink` / `--brand-accent-ink-dark` | Text on the accent | `#ffffff` / `#0d1620` |
| `--brand-highlight` / `--brand-highlight-dark` | Secondary/accent color (used for the star mark and priority numerals) | `#a86f12` / `#e2b45c` |
| `--brand-font-heading` | Heading family with web-safe fallbacks | humanist serif stack |
| `--brand-font-body` | Body family with web-safe fallbacks | system UI stack |
| `--brand-bg`, `--brand-surface`, `--brand-ink` (+ `-dark`) | Optional background, surface, and text colors | neutral cool greys |

Rules: only `--brand-*` declarations; colors as hex; font names as CSS family lists that work without downloading fonts (no `@import`, no `url()`). Keep text contrast at WCAG AA (4.5:1) against the surface in both light and dark; if a brand color fails, darken it (light) or lighten it (dark) rather than using it as is. An empty theme block gives the neutral default look. Example: `system/tests/dashboards/theme-sample.css`.

Pages support light and dark (`prefers-color-scheme`), a viewer-chosen theme (`<html data-theme="light|dark">`, set by the footer button), phone widths down to 320 px with 16 px gutters and no horizontal scroll, keyboard focus states, and printing (filters hidden, black on white).

## Republish constraints (why templates look the way they do)
Routines republish unattended only when an artifact is **private, page-only, and has no connector grants** (tactical §9.1, §12). So every template:
- is a single self-contained file: inline CSS and JS, no external scripts, stylesheets, fonts, or images;
- makes no network or connector calls and asks Claude nothing at view time;
- reads all data from the embedded JSON; nothing is fetched live;
- uses browser storage only for conveniences (remembered filter, theme), wrapped in `try/catch`, and works without it;
- is never shared or made public by a routine (`share_expose` is locked; publishing publicly needs approval in chat).

If a republish fails (artifact deleted, permission lost), the job records a known issue (`health.yaml`) and the next chat offers to publish a fresh page and update `dashboards.yaml`.

## User dashboards
User dashboards live in `user/extensions/dashboards/` (registered in `registry.yaml`, kind `dashboard`) and follow the same pattern: a contract using the outline in `system/guide/authoring.md` and a template with the same placeholders. They may inline `_base.css`/`_base.js` to match. A user dashboard with `overrides: <name>` replaces the built-in one.

## Testing
`system/tests/dashboards/` holds one fictional fixture per contract and `render.py`, which injects each fixture, writes `out/<name>.html`, and checks: valid HTML structure, placeholders replaced, embedded JSON round-trips, required `meta` fields, data within budget, base files in sync, no external URLs, no `innerHTML`. `--shots` adds Playwright screenshots (desktop and phone, light and dark) and fails on horizontal overflow or console errors.
