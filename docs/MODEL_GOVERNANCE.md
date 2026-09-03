# Analytical Model Governance

## Model purpose

Prioritize transactions for human review and support management decisions about review capacity. The model is **not** designed to classify fraud or determine employee/vendor intent.

## Model version

Current analytical configuration: **2.0.0**

A version change is required when any of the following change materially:

- signal definition;
- signal weight;
- peer-group hierarchy;
- anomaly-model features;
- decision threshold logic;
- workload assumptions;
- data source/schema.

## Evidence architecture

Signals are intentionally distributed across independent evidence families:

| Family | Examples |
|---|---|
| Magnitude | hierarchical peer amount |
| Pattern | near duplicate, same-day burst |
| Context | rare agency/category combination |
| Timing | weekend activity |
| Network | vendor concentration, cross-agency reach |
| Temporal | monthly vendor-spend spike |
| Relationship | newly observed agency/vendor relationship |
| Multivariate | Isolation Forest anomaly |

The `signal_family_count` prevents a case supported by one repeated idea from looking as strong as a case supported by several different evidence dimensions.

## Explainability requirement

Every selected transaction must retain:

- raw component signals;
- total priority score;
- priority band;
- reason codes;
- top weighted contributors;
- evidence-family count.

No transaction should be escalated solely because an opaque model produced a high value.

## Decision proxy limitation

Because the dataset has no validated outcome labels, the optimizer uses **priority-score coverage** rather than recall/precision. This is acceptable for scenario planning but must not be described as model accuracy.

## Monitoring controls for production

A production implementation should monitor:

1. source schema drift;
2. missingness and duplicate rates;
3. score-distribution drift;
4. alert volume by agency;
5. vendor concentration shifts;
6. reviewer disposition yield;
7. false-positive / explained-case rate;
8. average investigation time;
9. queue aging and SLA breaches;
10. rule/weight changes and approvals.

## Change control

Proposed model changes should include:

```text
Change request
→ business rationale
→ affected requirement/control
→ offline comparison
→ impact on queue/workload
→ reviewer sign-off
→ control-owner approval
→ version increment
→ deployment
→ post-change monitoring
```

## Ethical / interpretation safeguards

- Do not label a person, vendor or agency as fraudulent from these outputs.
- Avoid punitive decisions without independent evidence.
- Investigate whether data quality or operational context explains an alert.
- Review concentration indicators carefully: concentration can reflect legitimate contracts or specialized suppliers.

## Weight sensitivity stress test

Score weights encode business judgment and therefore create model risk. The project perturbs the governed weights around their baseline values using a Dirichlet distribution, recalculates the top-N queue, and measures **Jaccard overlap** with the baseline queue.

Management interpretation:

- high overlap → queue is relatively stable under reasonable weight changes;
- low overlap → queue depends materially on subjective weighting and requires stronger challenge/testing;
- this metric measures ranking robustness, **not** probability that an alert is correct.
