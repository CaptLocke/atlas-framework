---
type: skill-reference
skill: atlas-triage
---
# The cut list (ATL-134)

When the user owes too much that has already slipped, asking about each item one at a time doesn't work: they re-date one, it slips again, and the pile grows. Once a week at most, triage proposes one list instead, and one yes settles it.

## 1. When
Run `python3 -I system/tools/cutlist.py --today <today> --out .atlas-tmp/cutlist.json` (full mode only; not during away). The tool decides, so the same records always give the same answer.
- It's due when 5 or more of the user's own `i_owe` items are `slipped`, no cut list is open, and none was asked in the last 7 days, or 3 or more have slipped since the last one was asked.
- `due: false` → nothing to do. Say nothing about it.
- An open cut list asked 7 or more days ago with no answer is dismissed (`dismissed <date>: no answer in a week`) before the tool runs. Its items go back to the per-item "slipped and quiet" questions, and a new list can be asked next week.

## 2. The question
One entry in `user/inbox/questions.md`, kind `commitment` (`system/schemas/formats.md` §questions):

```markdown
## Q-2026-11-24-03 · open · commitment
- **Question:** 6 things you owe have slipped. Cut the list?
- **Cut list:** 6 items
- **Proposed change:** 1. Keep: Q4 board deck for Jordan, now Wed Nov 25 · 2. Hand off: usage export to Rey (already on it), with a note to send · 3. Re-date: SOC 2 summary to Fri Nov 27 · 4. Drop: reseller terms comments (nothing since Oct 30), with a note to Dana · …
- **Links:** [[commitments/…]], [[commitments/…]], …
- **Asked:** 2026-11-24
```

- **One line per item, in the tool's order and with the tool's action.** Each line gets a reason in a few words, taken from the record, and the tool's `date` for keep and re-date. A line says "with a note to send" for a hand-off, and "with a note to <name>" for a drop with `notify: true`.
- **Never change an action the tool chose.** If the records argue for a different one (say, the person to hand to has left), say so in that line's reason and leave it for the user.
- **Links name every item, so a page answer is limited to them.**
- **While the entry is open,** step 8's per-item "slipped and quiet" question isn't asked for any item it links, and none already open for them is repeated.

## 3. Applying an answer
- **Yes** (in a chat, or Yes on the Guide page, `atlas-dashboards` `reference/live.md`) applies every line.
- **Part of it** ("drop 1 and 3, keep the rest", "hand 2 to Sam instead") is chat only. Apply what was said, and leave unnamed lines as they are.
- **No** leaves every item as it is.
- In every case, mark the entry `answered` with the user's words.

Per line:
- **Keep, re-date:** set `due` to the line's date and status back to `open`, with a "was X, now Y" Updates line ("cut list <date>").
- **Drop:** `status: dropped`, with an Updates line ("dropped in the cut list <date>"). With a note: draft "letting you know" to the counterparty through `atlas-write` (§Hand-off and drop notes) and queue it for approval. The drop doesn't wait for the note.
- **Hand off:** draft a note to the person asking them to take it on, through `atlas-write`, and queue it for approval with `On send:` set to the hand-off (`formats.md` §3). The commitment stays the user's until the note is sent. Then it becomes `direction: waiting_on`, `owner` the person, `counterparty` the user, `status: open`, with an Updates line. If the user sends the note themselves, triage makes the change when it sees the note in sent mail, and marks the entry `executed`.
- **Sends are never part of the yes:** each note waits for its own approval (`system/rules/governance.md`). Several can go in one yes, as §Several at once there allows.

Log a `feedback` line for the answer (`reference/learning.md` §1, signal `cut_list`, dimension `yes`, `part` or `no`) in the change set that applies it.
