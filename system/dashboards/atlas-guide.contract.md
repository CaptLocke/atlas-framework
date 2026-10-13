---
type: dashboard-contract
name: atlas-guide
template: atlas-guide.html
republished_by: [update-check]
size_budget_kb: 250
---
# Dashboard: atlas-guide

## Purpose
The user's reference for everything Atlas can do: features, example requests, automations, controls, troubleshooting (re-authorizing GitHub, reconnecting connectors), and What's new. Built mechanically from the guide content in `system/guide/` and from `CHANGELOG.md`, so it is the same for every user of a version (only `meta` differs).

Republished by `update-check` after an update is applied (and by `atlas-setup` at first publish). A chat may republish it on request.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "atlas-guide", "schema_version": 1, "as_of": "2026-10-11", "…": "…" },
  "version": "1.0.0",
  "intro": "Talk to Atlas the way you would to a capable assistant who has read all your notes.",
  "whats_new": [ { "version": "1.0.0", "date": "2026-10-12", "items": ["First public release of Atlas."] } ],
  "sections": [
    { "id": "troubleshooting", "title": "If something looks wrong", "source": "system/guide/troubleshooting.md",
      "intro": "Most problems are a connection that needs signing in again.",
      "items": [ { "id": "reconnect", "title": "A connection expired",
                   "body": ["The Control Center shows which tool needs attention."],
                   "bullets": [],
                   "steps": ["In Claude, open Settings, then Connectors.", "Choose Connect next to the tool.", "Tell Atlas you reconnected it."],
                   "examples": ["I reconnected Outlook"] } ] }
  ]
}
```
Full example: `system/tests/dashboards/atlas-guide.json`. All strings are plain text (inline Markdown emphasis and links are stripped to their text; inline code keeps its text).

## Sources (file → field)
| Field | Source |
|---|---|
| `version` | `system/VERSION` |
| `intro` | A one-paragraph welcome; the fixed text "Talk to Atlas in your Atlas project the way you would to a capable assistant who has read all your notes. You never need to manage files or settings; just ask." unless the guide adds one |
| `sections[]` | Every `system/guide/*.md` file with frontmatter `type: guide`, **except** `section: whats-new` and `section: attestation` (and never `README.md` or `authoring.md`), ordered by frontmatter `order`. `id` = frontmatter `section`; `title` = frontmatter `title` (or the `#` heading); `source` = the path. Structure convention: `system/guide/README.md` |
| `sections[].intro` | Paragraph text between the `#` heading and the first `##` |
| `sections[].items[]` | One per `##` heading: `id` = slug of the heading, `title` = heading text |
| `items[].body` | Each paragraph under the heading |
| `items[].steps` | Items of a numbered list |
| `items[].examples` | The bullet list after a `**Try:**` line, plus any bullet that is entirely a quoted request (`"…"`); quotes removed |
| `items[].bullets` | Items of any other bullet list |
| `whats_new[]` | `CHANGELOG.md`: each `## <version>` heading (optionally followed by a date in parentheses or after a dash) → one release; `items` = bullets under its `### What's new` subsection only (`### Under the hood` is never shown). Newest first, starting at the installed version (`atlas.yaml: installed_version`); never list releases newer than the installed one |

Guide sections in 1.0.0: `features`, `requests`, `automations`, `controls`, `troubleshooting`. Unknown extra guide files are included by `order`; nothing is required for the page to render. Where guide text says "by default", `atlas-dashboards` may personalize it from `routines.yaml` and `governance.yaml` as `system/guide/README.md` allows; any other user detail belongs on the Control Center.

## Rendering notes
- Page order: table of contents, search, What's new (latest three releases shown, earlier ones collapsed), then sections in order.
- Search matches titles, body, bullets, steps, and examples; sections with no matches are hidden, and an empty result says to ask Atlas in chat.
- Caps: 5 releases in `whats_new`; 40 items per section; 10 examples per item. Over budget, drop older releases first, then trim `body` paragraphs to 600 characters. `meta.truncated` keys are `whats_new` and `sections.<id>`.
- Sub-headings deeper than `##` are folded into the parent item's body as paragraphs.
