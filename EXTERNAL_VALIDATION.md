# External validation contract

External validation is intentionally marked incomplete until a genuinely independent dataset is supplied.

An acceptable validation dataset must:

1. Come from a different collection process or time period than the synthetic development data.
2. Contain the documented pre-outcome input fields and a clearly defined Poor-sleep outcome.
3. Be frozen before model scoring; no retuning or threshold changes may use it.
4. Report missingness, cohort selection, outcome prevalence, and subgroup sample sizes.
5. Evaluate calibration intercept/slope, Brier score, ROC AUC, PR AUC, sensitivity, specificity, and bootstrap confidence intervals.
6. Report subgroup performance and explicitly document any unusable small cells.
7. Preserve the original model and threshold for the primary validation analysis.

Passing internal validation does not satisfy this contract.
