# Night Signals — End-to-End Technical Audit

> Historical audit snapshot from 2026-10-28. Several findings and metrics below were superseded by later fixes. The current technical status is maintained in `deliverables/Night_Signals_Technical_Status.tex`; do not cite this file as the current project verdict.

**Audit scope:** C:\Users\Saanvi\Downloads\Projects\Doom Scrolling\platform  
**Specification:** C:\Users\Saanvi\Desktop\SEM 5 PBLs\FDS PBL SYNOPSIS.pdf  
**Audit date:** 2026-10-28  
**Audit mode:** Read-only review of application/research code and artifacts, independent metric recomputation, headless Streamlit tests, frontend tests/build, and notebook execution attempt.

## 1. Executive verdict

### Verdict: substantial working prototype, not yet a fully defensible final research submission

Night Signals is more than a mock dashboard. The primary survey is present, the production binary model is persisted, the saved holdout metrics are reproducible from the saved joblib artifact, the Streamlit pages render headlessly, the React build and unit tests pass, and NHANES/PhysioNet artifacts exist.

It is not yet ready to be described as a complete, technically coherent, reproducible research project without corrections. The highest-impact findings are:

1. The research artifacts and the Streamlit application disagree on the high-exposure/resilience cohort. The dynamic app reports 250 high-exposure respondents and 23 favorable exceptions, while the saved exception artifact and analysis summary report 204 and 11.
2. The model registry/API says “synthetic survey” while the synopsis explicitly requires the dataset to be treated as self-reported and not called synthetic without source confirmation.
3. Ten synopsis workflow notebooks are generated, unexecuted two-cell wrappers with no outputs.
4. The joblib artifact was created with a different scikit-learn version than the pinned training requirement.
5. RQ5 is only partially implemented: NHANES is analyzed, but the newer multi-night PhysioNet layer described by the synopsis is absent.
6. Gradient and resilience statistics are incomplete for the stated methodology.

The application is suitable for continued development and a supervised college demonstration after the P0/P1 issues are fixed. It is not presently suitable for an unqualified claim of scientific completeness, independent validation, or portfolio-grade reproducibility.

### Evidence status

- **Verified working:** executed in this audit and independently checked.
- **Code-reviewed only:** implementation exists but was not fully validated.
- **Failed:** an execution or consistency check failed.
- **Not tested:** no reliable evidence was available.

## 2. Audit commands and results

| Check | Result | Status |
|---|---|---|
| Python Streamlit tests | 3 passed | Verified working |
| Model artifact test | Passed, with sklearn version warnings | Verified with warning |
| npm test | Typecheck, 3 Vitest tests, model test, chart test, and Vite build passed | Verified with warnings |
| Streamlit AppTest pages | No page exceptions | Verified render-level only |
| localhost:8501/healthz | HTTP 200 | Verified working |
| Independent holdout recomputation | Exact metric and probability agreement | Verified working |
| In-memory execution of all notebooks | Blocked by NoSuchKernel: no python3 kernel | Failed/blocked |

The frontend build also warned that Node 20.18.0 is below the declared/Vite-supported requirement. The model test emitted repeated InconsistentVersionWarning messages because the artifact was created with sklearn 1.9.1 while the active/pinned environment reports 1.5.2.

## 3. Synopsis compliance matrix

