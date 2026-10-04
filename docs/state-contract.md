# Case state contract — draft v0.1

This describes the target workflow state. Only the event and eligibility result are implemented in milestone 1. Other fields are a design contract for later milestones.

A case is the shared record of one review process. The orchestrator owns lifecycle changes; each node contributes its own result. A collected fact, a recommended action, a human decision, and an executed action are separate records.

## Fields and ownership

| Group | Fields | Writer |
| --- | --- | --- |
| Identity | case_id, order_id, customer_id, source_event_ids | Trigger / case registry |
| Trigger | block_reason, order_value, currency, hard_stop_flag, received_at | Trigger adapter |
| Lifecycle | case_status, created_at, updated_at, context_revision | Orchestrator |
| Eligibility | status, eligible, reasons, next_route, checked_at | Eligibility node |
| Business context | payment_rate_percent, credit_exceedance_eur, overdue_amount_eur, overdue_days, customer_tier, critical_escalation | Agent 1 through validated tools |
| Business provenance | source, source_record_id, retrieved_at, raw_value, normalized_value | Agent 1 / normalizer |
| Policy context | policy rules, contract constraints, approval requirements, evidence | Agent 2 |
| Collector results | agent_1_status, agent_2_status, missing_fields, invalid_fields, error_source, error_reason | Relevant collector |
| Assessment | risk_level, matched_criteria, allowed_actions, excluded_actions, recommended_action, summary, context_revision | Risk node / explanation node |
| Assignment | required_role, assigned_reviewer_id, assigned_at | Routing node |
| Human review | review_decision, selected_action, action_parameters, reviewer_id, verified_reviewer_role, reviewer_comment, reviewed_at, context_revision | Review service |
| Execution | execution_id, execution_status, executed_at, erp_action_reference, error_reason | Executor |
| Audit | event_id, actor_id, event_type, timestamp, case_id, context_revision, result_reference | Append-only audit writer |

The review service must obtain identity and authority from a trusted session/directory, not from a role supplied in an untrusted request. Personal credentials are not part of case state.

## Data validation

- Trigger order_value is a JSON number in EUR. Currency conversion is out of scope. Eligibility compares monetary values using Decimal.
- All three identifiers and block_reason must be nonempty strings.
- hard_stop_flag must be a boolean. Unknown, missing, 0 and the string "false" are not equivalent to false.
- Payment rate is a number from 0 to 100, measured over the last three months.
- Amounts are nonnegative EUR amounts; overdue_days is a nonnegative integer.
- Customer tier is Strategic or Standard; critical_escalation is a boolean.
- Unknown required data remains unknown. It cannot be replaced with zero or an invented default.
- Node outputs need runtime validation before downstream use; type hints alone are insufficient.
- Timestamps use timezone-aware UTC. User interfaces may display local time.

Eligibility has three distinct outcomes:

| status | eligible | Meaning | Route |
| --- | --- | --- | --- |
| completed | true | All three business conditions pass | collect_context |
| completed | false | Conditions were checked; at least one does not pass | manual_review |
| failed | null | A required input is missing or invalid | manual_review with validation reasons |

Manual review cannot authorize bypassing a hard-stop restriction. It means investigating the case through the appropriate process, not offering an automatic release action.

## Evidence contract

Each extracted rule carries document_id, document_name, version, effective_date, section, excerpt, extracted_rule, and retrieved_at. Agent 2 verifies active applicability to the customer/order. An unresolved version or document conflict prevents automatic risk/recommendation processing.

Actions are constrained by all applicable documents. Permission is not inferred merely from silence in a contract. The synthetic documents must explicitly define how permissions and prohibitions combine.

## Review and execution

review_decision is one of approve_recommendation, override_recommendation, request_more_information.

selected_action is separate: full_release, partial_release, temporary_limit_increase, require_prepayment, keep_blocked. Only actions in the case's allowed_actions can be selected. Override and request_more_information require a comment. Request_more_information does not execute an ERP action.

action_parameters must eventually specify the amount/portion, currency and duration appropriate to the action. They need validation against the applicable rules. This schema is still open; a bare action name is not sufficient for execution.

Approval references the exact context_revision. Before execution, recheck material facts and restrictions. A changed relevant fact invalidates the old approval for execution and triggers reassessment/review. Keep previous decisions in the audit trail.

Use one stable execution_id for one approved operation. On an uncertain ERP response, reconcile the actual ERP state before retrying. A retry reuses that ID. keep_blocked closes the review without releasing the order.

## Proposed lifecycle

```text
created -> eligibility_check -> collecting_context -> risk_evaluation
-> awaiting_human_review -> ready_for_execution -> executing -> completed
```

Alternative states: manual_review_required, waiting_for_information, re_evaluation_required, manual_execution_check, closed_without_action.

The exact transition table and checkpointer are still to be implemented. Failed collectors cannot pass the join gate. A failed explanation can use a template while preserving the rule-based assessment.
