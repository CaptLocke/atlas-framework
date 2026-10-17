---
type: skill-reference
skill: atlas-setup
also_used_by: [atlas-settings, atlas-update]
---
# Rhythms, the routine environment, and routines (step 10)

`atlas-settings` uses the same procedures to change schedules later, and `atlas-update` to change routine models.

## 1. Choosing a profile
| Plan (atlas.yaml `plan`) | Suggest | One-line description for the user |
|---|---|---|
| pro | **Lean** | "Once every evening I catch up on everything and get tomorrow ready. Plus a Friday review and a Sunday tidy-up." |
| max_5x | **Standard** | "A full morning run, quick refreshes at 10, 1, and 4 on weekdays, and an evening run." |
| max_20x | **Full** | "Near real time: new information every hour during work hours, insights every few hours." |
| team / enterprise | Ask how much they use Claude day to day; suggest **Standard**, or Lean if they're often near their limits | |

Say: heavier profiles use more of their Claude allowance; they can switch any time by asking. Their choice is the confirmation for `behavior_settings`.

## 2. Writing routines.yaml
1. Read `system/routine-profiles/<profile>.yaml`. Copy its `routines` into `user/settings/routines.yaml` with `profile: <profile>` and `routine_id: null` for each (format: `system/schemas/settings.md`).
2. Schedules are cron in the user's time zone (`atlas.yaml: timezone`), minutes off the hour (e.g. `7`), one schedule per routine.
3. Adjust schedules that depend on work hours (Full profile's "during work hours" routines; Standard's daytime refreshes) to the hours in `rhythms.yaml`. Example for work hours 09:00–17:00 weekdays, hourly ingest: `7 9-16 * * 1-5`.
4. If the user turned a moment off, leave the job in the routine: jobs read `rhythms.yaml` and skip themselves. Only remove jobs if the user asks.
5. Validate (`python3 system/tools/validate.py --all`), commit.

## 3. The routine environment (`ATLAS_CONTEXT=routine`)
Atlas's safety checks tell automatic runs from chats by one marker: `ATLAS_CONTEXT=routine`. A session with the marker is treated as unattended (no sending, sharing, deleting, or settings changes, even with an approval record). **Everything without it is a chat**, so chats (Cowork or any other chat surface) need no environment; locked actions there still need a single-use approval record quoting the user's yes.

So Atlas needs exactly one cloud environment:

| Name | Variable | Used by | Set up at |
|---|---|---|---|
| `Atlas routine` | `ATLAS_CONTEXT=routine` | Every Atlas routine, no exceptions | Step 10 (and whenever a routine is created later) |

If this session has a tool to create or edit cloud environments, create it (default network access; never put secrets in variables). Otherwise give the user the steps one at a time:
```
1. In Claude, open Settings and look for "Environments" (it may be under "Claude Code", "Cloud", or "Routines").
2. Create a new environment. Name it: Atlas routine
3. Under "Environment variables" (or similar), add exactly one line:
   ATLAS_CONTEXT=routine
4. Save. Every Atlas automation will use this environment.
```
"If it looks different: look for wherever you can add environment variables for cloud runs. The name and the line above are all that matter. Capitals and the underscore matter in ATLAS_CONTEXT; the value is routine in lower case, with no spaces or quotes."

**Why it matters:** the marker is how the safety hooks know a run is unattended. Since 1.0.2 they also treat a session that starts with an Atlas routine prompt as a routine, but the environment is still required: the routine prompt checks the marker first and stops without running any job if it's missing. Every run records the `ATLAS_CONTEXT` it saw in its run report (`atlas_context`); a run that doesn't see `routine` raises the high-severity known issue `routine-env-missing` naming the routine, and the weekly health check (`atlas-health`, via `maintenance`) looks for unmarked runs too.

