# Target and prediction-time definition

The primary classification target is the dataset's existing `sleep_quality_category` field, encoded as:

- `Poor` = 1 (positive class)
- `Good` or `Fair` = 0

The prediction moment is bedtime, after behavioral/context variables are available and before the sleep outcome occurs. The model excludes respondent ID, sleep quality, duration, latency, awakenings, sleep debt, daytime fatigue, and the categorical target itself.

This definition is fixed before model comparison. The decision threshold is selected only from development-set out-of-fold probabilities using a documented false-negative cost of 2 and false-positive cost of 1. The untouched holdout is opened only for final evaluation.
