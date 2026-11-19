# Architecture

## Scope and implementation status

The proof of concept addresses credit-blocked B2B orders denominated in EUR, with values from 50,000 to 250,000 inclusive. A hard stop excludes a case from automated analysis. Manual review means investigation through a separate process, not permission to bypass a hard stop.

| Component | Responsibility | Status |
| --- | --- | --- |
| Synthetic CLI | Read fixture events and display eligibility | Implemented |
| Eligibility gate | Validate required fields and apply admission rules | Implemented |
| Case registry | Separate event, case and order IDs; deduplicate by order and block reason | Planned |
| Business context collector | Retrieve and validate synthetic ERP/CRM facts | Planned |
| Policy context collector | Retrieve applicable policy, contract and SOP evidence | Planned |
| Join gate | Require both collectors, mandatory facts and consistent evidence | Planned |
| Risk engine | Calculate risk, route reviewer and constrain permitted actions | Planned |
| Explanation component | Summarise facts and evidence without changing risk | Planned |
| Review service | Pause, record decisions, validate authority and handle information requests | Planned |
| Safety gate and executor | Revalidate approval and current facts; execute against mock ERP | Planned |
| Audit store | Record transitions, evidence revisions and action outcomes | Planned |

The collectors are agent roles in the target design. The current implementation contains no autonomous agents or LLM calls.

## Component boundaries

The orchestrator owns state transitions. Collectors return typed, validated results and cannot release orders. The business collector reads ERP/CRM tools; the policy collector reads an approved document corpus. They may run concurrently, but the join gate must wait for both results and reject partial context.

The risk engine consumes validated facts. Policy and contract restrictions constrain actions separately from risk classification: a Low risk result does not imply that full release is permitted.

The review service obtains identity from a trusted source. A role string submitted by a client is not proof of authority. The executor accepts only a validated, current approval and an action with valid parameters.

## Target data sources and evidence

Business facts: payment rate over the last three months, credit-limit exceedance, overdue amount, overdue days, customer tier and critical escalation status. Every fact must retain source and retrieval time.

Policy sources: Credit Exception Policy, Customer Supply Agreement and Credit Exception Approval SOP. Evidence must identify document, version, section, excerpt and applicable rule. The retrieval layer must filter for effective version and customer applicability before a recommendation is considered.

Initial implementation should use explicit structured rules paired with synthetic document excerpts. This provides a reproducible offline baseline, not a claim of RAG. An optional retrieval and generation layer can later locate and explain evidence, with evaluation against the same scenarios. Retrieved text is untrusted data, never an instruction to tools.

## Execution boundary

Supported target actions are full release, partial release, temporary credit-limit increase, require prepayment and keep blocked. Amounts, allocation and expiry are part of an action, not optional annotations. Their schemas and policy limits must be defined before an executor is added.

Approval must reference a context revision and action parameters. Before execution, refresh material business facts, hard stops and applicable restrictions. A material change invalidates approval even if the risk band stays the same.

Use a stable operation ID and reconcile uncertain results with the mock ERP before retrying. A timeout is not evidence that the ERP did nothing.

## Deliberate limits

Use Python modules and synthetic tools before introducing a workflow framework. Add durable orchestration when pause/resume, retries and case persistence are implemented. A future LangGraph integration must preserve the same state and guardrail contracts.

Production concerns remain outside this milestone: identity integration, access controls, transactional persistence, concurrency control, monitoring, retention, real ERP connectivity and legal interpretation.
