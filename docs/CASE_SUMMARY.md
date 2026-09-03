# Case Summary

A short narrative of the problem, the approach and the outcome, for readers who want the
story before the code.

## The short version

“I used a public purchase-card dataset to model a realistic controls problem: a team has far more transactions than review capacity. Instead of building another dashboard, I treated it as a Business Analysis problem. I defined stakeholders and requirements, redesigned the exception-management process, created an explainable multi-signal prioritization engine, and then built a capacity optimizer that recommends a review threshold. I also used Monte Carlo simulation to show management the probability of creating a backlog. My audit background shaped the risk and evidence logic, while the project demonstrates how I apply that thinking to requirements, process design and decision support.”

## The longer version

### Situation

High-volume transaction review is often constrained by analyst time. A flat rule can generate more exceptions than the team can investigate.

### Task

Design a future-state process that prioritizes evidence-rich cases, explains why each case is selected and makes review capacity an explicit management decision.

### Action

I designed:

1. hierarchical peer benchmarking;
2. duplicate/burst/context/timing signals;
3. vendor concentration and cross-agency relationship features;
4. temporal spend-spike analysis;
5. an unsupervised anomaly signal;
6. evidence-family diversity;
7. transaction-level reason codes;
8. a capacity-constrained threshold optimizer;
9. Monte Carlo backlog simulation;
10. quality gates and model-governance controls.

I documented the work through a BRD, stakeholder map, process redesign, user stories, KPI dictionary, risk/control matrix and requirements traceability matrix.

### Result

The product does not just answer “what looks unusual?” It answers:

> “Given our analyst capacity, where should we set the review threshold, what workload does that create, and why is each selected transaction worth investigating?”

## Strong interview discussion points

### Why not call it fraud detection?

Because the public data has no investigation dispositions or supporting evidence. Calling anomalies fraud would be analytically and professionally unsound.

### Why use Isolation Forest if you already have rules?

Rules capture known business patterns; the anomaly model helps surface unusual multivariate combinations. It is deliberately only one component of an explainable score.

### Why Monte Carlo simulation?

Average review time hides operational risk. A long tail of complex cases can create backlog even when average planned hours appear feasible.

### Why evidence families?

Several correlated rules can exaggerate confidence. Independent evidence dimensions create a stronger basis for prioritization.

### What would you change with real investigation outcomes?

I would measure disposition yield, calibrate thresholds by segment, evaluate precision/recall where appropriate, monitor drift, and consider supervised models only after label quality had been assessed.
