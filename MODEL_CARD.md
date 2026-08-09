# Poor-sleep pre-outcome model — v2.0.0

## Intended use

Educational demonstration of a pre-outcome risk model evaluated on a synthetic survey. The prediction moment is bedtime, after exposure/context variables are known and before sleep duration, latency, wakeups, fatigue, sleep debt, or sleep-quality outcomes occur.

This model is not medical advice, is not externally validated, and must not be used for diagnosis, treatment, employment, insurance, or automated decisions about people.

## Evaluation design

- 1,000 synthetic rows; 750 development and 250 final holdout rows.
- The holdout was created before model comparison and opened once.
- Candidate families were tuned inside five-fold nested cross-validation on development data.
- The selected Logistic Regression was sigmoid-calibrated.
- The decision threshold was selected from development-only out-of-fold predictions, with false negatives assigned twice the cost of false positives.

## Results

- Majority baseline accuracy: 67.0%.
- Nested-CV balanced accuracy: 73.7% ± 4.1 percentage points.
- Untouched-holdout balanced accuracy: 77.5% (bootstrap 95% CI 71.8–82.8%).
- Holdout ROC AUC: 82.5% (95% CI 77.0–87.6%).
- Holdout PR AUC: 72.0%; Brier score: 0.155.
- Sensitivity: 75.9%; specificity: 79.0% at threshold 0.32.

## Known limitations

- Synthetic data may encode generator rules and is not representative of a population.
- No independent, temporal, prospective, geographic, or clinical validation has been performed.
- Self-reported exposures may be measured with error.
- Subgroup results are diagnostic only because the final holdout is small.
- Calibration and drift must be re-evaluated on any new population.

## Artifacts

The registry, schema, summary, subgroup audit, comparison table, and artifact SHA-256 are versioned in `public/data` and `outputs/tables`. Joblib files must only be loaded from trusted builds.
