from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from .config import (
    ANALYSIS_SUMMARY,
    HIGH_EXPOSURE_DOOMSCROLLER,
    HIGH_EXPOSURE_SCREEN_MINUTES,
    MODEL_SUMMARY,
    PRIMARY_DATA,
    TABLE_DIR,
)


@st.cache_data(max_entries=8, show_spinner=False)
def load_survey(path: str | Path = PRIMARY_DATA) -> pd.DataFrame:
    """Load and deterministically enrich the primary survey without mutating raw data."""
    df = pd.read_csv(path)
    out = df.copy()
    out["doomscroll_load_minutes"] = (
        out["doomscroll_sessions_per_night"] * out["avg_doomscroll_session_minutes"]
    )
    out["poor_sleep"] = out["sleep_quality_category"].eq("Poor")
    out["favorable_sleep"] = out["sleep_quality_category"].eq("Good")
    out["exposure_quartile"] = pd.qcut(
        out["bedtime_screen_time_minutes"],
        q=4,
        labels=["Q1 · lowest", "Q2", "Q3", "Q4 · highest"],
        duplicates="drop",
    )
    protective = pd.DataFrame(
        {
            "active": out["exercise_minutes_per_day"].fillna(0).ge(30),
            "restorative_routine": out["bedtime_routine_type"].isin(
                ["Reading", "Meditation/Journaling"]
            ),
            "phone_outside_bedroom": out["keeps_phone_in_bedroom"].eq("No"),
            "night_mode": out["uses_night_mode"].eq("Yes"),
            "recent_detox": out["days_since_last_digital_detox"].fillna(np.inf).le(30),
        }
    )
    out["protective_habit_count"] = protective.sum(axis=1)
    out["high_exposure"] = (
        out["bedtime_screen_time_minutes"].ge(HIGH_EXPOSURE_SCREEN_MINUTES)
        & out["doomscroller"].eq(HIGH_EXPOSURE_DOOMSCROLLER)
    )
    out["resilience_group"] = np.select(
        [out["high_exposure"] & out["favorable_sleep"], out["high_exposure"] & out["poor_sleep"]],
        ["High exposure · favorable sleep", "High exposure · poor sleep"],
        default="Other respondents",
    )
    out["age_group"] = pd.cut(
        out["age"], [0, 19, 29, np.inf], labels=["15–19", "20–29", "30+"]
    )
    return out


@st.cache_data(max_entries=32, show_spinner=False)
def read_csv_artifact(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLE_DIR / name)


@st.cache_data(max_entries=32, show_spinner=False)
def read_json_artifact(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_summaries() -> tuple[dict, dict]:
    return read_json_artifact(ANALYSIS_SUMMARY), read_json_artifact(MODEL_SUMMARY)


def apply_filters(
    df: pd.DataFrame,
    genders: list[str] | None = None,
    occupations: list[str] | None = None,
    exposure: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df
    if genders:
        filtered = filtered[filtered["gender"].isin(genders)]
    if occupations:
        filtered = filtered[filtered["occupation_status"].isin(occupations)]
    if exposure:
        filtered = filtered[filtered["exposure_quartile"].astype(str).isin(exposure)]
    return filtered.copy()


def audit_table(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "variable": df.columns,
            "dtype": [str(df[column].dtype) for column in df.columns],
            "missing_n": [int(df[column].isna().sum()) for column in df.columns],
            "missing_pct": [float(df[column].isna().mean() * 100) for column in df.columns],
            "unique_n": [int(df[column].nunique(dropna=True)) for column in df.columns],
        }
    )


def range_audit(df: pd.DataFrame) -> pd.DataFrame:
    """Check documented semantic bounds without silently deleting observations."""
    bounds = {
        "age": (0, 120),
        "total_daily_screen_time_hours": (0, 24),
        "bedtime_screen_time_minutes": (0, 1440),
        "doomscroll_sessions_per_night": (0, 100),
        "avg_doomscroll_session_minutes": (0, 1440),
        "phone_checks_per_night": (0, 200),
        "sleep_hours_per_night": (0, 24),
        "sleep_latency_minutes": (0, 1440),
        "number_of_night_wakeups": (0, 100),
        "weekly_sleep_debt_hours": (0, 168),
        "daytime_fatigue_score": (1, 10),
        "sleep_quality_score": (1, 5),
        "anxiety_score": (1, 10),
        "stress_score": (1, 10),
        "exercise_minutes_per_day": (0, 1440),
        "days_since_last_digital_detox": (0, 3650),
    }
    rows = []
    for column, (low, high) in bounds.items():
        if column not in df:
            continue
        values = pd.to_numeric(df[column], errors="coerce")
        invalid = values.notna() & ~values.between(low, high)
        rows.append({"variable": column, "allowed_min": low, "allowed_max": high, "observed_min": values.min(), "observed_max": values.max(), "out_of_range_n": int(invalid.sum())})
    return pd.DataFrame(rows)
