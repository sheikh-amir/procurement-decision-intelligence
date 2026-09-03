# KPI Dictionary

## Management KPIs

| KPI | Definition / formula | Decision supported | Interpretation control |
|---|---|---|---|
| Alert Rate | selected alerts / all transactions | How broad is the review queue? | Not misconduct rate |
| Review Hours | alerts × assumed review minutes / 60 | Can the queue be staffed? | Scenario-based |
| Proxy Risk Coverage | sum(priority scores selected) / sum(all priority scores) | How much modeled priority is retained at a threshold? | Not recall / accuracy |
| Multi-Family Rate | selected cases with 3+ evidence families / selected cases | Is the queue supported by diverse evidence? | Families may still have dependencies |
| Backlog Probability | Monte Carlo probability simulated workload exceeds capacity | How risky is the operating threshold? | Depends on workload assumptions |
| P90 Review Hours | 90th percentile simulated review workload | What capacity buffer is prudent? | Simulation output, not guarantee |
| High-Priority Volume | count(score ≥ 60) | Where is exception workload concentrated? | Score threshold is analytical |
| Average Priority Score | mean(priority score) | Segment/trend comparison | Sensitive to model-version changes |

## Relationship KPIs

| KPI | Definition | Business use | Caution |
|---|---|---|---|
| Vendor Agency Spend Share | vendor observed spend / agency observed spend | supplier dependency analysis | high share can be legitimate |
| Vendor Cross-Agency Reach | number of agencies using vendor | identify broad relationship footprint | scale is not risk by itself |
| Observed Relationship Age | days since first agency/vendor occurrence in dataset | contextualize newly observed relationships | left-censored dataset |
| Temporal Spend Spike | current month vendor spend vs recent observed history | surface sudden relationship change | seasonality can explain spikes |

## Data-quality KPIs

| KPI | Target | Action |
|---|---:|---|
| Required columns present | 100% | fail if not met |
| Duplicate OBJECTID rate | 0% | fail if > 0 |
| Numeric amount rate | ≥ 99% | fail if below |
| Required-field null rate | ≤ 5% preferred | investigate / warn |

## Future-state outcome KPIs

These require real investigation dispositions and therefore are intentionally **not fabricated** from the public dataset.

| KPI | Formula | Why valuable |
|---|---|---|
| Disposition Yield | actionable cases / reviewed cases | tune queue quality |
| Explained-Case Rate | legitimate/explained cases / reviewed cases | estimate reviewer noise |
| Average Case Cycle Time | close time − open time | process performance |
| SLA Breach Rate | overdue cases / open cases | queue governance |
| Corrective-Action Conversion | cases leading to process/control action / reviewed cases | business impact |
| Recurrence Rate | repeated issue pattern after remediation / remediated patterns | benefits realization |
