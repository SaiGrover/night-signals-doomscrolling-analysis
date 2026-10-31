# Night Signals

Night Signals is a Streamlit research atlas investigating relationships between nighttime digital behaviour, doomscrolling, sleep outcomes, resilience factors, and independent health evidence.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-streamlit.txt -r requirements-training.txt
python -m ipykernel install --user --name python3 --display-name "Python 3 (Night Signals)"
streamlit run streamlit_app.py
```

The saved joblib artifact was serialized with scikit-learn 1.5.2. Use the pinned `requirements-training.txt` for artifact tests or retraining; an existing virtual environment with a newer scikit-learn may fail to unpickle it. The portable JSON artifact supports the Streamlit inference path.

The application is Streamlit-only. The canonical source tree is `data/`, `night_signals/`, `app_pages/`, `notebooks/`, `scripts/`, and `outputs/`.

## Research workflow

1. Place the primary CSV at `data/sleep_doomscrolling_habits.csv`.
2. Run the evidence builders in `scripts/` when external raw files are available.
3. Run `python scripts/train_production_model.py` to regenerate the locked model and diagnostics.
4. Run `python scripts/export_interpretability_tables.py` to regenerate odds ratios and resilience effects.
5. Execute notebooks sequentially with Jupyter or `nbconvert`.
6. Run `pytest -q` and open the Streamlit app.

For reproducible claim checks, run `python scripts/audit_research_claims.py`. It writes the target-score crosstab, routine shares, and five FDR-adjusted association tests to `outputs/tables/`. The editable research report is `deliverables/Sleep_Doomscrolling_Report.tex`; after updating its metric snapshot from current tables, run `python scripts/build_current_report.py` to validate key metrics and compile the PDF with `pdflatex`. The unnumbered legacy analysis notebook and some legacy figures remain historical; see `RESEARCH_INTEGRITY.md` before citing them.
Run `python scripts/compare_simple_baselines.py` for a development-only simple-rule and feature-ablation comparison. Its fixed-threshold logistic scores are diagnostic and should not be compared directly with the tuned/calibrated model's nested-CV estimate.
Run `python scripts/check_holdout_calibration.py` for retrospective calibration slope and intercept from saved historical predictions.

## Scientific boundary

The primary file is a public Kaggle dataset described by its uploader as synthetic; we did not collect a survey. Its item-generation process and observation times are undocumented. Results describe this file and an internally validated label-recovery exercise, not population effects or clinical risk. NHANES and PhysioNet are separate context layers, never validation of the classifier. See `data/PROVENANCE.md`, `DATA_DICTIONARY.md`, and `RESEARCH_INTEGRITY.md`.

The poor-sleep model excludes measured sleep outcomes and uses nested development validation, calibration, threshold selection, bootstrap intervals, and subgroup diagnostics. The one-record-per-row file cannot prove a real bedtime prediction moment; earlier experiments may have accessed overlapping holdout rows. The model is an educational label-recovery exercise and must not be used for individual decisions.

## Repository map

- `streamlit_app.py` — multipage Streamlit entrypoint.
- `app_pages/` — landing page, atlas pages, external evidence, workflow, notebooks, and downloads.
- `night_signals/` — shared data, statistics, model, visualization, and UI modules.
- `data/` — canonical primary dataset and provenance notes.
- `outputs/` — versioned tables, figures, model artifacts, and summaries.
- `deliverables/*.tex` — editable research and current technical-status reports; the research PDF is compiled from TeX.
- `notebooks/` — sequential research workflow.
- `scripts/` — training, evidence, export, and validation scripts.
- `tests/` — Streamlit and model-artifact tests.

## License

See [LICENSE](LICENSE). External datasets remain subject to their original licenses and terms.
