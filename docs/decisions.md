# Architecture decisions

## 1. Keep business gates deterministic

Eligibility and risk thresholds are explicit. Implement them as Python rules with boundary tests, rather than asking an LLM to classify orders. This gives reproducible decisions and makes missing data distinguishable from ineligibility.

An LLM may explain a result using supplied evidence. Its output cannot change risk, permissions, routing or approval validity.

## 2. Separate business facts from policy evidence

ERP/CRM collection and document retrieval require different validation and provenance. Separate collectors can run in parallel; a join gate prevents incomplete context from entering assessment.

The trade-off is additional state and failure handling. A single conversational agent would be simpler to prompt but would obscure which source is missing and who owns a decision.

## 3. Build an offline baseline first

Use standard-library Python, synthetic ERP/CRM records and explicit policy rules before adding model APIs or a vector store. This keeps the demo reproducible without paid services and provides reference scenarios for future retrieval evaluation.

Structured fixture lookup is not RAG. Describe RAG as implemented only after retrieval and grounded generation exist and are evaluated.

## 4. Human approval for every action

The system prepares a recommendation; a human authorises the selected action. A Low classification does not grant automatic release.

| Verified role | Low | Medium | High |
| --- | --- | --- | --- |
| Credit Analyst | Yes | No | No |
| Credit Manager | Yes | Yes | No |
| Senior Credit Manager | Yes | Yes | Yes |

Default routing follows the risk level. Higher authority permits review of lower levels only with valid assignment. It never permits bypassing a hard stop or document restriction.

## 5. Intersect action permissions

Credit policy, supply agreement and approval SOP have different responsibilities. A permissive rule in one document cannot cancel a restriction in another. Silence is not permission.

If no action is clearly permitted, escalate. Keep blocked is a fallback only when it does not conflict with an applicable obligation.

## 6. Bind approval to facts and action parameters

Approve an exact context revision and action payload. Recheck material facts before execution. Even a change within the same risk band can affect the permitted amount or recommendation.

This adds a review cycle when facts change, but avoids executing a stale decision.

## 7. Reconcile uncertain execution

Use a stable operation ID. After a timeout, inspect the ERP outcome before retrying. A retry may otherwise repeat a release or credit-limit change.

Local idempotency alone does not guarantee exactly-once execution across systems. The mock adapter must expose a reconciliation lookup to demonstrate that distinction.

## 8. Defer framework selection until persistence is needed

Current code has one synchronous gate. LangGraph could support future branches and human-review pause/resume, but introducing it now would not implement those business capabilities by itself.

Keep contracts independent of a framework. Select persistence and orchestration together when durable cases are implemented.

## Open implementation decisions

- Demo identities, assignment, reassignment and approval expiry.
- Partial-release allocation and temporary-limit amount/duration limits.
- Effective synthetic policies and contractual obligation/conflict semantics.
- Material-fact comparison, freshness window and source failure handling.
- Persistent case/operation store and concurrency control.
- Retrieval evaluation dataset, model provider and explanation validation.
