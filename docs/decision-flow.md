# Decision flow

## Current executable path

The CLI passes each fixture object to the eligibility function and prints its result. It does not create cases or execute the returned route.

```mermaid
flowchart TD
    E["Synthetic event object"] --> V{"Required inputs valid?"}
    V -->|No| F["failed; eligible = null"]
    V -->|Yes| G{"Credit block, EUR 50k–250k, no hard stop?"}
    G -->|No| N["completed; eligible = false"]
    G -->|Yes| Y["completed; eligible = true"]
    F --> M["Return manual_review"]
    N --> M
    Y --> C["Return collect_context"]
```

## Target end-to-end workflow

Everything below is planned except the validation and eligibility rules. The ingestion and manual-review services are not implemented.

```mermaid
flowchart TD
    E["ERP blocked-order event"] --> V{"Input valid?"}
    V -->|No| M["Manual review with reason"]
    V -->|Yes| D{"Existing order and block-reason case?"}
    D -->|Yes| U["Attach event; inspect case and changed facts"]
    U -->|Unchanged| O["Return existing case; no duplicate action"]
    U -->|Changed| I["Invalidate prior approval"]
    D -->|No| C["Create case with distinct case ID"]
    C --> G{"Eligible?"}
    I --> G
    G -->|No| M
    G -->|Yes| B["Business context collector"]
    G -->|Yes| P["Policy context collector"]
    B --> J{"Both complete; facts and evidence valid?"}
    P --> J
    J -->|Missing, failed or conflicting| M
    J -->|Yes| R["Calculate deterministic risk"]
    R --> A["Intersect policy and contract actions"]
    A --> K{"Any permitted action?"}
    K -->|No or unresolved obligation| M
    K -->|Yes| Q["Prepare evidenced recommendation"]
    Q --> H["Route to authorised human"]
    H --> T{"Reviewer decision"}
    T -->|More information| F["Record question; invalidate pending approval"]
    F --> W{"Relevant context"}
    W -->|Business| B
    W -->|Policy| P
    W -->|Both| B
    W -->|Both| P
    T -->|Approve or justified override| S{"Approval, authority, action and parameters valid?"}
    S -->|No| H
    S -->|Yes| N{"Fresh hard stop and material facts checked?"}
    N -->|New hard stop or failed refresh| M
    N -->|Material change| I
    N -->|Unchanged| X{"Operation already executed?"}
    X -->|Yes| O
    X -->|No| Z["Execute approved mock ERP action"]
    Z --> ZR{"Outcome"}
    ZR -->|Confirmed| DONE["Record result; close case"]
    ZR -->|Known failure| M
    ZR -->|Uncertain| REC["Reconcile using stable operation ID"]
    REC -->|Confirmed applied| DONE
    REC -->|Confirmed not applied| S
    REC -->|Unresolved| MX["Manual execution check"]
    C -.-> AUD["Audit every transition and revision"]
    Q -.-> AUD
    T -.-> AUD
    ZR -.-> AUD
```

Audit arrows illustrate the cross-cutting requirement; all transitions, failures and retries must be recorded, not only the four shown.

## Risk rules

Evaluate only complete, valid facts. High triggers take precedence.

| Risk | Rule | Default reviewer |
| --- | --- | --- |
| High | Any: payment rate <90%; exceedance >EUR 75,000; overdue >30 days; critical escalation | Senior Credit Manager |
| Low | All: payment rate >=97%; exceedance <=EUR 25,000; overdue <=7 days; Strategic tier; no critical escalation | Credit Analyst |
| Medium | Every other valid case | Credit Manager |

Overdue amount is a required context fact but is not a risk threshold in this design. Missing facts must not become Medium by default.

A senior reviewer may handle lower levels, subject to assignment. Overrides require justification and cannot exceed policy, contract or authority limits. Keep blocked is a conservative recommendation only when permitted and no unresolved obligation requires escalation.
