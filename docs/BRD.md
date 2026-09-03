# Business Requirements Document (BRD)

## 1. Initiative

**Procurement Decision Intelligence — Explainable Exception Prioritization and Capacity Optimization**

## 2. Business problem

Transaction-review teams can face a structural mismatch between **transaction volume** and **available analyst capacity**. Traditional threshold or single-rule controls may create a queue that is either too broad to investigate or so narrow that potentially important patterns are ignored.

The decision problem is therefore not merely “which transactions are anomalous?” It is:

> **How should a control team prioritize transactions and choose a review threshold so that the queue is explainable, operationally feasible, and supported by diverse evidence?**

## 3. Objectives

1. Create a repeatable data-ingestion and quality-control process.
2. Detect several defensible exception patterns using different evidence dimensions.
3. Prioritize transactions through an explainable business score.
4. Distinguish evidence diversity from raw score magnitude.
5. Quantify the trade-off between coverage and analyst workload.
6. Recommend a review threshold under stated capacity constraints.
7. Estimate workload uncertainty rather than relying only on an average review time.
8. Provide management and analysts with an interactive decision interface.
9. Preserve traceability, assumptions and change-control evidence.

## 4. Stakeholder decisions

| Stakeholder | Primary decision supported |
|---|---|
| Procurement / Control Manager | What review threshold can the team sustainably operate? |
| Investigation Analyst | Which case should be reviewed next and why? |
| Governance / Risk Owner | Are model assumptions controlled and interpretable? |
| Data / BI Team | Is the source reliable enough to process? |
| Agency Manager | Which recurring patterns require process or control action? |

## 5. Scope

### In scope

- public purchase-card transaction ingestion;
- schema and quality controls;
- hierarchical peer analysis;
- repeat and burst patterns;
- agency/category context analysis;
- vendor concentration and relationship features;
- temporal spend-spike analysis;
- unsupervised anomaly support;
- explainable scoring;
- evidence-diversity measurement;
- threshold frontier and capacity optimization;
- Monte Carlo workload-risk simulation;
- dashboard and governed outputs;
- BA and control documentation.

### Out of scope

- declaring fraud, misconduct or policy breach;
- automatic punitive action;
- claims about DC's actual internal control process;
- policy-specific limits not verified from official policy;
- vendor-master entity resolution beyond observed source names;
- supervised learning without validated outcome labels;
- automated case assignment to real employees.

## 6. Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Retrieve all available source records using pagination. | Must |
| FR-02 | Validate required schema before analysis. | Must |
| FR-03 | Produce a data-quality control report and stop on critical failures. | Must |
| FR-04 | Normalize dates, amounts and core categorical fields reproducibly. | Must |
| FR-05 | Benchmark amount risk using a hierarchical peer strategy with fallback logic. | Must |
| FR-06 | Identify repeat, burst, contextual and timing exception signals. | Must |
| FR-07 | Derive agency/vendor concentration and cross-agency relationship indicators. | Must |
| FR-08 | Evaluate observed relationship age and temporal vendor-spend spikes. | Must |
| FR-09 | Produce a multivariate anomaly signal using deterministic configuration. | Should |
| FR-10 | Produce a 0–100 priority score using version-controlled weights. | Must |
| FR-11 | Retain every component signal and human-readable reason code. | Must |
| FR-12 | Calculate independent evidence-family count and evidence-confidence indicator. | Must |
| FR-13 | Produce a threshold decision frontier showing alerts, review hours and proxy coverage. | Must |
| FR-14 | Recommend a threshold subject to analyst-capacity and evidence-diversity constraints. | Must |
| FR-15 | Simulate workload uncertainty and backlog probability. | Must |
| FR-16 | Produce agency-level and vendor-level management summaries. | Should |
| FR-17 | Expose results in an interactive dashboard. | Should |
| FR-18 | Run end-to-end with a single pipeline command. | Must |

## 7. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | **Explainability:** no selected case may require an opaque score interpretation. |
| NFR-02 | **Reproducibility:** stochastic methods must use controlled random seeds. |
| NFR-03 | **Auditability:** analytical assumptions and decisions must be documented. |
| NFR-04 | **Maintainability:** configuration must be separated from transformation logic. |
| NFR-05 | **Data integrity:** critical source-quality failures must stop the pipeline. |
| NFR-06 | **Interpretation safety:** outputs must be described as screening indicators, not findings. |
| NFR-07 | **Traceability:** requirements must map to implementation and validation evidence. |
| NFR-08 | **Operational usability:** management must be able to understand workload implications without reading code. |

## 8. Business rules

1. Amount significance must be evaluated relative to relevant peers where enough peer data exists.
2. A repeated transaction pattern is an investigation indicator, not proof of duplicate payment.
3. Weekend and round-dollar signals are weak evidence and therefore receive limited weight.
4. Vendor concentration can reflect legitimate sourcing strategy and must not be interpreted as wrongdoing by itself.
5. “New vendor” means **newly observed within the available dataset**, not newly onboarded in the procurement system.
6. The configurable `$5,000` proximity setting is a scenario parameter and is not presented as an official DC threshold.
7. The anomaly model supports prioritization but cannot infer intent.
8. Priority-score coverage is a management proxy and must not be represented as recall or model accuracy.
9. A threshold recommendation is valid only under its stated analyst-capacity and review-time assumptions.

## 9. Management decision logic

The solution creates a decision frontier across score thresholds. A feasible threshold must satisfy:

```text
Estimated review hours <= available review capacity
AND
Evidence-diversity rate >= management minimum, where possible
```

Among feasible choices, the default recommendation selects the **lowest threshold** to preserve the broadest priority-score coverage.

## 10. Success criteria

The prototype is successful if it can:

- stop processing when a critical source-quality control fails;
- produce a ranked and explainable review queue;
- distinguish independent evidence families;
- show relationship and temporal patterns not visible in a flat rule set;
- quantify the queue-size/workload trade-off;
- recommend a capacity-feasible threshold;
- quantify backlog probability under review-time uncertainty;
- provide traceable BA and governance documentation;
- pass automated tests in CI.

## 11. Constraints and dependencies

- Public data may change schema or availability.
- Investigation outcomes are not provided.
- Supporting documentation and policy context are unavailable.
- Public vendor names may require stronger entity resolution in production.
- Review-time assumptions are scenario inputs, not observed organizational benchmarks.

## 12. Requirement traceability

Detailed implementation/test mapping is maintained in [`REQUIREMENTS_TRACEABILITY.md`](REQUIREMENTS_TRACEABILITY.md).
