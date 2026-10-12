---
type: schema
name: source
folder: user/knowledge/sources/
---
# Schema: source

## What it is
Where information came from. Every fact in Nova traces to a source.

## Fields (in addition to `_common.md`)
| Field | Type | Required | Values / notes |
|---|---|---|---|
| `kind` | enum | yes | email, meeting, message, doc, web, data, manual, journal, file, deliverable |
| `origin_uri` | text | no | Permalink, doc URL, thread ID, or path. |
| `connector` | text | no | Connector that provided it. |
| `captured_on` | date | yes |  |
| `occurred_on` | date | no | When the original happened. |
| `participants` | list of IDs | no |  |
| `retention` | enum | yes | full, summary, pointer, per data rules |
| `file_pointer` | text | no | For deliverables and drops: location in the user's cloud drive. |

## Status vocabulary
captured, processed

## Links
Typically links to: records derived from it (they link back via `sources`).

## Capture guidance
One source per email thread, meeting, document, page, drop, deliverable, or journal day. Body holds a summary and key excerpts (if `retention` allows). Binary files are never copied into the repo by default.
