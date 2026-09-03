# Risk and Control Matrix

| Risk / failure mode | Control objective | Analytical / process control | Owner | Evidence | Residual limitation |
|---|---|---|---|---|---|
| Source schema changes silently | Process only valid source structure | required-column validation | Data/BI | pipeline log | semantic changes can still occur |
| Duplicate source IDs | Avoid double counting | duplicate-ID quality gate | Data/BI | quality report | source may contain legitimate revisions |
| Invalid amounts | Prevent corrupted scoring | numeric parse threshold | Data/BI | quality report | business meaning of reversals may need context |
| One-size-fits-all amount threshold | Compare transactions fairly | hierarchical peer benchmark | Analytics/Governance | component score | peer groups can still be heterogeneous |
| Repeat transactions overlooked | Surface potential duplicate patterns | near-duplicate logic | Control Analyst | reason code | legitimate recurring purchases exist |
| Structural supplier dependency hidden | Make concentration visible | vendor share / reach metrics | Procurement | vendor view | contracts may justify concentration |
| Sudden relationship changes missed | Detect changes against observed history | temporal spend-spike feature | Control Analyst | temporal reason code | seasonal patterns can generate spikes |
| Opaque anomaly model drives action | Preserve explainability | anomaly has limited weight + retained reasons | Governance | score components | feature interactions remain complex |
| Correlated rules overstate confidence | Distinguish independent evidence | signal-family count | Governance | evidence-confidence field | families are designed, not statistically independent |
| Queue exceeds staff capacity | Operate sustainable control | threshold optimizer | Control Manager | decision frontier | review-time assumptions may be wrong |
| Average review time hides long tail | Quantify workload uncertainty | Monte Carlo simulation | Control Manager | backlog probability / P90 | distribution is scenario assumption |
| Analytics interpreted as fraud finding | Prevent unsupported conclusions | interpretation safeguards | Governance | README/model governance | user behavior cannot be fully controlled |
| Ad hoc model changes | Maintain controlled process | model version + decision log + CI | Governance | commit / version / test result | formal approval system not implemented |
