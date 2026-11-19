# Guardrails

Only input validation and eligibility are implemented. All other controls below are requirements for subsequent increments, not claims about current runtime protection.

| Control | Purpose | Enforcement | Failure behaviour | Status |
| --- | --- | --- | --- | --- |
| Required event fields | Prevent analysis of unknown identity or restriction state | Validate nonempty IDs/reason, EUR currency, finite nonnegative numeric value and boolean hard stop | failed; eligible=null; manual_review route | Implemented |
| Eligibility | Limit the pilot to credit blocks, inclusive EUR 50k–250k and explicitly clear hard stop | Python rules with Decimal monetary comparison | completed; eligible=false; manual_review route | Implemented |
| Case deduplication | Avoid duplicate handling of repeated ERP events | Registry keyed by order ID and block reason; retain event IDs separately | Return existing case or reassess changed facts | Planned |
| Fact validation | Prevent favourable defaults or fabricated inputs | Validate all required ERP/CRM facts and provenance | Manual review with missing/invalid fields | Planned |
| Evidence applicability | Avoid obsolete or unrelated rules | Approved corpus, effective versions, customer scope, sections and excerpts | Manual review for absent or conflicting evidence | Planned |
| Join gate | Prevent assessment from partial results | Require successful business and policy collector results | Manual review; no recommendation | Planned |
| Deterministic risk | Make classifications reproducible and testable | Explicit thresholds and boundary tests | Invalid facts cannot be classified | Planned |
| Action intersection | Prevent policy or contract bypass | Intersect explicit permissions; validate prohibitions and obligations | Exclude action; escalate unresolved conflicts | Planned |
| LLM separation | Prevent text generation from authorising actions | LLM can explain validated facts; cannot write risk, approval or execution fields | Reject invalid output; use deterministic template | Planned |
| Human decision | Require accountable approval | Verified identity, role, assignment, selected action and context revision | Pause or reject unauthorised decision | Planned |
| Override justification | Preserve rationale and authority limits | Require nonblank rationale and permitted action/parameters | Reject override | Planned |
| Information request | Resolve evidence gaps before action | Route to relevant collector; invalidate pending approval | Rejoin and reassess before new review | Planned |
| Approval freshness | Avoid execution based on stale facts | Recheck hard stop, material facts and applicable restrictions | Invalidate approval and reassess; hard stop goes to manual review | Planned |
| Action parameter validation | Prevent excessive or ambiguous release | Check amounts, allocation, currency and expiry against limits | Reject action | Planned |
| Idempotent execution | Prevent repeated financial operations | Stable operation ID with execution record and ERP reconciliation | Do not retry uncertain outcomes blindly | Planned |
| Auditability | Reconstruct facts, decisions and outcomes | Append-only events linked to case, revision and operation | Do not execute if required decision audit cannot be recorded | Planned |

## Why deterministic decisions

The eligibility and risk thresholds are explicit business rules. An LLM introduces variability without improving those calculations. Code can make the result reproducible and boundary-testable; for example, 90% payment rate does not meet the High trigger, while 89.99% does.

Permission checks must also be deterministic. A fluent explanation is not proof of reviewer authority, current approval or contractual permission. Generated text may help the reviewer understand evidence, but it must not expand the permitted action set.

## Input and operational limits

The current function expects a Python mapping; the CLI expects a trusted JSON fixture. Transport/schema validation of arbitrary top-level payloads is not implemented. Runtime type hints alone do not enforce this boundary.

Future document retrieval must treat prompt-like instructions in documents as untrusted content. Tool access must remain scoped, and extracted rules must be validated against an approved policy representation.

The mock environment must not contain real customer data or credentials. Production identity, audit integrity, access controls, concurrency safety and retention remain separate implementation work.
