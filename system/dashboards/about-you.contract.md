---
type: dashboard-contract
name: about-you
template: about-you.html
republished_by: [monthly, quarterly]
size_budget_kb: 200
stale_after_hours: 768
---
# Dashboard: about-you

## Purpose
Everything Nova believes about the user (profile basics, working, communication and thinking style, preferences, both voice guides, design system), each statement with where it came from and whether it is confirmed, plus the observations waiting for the user's OK. It makes personalization inspectable: anything wrong is fixed by telling Nova in chat (`profile_update`).

Republished by `monthly` (after the user health check) and `quarterly` (after the role refresh). A chat that changes the profile, or confirms or rejects a profile proposal, republishes it too.

## Data (JSON shape embedded in the page)
```json
{
  "meta": { "dashboard": "about-you", "schema_version": 1, "as_of": "2026-10-01", "…": "…" },
  "counts": { "statements": 19, "confirmed": 17, "proposed": 2 },
  "basics": { "name": "Maya Chen", "role": "Product Manager, Platform",
              "company": { "id": "organizations/acme", "title": "Acme" },
              "manager": { "id": "people/jordan-lee", "title": "Jordan Lee" },
              "timezone": "America/Los_Angeles (Pacific)", "self": { "id": "people/maya-chen", "title": "Maya Chen" },
              "key_people": [ { "id": "people/priya-nair", "title": "Priya Nair" } ],
              "goals": [ { "id": "goals/2026-q4-retention", "title": "Q4 retention" } ] },
  "proposals": [ { "id": "Q-2026-09-30-01", "text": "Should I default to shorter emails?",
                   "proposed_change": "Keep emails under about 120 words (personal voice)", "asked": "2026-09-30" } ],
  "files": [
    { "part": "communication-style", "title": "How you like information", "path": "user/profile/communication-style.md",
      "updated": "2026-09-25", "description": "Length, format, and how to lead.",
      "groups": [ { "heading": null, "statements": [
        { "text": "Bullet summaries over prose for status updates.", "provenance": "observed", "status": "confirmed",
          "date": "2026-10-02", "evidence": [ { "id": "sources/2026-09-30-status-draft-edits" } ] } ] } ] }
  ],
  "design": { "path": "user/profile/design-system.md", "summary": "…",
              "colors": [ { "name": "Acme Teal", "hex": "#0F5C5C", "use": "primary" } ],
              "fonts": [ { "role": "Headings", "family": "Source Serif 4, Georgia" } ] }
}
```
Full example: `system/tests/dashboards/about-you.json`.

| Field | Notes |
|---|---|
| `statements[].provenance` | `stated`, `observed`, `researched`, `uploaded` (profile tag grammar, `system/schemas/profile.md`). |
| `statements[].status` | `confirmed` (agreed or stated) or `proposed`. A `stated` line with no status is `confirmed`. Proposed lines normally live in `proposals`, not in files. |
| `statements[].date` | The date in the tag. `evidence` = the tag's source links as `{ "id" }`. |
| `files[].part` | File stem; order: working-style, communication-style, thinking-style, preferences, voice-personal, voice-house. |

## Sources (file → field)
| Field | Source |
|---|---|
| `basics` | `user/profile/profile.md` (name, role, company, manager, key people, goals, time zone, self record) |
| `files[]` | Each profile file's frontmatter (`part`, `updated`); every `## heading` → a group; every statement line → a statement, parsed from its `[provenance · status date · evidence]` tag. `title`/`description` are fixed plain-language labels per part (the page shows them) |
| Voice guides | `voice-personal.md`, `voice-house.md`: include the `Summary`, `Tone`, `Vocabulary`, and `Don't` groups; skip `Examples` (excerpts may quote other people) |
| `design` | `user/profile/design-system.md`: `Brand summary` → `summary`; `Colors` → `colors` (name, hex, use; light values); `Typography` → `fonts` |
| `proposals[]` | `user/inbox/questions.md`, kind `profile`, status `open` |
| `counts` | Totals over all statement lines (`proposed` includes open profile proposals) |

## Rendering notes
- Never include protected or sensitive attributes (they are not allowed in the profile at all; if one is found, leave it out and flag it in the health check).
- Statements keep file order. Proposed statements are visually distinct and labeled "Not yet confirmed".
- Caps: 40 statements per file, 20 proposals, 12 colors. Over budget, drop the oldest statements in the longest file first; `meta.truncated` keys are `files.<part>` and `proposals`.
- Text limit: 300 characters per statement.
- Swatch colors are only rendered from valid hex values; anything else shows an empty swatch.