**Fixing `routine-env-missing`** (offer this in the next chat):
```
1. In Claude, open Routines (it may be under "Claude Code") and open the routine named "Atlas · <routine name>".
2. Find its Environment setting and choose: Atlas routine
   (If there's no "Atlas routine" environment, create it first with the steps above.)
3. Save. Then press "Run now" (if you see it) so I can check it worked.
```
After the test run, read its run report: `atlas_context: routine` means fixed; close the known issue.

## 4. Creating routines
For each routine in `routines.yaml`:

| Setting | Value |
|---|---|
| Name | `Atlas · <routine name>` (e.g. `Atlas · nightly-cycle`) |
| Prompt | The thin pointer from `system/jobs/README.md`, with the routine name filled in |
| Repository | The user's Atlas repo only |
| Environment | `Atlas routine` (always; a routine without it isn't guarded by the safety hooks) |
| Branch pushes | Allow pushing to `main` if the option exists |
| Connectors | Only connectors in `connectors.yaml` that the routine's jobs read from; never a connector with send, share or delete tools (routines only draft), and never extra ones |
| Model | `system/manifest.yaml: models.<role>` for the routine's `model` role; if a routine mixes fast and strongest jobs, strongest |
| Schedule | The cron from `routines.yaml`, in the user's time zone |

The prompt (exact, with the name filled in):
```
Run the Atlas routine `nightly-cycle`. First run `echo $ATLAS_CONTEXT`: if it doesn't print `routine`, add a high-severity known issue `routine-env-missing` naming this routine to user/.state/health.yaml, commit and push it, and do nothing else. Otherwise read `timezone` in user/settings/atlas.yaml and run `TZ=<timezone> date`; use that as the current date and time for this whole run and ignore the session's stated date. Then look up the routine in user/settings/routines.yaml and run its jobs in order. Push all changes directly to main.
```

If this session can create routines (a routine or scheduled-task tool), create each, then save its ID as `routine_id` and commit. Check the result shows the right repo, environment, and model.

If not, show one copy-paste block per routine and wait for "done" each time:
```
In Claude, open Routines → New routine → Cloud.

Name:        Atlas · nightly-cycle
Repository:  maya-chen/atlas
Environment: Atlas routine
Model:       claude-opus-5-5
Schedule:    Every day at 8:07 PM (your time zone)
Connectors:  Gmail, Google Calendar, Google Drive   (turn off any others)
Branches:    allow pushing to main (if you see this option)

Instructions (copy exactly):
Run the Atlas routine `nightly-cycle`. First run `echo $ATLAS_CONTEXT`: if it doesn't print `routine`, add a high-severity known issue `routine-env-missing` naming this routine to user/.state/health.yaml, commit and push it, and do nothing else. Otherwise read `timezone` in user/settings/atlas.yaml and run `TZ=<timezone> date`; use that as the current date and time for this whole run and ignore the session's stated date. Then look up the routine in user/settings/routines.yaml and run its jobs in order. Push all changes directly to main.
```
Translate cron to plain words for the user ("Every Friday at 2:07 PM", "Weekdays every hour from 9:07 AM to 4:07 PM"). Values in the example are fictional; fill in the user's. When the user says it's done, set `routine_id: "manual:<routine name>"` (so health checks know it exists but can't be edited from chat) and commit.

## 5. After creating
- Start one routine once now ("run now"; if Claude can't, ask the user to press it), ideally `upkeep` (cheap). When it finishes, pull and read its run report: it must show `atlas_context: routine`, which confirms the routine is attached to the "Atlas routine" environment. Anything else: walk the user through the fix in §3 and test again. The run report also confirms `available_in_routines` for connectors (`atlas-connectors`).
- Tell the user: routines run whether their computer is on or off; if GitHub access lapses for 3 days, the platform turns routines off and Atlas will tell them how to turn them back on.

## 6. Changing later
- Job list or modifiers: settings edit only (`routines.yaml`).
- Schedule, model, connectors, or a new/removed routine: also update the platform routine (same tool or copy-paste path). Every new routine uses the "Atlas routine" environment (§3, §4) and gets a test run as in §5. Removing a platform routine counts as deleting (`destructive`, approval); prefer turning it off.
