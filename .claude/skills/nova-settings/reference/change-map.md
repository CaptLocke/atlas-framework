---
type: skill-reference
skill: nova-settings
---
# Change map: request → file → class → follow-up

Formats: `system/schemas/settings.md`. Classes and locked levels: `system/rules/governance.md`.

| User says (examples) | File · field | Class | Follow-up |
|---|---|---|---|
| "Update my profile on your own", "ask before editing my journal" | `governance.yaml · autonomy.<class>` | `governance_settings` 🔒 | none |
| "Ask before filing anything about Acme", "auto-file everything from my calendar", "ask before CRM updates" | `governance.yaml · overrides` (`scope: organizations/acme` / `connector:google-calendar` / `category:crm`) | `governance_settings` 🔒 | none |
| "Never send without asking" / "let Nova send routine replies" | locked: refuse | n/a | offer preferences or override on `drafts_create` |
| "Store health info as pointers", "keep full copies of financial emails" | `data-rules.yaml · categories.<cat>` | `governance_settings` 🔒 | warn on loosening phi/legal_privileged/confidential |
| "Treat board materials as summaries" | `data-rules.yaml · custom[]` (`name`, plain-language `match`, `handling`) | `governance_settings` 🔒 | none |
| "Don't read #random", "ignore emails from newsletter.example.com", "skip my Personal calendar" | `data-rules.yaml · exclusions[]` (`messaging: channel:#random`, `mail: from:*@newsletter.example.com`, `calendar: series:Personal`) | `governance_settings` 🔒 | offer archive/forget of past items (`nova-memory`) |
| "Turn off Evening Thoughts / the weekly review / status updates" | `rhythms.yaml · moments.<moment>` | `behavior_settings` | none (jobs skip themselves) |
| "Status updates to Jordan and Priya on Thursdays" | `rhythms.yaml · moments.status_updates` (`audiences`, `day`) | `behavior_settings` | the job checks `day` itself; ensure a routine runs `status-updates` on that weekday, adding a small `status-updates` routine if none does |
| "My hours are 9 to 5, Mon–Thu" | `rhythms.yaml · work_hours` | `behavior_settings` | re-derive work-hour schedules; update platform routines |
| "Don't create people automatically", "deadline reminders 5 days ahead" | `rhythms.yaml · triggers.<trigger>` (`on`/`off` or `{ enabled, days }`) | `behavior_settings` | none |
| "Only one insight in the brief", "stop adapting insight volume" | `rhythms.yaml · insights` (`brief_max`, `engagement: adaptive|fixed`) | `behavior_settings` | none |
| "Stop suggesting ideas", "fewer people insights", "no more pattern insights" | `rhythms.yaml · insights.suppressed_kinds` (add the insight kind, e.g. `[idea]`; remove to bring it back) | `behavior_settings` | none; "fewer" (not none) → lower `brief_max` or keep adaptive, and say which |
| "Pause/resume the weekly review", "I'm away" | `rhythms.yaml · away / paused` | `behavior_settings` | hand to `nova-away` |
| "Switch me to Standard" | `routines.yaml · profile` + rebuild `routines` | `behavior_settings` | reconcile platform routines; carry over user jobs |
| "Run the nightly at 9 pm", "weekly review on Thursday afternoon" | `routines.yaml · routines[].schedule` | `behavior_settings` | update platform routine schedule |
| "Add the pipeline summary to the nightly run", "skip email drafts on Mondays" | `routines.yaml · routines[].jobs` (job name or `{ job, when, target, mode }`) | `behavior_settings` | none (job list is read each run); `profile: custom` |
| "Use the strongest model for upkeep" | `routines.yaml · routines[].model` | `behavior_settings` | update platform routine model |
| "Stop ingesting Teams", "read only my inbox, not other folders", "also read my CRM" | `sources.yaml · ingest[]` (`scope`, add/remove) | `behavior_settings` | connector needed? → `nova-connectors` |
| "I can't connect our CRM; I'll forward updates" | `sources.yaml · fallbacks[]` | `behavior_settings` | explain the fallback steps to the user |
| "Re-publish my dashboards", "I lost the Work Board link" | `dashboards.yaml` | `behavior_settings` / `dashboards_refresh` | `nova-dashboards` |
| "Connect/disconnect a tool", "fix my connector map" | `connectors.yaml` | `governance_settings` 🔒 | `nova-connectors` |
| "Change where finished files go" | `nova.yaml · deliverables_folder` | `behavior_settings` | find/create folder (`files.create_folder`) |
| "My time zone is now Europe/Berlin" | `nova.yaml · timezone` | `behavior_settings` | all schedules are local; update every platform routine's time zone |
| "Updates: ask me before minor updates too" | `governance.yaml · autonomy.updates_minor: propose` | `governance_settings` 🔒 | none |

## Plain-language level names
- `auto` → "I do it and log it."
- `propose` → "I prepare it and ask you first (or queue it when I'm running on my own)."
- `approve` → "Always needs your explicit OK; can't be changed."
- `never` → "I never do it; can't be changed."

## Explaining locked refusals (examples)
- "Sending is always your call. I'll keep preparing drafts so it's one click for you."
- "Changing these safety settings always needs your OK in a chat; that protects you from anything I read in an email trying to change them."
- "I never make payments, accept terms, or touch passwords, even if asked. I can draft the request for you to do it."
