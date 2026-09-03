# Requirements Traceability Matrix

| ID | Business requirement | Implementation | Test / control | Output / evidence |
|---|---|---|---|---|
| BR-01 | Source data must be reproducibly ingested | `src/data.py` | schema test | raw CSV |
| BR-02 | Critical data defects must stop scoring | `src/quality.py` | `test_quality_report_flags_duplicate_ids` | data-quality report |
| BR-03 | Amount significance must use relevant peers | `engine._hierarchical_peer_score` | feature-bound tests | `peer_amount` |
| BR-04 | Repeat patterns must be detectable | `engine.add_features` | near-duplicate test | `near_duplicate` |
| BR-05 | Relationship concentration must be visible | `network.add_network_features` | advanced bounds test | vendor share / concentration |
| BR-06 | Changes over time must be evaluated | `engine._temporal_relationship_features` | advanced bounds test | temporal-spike signal |
| BR-07 | Multivariate anomalies must support, not dominate, decisions | `engine._isolation_signal` + governed weight | score-bound test | `unsupervised` |
| BR-08 | Every score must be explainable | `explain.add_explanations` | explainability test | reason codes / contributors |
| BR-09 | Independent evidence must be distinguishable | signal-family design | evidence-diversity test | family count/confidence |
| BR-10 | Management must see threshold/workload trade-off | `optimizer.threshold_frontier` | monotonicity test | decision frontier |
| BR-11 | Threshold recommendation must respect capacity | `optimizer.recommend_threshold` | capacity test | recommended threshold |
| BR-12 | Workload uncertainty must be quantified | `optimizer.monte_carlo_backlog` | reproducibility test | backlog probability / P90 hours |
| BR-13 | Outputs must be usable without code inspection | `app.py` | manual UAT | Streamlit cockpit |
| BR-14 | Analytical assumptions must be governable | `config.py` + governance docs | change-control review | versioned config |