| Synopsis requirement | Status | Evidence and finding |
|---|---|---|
| Primary Kaggle survey identified and treated as self-reported/cross-sectional | Partially implemented | Narrative is cautious, but acquisition metadata, source snapshot, license capture, and checksum are absent. |
| Preserve original data and create separate cleaned copy | Missing/incorrectly represented | Only one logical survey file is used; load_survey derives features in memory and does not establish raw/clean lineage. |
| Audit rows, columns, types, missingness, duplicates, ranges, categories, outliers, class balance, correlations | Partially implemented | Rows, columns, missingness, duplicates, ranges, and class counts exist. Outlier investigation is only a range check; category validation and missingness sensitivity are incomplete. |
| Multi-outcome EDA | Implemented with limitations | Substantive notebook and pages exist. Gradient UI exposes only three outcomes while associations cover six; old and new workflows are not one canonical pipeline. |
| RQ1 association analysis | Implemented descriptively | Spearman associations and BH-FDR correction exist. No causal or temporal inference is made. |
| RQ2 exposure gradient | Partially implemented | Quartile means and 95% intervals exist, but there is no formal ordered-trend test, omnibus/post-hoc testing, or consistent gradient effect size. |
| RQ3 resilience/exception analysis | Partially implemented and inconsistent | Saved artifacts use bedtime screen >=66 plus doomscroller=Yes; current app uses top-quartile doomscroll load without the label. |
| Required resilience factors | Partially implemented | Exercise, detox timing, anxiety, stress, protective count, and phone checks are tested. Reading, meditation/journaling, phone placement, night mode, bedtime routine, and negative-news exposure are not independently tested. |
| Fixed binary target | Implemented | TARGET_DEFINITION.md and training script define Poor=1 and Good/Fair=0. |
| Prediction-time leakage audit | Partially implemented | Outcome exclusions exist, but stress/anxiety timing is not evidenced as pre-outcome. |
| Required model families | Implemented in production script | Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and RBF SVM are compared. |
| Nested CV and untouched holdout | Mostly implemented | Candidate comparison is nested on development data. Threshold OOF probabilities use a final estimator whose hyperparameters were selected using all development rows, so threshold OOF is not fully nested. |
| Accuracy, precision, recall, F1, ROC-AUC, PR-AUC, Brier, calibration | Partially implemented | Core point metrics and a calibration curve exist. Production confusion matrix, calibration intercept/slope, and reliability uncertainty are absent. |
| Bootstrap uncertainty | Partially implemented | Intervals exist for selected metrics; no calibration/threshold uncertainty plots. |
| Model interpretation | Partially implemented | Permutation importance exists; logistic odds-ratio artifact exists but is not integrated into the Streamlit model page. |
| Subgroup performance | Partially implemented | Gender, age group, occupation, and country are included. Exposure and stress subgroups required by the synopsis are absent. |
| NHANES independent evidence | Implemented with limitations | Separate XPT pipeline exists; complex survey weights/PSU/strata variance are not used. |
| PhysioNet evidence | Partially implemented | Sleep-Accel HR/stage summaries exist; the newer multi-night 47-adult/253-night layer and acceleration analysis are absent. |
| No row-level merging | Implemented | Code and narrative keep datasets independent. |
| Research Atlas | Implemented as two divergent surfaces | React/Vercel and Streamlit have different page maps and artifact paths; authoritative surface is unclear. |
| Basic MLOps | Partially implemented | Version/hash/monitoring documentation exist, but no persistent monitoring store, training date, environment lock, or correct registry provenance. |
| Reproducible notebooks | Missing for new ten-notebook workflow | Ten notebooks have unexecuted cells and zero outputs; older substantive notebooks are separate. |
| Final deliverables | Partially implemented | PDF, source, outputs, notebooks, and applications exist, but canonical-run traceability is incomplete. |

## 4. Data science and statistical findings

### Verified primary data checks

Independent checks verified:

- 1,000 rows and 30 columns, with 29 analytic variables excluding respondent_id.
- 0 duplicate full rows and 0 duplicated respondent IDs.
- 220 missing cells: caffeine 50, exercise 50, sleep-quality score 40, occupation 30, device 30, bedtime routine 20.
- Sleep-quality classes: Good 340, Fair 330, Poor 330.
- No observed values outside the project’s semantic range checks.

These checks do not prove provenance, representativeness, real-world collection, or absence of generator assistance.

### P1 — data lineage is incomplete

**Affected:** data/sleep_doomscrolling_habits.csv, public/data/sleep_doomscrolling_habits.csv, night_signals/data.py, app_pages/data_audit.py.

The application calls the loaded frame “raw” after adding derived columns in memory. There is no primary acquisition script, source card capture, license record, checksum manifest, cleaned analytical file, or transformation log. The two CSV copies are value-equal but have different byte hashes with no documented reason.

**Fix:** establish raw/processed directories, source metadata, SHA-256 checksums, and a deterministic cleaning/feature script.

**Acceptance:** a clean checkout can reproduce the processed file byte-for-byte and report each transformation and row count.

### P1 — resilience cohort correctness bug

Independent recomputation found:

| Definition | High exposure | Favorable | Poor |
|---|---:|---:|---:|
| Saved artifact: bedtime screen >=66 and doomscroller=Yes | 204 | 11 | 147 |
| Current load_survey dynamic cohort: doomscroll-load top quartile | 250 | 23 | 160/161 |

The dashboard can therefore show counts from one cohort and effect tables from another. This is a direct correctness failure.

**Fix:** define one shared cohort function, regenerate all dependent artifacts, and add a test for cohort counts.

### P1 — gradient inference is incomplete

exposure_gradient reports means and t-based confidence intervals by quartile, but no ordered trend statistic, omnibus/post-hoc procedure, or consistent gradient effect size. A visually monotonic line is not evidence of a gradient by itself.

