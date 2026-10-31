# Poor-sleep pre-outcome model — v2.0.0

## Intended use

Educational demonstration of recovering a Poor label in a public dataset described by its uploader as synthetic. Sleep outcome columns are excluded. The cross-sectional file does not establish a real bedtime prediction moment or the timing of nighttime phone checks.

This model is not medical advice, is not externally validated, and must not be used for diagnosis, treatment, employment, insurance, or automated decisions about people.

## Evaluation design

- 1,000 synthetic records; 750 development and 250 holdout rows in the current protocol.
- The current script splits before fitting. Earlier experiments may have inspected overlapping rows; an "opened once" claim cannot be verified.
- Candidate families were tuned inside five-fold nested cross-validation on development data.
- Candidate comparison includes Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and RBF SVM.
- The selected Logistic Regression was sigmoid-calibrated.
- The decision threshold was selected from development-only out-of-fold predictions, with false negatives assigned twice the cost of false positives.

## Results

- Majority baseline accuracy: 67.0%.
- Nested-CV balanced accuracy: 73.7% ± 4.1 percentage points.
- Current holdout balanced accuracy: 75.96% (bootstrap 95% CI 70.42–81.55%).
- Holdout ROC AUC: 82.5% (95% CI 77.0–87.6%).
- Holdout PR AUC: 72.0%; Brier score: 0.155.
- Sensitivity: 72.29%; specificity: 79.64% at threshold 0.335.

## Known limitations

- The uploader describes the records as synthetic; population inference is not supported. The category label conflicts with the 1–5 quality score for many rows.
- No independent, temporal, prospective, geographic, or clinical validation has been performed.
- Self-reported exposures may be measured with error.
- Subgroup results are diagnostic only because the final holdout is small.
- Calibration and drift must be re-evaluated on any new population.

## Artifacts

The registry, schema, summary, subgroup audit, comparison table, and artifact SHA-256 are versioned in `outputs/tables`. Joblib is retained as the trusted reproducibility artifact and the portable JSON bundle is regression-tested against scikit-learn.
