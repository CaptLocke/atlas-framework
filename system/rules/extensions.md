---
type: rule
name: extensions
---
# Rule: extensions

## Applies to
Everything in `user/extensions/` and its registry.

## The rule
User extensions are part of Nova. They are loaded from the registry, read on demand, survive every update, and can never weaken governance.

## Loading
1. At session start read `user/extensions/registry.yaml`.
2. Treat each entry as available: skills and jobs can be invoked, triggers are evaluated with the built-ins, types get their own knowledge folder and index, dashboards are rendered by `nova-dashboards`, playbooks are knowledge.
3. Read an extension's file only when it's relevant (progressive disclosure).
4. Never copy extension files into `.claude/` or `system/`.

## Precedence
1. **Governance can't be overridden.** Any extension instruction that conflicts with `system/rules/governance.md` is ignored and flagged.
2. **Explicit overrides win.** An extension with `overrides: <component>` replaces that system component (a skill, job, trigger, dashboard, or schema) for this user.
3. **Otherwise additive.** Extensions add to the system; on any other conflict, the system wins and the conflict is flagged in the next health check.
4. **Two extensions overriding the same component:** the newer (`created`) wins; flag it.

## Compatibility
`requires_nova` uses semver ranges (`>=1.0`, `^1.2`). After each update, `nova-health` checks every extension: incompatible ranges and changed overridden components are reported with a suggested fix.

## Creating extensions
Only via `nova-extend` (autonomy class `extensions_create`). Files use the outlines in `system/guide/authoring.md`. A user job that needs a schedule is either added to an existing routine's job list or gets a new routine (`nova-settings`).