**Fix:** pre-specify a trend test or regression contrast, report denominators, and correct the family of gradient tests.

### P1 — resilience inference is underpowered/incomplete

The favorable high-exposure group has only 11 rows in the saved artifact. resilience_effects tests only six derived factors and lacks bootstrap intervals for factor differences. Several factors named in the synopsis are absent.

**Fix:** include every required factor, show missingness and denominators, report uncertainty, and label all results exploratory.

### P1 — NHANES is not survey-design corrected

build_nhanes_evidence.py computes unweighted means and Welch tests after merging files. NHANES is a complex survey; unweighted results are not automatically population-representative and standard errors should use weights/strata/PSU or be explicitly labeled as unweighted sample summaries.

### P2 — external variable semantics need codebook verification

The NHANES script treats PAD800 and PAD820 as minute quantities and sums them. Confirm the exact codebook units and semantics before publication.

### P2 — PhysioNet uncertainty is limited

The PhysioNet script averages subject-level stage means and reports mean within-subject standard deviations as variability. This is not a between-subject standard error or confidence interval. The label/HR alignment and denominator semantics should be documented.

## 5. Machine-learning audit

### 5.1 Independently verified metrics

Using the deterministic split and saved joblib artifact:

- Holdout size: 250.
- Stored holdout truth order matched exactly.
- Maximum probability difference versus saved holdout probabilities: 1.11e-16.
- Accuracy: 0.780.
- Balanced accuracy: 0.7747.
- ROC-AUC: 0.8247.
- PR-AUC: 0.7200.
- F1: 0.6961.
- Precision: 0.6429.
- Sensitivity: 0.7590.
- Specificity: 0.7904.
- Brier score: 0.1551.
- False negatives/positives: 20/35.

The saved model metrics are genuine and traceable to the persisted artifact.

### 5.2 Target and leakage

The production model excludes the target, sleep-quality score, sleep duration, latency, awakenings, daytime fatigue, sleep debt, and respondent ID. Preprocessing is inside a scikit-learn pipeline.

The remaining concern is timing evidence: stress and anxiety are included, but the synopsis requires confirmation that they were available before the sleep outcome. That confirmation is not present.

### P1 — threshold OOF is not fully nested

**Affected:** scripts/train_production_model.py around final_search, calibrated_template, cross_val_predict, and threshold selection.

Candidate comparison is nested, but final hyperparameters are selected on all development rows before threshold OOF probabilities are generated. The final holdout remains untouched, so final metrics are not holdout-contaminated, but threshold selection can be optimistic.

**Fix:** tune and calibrate inside each outer training fold, generate fully nested OOF probabilities, select the threshold only from those probabilities, then fit the final model on all development data.

**Acceptance:** an independent implementation confirms that each OOF probability was generated without using that row for estimator hyperparameter selection.

### P1 — model diagnostics are incomplete

- Confusion matrix is calculated transiently but not persisted/displayed for the production model.
- Calibration intercept/slope and expected calibration error are absent.
- Bootstrap intervals are not visualized.
- Subgroup exclusions and omitted small cells are not prominently reported.
- Exposure/stress subgroups required by the synopsis are absent.
- Logistic odds-ratio artifacts are not integrated into the current modeling page.
- Holdout permutation importance is post-hoc and must never feed model selection.

### Rule-baseline audit

Simple holdout rules were weaker than the calibrated model but non-trivial:

| Rule | Balanced accuracy | ROC-AUC |
|---|---:|---:|
| doomscroller=Yes | 0.687 | 0.687 |
| bedtime screen >=60 | 0.688 | 0.688 |
| doomscroll load >=66 | 0.690 | 0.690 |
| stress >=6 | 0.571 | 0.571 |
| anxiety >=5 | 0.609 | 0.609 |
| Production model | 0.775 | 0.825 |

This supports incremental model value, but formal rule baselines should be included in the canonical modeling workflow.

### P0 — serialized artifact version mismatch

**Affected:** requirements-training.txt, outputs/models/poor_sleep_preoutcome_model.joblib, scripts/test_model_artifact.py.

The pinned requirement says scikit-learn 1.5.2, while artifact loading warns that the estimators were serialized with 1.9.1. A passing test does not remove the version-sensitive persistence risk.

**Fix:** rebuild under the pinned version or pin the actual training/runtime version and record environment hashes.

**Acceptance:** clean installation loads the artifact with zero InconsistentVersionWarning and reproduces holdout probabilities.

## 6. Jupyter notebook findings

### Inventory

