---
type: guide-index
audience: Nova (nova-dashboards, nova-setup, nova-update) and maintainers
---
# Nova Guide content

Source content for the **Nova Guide** dashboard and for answering "what can you do?" / "how do I…?" in chat. Written for the user, in plain language. The setup guide for new users lives in `docs/setup/` (it must work before Nova exists); the Guide links to it rather than repeating it.

## Files
| File | `section` | Holds |
|---|---|---|
| `features.md` | features | Every feature in plain language, with example requests |
| `requests.md` | requests | Cheat sheet of things to say, grouped |
| `automations.md` | automations | What runs when on each profile; what each automation does; triggers |
| `controls.md` | controls | Autonomy, approvals, data rules, forget/erase, away, pausing, profile changes |
| `troubleshooting.md` | troubleshooting | Reconnecting, stopped routines, missing brief, reporting an issue |
| `whats-new.md` | whats-new | How "What's new" is produced (from `CHANGELOG.md`) |
| `attestation.md` | attestation | The permission explanation and statement (used by `nova-setup` and `nova-review`) |
| `authoring.md` | (not user-facing) | Outlines for system files and extensions |

## Structure convention (for the dashboard data contract)
Every user-facing file follows the same shape so it maps directly to dashboard data:
- Frontmatter: `type: guide`, `section`, `title`, `order` (display order), `version` (Nova version the content describes).
- The `#` title is the section `title`; the paragraph after it is the section `intro`.
- Each `##` heading is one **item** (`items[].title`; `id` = the heading slug). There is no deeper level.
- Within an item: paragraphs → `body[]`; a bullet list → `bullets[]`; a numbered list → `steps[]`; a `**Try:**` line followed by a bullet list → `examples[]` (quotes stripped). This matches the data the `nova-guide.html` template renders (`sections[].items[]` with `body`, `bullets`, `steps`, `examples`).
- Cross-references name the other item in bold ("see **Automations**"), never a file path, so they read well on the dashboard.
- `whats-new.md` and `attestation.md` are not rendered as sections: What's new comes from `CHANGELOG.md` (`whats_new[]`), and the attestation text is used in conversation only.

Personalize when rendering: replace the generic profile names with the user's actual schedule from `user/settings/routines.yaml` and their autonomy levels from `governance.yaml` where the content says "by default".
