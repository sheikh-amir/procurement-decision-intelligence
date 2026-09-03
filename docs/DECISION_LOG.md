# Decision Log

| ID | Decision | Rationale | Trade-off / limitation |
|---|---|---|---|
| D-01 | Treat output as prioritization, not fraud classification | no validated outcome labels or investigative evidence | cannot claim precision/recall |
| D-02 | Use hierarchical peers rather than a global amount rule | context varies by agency and merchant category | smaller groups require fallback |
| D-03 | Use robust statistics | reduce influence of extreme amounts | less intuitive than simple z-score |
| D-04 | Keep weekend/round-dollar features low-weight | weak signals can still add context | may add noise |
| D-05 | Include vendor relationship features | transaction-only analysis misses structural dependency | concentration can be legitimate |
| D-06 | Add temporal vendor-spend spikes | change over time can matter more than absolute level | history may be short/seasonal |
| D-07 | Keep Isolation Forest as one component | surfaces combinations not captured by rules | unsupervised output is not ground truth |
| D-08 | Separate evidence diversity from priority score | correlated rules can create false confidence | family design requires governance judgment |
| D-09 | Use priority-score coverage for scenario optimization | no ground truth exists | must not be called recall/accuracy |
| D-10 | Recommend lowest feasible threshold | preserves broader modeled coverage under capacity constraint | management may prefer a different operating point |
| D-11 | Simulate review-time uncertainty with a long-tailed distribution | case complexity is not constant | distribution is assumed until real cycle-time data exists |
| D-12 | Fail the pipeline on critical quality defects | avoid producing confident outputs from broken data | may temporarily interrupt reporting |
| D-13 | Version analytical configuration | score changes must be traceable | formal registry is not implemented in prototype |
