# External validation contract

External validation is intentionally marked incomplete until a genuinely independent dataset is supplied.

An acceptable validation dataset must:

1. Come from a different collection process or time period than the self-reported survey development data.
2. Contain the documented pre-outcome input fields and a clearly defined Poor-sleep outcome.
3. Be frozen before model scoring; no retuning or threshold changes may use it.
4. Report missingness, cohort selection, outcome prevalence, and subgroup sample sizes.
5. Evaluate calibration intercept/slope, Brier score, ROC AUC, PR AUC, sensitivity, specificity, and bootstrap confidence intervals.
6. Report subgroup performance and explicitly document any unusable small cells.
7. Preserve the original model and threshold for the primary validation analysis.

Passing internal validation does not satisfy this contract.

## Independent evidence layers vs. model external validation

The project analyses two independent public datasets — **NHANES 2021-2023** (population
health) and **PhysioNet Sleep-Accel** (objective wearable physiology) — as separate
evidence layers (see the Evidence Synthesis page and `build_nhanes.py` /
`build_physionet.py`). These strengthen the surrounding scientific context, but they do
**not** by themselves satisfy the contract above: they use different populations,
variables, and outcome definitions, so they cannot serve as a frozen, matched external
test set for the poor-sleep classifier. Model external validation therefore remains
intentionally incomplete until a matched dataset (per the criteria above) is supplied.
