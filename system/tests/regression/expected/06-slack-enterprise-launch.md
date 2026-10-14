---
type: regression-expected
input: "06"
input_file: inputs/06-slack-enterprise-launch.md
covers: [source(message), risk(active), project(update), commitment(waiting_on), person, noise filtering]
---
# Expected: 06 Slack #enterprise-launch

Channel thread mixing a real blocker, a bot, and chatter. Tests an active issue, updating a seeded project's health, and ignoring noise.

## Sources
| ID | Level | Expectation |
|---|---|---|
| E06-S1 | M | One source, `kind: message`, for the channel thread; participants Sam, Maya (Lena optional). |

## Records
| ID | Level | Type | Expectation |
|---|---|---|---|
| E06-R1 | M | risk | SSO integration blocked: identity vendor's API change broke SAML connector validation; no ETA; could push the 2026-11-02 beta. `status: active`; `impact: high` (or medium); linked to `projects/enterprise-launch`; `owner` Sam (S). |
| E06-R2 | M | project (existing) | `projects/enterprise-launch` reused: `health: at_risk` (or `off_track`) and an Updates line citing E06-S1. No new enterprise launch project. |
| E06-R3 | M | person | Sam Okafor: `org` Acme, engineering lead (or engineering), `relationship: peer`. |

## Commitments
| ID | Level | Direction | Owner | Counterparty | Due | Notes |
|---|---|---|---|---|---|---|
| E06-C1 | M | waiting_on | Sam | Maya | 2026-10-16 | Revised SSO estimate "by Friday". |

## Must not
| ID | Expectation |
|---|---|
| E06-X1 | Any record, insight, or brief item about the coffee machine. |
| E06-X2 | A person record for "Jira Bot", or records/sources for the Jira status messages on their own. (Mentioning ENT-142 inside the risk is fine.) |
| E06-X3 | A commitment for Lena's mockups ("in Figma if anyone wants a look"). |
