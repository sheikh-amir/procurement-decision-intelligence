# User Stories and Acceptance Criteria

## Epic A — Reliable source processing

### US-01 — Data quality gate

**As a Data/BI owner, I want the analytical pipeline to stop when critical source-quality rules fail so that unreliable data cannot silently produce management alerts.**

**Acceptance criteria**

- Given a required field is missing, when the pipeline validates the schema, then processing fails with the missing field identified.
- Given duplicate `OBJECTID` values exist, when the quality gate runs, then the quality report records a FAIL and scoring does not continue.
- Given amount parsing falls below the accepted level, then the quality gate fails.

## Epic B — Explainable prioritization

### US-02 — Evidence-rich case queue

**As an Investigation Analyst, I want cases ranked by several different evidence dimensions so that I can focus on patterns supported by more than one type of signal.**

**Acceptance criteria**

- Every record has a 0–100 score.
- Every record retains component signal values.
- Every record has human-readable reason codes.
- Every record has a count of independent evidence families.
- The user can filter by minimum priority score.

### US-03 — Relationship context

**As an Investigation Analyst, I want to see vendor concentration and cross-agency reach so that I can understand whether a transaction is part of a broader relationship pattern.**

**Acceptance criteria**

- Vendor share of agency observed spend is available.
- Number of agencies associated with the vendor is available.
- The dashboard displays relationship metrics without describing them as proof of wrongdoing.

### US-04 — Temporal change

**As an Investigation Analyst, I want to see recent vendor-spend spikes relative to observed history so that sudden changes are visible even when the absolute amount is not extreme.**

**Acceptance criteria**

- Current month vendor spend is compared against prior observed months.
- Records without enough history use a documented fallback.
- “New relationship” wording states that it means newly observed in the dataset.

## Epic C — Management decision support

### US-05 — Threshold decision frontier

**As a Control Manager, I want to see the workload and priority-coverage impact of different score thresholds so that I can make an explicit control-setting decision.**

**Acceptance criteria**

- The frontier includes score threshold, alert count, review hours and proxy coverage.
- Alert volume does not increase when the threshold rises.
- Proxy coverage does not increase when the threshold rises.
- The interface states that proxy coverage is not accuracy/recall.

### US-06 — Capacity-constrained recommendation

**As a Control Manager, I want a threshold recommendation based on available review hours and minimum evidence diversity so that the operating queue is sustainable.**

**Acceptance criteria**

- Capacity is a configurable input.
- The recommended threshold meets capacity when a feasible threshold exists.
- The chosen recommendation logic is documented.

### US-07 — Backlog risk

**As a Control Manager, I want the probability of exceeding weekly review capacity so that I can account for complex cases and not rely solely on an average review time.**

**Acceptance criteria**

- Simulation is reproducible under a fixed random seed.
- Output includes P50 and P90 workload hours.
- Output includes backlog probability.
- Increasing capacity cannot increase backlog probability when all other inputs are unchanged.

## Epic D — Governance

### US-08 — Change traceability

**As a Governance Owner, I want analytical configuration and requirements traceable to tests and outputs so that changes can be reviewed before release.**

**Acceptance criteria**

- A model version is available.
- Requirements trace to implementation.
- Automated tests run in CI.
- Material score/config changes require a version increment in the governance process.
