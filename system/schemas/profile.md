---
type: schema
name: profile
folder: user/profile/
---
# Schema: profile

The profile is who the user is and how they want Nova to behave. It is core configuration, and it links to knowledge.

## Files
| File | Holds |
|---|---|
| `profile.md` | Name, role, company (`[[organizations/...]]`) with a short company summary (what it does, industry, size, fiscal year; detail lives in the employer record, `organization.md` §Employer), manager and key people (links), responsibilities, current goals (links), time zone, the user's own person record (`[[people/<slug>]]`, `relationship: self`), public background (from LinkedIn, if shared) |
| `working-style.md` | How they plan, focus, prioritize, and like work organized |
| `communication-style.md` | How they like to receive information (length, format, numbers-first vs narrative), meeting habits |
| `thinking-style.md` | How they reason and decide (data-led, intuitive, collaborative), what they want challenged |
| `preferences.md` | Likes and dislikes about their work; standing behavior preferences for Nova ("never draft to my CEO without asking") |
| `voice-personal.md` | Personal voice guide (see below) |
| `voice-house.md` | Company/house voice guide (see below) |
| `design-system.md` | Company design system (see below) |
| `assets/` | Logo files and brand assets referenced by `design-system.md` |

## Frontmatter (every profile file)
```yaml
---
type: profile
part: working-style        # file stem
updated: 2026-10-12
---
```

## Statement lines
Profile content is a list of statements, one per line, each tagged:
```
- Prefers bullet summaries over prose for status updates [observed · confirmed 2026-10-02 · [[sources/2026-09-30-...]]]
- Wants risks stated before recommendations [stated · 2026-10-01]
```
Tag grammar: `[<provenance> · <status> <date> · <evidence links>]`
- **provenance:** `stated` (user said it), `observed` (seen in their behavior or edits), `researched` (public information), `uploaded` (from a document they provided).
- **status:** `confirmed` (user agreed or stated it) or `proposed` (awaiting confirmation; lives in `user/inbox/questions.md` until confirmed, see `nova-review` user health check). Only `confirmed` and `stated` lines may be relied on as fact.
- **evidence:** optional source links.

Group statements under `##` headings within each file. Never record protected or sensitive personal attributes (health, religion, etc.) in the profile.

## Voice guides
`voice-personal.md` and `voice-house.md` share this outline:
```markdown
## Summary            (3–5 lines: the voice in a nutshell)
## Tone
## Structure and length
## Vocabulary         (words they use; words they avoid)
## Openings and sign-offs
## Formatting habits
## Examples           (short excerpts with source links)
## Don't
```
Built at setup from writing samples, sent email (if connected), and research; refined from the user's edits to drafts.

## Design system
`design-system.md` outline:
```markdown
## Brand summary
## Colors            (name, hex, use: primary/secondary/accent/text/background; light and dark)
## Typography        (families with web-safe fallbacks; heading/body sizes)
## Logo              (paths in assets/, clear-space and placement rules)
## Layout            (grid, spacing, density preferences)
## Charts and data   (palette order, number formats)
## Document patterns (title slides, one-pagers, memos)
## Do / Don't
```
Used by `nova-write` for deliverables and by `nova-dashboards` for theming.

## Attestation
The user's permission to store work data is recorded in `user/settings/nova.yaml: attestation` (see `settings.md`), not in the profile.