- Ten generated workflow notebooks: one code cell each, execution count None, zero outputs.
- sleep_doomscrolling_analysis.ipynb: 16 executed code cells, 26 outputs.
- sleep_doomscrolling_predictive_modeling.ipynb: 6 executed code cells, 7 outputs.
- external_evidence.ipynb: 2 executed code cells, 4 outputs.

The ten notebooks are created by scripts/build_research_notebooks.py, which explicitly writes unexecuted cells and empty outputs. They are not complete executed research notebooks.

### Execution blocker

An in-memory nbclient execution attempt was made for all 13 notebooks. Every attempt failed before running cells with:

NoSuchKernel: No such kernel named python3

The active .venv has nbclient and nbformat but not ipykernel, and no Jupyter executable/kernel was available.

### Additional notebook issue

The two older substantive notebooks use a separate historical workflow from scripts/train_production_model.py. The repository does not identify one canonical notebook/model pipeline, so a reviewer cannot be certain which workflow produced the final artifacts without manual reconstruction.

**P1 fix:** add/register a pinned ipykernel, choose one canonical sequence, execute it in CI from a clean environment, and fail CI on notebook errors.

## 7. Streamlit application audit

### Verified strengths

- st.navigation/st.Page architecture is used.
- All registered pages render in Streamlit AppTest without exceptions.
- Survey/artifact/model reads use st.cache_data or st.cache_resource.
- The risk demo uses st.form.
- Plotly charts use alt text and responsive configuration in the updated modeling page.
- The model page uses the portable JSON artifact, with a regression check against joblib.
- External pages state that datasets are independent and not row-merged.

### P1 — two divergent frontends

The README and Vercel deployment describe the React/Vite atlas, while the local project also contains a separate Streamlit migration with a different page map and implementation. Deployment builds React, not Streamlit. Declare the authoritative surface or create parity checks.

### P1 — mixed live/saved resilience data

app_pages/resilience.py computes dynamic counts but reads a saved effect table produced under a different cohort definition. Fix with the shared cohort function described above.

### P2 — brittle global CSS

night_signals/ui.py uses broad Streamlit internal selectors. Earlier changes demonstrated that global font rules can replace Material Symbols ligatures with literal icon names. Scope CSS to the sidebar/content regions and rely on config.toml for base theme values where possible.

### P2 — inconsistent Plotly theming

Some NHANES and PhysioNet pages use raw Plotly Express figures without the shared finish() layout/theme. Standardize margins, fonts, colors, hover templates, and responsive settings.

### P2 — shallow behavior tests

Current tests check render success and one model-form output. They do not assert filter effects, query-param behavior, chart data, downloads, notebook output rendering, or error states.

## 8. Software engineering and reproducibility

### Strengths

- Reasonable separation of pages, shared modules, scripts, outputs, and model artifacts.
- Model version, artifact hash, prediction schema, and model card exist.
- Python and frontend tests exist.
- No obvious hard-coded secrets were found; env files are ignored.
- Vercel headers provide useful security defaults.

### P0/P1 findings

1. **Environment mismatch:** model artifact versus sklearn pin.
2. **Node runtime mismatch:** package.json declares Node >=22.13.0; audit ran Node 20.18.0 and Vite warned.
3. **External data is ignored without a manifest:** exact NHANES/PhysioNet inputs are not recoverable from a clean checkout without network access.
4. **Primary acquisition is not reproducible:** no Kaggle download/version/license/checksum script.
5. **Generated artifacts can drift:** outputs, public data, plot specs, notebooks, and PDF are materialized separately without one run manifest.
6. **API limiter is process-local:** api/predict.js uses an in-memory Map with no durable shared enforcement.
7. **API scientific copy is incorrect:** validation_status says internal synthetic-data validation only.

## 9. Research integrity

### Confirmed contradiction

public/data/model_registry.json contains:

“trained_on”: “synthetic survey; n=750 development”

The synopsis says the project must not call the primary dataset synthetic unless source documentation confirms it. This wording must be removed or sourced.

### Defensible claims

- The primary dataset is self-reported and cross-sectional.
- The primary model has internal deterministic holdout evaluation.
- NHANES and PhysioNet are independent evidence layers, not external classifier validation.
- Saved model metrics reproduce from the artifact.
- No clinical or diagnostic use is justified.

### Claims requiring qualification

- “Complete reproducible workflow” is unsupported while ten notebooks are unexecuted and the kernel is missing.
- “External evidence” is contextual evidence; RQ5 is incomplete relative to the multi-night PhysioNet requirement.
- “High-exposure exceptions” are not reliable until cohort definitions are unified.
- “Validation” must be called internal holdout validation.
- “Synthetic survey” must be removed unless the Kaggle source confirms it.

