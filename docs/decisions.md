# Decisions and open questions

## Recovered baseline

Design baseline established in July 2026 and reviewed in September 2026.

- One credit-related B2B exception workflow with synthetic data.
- Three eligibility conditions: credit block, EUR 50k–250k inclusive, no hard stop.
- Parallel business and policy context collection; both must complete before assessment.
- Low: all criteria pass — payment rate >=97%, exceedance <=EUR25k, overdue <=7 days, Strategic, no critical escalation.
- High: any trigger — payment rate <90%, exceedance >EUR75k, overdue >30 days, critical escalation present.
- Otherwise Medium, provided all required inputs are valid. High triggers take precedence over Low classification.
- Risk, authority and routing are deterministic; LLM explains, without changing the result.
- All cases require human review before any mock release or limit change.
- Every decision and execution must be traceable. Unknown input must never become invented evidence.
- Contract, policy and applicable mandatory restrictions jointly constrain actions.

These thresholds are illustrative business assumptions, not externally validated credit policy.

## New decision: reviewer authority, October 4, 2026

Anna selected: a senior reviewer may review their own risk level and lower levels.

Proposed hierarchical matrix for the prototype:

| Verified role | Low | Medium | High |
| --- | --- | --- | --- |
| Credit Analyst | Yes | No | No |
| Credit Manager | Yes | Yes | No |
| Senior Credit Manager | Yes | Yes | Yes |

Default routing remains Low -> Analyst, Medium -> Manager, High -> Senior Manager. Having authority does not automatically assign a case. The reassignment procedure remains to be designed.

Role authority never permits an action prohibited by policy, contract or a hard stop. Demonstration identities will be synthetic. Production identity verification and permissions are not implemented in milestone 1.

## Collaboration

Codex prepares small implementation increments, documentation and checks. Anna owns business choices and explains the examples back in her own words. Changes are discussed in terms of inputs, outputs, permitted actions and failure behavior before adding framework complexity.

## Open before later milestones

- Bind assigned reviewer identity to a trusted session; select demo authentication mechanism.
- Define reassignment, absence handling and expiry of approvals.
- Finalize monetary/action parameters and partial-release semantics.
- Define permitted-action mappings using coherent synthetic policy/contract/SOP documents.
- Define assessment freshness, context revision changes and legal/compliance source boundaries.
- Choose LLM provider, retrieval storage and LangGraph persistence.
- Reconcile status names in the older discussion into one transition table.
