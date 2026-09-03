# Stakeholder Analysis

| Stakeholder | Influence | Primary need | Decision / action | Main concern |
|---|---|---|---|---|
| Control / Procurement Manager | High | sustainable, defensible review queue | set threshold and capacity | too many alerts or missed patterns |
| Investigation Analyst | High | explainable prioritization | investigate / disposition case | opaque score, false positives |
| Governance / Risk Owner | High | controlled analytical process | approve changes / challenge assumptions | unmanaged model risk |
| Data / BI Owner | Medium-High | stable source and reproducible pipeline | maintain data process | schema/data-quality failure |
| Agency Manager | Medium | meaningful root-cause insight | remediate process/control issue | unfair comparison or context loss |
| Internal Audit / Assurance | Medium | evidence of control design and traceability | assess process/control effectiveness | overreliance on analytics |

## Power-interest approach

### Manage closely

- Control / Procurement Manager
- Governance / Risk Owner
- Investigation Analyst

### Keep satisfied

- Agency management
- Assurance / Audit

### Keep informed

- Data/BI operational stakeholders

## Key elicitation questions

### Control Manager

- How many analyst hours are actually available for this queue?
- Is the objective broad preventive coverage or narrow high-confidence escalation?
- What level of queue volatility is operationally acceptable?
- Which alerts require same-day vs weekly review?

### Analyst

- What information is required before an investigation can start?
- Which existing alerts are consistently explainable/benign?
- What makes one case materially harder than another?
- Which reason codes would be actionable?

### Governance Owner

- Which model/config changes require approval?
- What evidence is required to justify a threshold change?
- Which metrics should trigger a model review?
- What language is prohibited because it could overstate the model's meaning?

## Core conflict to manage

```text
Management wants fewer alerts
        ↕
Analysts want higher-quality evidence
        ↕
Governance wants defensibility
        ↕
Risk owners want sufficient coverage
```

The decision frontier makes this trade-off visible instead of hiding it inside a technical score.
