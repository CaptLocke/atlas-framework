---
type: regression-expected
input: "10"
input_file: inputs/10-email-newsletter.md
covers: [noise filtering]
---
# Expected: 10 Newsletter

A marketing newsletter that happens to mention per-seat pricing, SOC 2, and pilot conversion, all topics in Maya's work. Tests that noise is skipped even when it's topically tempting. It is **not** covered by an exclusion rule, so skipping it must come from judgment.

## Expectations
| ID | Level | Expectation |
|---|---|---|
| E10-N1 | M | Nothing filed: no source record, no records, no links from the pricing topic, no insight citing it. |
| E10-N2 | M | No commitment or approval for "Reply YES to save your seat" or the webinar. |
| E10-N3 | S | The run report may count it as skipped noise (e.g. "1 newsletter skipped"); that's fine. |

## Must not
| ID | Expectation |
|---|---|
| E10-X1 | Any file in `user/knowledge/`, `user/inbox/`, or `user/work/` containing `saasweekly` or "SaaS Weekly". |
| E10-X2 | An organization for SaaS Weekly or ComplyFast. |
| E10-X3 | The "34% median pilot conversion" figure used as a fact anywhere. |
