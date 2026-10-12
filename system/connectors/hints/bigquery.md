---
type: connector-hint
connector: bigquery
categories: [data]
checked: "2026-10: general knowledge of BigQuery; tool names not verified"
---
# Hint: BigQuery

Tool names vary; always verify from the live tool list. Guide: `system/connectors/data.md` (read-only, query text in every Source).

## Likely categories
`data`.

## Typical operations
| Operation | What to look for |
|---|---|
| `query` | Execute SQL / run query (GoogleSQL); sometimes a separate dry-run or estimate tool |
| `list_tables` | List datasets, list tables, get table schema/metadata |

## Cursor ideas
- Period-based: filter on the table's date or timestamp column (or the partition column, e.g. `_PARTITIONDATE` for ingestion-time partitioned tables) for the next complete period after `last_seen`.
- Always include a date filter on partitioned tables to keep cost down.

## Known quirks
- Queries are billed by bytes scanned: prefer a dry run to see bytes processed, select only needed columns (avoid `SELECT *`), and add `LIMIT` for exploration (note that `LIMIT` does not reduce bytes scanned on most tables; filters on partitioned columns do).
- Fully qualified names look like `project.dataset.table`; record the default project at mapping.
- Datasets live in regions; a query must run in the dataset's location.
- `INFORMATION_SCHEMA` views list tables and columns cheaply.
- Results can be large: summarize in the Source, keep at most a small aggregate table.

## Risk-sensitive tools
- A general "execute SQL" tool can run DML/DDL: tag it `write`, and send it SELECT-only statements (see `data.md`).
- `delete`: delete table/dataset, truncate, drop.
- `write`: create table/view, insert, load data, scheduled queries, export to Cloud Storage.
- `share`: change dataset IAM/permissions, authorized views.
- `security`: service accounts, keys, IAM roles.

## Fallback
"Export the result of your usual query or dashboard (CSV) into your **Nova Drop** folder, or tell Nova the number in chat."
