# Security policy

Atlas keeps a person's work knowledge and can act through their connected tools, so security problems matter. Thank you for reporting them privately.

## Reporting a vulnerability

Please **don't open a public issue**. Use either:

- GitHub's private form: the repo's **Security** tab → **Report a vulnerability**, or
- email **atlas.framework.support@gmail.com** with **SECURITY** at the start of the subject.

Include what you found, how to reproduce it, and what an attacker could do with it. Don't include anyone's real data.

You'll get an acknowledgement within **7 days**. Fixes ship as a signed release; you'll be credited in the changelog unless you'd rather not be.

## In scope

- The safety hooks in `.claude/hooks/` and the rules they enforce (`system/rules/governance.md`)
- The update flow: release signatures (`system/tools/release_check.py`), `atlas-update`, rollback
- Dashboards: templates, the render script (`system/tools/render.py`), and the page security policy
- Anything that lets content (an email, a document, a web page) make Atlas send, share, delete, or change its own rules
- Issue reports leaking personal or work details (`atlas-report-issue`, `system/tools/redact_check.py`)

## Out of scope

- Claude, Cowork, GitHub, or connector services themselves (report those to their makers)
- Attacks that need control of the user's GitHub account or computer
- A user deliberately turning off a protection in their own copy

Known limits (where the hooks run, and the routes they don't cover) are described in `system/rules/governance.md`, in the paragraph on hooks under the non-negotiables.
