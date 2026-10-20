---
name: atlas-dashboards
description: "Publish and refresh Atlas's pages (Today, Work, Guide), project pages and user dashboards, and keep their links. Use for \"update my dashboards\", \"where's my Work page?\", \"make a page for Orion\", \"send me the link to my brief\"."
---
# Dashboards

## Purpose
Keep three always-current, browsable pages, Today, Work and Guide, plus project pages on request and the user's own dashboards. Each page is a self-contained HTML file built from a system template with the data embedded, themed to the user's design system, and published privately so routines can refresh it unattended.

## When to use
- Setup step 11: publish all three (`atlas-setup`).
- Jobs (per each contract's `republished_by`, e.g. `daily-brief`, `triage`, `weekly-review`, `monthly`): republish the dashboards whose data changed.
- Skills after relevant changes: `atlas-settings`/`atlas-away` (Guide, Today), `atlas-update` (Guide), `atlas-review` (Work; Guide after the monthly and quarterly reviews), `atlas-health` (Guide).
- User: "refresh my dashboards", "I lost the link to …", "make a project page for Orion", "add the deals dashboard I built".
- Dashboards are views only. Requests to change things *from* a dashboard ("mark that done") are handled in chat by the owning skill, then the page is republished.

## Inputs
- `system/dashboards/<name>.html` (template) and `system/dashboards/<name>.contract.md` (data shape, sources, `republished_by`, `size_budget_kb`, rendering notes) for the three dashboards and `project-page`.
- User dashboards: `user/extensions/dashboards/<name>.html` + `<name>.contract.md`, registered in `user/extensions/registry.yaml` (kind `dashboard`). A user dashboard with `overrides: <system dashboard>` replaces it (`system/rules/extensions.md`).
- The files named in each contract's "Sources" section; `user/profile/design-system.md` for theme; `user/settings/dashboards.yaml` for URLs.
- Rendering detail, theming, size trimming, and publishing rules: `reference/rendering.md`.

## Procedure
### Render (every publish or republish)
1. **Pick the template and contract** (user override or extension first, then system).
2. **Build the data** exactly in the contract's JSON shape, reading only the sources it lists. Fill `meta.nav` with every dashboard in `dashboards.yaml` that has a `url` (the page sorts them). Write `meta.headline`: one plain sentence on what matters most on this page right now, from this render's data (what each page's headline leads with: `system/dashboards/README.md` §Page header). Set `meta.generated_at` to the render time and `meta.generated_by` to `chat` or `routine:<name>`, and copy the contract's `stale_after_hours` into `meta` when it has one: together they drive the refresh marker every page shows. Every item that represents a record carries its record ID (used for search and the record panel; pages never show it). Never include `notes_private`, content stored as `pointer`, or anything the data rules exclude. Dates in the user's time zone and locale.
3. **Theme** from `design-system.md` into the `--brand-*` tokens (`system/dashboards/README.md` §Theming contract); if there is no design system, leave the theme empty and the default Atlas palette applies.
4. **Fit the size budget** (`size_budget_kb`): if the data is too large, trim by the contract's rules (oldest and lowest-priority items first, cap lists, summarize long text), and record what was left out in `meta.truncated` (the page then says "N more not shown here"). Never exceed the budget.
5. **Embed** with the render script, never by hand: write the JSON to `.atlas-tmp/dashboards/<name>.json` and the theme to `.atlas-tmp/dashboards/theme.css` (or pass `-` for none), then run `python3 -I system/tools/render.py <template> .atlas-tmp/dashboards/<name>.json <theme or -> .atlas-tmp/dashboards/<name>.html`. It escapes the data so text from emails or documents can't run as code, and prints the page size (never committed). Check: under budget, no secrets. Templates carry a content security policy, so a page can't load or send anything from the network.

### Publish (first time, chat only)
6. Publish the page as a **private** artifact: page only (no extra files), no connector or data grants, no runtime capabilities, nothing public or shared. Save the URL and `last_published` in `user/settings/dashboards.yaml` (project pages under `project_pages: { <project ID>: url }`; user dashboards as an additional key named after the extension). Commit.

### Republish (chats and routines)
7. Republish to the stored URL with the new page (same title). Keep it private, page-only, without grants, so routines can update it unattended. Update `last_published`. Batch: render and republish only dashboards whose sources changed since `last_published`, plus any the caller names.
8. **If republish fails:** in a routine, record it in the run report and as a known issue in `user/.state/health.yaml` ("Dashboards couldn't update; I'll refresh them when you next chat"), don't retry endlessly; in a chat, retry once, then publish a new private page, update the URL, tell the user the new link, and close the known issue. If a URL is missing (never published, or lost), publish fresh in a chat; a routine records a known issue instead. A built-in dashboard with no entry in `dashboards.yaml` at all (new in an update) is added there with `url: null` and published at the next chat, with one line telling the user what it is ("New: a page that shows …", in a sentence); routines skip it without a known issue.

### Project pages and user dashboards
9. **Project page** ("make a page for Orion"): resolve the project, render `project-page` with that project's data, publish privately, store in `project_pages`. Republish it when the project changes (`triage`, `weekly-review`) while it's listed. Remove the entry (not the page) if the user says they no longer need it; deleting the published page is `destructive` and needs approval. After adding or removing a `project_pages` entry, republish Work so that project's card opens the page (or stops linking to it).
10. **User dashboard:** created by `atlas-extend` (template + contract in `user/extensions/dashboards/`); this skill renders and publishes it like a system dashboard and adds its key to `dashboards.yaml`.

### Links
11. When the user asks for a dashboard, give its stored link. If they ask to share it with someone, that's `share_expose` (locked): follow the approval-record procedure; never make a page public otherwise.

## Outputs
- Published/republished private pages; `user/settings/dashboards.yaml` URLs and `last_published` dates.
- Rendered files only in `.atlas-tmp/dashboards/` (git-ignored).
- Run-report lines ("republished 4 dashboards") or a one-line chat note; known issues on failure.

## Guardrails
- Governance: `system/rules/governance.md`. Classes touched: `dashboards_refresh` (auto: render, publish privately, republish), `behavior_settings` (adding/removing entries in `dashboards.yaml` at the user's request), `share_expose` 🔒 (sharing or making any page public: approval record, chat only, never in routines), `destructive` 🔒 (deleting a published page).
- Pages stay private, page-only, and without connector grants; anything else breaks unattended republish and may expose data.
- Data rules apply to dashboards exactly as to answers: excluded and pointer-only content never appears; `notes_private` never appears.
- Never put secrets, tokens, or the repo's credentials into a page.
- Dashboards never take actions; no forms that change data.

## Done when
- Each requested dashboard is rendered from the right template, matches its contract's shape, is under budget, and is published privately at the URL recorded in `dashboards.yaml` with today's `last_published`.
- Every record shown carries its record ID in the data; pages show only the title (never IDs, inbox entry numbers, or file paths).
- Failures are recorded as known issues with a plain-language fix, and cleared once fixed.
