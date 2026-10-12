---
type: authoring-guide
audience: Nova maintainers and anyone writing system files or extensions
---
# Authoring Nova files

Every Nova instruction file follows one of the outlines below so files read consistently, stay short, and load cheaply. Instructions describe **outcomes and checks**, not brittle phrasing.

## General rules
- Markdown with YAML frontmatter. Sentence case headings. Plain language.
- Say what must be true when done ("every commitment has a direction and a due date or `due: null`"), not just steps.
- Reference other files by path (`system/rules/knowledge.md`) rather than repeating them.
- Size targets: kernel under ~300 lines; a `SKILL.md` under ~250 lines (move detail to `reference/*.md` beside it); a job spec under ~120 lines; a rule under ~200 lines.
- Never put user data, names, or secrets in system files.
- Locked behaviors (approvals, non-negotiables) are stated once in `system/rules/governance.md`; other files point to it.

## Skill outline (`.claude/skills/<name>/SKILL.md`)
```markdown
---
name: nova-<name>
description: <one sentence: what it does and when to use it, including typical user phrases>
---
# <Title>
## Purpose
## When to use
- Trigger phrases and situations (chat), and which jobs invoke it
## Inputs
## Procedure
1. ...
## Outputs
- Files written (exact paths), records changed, messages to the user
## Guardrails
- Autonomy classes involved; approvals; data rules; what never to do
## Done when
- Checkable conditions
```

## Job outline (`system/jobs/<job>.md`)
```markdown
---
type: job
name: <job>
model: fast | strongest
skills: [nova-..., ...]
---
# Job: <name>
## Purpose
## Runs when
- Profiles/routines that include it; date conditions; modifiers it honors (when, target, mode)
## Away and paused
## Readiness check
## Inputs
## Steps
## Outputs
## Early exit
## Guardrails
## Run report
- What this job adds to the run report
```

## Rule outline (`system/rules/<rule>.md`)
```markdown
---
type: rule
name: <rule>
---
# Rule: <name>
## Applies to
## The rule
## Details
## Examples
## Checks
```

## Schema outline (`system/schemas/<type>.md`)
```markdown
---
type: schema
name: <type>
folder: user/knowledge/<folder>/
---
# Schema: <type>
## What it is
## Fields (in addition to _common)
| Field | Type | Required | Values / notes |
## Status vocabulary
## Links
## Example
## Capture guidance
```

## Migration outline (`system/migrations/NNNN-<slug>.md`)
```markdown
---
type: migration
id: NNNN
from_data_version: N
to_data_version: N+1
additive: true | false
needs_user_input: true | false
---
# Migration NNNN: <title>
## Purpose
## Affected paths
## Transformation
## Validation
## Questions for the user
## Reverse step
```

## Dashboard contract outline (`system/dashboards/<name>.contract.md`)
```markdown
---
type: dashboard-contract
name: <name>
template: <name>.html
republished_by: [<job>, ...]
size_budget_kb: <n>
---
# Dashboard: <name>
## Purpose
## Data (JSON shape embedded in the page)
## Sources (file → field)
## Rendering notes
```
