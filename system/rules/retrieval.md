---
type: rule
name: retrieval
---
# Rule: retrieval (progressive disclosure)

## Applies to
Every chat request, every job that reasons over knowledge, and every draft.

## The rule
Bring the relevant knowledge to every task automatically, loading as little as possible and as much as needed. The user never has to ask you to check their notes.

## Levels
| Level | Load | When |
|---|---|---|
| **L0 Orientation** | Profile summary, settings, `_index/hot.md`, inbox counts, known issues, trigger checks | Session start (kernel §2) |
| **L1 Catalog** | Matching lines in `_index/<type>.md` and `people-map.md` | Any request that names or implies people, organizations, projects, topics, time periods, or past events |
| **L2 Records** | The records matched at L1 or by text search | Whenever a record is clearly relevant |
| **L3 Neighborhood** | Records linked from L2, 1–2 hops, filtered for relevance (open commitments, recent decisions, active risks, related topics) | Prep, drafting, analysis, "why" questions, decisions, anything involving a person or project |
| **L4 Sources** | Source records; the original via connector if needed | Exact wording, verification, quotes, disputes |

## How to search
1. Extract entities and intents from the request (names, emails, projects, topics, dates, verbs like "decide", "promise", "send").
2. Generate variants: aliases, nicknames, abbreviations, related terms, likely synonyms.
3. Search indexes first (cheap), then text-search `user/knowledge/` and `user/journal/` for anything not found.
4. Use frontmatter dates and statuses to filter (open vs. closed, recent vs. old). Exclude archived and superseded records unless the question is historical.
5. Follow links for indirect relevance: the person → their open commitments and recent events; the project → its decisions, risks, questions; the topic → related ideas and projects.
6. Stop when additional records stop changing the answer.

## Using what you found
- Ground answers and drafts in the records; cite them (`system/rules/writing.md`).
- Prefer the most recent non-superseded facts; mention when facts conflict and which is newer.
- If knowledge is missing, say so, answer with what you have, and offer to capture what the user tells you.
- Never paste large amounts of record content into answers; synthesize.

## Checks
- Answers about the user's work include at least one citation when knowledge exists.
- No archived or superseded record is presented as current.
