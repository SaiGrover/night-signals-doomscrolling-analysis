from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from night_signals.config import NOTEBOOK_DIR, OUTPUT_DIR, PRIMARY_DATA
from night_signals.ui import footer, page_intro


@st.cache_data(max_entries=16, show_spinner=False)
def notebook_catalog() -> list[dict]:
    rows = []
    for path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        document = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "name": path.name,
                "title": path.stem.replace("_", " ").title(),
                "path": str(path),
                "cells": len(document.get("cells", [])),
                "executed_outputs": sum(len(cell.get("outputs", [])) for cell in document.get("cells", []) if cell.get("cell_type") == "code"),
            }
        )
    return rows


@st.cache_data(max_entries=16, show_spinner=False)
def read_notebook(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def stage_outputs(stem: str) -> list[Path]:
    keywords = {
        "01": ["analysis_summary.json", "01_", "sleep_doomscrolling_habits.csv"],
        "02": ["prediction_schema.json", "primary_model_odds_ratios.csv", "model_registry.json"],
        "03": ["01_", "02_", "03_", "04_", "05_", "06_", "07_", "08_", "10_", "11_", "12_"],
        "04": ["exception_effect_sizes.csv", "primary_model_odds_ratios.csv", "association"],
        "05": ["protective_habits_summary.csv", "exception_effect_sizes.csv", "06_", "07_", "10_"],
        "06": ["production_model_comparison.csv", "nested_cv_fold_results.csv", "13_model_comparison.png"],
        "07": ["production_model_summary.json", "production_feature_importance.csv", "subgroup_performance.csv", "15_production_risk_model.png"],
        "08": ["nhanes_", "16_nhanes_evidence.png"],
        "09": ["physionet_", "17_physionet_evidence.png"],
        "10": ["analysis_summary.json", "production_model_summary.json", "nhanes_summary.json", "physionet_summary.json"],
    }
    key = next((prefix for prefix in keywords if stem.startswith(prefix)), "")
    matches = []
    for folder in [OUTPUT_DIR / "tables", OUTPUT_DIR / "figures", OUTPUT_DIR / "models", OUTPUT_DIR / "analysis_summary.json"]:
        candidates = [folder] if folder.is_file() else list(folder.glob("*")) if folder.exists() else []
        for path in candidates:
            if any(token in path.name for token in keywords.get(key, [])):
                matches.append(path)
    return sorted({path for path in matches}, key=lambda path: path.name)


def render_saved_output(path: Path) -> None:
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
        st.dataframe(frame.head(50), hide_index=True, alt=f"Saved output table {path.name}")
    elif path.suffix.lower() == ".json":
        st.json(json.loads(path.read_text(encoding="utf-8")))
    elif path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        st.image(path, caption=path.name, alt=f"Saved analytical figure {path.name}")


page_intro("Notebook studio", "Every notebook is exposed as a readable, downloadable research stage with its saved tables, figures, and model outputs alongside it.", ":material/menu_book:")
catalog = notebook_catalog()
if not catalog:
    st.warning("No notebooks were found in the configured notebook directory.", title="Notebook inventory unavailable", icon=":material/warning:")
else:
    st.dataframe(pd.DataFrame(catalog)[["name", "cells", "executed_outputs"]], hide_index=True, alt="Inventory of all research notebooks and their executed output counts")
    selected_name = st.selectbox("Notebook", [row["name"] for row in catalog], key="selected_notebook")
    selected = next(row for row in catalog if row["name"] == selected_name)
    document = read_notebook(selected["path"])
    source_mode = st.segmented_control("View", ["Stage overview", "Notebook source", "Cell outputs"], default="Stage overview", key="notebook_view") or "Stage overview"
    path = Path(selected["path"])
    with st.container(horizontal=True, gap="medium"):
        st.metric("Cells", selected["cells"], border=True)
        st.metric("Saved cell outputs", selected["executed_outputs"], border=True)
        st.download_button("Download notebook", path.read_bytes(), file_name=path.name, mime="application/x-ipynb+json", width="stretch", icon=":material/download:")

    if source_mode == "Stage overview":
        st.html('<div class="ns-script">A notebook is a chain of evidence, not just a code file.</div>')
        st.write("This stage is part of the reproducible Night Signals workflow. The app keeps the source notebook and the artifacts it produced adjacent so a reviewer can move from method to result without hunting through folders.")
        outputs = stage_outputs(path.stem)
        st.subheader("Connected saved outputs", icon=":material/attachment:")
        if outputs:
            for output in outputs:
                with st.container(border=True):
                    st.markdown(f"**{output.name}**")
                    render_saved_output(output)
        else:
            st.info("This notebook is source-defined but has no matching saved artifact in the current checkout.", icon=":material/info:")
    elif source_mode == "Notebook source":
        for index, cell in enumerate(document.get("cells", []), start=1):
            if cell.get("cell_type") == "markdown":
                st.markdown("".join(cell.get("source", [])))
            else:
                st.code("".join(cell.get("source", [])), language="python", line_numbers=True)
    else:
        outputs = [output for cell in document.get("cells", []) for output in cell.get("outputs", [])]
        if not outputs:
            st.info("This notebook has no embedded execution outputs. Use the connected saved outputs in Stage overview; generated stages read the validated project artifacts at runtime.", icon=":material/info:")
        for index, output in enumerate(outputs, start=1):
            st.markdown(f"**Cell output {index}**")
            if "text" in output:
                st.code("".join(output["text"]), language="text")
            data = output.get("data", {})
            if "text/plain" in data:
                st.code("".join(data["text/plain"]), language="text")
            if "image/png" in data:
                st.image(io.BytesIO(base64.b64decode("".join(data["image/png"]))), alt=f"Notebook output image {index}")

st.info(f"Primary dataset: {PRIMARY_DATA.name} · Notebook directory: {NOTEBOOK_DIR.name} · Outputs are read from the versioned project artifact folder.", title="Reproducibility boundary", icon=":material/verified:")
footer()
