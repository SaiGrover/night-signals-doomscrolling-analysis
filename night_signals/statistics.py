from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from .config import OUTCOME_COLUMNS, RANDOM_STATE


def mean_ci(series: pd.Series, confidence: float = 0.95) -> tuple[float, float, float]:
    values = pd.to_numeric(series, errors="coerce").dropna().to_numpy()
    if len(values) < 2:
        return (float(np.nanmean(values)) if len(values) else np.nan, np.nan, np.nan)
    mean = float(values.mean())
    margin = float(stats.t.ppf((1 + confidence) / 2, len(values) - 1) * stats.sem(values))
    return mean, mean - margin, mean + margin


def cohens_d(a: pd.Series, b: pd.Series) -> float:
    x = pd.to_numeric(a, errors="coerce").dropna().to_numpy()
    y = pd.to_numeric(b, errors="coerce").dropna().to_numpy()
    if min(len(x), len(y)) < 2:
        return np.nan
    pooled = np.sqrt(((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1)) / (len(x) + len(y) - 2))
    return float((x.mean() - y.mean()) / pooled) if pooled else np.nan


def cramers_v(table: pd.DataFrame) -> float:
    if min(table.shape) < 2 or table.to_numpy().sum() == 0:
        return np.nan
    chi2 = stats.chi2_contingency(table, correction=False)[0]
    n = table.to_numpy().sum()
    return float(np.sqrt((chi2 / n) / min(table.shape[0] - 1, table.shape[1] - 1)))


def association_matrix(df: pd.DataFrame) -> pd.DataFrame:
    exposures = [
        "bedtime_screen_time_minutes",
        "doomscroll_load_minutes",
        "doomscroll_sessions_per_night",
        "phone_checks_per_night",
        "anxiety_score",
        "stress_score",
    ]
    rows: list[dict] = []
    for exposure in exposures:
        for outcome in OUTCOME_COLUMNS:
            pair = df[[exposure, outcome]].dropna()
            rho, p_value = stats.spearmanr(pair[exposure], pair[outcome])
            rows.append(
                {
                    "exposure": exposure,
                    "outcome": outcome,
                    "n": len(pair),
                    "spearman_rho": float(rho),
                    "p_value": float(p_value),
                }
            )
    result = pd.DataFrame(rows)
    result["p_fdr_bh"] = multipletests(result["p_value"], method="fdr_bh")[1]
    result["significant_fdr_05"] = result["p_fdr_bh"].lt(0.05)
    return result


def exposure_gradient(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    trend = {}
    for outcome in OUTCOME_COLUMNS:
        pair = df[["exposure_quartile", outcome]].dropna().copy()
        pair["quartile_rank"] = pair["exposure_quartile"].cat.codes + 1
        rho, p_value = stats.spearmanr(pair["quartile_rank"], pair[outcome]) if len(pair) >= 3 else (np.nan, np.nan)
        trend[outcome] = (float(rho), float(p_value))
    for level, group in df.groupby("exposure_quartile", observed=True):
        for outcome in OUTCOME_COLUMNS:
            mean, low, high = mean_ci(group[outcome])
            rho, p_value = trend[outcome]
            rows.append(
                {
                    "exposure_quartile": str(level),
                    "outcome": outcome,
                    "n": int(group[outcome].notna().sum()),
                    "mean": mean,
                    "ci_low": low,
                    "ci_high": high,
                    "ordered_trend_rho": rho,
                    "ordered_trend_p": p_value,
                }
            )
    return pd.DataFrame(rows)


def resilience_effects(df: pd.DataFrame) -> pd.DataFrame:
    high = df[df["high_exposure"]]
    good = high[high["favorable_sleep"]]
    poor = high[high["poor_sleep"]]
    factors = [
        "exercise_minutes_per_day",
        "days_since_last_digital_detox",
        "bedtime_routine_type",
        "keeps_phone_in_bedroom",
        "uses_night_mode",
        "consumes_negative_news_content",
        "anxiety_score",
        "stress_score",
        "protective_habit_count",
        "phone_checks_per_night",
    ]
    rows = []
    for factor in factors:
        good_values = good[factor].dropna()
        poor_values = poor[factor].dropna()
        if pd.api.types.is_numeric_dtype(df[factor]):
            if len(good_values) and len(poor_values):
                test = stats.mannwhitneyu(good_values, poor_values, alternative="two-sided")
                p_value = float(test.pvalue)
            else:
                p_value = np.nan
            favorable_mean = float(good_values.mean()) if len(good_values) else np.nan
            poor_mean = float(poor_values.mean()) if len(poor_values) else np.nan
            effect = cohens_d(good_values, poor_values)
            test_name = "Mann-Whitney U"
        else:
            combined = pd.concat([good_values, poor_values], ignore_index=True)
            labels = ["favorable"] * len(good_values) + ["poor"] * len(poor_values)
            table = pd.crosstab(combined, labels)
            p_value = float(stats.chi2_contingency(table, correction=False)[1]) if table.shape[0] > 1 and table.shape[1] > 1 else np.nan
            favorable_mean = np.nan
            poor_mean = np.nan
            effect = np.nan
            test_name = "chi-square"
        rows.append(
            {
                "factor": factor,
                "favorable_mean": favorable_mean,
                "poor_mean": poor_mean,
                "cohens_d": effect,
                "p_value": p_value,
                "favorable_n": int(good[factor].notna().sum()),
                "poor_n": int(poor[factor].notna().sum()),
                "test": test_name,
            }
        )
    result = pd.DataFrame(rows)
    valid = result["p_value"].notna()
    result["p_fdr_bh"] = np.nan
    if valid.any():
        result.loc[valid, "p_fdr_bh"] = multipletests(result.loc[valid, "p_value"], method="fdr_bh")[1]
    return result


def bootstrap_difference(
    a: pd.Series, b: pd.Series, repeats: int = 2000, seed: int = RANDOM_STATE
) -> tuple[float, float, float]:
    x = pd.to_numeric(a, errors="coerce").dropna().to_numpy()
    y = pd.to_numeric(b, errors="coerce").dropna().to_numpy()
    rng = np.random.default_rng(seed)
    diffs = np.array(
        [rng.choice(x, len(x), replace=True).mean() - rng.choice(y, len(y), replace=True).mean() for _ in range(repeats)]
    )
    return float(x.mean() - y.mean()), float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))
