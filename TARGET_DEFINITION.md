# Target and prediction-time definition

The primary classification target is the dataset's existing `sleep_quality_category` field, encoded as:

- `Poor` = 1 (positive class)
- `Good` or `Fair` = 0

The model excludes respondent ID, sleep quality, duration, latency, awakenings, sleep debt, daytime fatigue, and the categorical target itself. The file is cross-sectional and contains no observation timestamps or original item wording, so actual availability at bedtime cannot be established. Nighttime phone checks may occur after sleep onset.

The current script fixes this target before model comparison. Its decision threshold is selected from development-set out-of-fold probabilities using a false-negative cost of 2 and false-positive cost of 1. Earlier experiments may have accessed overlapping rows in the 250-row historical holdout; prospective independence cannot be claimed.
