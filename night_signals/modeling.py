from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from .config import PORTABLE_MODEL


@st.cache_resource(show_spinner=False)
def load_portable_model(path: str | Path = PORTABLE_MODEL) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1 / (1 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1 + exp_value)


def predict_probability(payload: dict, model: dict | None = None) -> tuple[float, list[str]]:
    """Run the portable calibrated logistic ensemble without version-sensitive pickle loading."""
    model = model or load_portable_model()
    warnings: list[str] = []
    calibrated = []
    for name, baseline in model["drift_baseline"]["numeric"].items():
        value = float(payload.get(name, model["defaults"][name]))
        if baseline["sd"] and abs(value - baseline["mean"]) > 3 * baseline["sd"]:
            warnings.append(f"{name.replace('_', ' ')} is outside the 3-SD training envelope")
    for estimator in model["estimators"]:
        vector: list[float] = []
        for spec in estimator["numeric"]:
            raw = payload.get(spec["name"], spec["impute"])
            value = spec["impute"] if raw is None or pd.isna(raw) else float(raw)
            vector.append((value - spec["mean"]) / (spec["scale"] or 1.0))
        for spec in estimator["categorical"]:
            value = str(payload.get(spec["name"], spec["impute"]))
            if value not in spec["categories"]:
                warnings.append(f"{spec['name'].replace('_', ' ')} contains an unseen category")
            vector.extend([1.0 if value == category else 0.0 for category in spec["categories"]])
        score = float(np.dot(vector, estimator["coefficients"]) + estimator["intercept"])
        calibration = estimator["calibration"]
        calibrated.append(_sigmoid(-(calibration["a"] * score + calibration["b"])))
    return float(np.mean(calibrated)), sorted(set(warnings))


def risk_band(probability: float) -> str:
    if probability < 0.25:
        return "Lower model-estimated risk"
    if probability < 0.50:
        return "Moderate model-estimated risk"
    return "Higher model-estimated risk"
