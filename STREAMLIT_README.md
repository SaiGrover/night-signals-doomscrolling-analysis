# Night Signals Streamlit migration

The Streamlit application lives in `streamlit_app.py` and uses `app_pages/` for the research atlas. It is designed as a read-only presentation layer over the validated notebooks, model artifacts, and external-evidence summaries already produced by the project.

## Run locally

```powershell
cd "C:\Users\Saanvi\Downloads\Projects\Doom Scrolling\platform"
.\.venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
```

The app expects the existing project artifacts in `data/`, `outputs/`, and `notebooks/`. The path resolver also falls back to the parent project checkout when the migration is run from a packaged layout.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

The tests use Streamlit's in-process `AppTest` API to cover entrypoint rendering, all registered pages, and the model-risk form without starting a browser or server.

## Research boundary

The primary Kaggle file is described by its uploader as synthetic; its item timing and label rule are undocumented. NHANES and PhysioNet are separate context layers, not classifier validation. Model results are internal label-recovery diagnostics and are not clinical advice.
