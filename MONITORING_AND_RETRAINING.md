# Monitoring and retraining

Night Signals is an internal research demonstration, not a production clinical system. The published classifier is versioned through `MODEL_VERSION`, its portable-model schema, the training seed, and the SHA-256 hash recorded in `outputs/tables/production_model_summary.json`.

## Monitoring checklist

For each new survey batch, preserve the raw snapshot and run the same provenance, schema, missingness, range, duplicate, category, and class-distribution audits. Compare numeric feature distributions with the stored `drift_baseline` using PSI or an equivalent documented shift statistic. Review subgroup counts before interpreting subgroup metrics.

If outcomes become available, recompute ROC-AUC, PR-AUC, sensitivity, specificity, balanced accuracy, Brier score, calibration curves, and bootstrap confidence intervals. Flag material calibration drift separately from ranking drift; do not silently change the decision threshold.

## Retraining procedure

1. Freeze the incoming dataset snapshot and record its source, date, schema, and hash.
2. Re-run the ten notebooks in order and the production training script with the recorded random seed.
3. Keep an untouched holdout or time-separated evaluation sample. Never use it for tuning or threshold selection.
4. Compare the candidate model against the current version on the same locked evaluation protocol, including calibration and subgroup checks.
5. Publish a new model version only when the comparison, leakage audit, and limitations review are documented. Update the model card and portable artifact together.

There is no automatic deployment, automatic threshold adjustment, or individual-level intervention. Any future independent validation must remain separate from the primary survey and must not be row-merged with it.
