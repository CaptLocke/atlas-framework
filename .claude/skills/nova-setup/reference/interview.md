---
type: skill-reference
skill: nova-setup
---
# Welcome, gather, research, and confirm (steps 6–8)

Order matters: **material first, questions last.** Nova reads everything it can (website, LinkedIn, attachments, public sources), drafts the profile, shows it for correction, and only then asks what the material didn't answer.

## Welcome
Before step 5, in the user's language. Adapt this; don't read it out:

> Hi, I'm Nova. I'll remember what's said, decided, and promised across your work, with links back to where it came from. I'll keep track of what you owe and what you're waiting on, prepare you for meetings, and draft your routine writing in your voice. While you're offline I'll bring in new email, meetings, and messages, so a Daily Brief is waiting each morning.
>
> Setting me up takes about 30–45 minutes of conversation. You can stop any time, and at the end you'll get your first Daily Brief. First, one quick permission check.

## Gather (step 6)
One message. Adapt this:

> To get to know you and your company quickly, I'll read before I ask. Share whatever's handy:
> 1. **Your company's website** (for example acme.com). *(I'll suggest one if your email makes it obvious.)*
> 2. **Your LinkedIn profile, optional.** Easiest: on your profile, click **More → Save to PDF** and attach the file here. A link works too, but LinkedIn often blocks me from reading it.
> 3. **Any documents, all optional:** a few emails or memos you've written, something your company published, a brand guide, logo, or slide template, an org chart or team list, strategy or planning docs, recent reports or decks.
>
> Attach what you have now (you can add more in any chat later), or say "skip".

- The website is the one thing to push for gently: if they skip it, ask once more with the reason ("it's how I learn what your company does and how it looks").
- LinkedIn is optional: never ask twice. A URL that can't be read gets one line ("LinkedIn didn't let me read that; a PDF works if you'd like") and nothing more.
- Don't wait for all attachments; continue to step 7 once they've replied.

## Company profile (steps 7–8)
Fill from research first; ask only what's missing. Each item is a section in the employer record (`system/schemas/organization.md` §Employer), with the summary line in `profile.md` ## Company.

| Item | Where it usually comes from | Ask if missing? |
|---|---|---|
| Company name, website | User (step 6) | Yes |
| Email domains (all the company uses) | User's email, website, mail later | **Always confirm** |
| Industry and sub-industry | Website, news | **Always confirm** |
| Size (employees, rough revenue if public) | Website, careers, news | No |
| Headquarters and main locations | Website | No |
| What they sell, and to whom (products, services, customer segments) | Website | Yes, one question |
| Business model (how it makes money) | Website, investor pages | No |
| Main competitors | Website, news, industry research | No (propose) |
| Fiscal year start | Investor pages; else ask | **Always confirm** (default January) |
| User's team and where it sits | LinkedIn, org chart | Yes |
| Internal terms and acronyms | Documents | No (learned over time) |
| Recent news (last 12 months) | News search | No |

Record in `nova.yaml: company`: `website`, `email_domains`, `fiscal_year_start_month`, `fiscal_year_label` (`end` if their fiscal year is named for the calendar year it ends in, the common case; `start` otherwise; irrelevant when the year starts in January).

## Research rules (step 7)
- Read the company website first, then public news from the last 12 months, then industry sources. Cite every web fact by URL; each page used becomes a web Source record.
- Role: what someone with their title typically owns at a company like theirs, used only as suggested responsibilities and goals.
- The user's LinkedIn (PDF or readable URL) is used only for their own role, title, tenure, background, and skills.
- Never state researched facts about named people beyond their public job title.
- Everything researched is a draft until confirmed in step 8: `[researched · confirmed <today> · <url>]` once agreed; otherwise a `[researched · proposed]` entry in `user/inbox/questions.md` (kind `profile`).

