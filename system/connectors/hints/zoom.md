---
type: connector-hint
connector: zoom
categories: [meetings]
checked: "2026-10: general knowledge of Zoom recordings and transcripts; tool names not verified"
---
# Hint: Zoom (recordings and transcripts)

Tool names vary; always verify from the live tool list. Guide: `system/connectors/meetings.md`.

## Likely categories
`meetings`. Some Zoom connectors also expose scheduled meetings (`calendar`-like) and Team Chat (`messaging`); prefer the user's main calendar for `calendar` and map Team Chat only if the user uses it.

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | List cloud recordings / past meetings in a date range (from/to) |
| `read_transcript` | Get recording transcript (often a VTT/text file per recording) |
| `read_summary` | Meeting summary / AI Companion summary, next steps |
| (read) | Past meeting details, participants |

## Cursor ideas
- Date-range listing: query from the day of `last_seen` to today and dedupe by meeting/recording ID. Some APIs cap the range per call (often about a month); split long first-run lookbacks into chunks.
- Recurring meetings can share a meeting ID: dedupe by the occurrence's unique ID (UUID-style) plus start time.

## Known quirks
- Only **cloud** recordings and transcripts are available; local recordings are not. If the user records locally, use the drop fallback.
- Transcripts appear some time after the meeting ends (processing delay): hold the cursor as the meetings guide says.
- Transcripts may be off for some meetings (host setting); summaries may exist without transcripts and vice versa.
- Speaker names come from display names ("iPhone", "Conference Room 3"): match people carefully; uncertain speaker → question, not commitment.
- The user may be a participant but not the host; recordings owned by another host may be inaccessible.

## Risk-sensitive tools
- `share`: share recording, change recording sharing settings, get a public share link.
- `delete`: delete recording, delete meeting.
- `send`: create/update meeting **with invitees**, send chat messages, send summary to participants.
- `security`: change account, passcode, or security settings.

## Fallback
"In Zoom, open *Recordings*, download the transcript (.vtt or .txt), and put it in your **Atlas Drop** folder."
