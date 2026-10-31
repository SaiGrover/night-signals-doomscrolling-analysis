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

The same script writes `development_paired_comparison.json`: on identical development rows, the full untuned logistic model minus the rule has balanced-accuracy difference −0.019 (stratified paired bootstrap 95% CI −0.052 to +0.014). The full model's ROC AUC is 0.062 higher (95% CI +0.035 to +0.091), but the rule is binary and that ranking metric does not establish clinical or classification utility. This comparison does not substitute for independent validation.

`python scripts/check_holdout_calibration.py` fits a logistic recalibration model on the saved historical holdout probabilities. Slope 1.218 (95% CI 0.889-1.546) and intercept 0.149 (95% CI -0.231-0.529) are retrospective diagnostics only; they cannot replace external calibration.

The raw quality score contradicts the Poor category for 213 of 330 Poor records (score 5/5). The target's construction is undocumented. A model trained on this label learns its encoding, not an established sleep disorder. The current holdout balanced accuracy is 0.75965 (95% bootstrap interval 0.70416–0.81551) at threshold 0.335. This supersedes the stale 77.5% text in earlier reports.

`python scripts/analyze_label_and_habits.py` records an arbitrary score<5 sensitivity label in `target_sensitivity.json`. Among 960 complete rows it agrees with the original Poor label in 75.5% (Cohen's kappa 0.355). This sensitivity check shows label dependence; it does not validate either construct. Its adjusted routine analysis (`adjusted_habit_associations.csv`, 953 complete rows) uses logistic regression with age, gender, occupation, bedtime exposure, doomscroller label, negative-news exposure, night mode, and phone location. No routine coefficient survives seven-term FDR adjustment. Confounding and the small high-exposure favorable subgroup remain.

NHANES has no matching doomscrolling exposure and PhysioNet participants are unrelated to the Kaggle records. Their findings are background context only. NHANES MEC-outcome regression now uses MEC weights alone and stratum-centered masked-PSU Taylor variance with 15 design degrees of freedom. The adult complete-case domain is still an approximation; its unweighted descriptive Welch tests must not be interpreted as design-based inference. The adjusted systolic contrast is 0.82 mmHg (95% CI −0.86 to 2.50; p=0.316), and the adjusted diastolic contrast is 1.93 mmHg (95% CI 0.67 to 3.19; p=0.005). PAD800/PAD820 record minutes per occasion, not minutes per day. The activity association is descriptive, without a protective interpretation. CDC design guidance: https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx and https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm.

The report is authored in `deliverables/Sleep_Doomscrolling_Report.tex`; `scripts/build_current_report.py` checks key values against current tables and compiles its PDF. The unnumbered legacy analysis notebook and older figures document earlier experiments, including a three-class model with sleep outcomes; they must not be cited as evidence for the current binary model. Use `outputs/tables/production_model_summary.json` as the metric source.
