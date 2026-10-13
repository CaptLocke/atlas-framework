---
type: connector-hint
connector: meeting-notetaker (Fireflies, Otter, Granola, and similar)
categories: [meetings]
checked: "2026-10: generic pattern across notetaker tools; tool names not verified"
---
# Hint: meeting notetakers

Tool names vary; always verify from the live tool list. Guide: `system/connectors/meetings.md`.

## Likely categories
`meetings`. Some also expose a searchable meeting library (still `meetings`) or push notes into docs (then `files` holds the notes).

## Typical operations
| Operation | What to look for |
|---|---|
| `list_recent` | List meetings / transcripts / notes, newest first, with a date filter |
| `read_transcript` | Get transcript (with speakers and timestamps) |
| `read_summary` | Summary, action items, key decisions, topics |
| (read) | Search across meetings by keyword or participant |

## Cursor ideas
- Meeting date/end time as `last_seen`; dedupe by the tool's meeting ID.
- If listing has no date filter, page newest-first and stop at the first already-filed meeting.

## Known quirks
- **Vendor action items are suggestions.** Re-check each against the transcript and Atlas's commitment test (`system/rules/knowledge.md`); many are vague or misattributed.
- Bot-based notetakers join only meetings they were invited to or that are on a connected calendar; notes-app style tools (user-typed notes enhanced by AI) mix the user's own notes with transcript: treat the user's typed notes as `provenance: stated`.
- The same meeting may also be transcribed by Zoom or Teams: file one Source per meeting (prefer the transcript with reliable speaker names) and link both URIs if useful.
- Some tools auto-email summaries to all attendees; that is a vendor setting the user controls, not Atlas.
- Free tiers may limit transcript history or hide full transcripts.

## Risk-sensitive tools
- `send`: send/share summary to attendees, post to Slack/Teams, invite the bot to meetings, push to CRM with notifications.
- `share`: share meeting link, change visibility of meetings or channels.
- `delete`: delete meeting, transcript, or recording.
- `write`: push notes to CRM or task tool (that is `shared_records_update` or `tasks_manage`, propose).

## Fallback
"Export the transcript or notes (*Download* / *Export* as text or PDF) and put it in your **Atlas Drop** folder, or set the tool to email you summaries."
