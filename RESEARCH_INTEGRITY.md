# Research integrity and interpretation

The primary Kaggle uploader describes the 1,000 records as synthetic. This project did not collect a survey. The categories, correlations and model metrics characterize this file; they are not estimates for a real population. Source and checksum: `data/PROVENANCE.md`.

## Explicit research questions and analysis rules

The following are exploratory checks, specified here after the dataset and prior outputs were inspected. They are **not preregistered hypotheses**. Recompute with `python scripts/audit_research_claims.py`.

1. Are bedtime routine categories associated with Good/Fair/Poor labels? Pearson chi-square and Cramer's V.
2. Are night mode, phone location, negative-news exposure, and the doomscroller label associated with the category? The same tests.
3. Apply Benjamini–Hochberg FDR to these five tests as one family. Report effect size and group sizes regardless of significance.
4. Inspect the category × numeric quality-score crosstab as a construct-validity check.

The routine comparison is unadjusted and confounded by exposure. Reading has a lower Good share than the file-wide base rate; the "no fixed routine" group has the highest Good share. Neither reading nor meditation can be called protective from this table. Negative-news exposure must be reported even if its association is null. The high-exposure favorable-sleep subgroup is small; differences in sleep duration, latency, debt and fatigue follow from its outcome definition and do not identify protective factors. Exercise and routine contrasts are exploratory.

The current model excludes sleep outcome columns and uses nested development validation. It does not establish predictor availability at bedtime. `phone_checks_per_night` may occur after sleep onset. Earlier model versions reported holdout scores and overlap with the current split cannot be ruled out. Treat the 250-row score as an internal benchmark, not a prospectively untouched test. External model validation has not been performed.

`python scripts/compare_simple_baselines.py` writes `development_baselines_ablations.csv` using only the 750 development records. At a fixed 0.5 threshold, the doomscroller-label rule attains balanced accuracy 0.713, while an untuned full logistic model attains 0.694. The fixed-threshold figures are not equivalent to the tuned, calibrated nested-CV production score. The simple-rule strength materially limits claims of added complexity or prospective signal.

The raw quality score contradicts the Poor category for 213 of 330 Poor records (score 5/5). The target's construction is undocumented. A model trained on this label learns its encoding, not an established sleep disorder. The current holdout balanced accuracy is 0.75965 (95% bootstrap interval 0.70416–0.81551) at threshold 0.335. This supersedes the stale 77.5% text in earlier reports.

NHANES has no matching doomscrolling exposure and PhysioNet participants are unrelated to the Kaggle records. Their findings are background context only. The NHANES WLS model with stratum fixed effects and clustered PSU covariance is an approximation to complex-survey inference; it is not a full design-based analysis. PAD800/PAD820 record minutes per occasion, not minutes per day. The direction of the activity association should be reported without a protective interpretation.

Legacy figures and the PDF document earlier experiments, including a three-class model with sleep outcomes. They must not be cited as evidence for the current binary model. Use `outputs/tables/production_model_summary.json` as the metric source until the report is regenerated from the current pipeline.
