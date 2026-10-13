---
type: skill-reference
skill: nova-triage
---
# Learning from the user: triage and insights

Nova gets better at what it files, how it ranks, and which insights it shows by noticing when the user corrects it. The rule is the same as for voice learning (`nova-write`): **one instance is noise; a consistent pattern becomes a proposal; only the user's yes makes it a rule.**

## 1. Signals
Whenever one of these happens, write one activity-log line (`system/schemas/formats.md` §4) with the action `feedback` and the summary `<signal> · <subject> · <dimension>`. Write it in the same change set as the fix itself. Never include message text or sensitive content: name records by ID and describe the pattern in a few generic words.

| Signal | When | Logged by |
|---|---|---|
| `not_a_commitment` | The user drops a commitment Nova created because it was never a promise, or answers a vague-commitment question "no" | `nova-triage`, `nova-memory` |
| `missed_commitment` | The user adds a commitment from a source Nova had already filed | `nova-capture` |
| `wrong_close` | The user reopens something Nova closed or marked done | `nova-triage`, `nova-memory` |
| `priority_up` / `priority_down` | The user changes a priority Nova set, or says something matters more or less | `nova-triage` |
| `noise` | The user says to stop filing or flagging something ("ignore these vendor newsletters", "that's not worth tracking") | any skill |
| `insight_useful` / `insight_noise` | The user says an insight helped, or that it was wrong or not useful (not "not now") | `nova-insights` |

**Dimension** is what the pattern is about, chosen from: a person, an organization, a project or topic (by ID), a sender or channel (`from:*@vendor.com`, `channel:#alerts`), a phrase type ("I'll take a look"), a commitment kind ("intro requests"), or an insight kind plus subject (`quiet_person · vendors`). Example:
```
- 2026-10-12 15:02 · chat · feedback · not_a_commitment · [[commitments/look-at-deck]] · phrase "I'll take a look" · commit 9b31e07
```
Silent signals count too, but only where the evidence is clear. The learning pass (§2) counts them from records; nothing is logged for them:
- Records from one sender, channel, or series that the user archived, dropped, or never touched across ≥ 5 items in 60 days. These count as `noise`.
- Insights about the same subject dismissed ≥ 3 times and never acted on. These count as `insight_noise`.

## 2. The learning pass (monthly, and on demand)
Runs in the monthly automation review (`nova-review`, `reference/monthly.md` §What Nova learned). It also runs in chat when the user asks "what have you learned about how I work?".
1. Gather `feedback` lines from the last 60 days of activity logs, plus the silent signals above.
2. Group them by signal and dimension. A **pattern** is ≥ 3 signals with the same signal and dimension in 60 days, none contradicting it, and no open or dismissed proposal for the same rule in that time.
3. For each pattern, write one proposal in `user/inbox/questions.md` (kind `profile`) with the evidence count and the exact rule line to add. Cap it at 3 proposals a month, strongest first. For example:
```markdown
## Q-2026-11-02-01 · open · profile
- **Question:** You've dropped 4 commitments where you said "I'll take a look". Should I stop treating that phrase as a promise?
- **Proposed change:** preferences.md ## Triage rules: "'I'll take a look' is not a commitment unless a date is given" [observed · proposed]
- **Asked:** 2026-11-02
```
4. **Noise from a whole sender or channel** is a data-rule exclusion, which is governed. The question names the exact exclusion (`mail: from:*@vendor.example`). On a yes in chat, `nova-settings` writes it through the approval-record procedure. Nova never writes an exclusion from a routine.
5. On the user's yes, write the line under the right heading in `user/profile/preferences.md`, tagged `[observed · confirmed <date>]` with the evidence count. A rule the user states directly ("never track intro requests") is written at once, tagged `[stated · <date>]`. Both follow `profile_update` (default propose; the user's yes is the confirmation).
6. A rule the user later contradicts (≥ 2 signals against it) is proposed for removal the same way. Rules are never deleted silently.

## 3. Where the rules live and who applies them
`user/profile/preferences.md` has two headings, one rule per line, in plain language:
- **`## Triage rules`**, which covers:
  - What counts as a commitment (`nova-capture` reads them before deciding explicit vs vague).
  - What to close or never close (`nova-triage` step 4).
  - Priority shifts, such as "intro requests are low priority" or "anything from Sam is high" (`nova-triage` step 7, applied after the rubric).
  - What to skip as noise (`nova-capture` classify step).
- **`## Insight rules`**: kinds or subjects to show less or more (`nova-insights` step 6, after the engagement adjustment). Examples: "No quiet-person insights about vendors", "Always show risks about Globex".

When a rule changes an outcome, say so where it shows: in the `insight` line ("Low per your rule on intro requests") or in the run report. That lets the user see the rule working and correct it.

## 4. Reporting
The monthly report's **What Nova learned** section lists:
- Rules confirmed this month.
- Proposals waiting for an answer.
- The count of `feedback` lines by signal, against last month.

Falling counts mean Nova is learning; the existing `corrections` indicator (`nova-review`, `reference/indicators.md`) also counts `feedback` lines.