## Uploads (step 7)
- Each file goes through `nova-capture` as a drop (Source record, data rules, originals to `user/library/` if allowed and under 10 MB).
- **Voice guides:** fill the outline in `system/schemas/profile.md` (Summary, Tone, Structure and length, Vocabulary, Openings and sign-offs, Formatting habits, Examples with source links, Don't). Personal voice from their own writing; house voice from company writing, or from the website if nothing was attached.
- **Design system:** from a brand guide or template if attached; otherwise derive from the website (colors with hex for light and dark, typography with web-safe fallbacks, logo saved to `user/profile/assets/`, layout, chart palette order, do/don't).
- **Records:** org charts → people with `relationship` (per `system/schemas/person.md` §Relationships), `org`, `role`, and reporting links; strategy docs → goals, projects, topics, decisions (`provenance: observed`, cited to the upload's Source).
- Mark profile lines `[uploaded · confirmed <today> · [[sources/...]]]` once the user agrees with the summary in step 8.
- If mail is connected later (step 9), offer once to refine the personal voice from recent sent mail (`mail.list_sent`), as proposals.

## Confirm (step 8)
Show findings in short sections, one at a time, each ending "Anything wrong or missing?":
1. **Your company:** 5–8 bullets from the company profile, with the always-confirm items (domains, industry, fiscal year start) stated plainly so a wrong one is easy to spot.
2. **Your role:** title, team, responsibilities (suggestions labeled as such).
3. **People and goals** found in documents.
4. **How you write and how your company looks:** the voice Summaries and a small design sample, only if built.
Corrections replace the draft line (the old one stays only in history).

## Gap questions (step 8)
Ask only what the material didn't answer, one per message, in this order of value. Stop at about 8; leftovers become proposals later (monthly user health check).

| # | Ask | Default if skipped | Writes to |
|---|---|---|---|
| 1 | Who's your manager? (name, and email if handy) | none | person record `relationship: manager`; `profile.md` link |
| 2 | Who are the 3–5 people you work with most? How do you know them (team, customer, prospect, partner, board)? | Learned from mail/calendar later | person records with `relationship` chosen per `system/schemas/person.md` §Relationships; `profile.md` ## Key people |
| 3 | What are you trying to achieve this quarter or year? | Draft from research and documents; confirm at quarterly reset | goal records (`status: active`, `horizon`, `period`); `profile.md` ## Current goals |
| 4 | What big projects or initiatives are you on right now? | Discovered by ingest | project records |
| 5 | What does your job involve day to day? (only if research and LinkedIn didn't make it clear) | Suggested responsibilities from research | `profile.md` ## Responsibilities |
| 6 | When I report to you, what works best: short bullets, a few sentences, numbers first, or the story first? And how long should a brief be? | Short bullets, most important first; two-minute read | `communication-style.md` |
| 7 | How do you like to plan your day or week? Any focus-time habits? | Empty | `working-style.md` |
| 8 | When you make a decision, what do you lean on: data, gut, other people's views? What should I challenge you on? | Empty | `thinking-style.md` |
| 9 | Anything I should always or never do? (e.g., "never draft to my CEO without asking") | Empty | `preferences.md` ## Standing instructions |
| 10 | What parts of your work do you enjoy? What drains you? | Empty | `preferences.md` ## Likes / ## Dislikes |
| 11 | How would you describe your writing? Any sign-off you always use? (only if no writing samples) | Learned from mail later | `voice-personal.md` |
| 12 | Does your company have words to use or avoid with customers? (only if no company writing) | Learned from website | `voice-house.md` |

## Principles
- One question per message. Short. A default or example with each. "Skip" always works.
- Reflect back briefly ("Got it: you run product for the payments team.") and move on; don't interrogate.
- Follow the user's energy: long answers → fewer follow-ups; terse answers → rely on defaults and research.
- Answers are `stated`: write them as `[stated · confirmed <today>]` lines under `##` headings in the file shown. Never record protected or sensitive personal attributes (health, religion, politics, etc.) even if volunteered.
- At the end, summarize in 3–5 lines ("Here's how I'll work with you…") and ask for corrections.