## 10. Project scorecard

| Dimension | Score / 10 | Rationale |
|---|---:|---|
| Methodology | 6.0 | Clear scope and evidence separation, but incomplete RQ3/RQ5 and inconsistent cohorts. |
| ML rigor | 6.5 | Strong saved artifact and honest holdout recomputation; version mismatch and threshold nesting concern. |
| Statistical validity | 5.5 | FDR/basic effect sizes are useful; gradient, resilience, survey-design, and uncertainty gaps remain. |
| Synopsis completeness | 5.5 | Many components exist, but notebooks, multi-night PhysioNet, required factors, and traceability are incomplete. |
| Reproducibility | 4.5 | Tests pass, but kernel/version/acquisition/manifest issues are material. |
| Streamlit/UI functionality | 7.0 | Pages render and model form works; interactive behavior coverage is shallow. |
| Code quality | 6.5 | Reasonable modularity, but duplicated frontends/artifacts and brittle CSS/registry inconsistencies. |
| Portfolio readiness | 5.5 | Strong prototype potential, but technical reviewers will find the contradictions. |
| **Overall readiness** | **5.8** | Strong research prototype; not yet a defensible finished artifact. |

## 11. Prioritized corrective action plan

### P0 — critical

#### P0.1 Correct provenance/registry/API wording

- Affected: scripts/train_production_model.py, public/data/model_registry.json, api/predict.js.
- Fix: replace synthetic wording with “self-reported survey; provenance and sampling incompletely documented” unless source evidence proves otherwise.
- Acceptance: no primary-data registry/API string describes the survey as synthetic.

#### P0.2 Reconcile the resilience cohort

- Affected: night_signals/data.py, night_signals/statistics.py, scripts/export_interpretability_tables.py, exception artifacts, analysis summary, app_pages/resilience.py.
- Fix: one shared cohort function, regenerate all artifacts, add exact-count regression tests.
- Acceptance: app, CSV, report, and JSON counts match exactly.

#### P0.3 Rebuild/pin the model environment

- Affected: requirements-training.txt, joblib artifact, model tests.
- Fix: rebuild under the pinned version or pin the actual training version and record the environment.
- Acceptance: zero version warnings and exact probability reproduction.

### P1 — high

- Select and document one authoritative frontend, or add React/Streamlit parity checks.
- Execute the ten-notebook workflow from a clean environment with ipykernel.
- Correct fully nested threshold selection.
- Complete RQ3 factor coverage and RQ5 multi-night PhysioNet scope.
- Add confusion matrix, odds ratios, calibration intercept/slope, uncertainty visuals, subgroup exclusions, and rule baselines.
- Add source manifests/checksums for Kaggle, NHANES, and PhysioNet.

### P2 — medium

- Add AppTest assertions for filters, charts, downloads, and query parameters.
- Standardize all Plotly figures through one theme function.
- Add missing-data/outlier sensitivity analyses.
- Add API body limits and durable rate limiting if deployed.
- Align Node version with the package and Vite requirements.

### P3 — polish

- Reduce dependence on Streamlit internal CSS selectors.
- Show artifact version/timestamp/source badges.
- Improve chart descriptions with denominators and interval semantics.
- Add “what this does not prove” beside each headline result.
- Perform browser-based responsive QA on every route.

## 12. Final acceptance checklist

- [ ] No unsupported synthetic-survey wording remains.
- [ ] One resilience cohort definition is used everywhere.
- [ ] Model artifact and requirements use the same sklearn version.
- [ ] All required notebooks execute sequentially from a clean environment.
- [ ] Acquisition/external manifests include source hashes.
- [ ] RQ3 includes every required protective/context factor.
- [ ] RQ5 includes the multi-night layer or the synopsis/report is explicitly narrowed.
- [ ] Gradient and resilience analyses report formal uncertainty and denominators.
- [ ] Confusion matrix, calibration diagnostics, odds ratios, and subgroup exclusions are visible.
- [ ] React and Streamlit responsibilities are documented and parity-tested.
- [ ] Node/Python runtime versions are reproducible.
- [ ] Fresh-install smoke test passes without validity-affecting warnings.

**Bottom line:** Night Signals has a credible foundation and genuinely verified components, especially the persisted primary model and basic application test surface. It should be presented as a strong research prototype until the provenance wording, resilience inconsistency, notebook execution, environment pinning, and RQ5/statistical completeness gaps are resolved.

