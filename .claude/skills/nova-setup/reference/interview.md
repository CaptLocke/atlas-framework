---
type: skill-reference
skill: nova-setup
---
# Interview, research, and uploads (steps 6–8)

## Interview principles
- One question per message. Short. A default or example with each. "Skip" always works.
- Reflect back briefly ("Got it: you run product for the payments team.") and move on; don't interrogate.
- Follow the user's energy: if they give long answers, ask fewer follow-ups; if they're terse, rely on defaults and research.
- Stop after ~15 questions even if not all are asked; remaining gaps become proposals later (monthly user health check).
- Answers are `stated`: write them as `[stated · confirmed <today>]` lines under `##` headings in the file shown. Never record protected or sensitive personal attributes (health, religion, politics, etc.) even if volunteered.

## Question bank (in order; skip what's already known from step 5)
| # | Ask | Default if skipped | Writes to |
|---|---|---|---|
| 1 | What does your job involve day to day? What are you responsible for? | Research the role (step 7) | `profile.md` ## Responsibilities |
| 2 | Who's your manager? (name, and email if handy) | none | person record `relationship: manager`; `profile.md` link |
| 3 | Who are the 3–5 people you work with most? How do you know them (team, customer, partner)? | Learned from mail/calendar later | person records; `profile.md` ## Key people |
| 4 | What are you trying to achieve this quarter or year? | Draft from research; confirm at quarterly reset | goal records (`status: active`, `horizon`, `period`); `profile.md` ## Current goals |
| 5 | What big projects or initiatives are you on right now? | Discovered by ingest | project records |
| 6 | How do you like to plan your day or week? Any focus-time habits? | "Plans weekly, protects mornings" not assumed; leave empty | `working-style.md` |
| 7 | When I report to you, what works best: short bullets, a few sentences, numbers first, or the story first? | Short bullets, most important first | `communication-style.md` |
| 8 | How long should a typical brief be? (2 minutes is the default) | Two-minute read | `communication-style.md` |
| 9 | When you make a decision, what do you lean on: data, gut, other people's views? What should I challenge you on? | Empty | `thinking-style.md` |
| 10 | What parts of your work do you enjoy? What drains you? | Empty | `preferences.md` ## Likes / ## Dislikes |
| 11 | Anything I should always or never do? (e.g., "never draft to my CEO without asking") | Empty | `preferences.md` ## Standing instructions |
| 12 | How would you describe your writing: formal or casual, short or detailed? Any sign-off you always use? | Learned from samples | `voice-personal.md` (Summary/Openings and sign-offs) |
| 13 | Does your company have a particular way of writing for customers? Words to use or avoid? | Learned from website/samples | `voice-house.md` |

At the end, summarize in 3–5 lines ("Here's how I'll work with you…") and ask for corrections. Corrections replace the line (keep the old one in the file's history via git, nothing more).

## Research (step 7)
- Company: what it does, size, products/services, customers, competitors, recent news (last 12 months), leadership names only when public and relevant.
- Industry: key terms, trends, regulators if relevant.
- Role: what someone with that title typically owns at a company like theirs (used to suggest goals and responsibilities, labeled as suggestions).
- The user's public profile (e.g., a professional networking page or company bio): **only if they agree**.
- Present as 5–8 bullets with URLs. Ask "Anything wrong or missing?" Write confirmed items:
  - Employer organization record: `domain`, `industry`, `kind: employer`, summary; `provenance: researched`; a web source record per page used.
  - `profile.md` lines `[researched · confirmed <today> · <url>]`.
  - Unconfirmed items → `user/inbox/questions.md` entries (kind `profile`) with the proposed line marked `[researched · proposed]`.
- Never state researched facts about named people beyond their public job title.

## Uploads (step 8)
Invite with a short menu; all optional:
1. "Two or three things you've written that sound like you" (emails, memos, posts) → personal voice.
2. "Something your company published" (web page, announcement, customer email) → house voice. If none, offer to read the company website.
3. "A brand guide, logo, or slide template" → design system. If none, offer to derive one from the website (colors, fonts, logo).
4. "An org chart, team list, or strategy/planning doc" → initial records.
5. "Recent reports or decks you're proud of" → voice, design, and accomplishments.

Processing:
- Each file goes through `nova-capture` as a drop (source record, data rules, originals to `user/library/` if allowed and under 10 MB).
- **Voice guides:** fill the outline in `system/schemas/profile.md` (Summary, Tone, Structure and length, Vocabulary, Openings and sign-offs, Formatting habits, Examples with source links, Don't). Show the Summary and ask "Does this sound like you?" Mark lines `[uploaded · confirmed <today> · [[sources/...]]]` once agreed; otherwise `proposed` in questions.md.
- **Design system:** fill the outline (colors with hex for light and dark, typography with web-safe fallbacks, logo files saved to `user/profile/assets/`, layout, chart palette order, do/don't). Show a small sample (a heading, a color strip) in chat if possible.
- **Records:** org charts → people with `relationship`, `org`, `role`, and reporting links; strategy docs → goals, projects, topics, decisions (`provenance: observed`, cited to the upload's source record).
- If mail is connected later (step 9), offer once to refine the personal voice from recent sent mail (`mail.list_sent`), as proposals.
