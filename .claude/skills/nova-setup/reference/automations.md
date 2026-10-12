---
type: skill-reference
skill: nova-setup
also_used_by: [nova-settings, nova-update]
---
# Rhythms, environments, and routines (step 10)

`nova-settings` uses the same procedures to change schedules later, and `nova-update` to change routine models.

## 1. Choosing a profile
| Plan (nova.yaml `plan`) | Suggest | One-line description for the user |
|---|---|---|
| pro | **Lean** | "Once every evening I catch up on everything and get tomorrow ready. Plus a Friday review and a Sunday tidy-up." |
| max_5x | **Standard** | "A full morning run, quick refreshes at 10, 1, and 4 on weekdays, and an evening run." |
| max_20x | **Full** | "Near real time: new information every hour during work hours, insights every few hours." |
| team / enterprise | Ask how much they use Claude day to day; suggest **Standard**, or Lean if they're often near their limits | |

Say: heavier profiles use more of their Claude allowance; they can switch any time by asking. Their choice is the confirmation for `behavior_settings`.

## 2. Writing routines.yaml
1. Read `system/routine-profiles/<profile>.yaml`. Copy its `routines` into `user/settings/routines.yaml` with `profile: <profile>` and `routine_id: null` for each (format: `system/schemas/settings.md`).
2. Schedules are cron in the user's time zone (`nova.yaml: timezone`), minutes off the hour (e.g. `7`), one schedule per routine.
3. Adjust schedules that depend on work hours (Full profile's "during work hours" routines; Standard's daytime refreshes) to the hours in `rhythms.yaml`. Example for work hours 09:00–17:00 weekdays, hourly ingest: `7 9-16 * * 1-5`.
4. If the user turned a moment off, leave the job in the routine: jobs read `rhythms.yaml` and skip themselves. Only remove jobs if the user asks.
5. Validate (`python3 system/tools/validate.py --all`), commit.

## 3. Environments (`NOVA_CONTEXT`)
Nova's safety checks use `NOVA_CONTEXT` to tell chats from automatic runs. If it's missing in a chat, they treat the chat like an unattended run (fail closed), which blocks everything that needs the user's OK. Two cloud environments are needed:

| Name | Variable | Used by | Set up at |
|---|---|---|---|
| `Nova chat` | `NOVA_CONTEXT=chat` | Chats in the Nova project | Start of setup (checked before step 5) |
| `Nova routines` | `NOVA_CONTEXT=routine` | Every Nova routine | Step 10 |

If this session has a tool to create or edit cloud environments, create the needed one (default network access; never put secrets in variables). Otherwise give the user the steps one at a time.

**Chat environment (start of setup, when `echo $NOVA_CONTEXT` isn't `chat`):**
```
1. In Claude, open Settings and look for "Environments" (it may be under "Claude Code", "Cloud", or a project's settings).
2. Create a new environment (or edit the one your Nova project uses). Name it: Nova chat
3. Under "Environment variables", add exactly one line:
   NOVA_CONTEXT=chat
4. Save, and make sure your Nova project's chats use "Nova chat" (look for an environment picker in the project or chat settings).
5. Start a NEW chat in your Nova project and say: continue setup
   (Settings like this only apply to new chats, not this one.)
```
"If it looks different: look for wherever you can add environment variables for cloud sessions and choose which one your Nova chats use; the name and the line above are all that matter."

Check in the new chat: `echo $NOVA_CONTEXT` prints `chat`. If the user can't set it up, continue setup in **degraded mode**: Nova can still save setup and files, but it can't send, share, or delete even with their OK, and it can't change safety settings after setup, until this is fixed. Record a known issue in `user/.state/health.yaml` (`id: env-chat-missing`, `severity: high`, `fix`: the steps above) and tell the user plainly which things won't work yet.

**Routine environment (step 10):**
```
1. In Claude, open Settings → Environments (same place as before).
2. Create a new environment. Name it: Nova routines
3. Under "Environment variables", add exactly one line:
   NOVA_CONTEXT=routine
4. Save. Each Nova routine will use this environment.
```
If routines end up without it, nothing unsafe happens (a missing value is treated as a routine), so this is lower risk; still set it for clarity.

## 4. Creating routines
For each routine in `routines.yaml`:

| Setting | Value |
|---|---|
| Name | `Nova · <routine name>` (e.g. `Nova · nightly-cycle`) |
| Prompt | The thin pointer from `system/jobs/README.md`, with the routine name filled in |
| Repository | The user's Nova repo only |
| Environment | `Nova routines` |
| Branch pushes | Allow pushing to `main` if the option exists |
| Connectors | Only connectors in `connectors.yaml` that the routine's jobs use (usually all mapped ones except `web`-only tools it doesn't need); never extra ones |
| Model | `system/manifest.yaml: models.<role>` for the routine's `model` role; if a routine mixes fast and strongest jobs, strongest |
| Schedule | The cron from `routines.yaml`, in the user's time zone |

The prompt (exact, with the name filled in):
```
Run the Nova routine `nightly-cycle`: look it up in user/settings/routines.yaml and run its jobs in order. Push all changes directly to main.
```

If this session can create routines (a routine or scheduled-task tool), create each, then save its ID as `routine_id` and commit. Check the result shows the right repo, environment, and model.

If not, show one copy-paste block per routine and wait for "done" each time:
```
In Claude, open Routines → New routine → Cloud.

Name:        Nova · nightly-cycle
Repository:  maya-chen/nova
Environment: Nova routines
Model:       claude-opus-5-5
Schedule:    Every day at 8:07 PM (your time zone)
Connectors:  Gmail, Google Calendar, Google Drive   (turn off any others)
Branches:    allow pushing to main (if you see this option)

Instructions (copy exactly):
Run the Nova routine `nightly-cycle`: look it up in user/settings/routines.yaml and run its jobs in order. Push all changes directly to main.
```
Translate cron to plain words for the user ("Every Friday at 2:07 PM", "Weekdays every hour from 9:07 AM to 4:07 PM"). Values in the example are fictional; fill in the user's. When the user says it's done, set `routine_id: "manual:<routine name>"` (so health checks know it exists but can't be edited from chat) and commit.

## 5. After creating
- Offer to start one routine once now ("run now") to confirm it works, ideally `upkeep` (cheap). Its run report confirms `available_in_routines` for connectors (`nova-connectors`).
- Tell the user: routines run whether their computer is on or off; if GitHub access lapses for 3 days, the platform turns routines off and Nova will tell them how to turn them back on.

## 6. Changing later
- Job list or modifiers: settings edit only (`routines.yaml`).
- Schedule, model, connectors, or a new/removed routine: also update the platform routine (same tool or copy-paste path). Removing a platform routine counts as deleting (`destructive`, approval); prefer turning it off.
