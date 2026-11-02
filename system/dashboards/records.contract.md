---
type: dashboard-contract
name: records
template: records.html
republished_by: [triage, weekly-review]
size_budget_kb: 900
stale_after_hours: 192
---
# Dashboard: Records (`records`)

## Purpose
**What does Atlas keep, and how does it connect?** Every record Atlas keeps (people, organizations, projects, commitments, goals, meetings and events, decisions, risks, ideas, topics, and open questions) and the links between them, as one web you can zoom into, with search by name and a library of what needs attention and what is most connected. Zooming into a project shows its people, commitments, decisions, risks, questions, ideas and meetings: what a project page used to show, except its update history and sources, which are chat questions.

## Data (JSON shape embedded in the page)
Envelope: `meta` as in `system/dashboards/README.md`; `meta.title` = `"Records"`. Everything else is the output of `system/tools/graph.py`, unchanged: the model doesn't build or edit it.

```json
{
  "meta": { "dashboard": "records", "schema_version": 1, "title": "Records", "as_of": "2026-10-13", "…": "…" },
  "records": [ { "id": "people/dana-ruiz", "type": "person", "title": "Dana Ruiz", "status": "active", "updated": "2026-10-12" },
               { "id": "commitments/dana-msa-review", "type": "commitment", "title": "Dana reviews the enterprise MSA", "status": "slipped",
                 "updated": "2026-10-12", "attention": "critical", "status_word": "Slipped" } ],
  "links": [ [0, 1] ],
  "truncated": 0
}
```

| Field | Notes |
|---|---|
| `records[]` | Every record of the drawn types, titles and statuses only (`graph.py` says which are left out: archived, superseded, closed and older than 90 days, closed questions; never sources, playbooks or user types). Sorted by type, then title. |
| `records[].attention` | `critical` or `warning` when the record needs a look, with its `status_word` from the status vocabulary (Slipped, Overdue, Due today, Off track, At risk, Critical, On edge, Needs action); missing otherwise. |
| `links` | Pairs of indexes into `records`, once per pair: two records are linked when either names the other anywhere in its frontmatter (except `sources`) or body. |
| `truncated` | How many records were left out to stay under `graph.py --max` (most recent kept). |

## Sources (file → field)
| File | Field |
|---|---|
| `user/knowledge/<type folder>/*.md` (frontmatter and body links) | `records`, `links`, through `python3 -I system/tools/graph.py` |
| `user/settings/atlas.yaml: timezone` | the day `graph.py` counts 90 days and overdue from |

## Rendering notes
- **Head:** title "Records"; date line "Everything Atlas keeps, and how it connects."; lead (`meta.headline`): what's most connected or most in need of a look, in one sentence; two plain counts beside it, records and links.
- **Search** by name across `records` (on the page, nothing fetched), up to 8 results, needs-a-look first; choosing one zooms the web to it. **Start from** chips: the critical record with the most links (Focus), the most connected project or goal that's off track or at risk (Off track), the most connected record (Most connected; "You" when it is the user's own person record, by `meta.user_display_name`), and the person updated most recently (Recent).
- **The web** (`N.web`): every type as a root system at a fixed place, records as dots (critical and warning dots in their status colors), links between types bundled at a waist. Choose a type or record once to light its links; again to zoom in. A zoomed record pulls up to 12 linked records in around it, a dashed thread back to where each lives; the trail (Library › type › record) and Zoom out step back. Motion stops under reduced motion.
- **The library card** under the web (a night card) follows the web: nothing chosen, **Needs attention** (critical records, most linked first) and **Most connected**; a type chosen, its records with Needs attention, Most linked and A to Z, 12 at a time; a record chosen, its type, title, status, how many records it links, Zoom in, its linked records grouped by type, and prompts to copy ("What's the latest on …?").
- **Phones:** the web scales down; labels shrink, the hint hides, and the library card and search carry the page. No pinch-zoom.
- No actions change anything: records change in chat. The prompts copy a question for chat.
- **Size:** about 120 bytes a record and 10 a link; the 900 KB budget holds `graph.py`'s 3,000-record cap with room. On a live page `records` and `links` are separate sections.
