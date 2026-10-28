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

The application is Streamlit-only. The canonical source tree is `data/`, `night_signals/`, `app_pages/`, `notebooks/`, `scripts/`, and `outputs/`.

## Research workflow

1. Place the primary CSV at `data/sleep_doomscrolling_habits.csv`.
2. Run the evidence builders in `scripts/` when external raw files are available.
3. Run `python scripts/train_production_model.py` to regenerate the locked model and diagnostics.
4. Run `python scripts/export_interpretability_tables.py` to regenerate odds ratios and resilience effects.
5. Execute notebooks sequentially with Jupyter or `nbconvert`.
6. Run `pytest -q` and open the Streamlit app.

## Scientific boundary

The primary dataset is self-reported and cross-sectional. Its acquisition and sampling provenance remain incomplete. Results are descriptive or internally validated predictive results, not causal, clinical, or externally validated claims. NHANES and PhysioNet are independent evidence layers and are never row-merged with the primary survey.

The poor-sleep model uses a fixed pre-outcome feature set, nested development validation, an untouched holdout, calibration, threshold selection, bootstrap intervals, and subgroup diagnostics. It is not a medical device and must not be used for individual decisions.

## Repository map

- `streamlit_app.py` — multipage Streamlit entrypoint.
- `app_pages/` — landing page, atlas pages, external evidence, workflow, notebooks, and downloads.
- `night_signals/` — shared data, statistics, model, visualization, and UI modules.
- `data/` — canonical primary dataset and provenance notes.
- `outputs/` — versioned tables, figures, model artifacts, and summaries.
- `notebooks/` — sequential research workflow.
- `scripts/` — training, evidence, export, and validation scripts.
- `tests/` — Streamlit and model-artifact tests.

## License

See [LICENSE](LICENSE). External datasets remain subject to their original licenses and terms.
