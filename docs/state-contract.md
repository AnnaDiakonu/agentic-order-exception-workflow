# State contract

## Implemented contract

`check_eligibility(event)` accepts a mapping and returns an immutable `EligibilityResult`. It does not create or persist a case.

Required inputs: nonempty string `block_event_id`, `order_id`, `customer_id`, `block_reason`; `currency="EUR"`; finite nonnegative numeric `order_value`; boolean `hard_stop_flag`. Booleans and numeric strings are rejected as amounts.

| status | eligible | reasons | next_route |
| --- | --- | --- | --- |
| completed | true | Empty tuple | collect_context |
| completed | false | Failed business conditions | manual_review |
| failed | null | Missing or invalid fields | manual_review |

The CLI converts this dataclass to JSON. Route labels have no execution side effects.

## Target case record — planned

The orchestrator owns lifecycle changes; collectors own their outputs. Facts, assessments, approvals and executions remain separate records.

| Group | Fields | Owner |
| --- | --- | --- |
| Identity | case_id, order_id, customer_id, source_event_ids, block_reason | Case registry |
| Trigger | order_value, currency, hard_stop_flag, received_at | Event adapter |
| Lifecycle | status, created_at, updated_at, context_revision | Orchestrator |
| Eligibility | status, eligible, reasons, checked_at | Eligibility gate |
| Business facts | payment_rate_percent, credit_exceedance_eur, overdue_amount_eur, overdue_days, customer_tier, critical_escalation | Business collector |
| Fact provenance | source, source_record_id, retrieved_at, raw_value, normalized_value | Business collector |
| Policy | constraints, evidence, applicable_versions | Policy collector |
| Collector outcomes | status, missing_fields, invalid_fields, error_reason | Each collector |
| Assessment | risk, matched_criteria, allowed_actions, excluded_actions, recommended_action, explanation, context_revision | Risk and explanation components |
| Assignment | required_role, assigned_reviewer_id, assigned_at | Review service |
| Decision | decision_id, decision_type, action, parameters, reviewer_id, verified_role, justification, reviewed_at, expires_at, context_revision | Review service |
| Execution | operation_id, approval_id, status, erp_reference, attempted_at, reconciled_at, error_reason | Executor |
| Audit | audit_event_id, case_id, context_revision, actor_id, event_type, timestamp, result_reference | Audit writer |

Event ID identifies a notification; order ID identifies the ERP order; case ID identifies a review. Deduplicate cases by order and block reason, retaining all source event IDs. A changed event must not silently overwrite an approved snapshot.

## Fact and evidence validation

Payment rate covers the last three months and is a number from 0 to 100. Amounts are finite nonnegative EUR values; overdue days is a nonnegative integer. Tier is Strategic or Standard. Critical escalation is boolean. Reject booleans as numbers and never replace unknowns with zero.

Each evidence record must include document ID/name, version, effective date, customer scope, section, excerpt, applicable rule and retrieval time. Unresolved applicability or conflicts fail the join gate.

Timestamps use timezone-aware UTC. Runtime validation is required; annotations alone are not sufficient.

## Review decisions

- `approve_recommendation`: approve the exact recommended action and parameters.
- `override_recommendation`: select a different permitted action with mandatory justification.
- `request_more_information`: record the question and collector target; no execution approval.

Reviewer role must come from a trusted identity mapping, not a client-supplied role. A demo identity mapping must be explicitly labelled simulated.

Actions: `full_release`, `partial_release`, `temporary_limit_increase`, `require_prepayment`, `keep_blocked`. Partial release requires allocation and amount; temporary increase requires amount and expiry. Their precise schemas and policy bounds remain open and must be implemented before execution.

## Target transitions

| State | Successful next state | Failure or alternate path |
| --- | --- | --- |
| created | eligibility_check | Duplicate returns existing case |
| eligibility_check | collecting_context | manual_review_required |
| collecting_context | assessing | manual_review_required |
| assessing | awaiting_human_review | manual_review_required |
| awaiting_human_review | ready_for_execution | waiting_for_information |
| waiting_for_information | collecting_context | Remain waiting; no execution |
| ready_for_execution | executing | Reassess changed context or reject approval |
| executing | completed | Known failure: manual review; uncertain: manual_execution_check |
| manual_execution_check | completed after confirmation | Revalidate before retry only if confirmed not applied |

Information requests and material changes invalidate pending approval. Reassessment must use a new context revision and preserve previous evidence and decisions.

Before execution, validate approval, reviewer authority, action parameters, justification, expiry, current hard stop and material facts. Check prior operation outcome. An uncertain outcome must be reconciled before another attempt.

The case store, transition enforcement, revisioning, approval checks, executor and audit writer are all planned.
