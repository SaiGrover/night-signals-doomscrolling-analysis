"""Export interpretation tables for the primary model and exception analysis."""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public/data/sleep_doomscrolling_habits.csv"
TABLES = ROOT / "outputs/tables"
PUBLIC = ROOT / "public/data"
MODEL = ROOT / "outputs/models/poor_sleep_preoutcome_model.joblib"
RANDOM_STATE = 42

TABLES.mkdir(parents=True, exist_ok=True)
PUBLIC.mkdir(parents=True, exist_ok=True)


def clean_feature_name(name: str) -> str:
    value = name.replace("numeric__", "").replace("categorical__", "")
    value = value.replace("_", " ").replace("<=14d", "within 14d")
    return value.title().replace(" Mg ", " mg ").replace(" Per ", " per ")


def export_odds_ratios() -> pd.DataFrame:
    artifact = joblib.load(MODEL)
    calibrated = artifact["model"]
    frames = []
    for index, fold_model in enumerate(calibrated.calibrated_classifiers_):
        estimator = fold_model.estimator
        features = estimator.named_steps["preprocess"].get_feature_names_out()
        coefficients = estimator.named_steps["model"].coef_[0]
        frames.append(pd.DataFrame({"fold": index, "feature": features, "log_odds": coefficients}))

    folded = pd.concat(frames, ignore_index=True)
    summary = folded.groupby("feature", as_index=False).agg(
        log_odds=("log_odds", "mean"),
        log_odds_sd=("log_odds", "std"),
    )
    summary["odds_ratio"] = np.exp(summary["log_odds"])
    summary["direction"] = np.where(summary["odds_ratio"] >= 1, "Higher poor-sleep odds", "Lower poor-sleep odds")
    summary["feature_label"] = summary["feature"].map(clean_feature_name)
    summary["abs_log_odds"] = summary["log_odds"].abs()
    summary = summary.sort_values("abs_log_odds", ascending=False)
    summary.to_csv(TABLES / "primary_model_odds_ratios.csv", index=False)
    summary.to_csv(PUBLIC / "primary_model_odds_ratios.csv", index=False)
    return summary


def bootstrap_mean_difference(good: pd.Series, poor: pd.Series, repeats: int = 2000) -> tuple[float, float, float, float]:
    good_values = good.dropna().to_numpy(dtype=float)
    poor_values = poor.dropna().to_numpy(dtype=float)
    rng = np.random.default_rng(RANDOM_STATE)
    observed = float(good_values.mean() - poor_values.mean())
    pooled_sd = np.sqrt(((len(good_values) - 1) * good_values.var(ddof=1) + (len(poor_values) - 1) * poor_values.var(ddof=1)) / (len(good_values) + len(poor_values) - 2))
    cohen_d = float(observed / pooled_sd) if pooled_sd else 0.0
    boot = []
    for _ in range(repeats):
        good_sample = rng.choice(good_values, size=len(good_values), replace=True)
        poor_sample = rng.choice(poor_values, size=len(poor_values), replace=True)
        boot.append(float(good_sample.mean() - poor_sample.mean()))
    low, high = np.quantile(boot, [.025, .975])
    return observed, float(low), float(high), cohen_d


def export_exception_effects() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    heavy = df[(df["doomscroller"].astype(str).str.lower() == "yes") & (df["bedtime_screen_time_minutes"] >= 66)].copy()
    good = heavy[heavy["sleep_quality_category"] == "Good"]
    poor = heavy[heavy["sleep_quality_category"] == "Poor"]
    metrics = [
        ("sleep_hours_per_night", "Sleep hours per night", "hours", "Higher is better"),
        ("weekly_sleep_debt_hours", "Weekly sleep debt", "hours/week", "Lower is better"),
        ("sleep_latency_minutes", "Sleep latency", "minutes", "Lower is better"),
        ("number_of_night_wakeups", "Night wakeups", "count", "Lower is better"),
        ("daytime_fatigue_score", "Daytime fatigue", "1-10 score", "Lower is better"),
        ("exercise_minutes_per_day", "Exercise", "minutes/day", "Higher is better"),
    ]
    rows = []
    for column, label, unit, desirable in metrics:
        diff, low, high, cohen_d = bootstrap_mean_difference(good[column], poor[column])
        rows.append({
            "metric": column,
            "label": label,
            "unit": unit,
            "n_good_heavy": int(len(good)),
            "n_poor_heavy": int(len(poor)),
            "good_heavy_mean": float(good[column].mean()),
            "poor_heavy_mean": float(poor[column].mean()),
            "mean_difference_good_minus_poor": diff,
            "bootstrap_95_low": low,
            "bootstrap_95_high": high,
            "cohen_d": cohen_d,
            "desirable_direction": desirable,
        })
    effects = pd.DataFrame(rows)
    effects.to_csv(TABLES / "exception_effect_sizes.csv", index=False)
    effects.to_csv(PUBLIC / "exception_effect_sizes.csv", index=False)
    return effects


if __name__ == "__main__":
    odds = export_odds_ratios()
    effects = export_exception_effects()
    print(odds.head(12).to_string(index=False))
    print(effects.to_string(index=False))
