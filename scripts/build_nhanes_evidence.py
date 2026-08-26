"""Layer B - NHANES independent population-health evidence (RQ5, synopsis 4.12).

Self-contained: downloads the public CDC NHANES August 2021-2023 files if they
are not already present under `external/nhanes/`, then analyses usual sleep
duration against blood pressure, BMI, and physical activity. NHANES is used as
an INDEPENDENT evidence layer only - never row-merged with the primary survey.

Run from the repository root:  python scripts/build_nhanes_evidence.py

Outputs (consumed by the Research Atlas Evidence Synthesis page):
  public/data/nhanes_summary.json
  outputs/tables/nhanes_*.csv
  outputs/figures/16_nhanes_evidence.png
  public/assets/16_nhanes_evidence.png
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy import stats as _stats
    HAVE_SCIPY = True
except Exception:  # pragma: no cover
    HAVE_SCIPY = False

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "external" / "nhanes"
TABLES = ROOT / "outputs" / "tables"
FIGS = ROOT / "outputs" / "figures"
PUBLIC = ROOT / "public" / "data"
ASSETS = ROOT / "public" / "assets"
for d in (RAW, TABLES, FIGS, PUBLIC, ASSETS):
    d.mkdir(parents=True, exist_ok=True)

BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles"
FILES = ["SLQ_L", "BMX_L", "BPXO_L", "PAQ_L", "DEMO_L"]
CYCLE = "August 2021-2023 (NHANES L cycle)"


def ensure_data() -> None:
    for name in FILES:
        dest = RAW / f"{name}.xpt"
        if dest.exists() and dest.stat().st_size > 10_000:
            continue
        print(f"downloading {name}.xpt ...")
        urllib.request.urlretrieve(f"{BASE}/{name}.xpt", dest)


def load(name: str, cols: list[str]) -> pd.DataFrame:
    df = pd.read_sas(RAW / f"{name}.xpt")
    return df[[c for c in cols if c in df.columns]].copy()


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / sp) if sp else float("nan")


def welch(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    if not HAVE_SCIPY or len(a) < 2 or len(b) < 2:
        return float("nan")
    return float(_stats.ttest_ind(a, b, equal_var=False).pvalue)


def build() -> dict:
    ensure_data()
    slq = load("SLQ_L", ["SEQN", "SLD012", "SLD013"])
    bpx = load("BPXO_L", ["SEQN", "BPXOSY1", "BPXOSY2", "BPXOSY3", "BPXODI1", "BPXODI2", "BPXODI3"])
    bmx = load("BMX_L", ["SEQN", "BMXBMI"])
    paq = load("PAQ_L", ["SEQN", "PAD680", "PAD800", "PAD820"])
    demo = load("DEMO_L", ["SEQN", "RIDAGEYR", "RIAGENDR"])

    df = demo.merge(slq, on="SEQN", how="left").merge(bmx, on="SEQN", how="left")
    df = df.merge(bpx, on="SEQN", how="left").merge(paq, on="SEQN", how="left")
    df = df[df["RIDAGEYR"] >= 18]
    df["sleep_hours"] = pd.to_numeric(df["SLD012"], errors="coerce")
    df = df[df["sleep_hours"].between(2, 14)]

    df["systolic"] = df[["BPXOSY1", "BPXOSY2", "BPXOSY3"]].mean(axis=1)
    df["diastolic"] = df[["BPXODI1", "BPXODI2", "BPXODI3"]].mean(axis=1)
    df["bmi"] = pd.to_numeric(df["BMXBMI"], errors="coerce")
    df["sedentary_min"] = pd.to_numeric(df["PAD680"], errors="coerce")
    df.loc[df["sedentary_min"] > 1320, "sedentary_min"] = np.nan
    mod = pd.to_numeric(df["PAD800"], errors="coerce").where(lambda s: s <= 840)
    vig = pd.to_numeric(df["PAD820"], errors="coerce").where(lambda s: s <= 840)
    df["activity_min"] = mod.fillna(0) + vig.fillna(0)
    df["activity_group"] = np.where(df["activity_min"] >= 30, "Meets activity (>=30 min/day)",
                                    "Below activity floor (<30 min/day)")
    df["short_sleep"] = np.where(df["sleep_hours"] < 7, "Short (<7h)", "Adequate (>=7h)")
    df["bmi_category"] = pd.cut(df["bmi"], [0, 18.5, 25, 30, 100],
                                labels=["Underweight", "Normal", "Overweight", "Obese"])

    summary: dict = {"dataset": "NHANES", "cycle": CYCLE,
                     "role": "Secondary, independent population-health evidence (not linked to primary respondents)",
                     "analytic_adults": int(len(df)),
                     "note": "Cross-sectional survey; associations only, no causal or clinical claims."}

    bp = df.dropna(subset=["systolic", "diastolic"])
    bp_tbl = pd.DataFrame([{"sleep_group": g, "n": int(len(s)),
                            "mean_systolic": round(s["systolic"].mean(), 2),
                            "mean_diastolic": round(s["diastolic"].mean(), 2)}
                           for g, s in bp.groupby("short_sleep")])
    bp_tbl.to_csv(TABLES / "nhanes_sleep_blood_pressure.csv", index=False)
    short = bp[bp["short_sleep"] == "Short (<7h)"]
    adeq = bp[bp["short_sleep"] == "Adequate (>=7h)"]
    summary["B1_sleep_blood_pressure"] = {
        "systolic_diff_short_minus_adequate": round(short["systolic"].mean() - adeq["systolic"].mean(), 2),
        "systolic_p": welch(short["systolic"].to_numpy(), adeq["systolic"].to_numpy()),
        "systolic_cohens_d": round(cohens_d(short["systolic"].to_numpy(), adeq["systolic"].to_numpy()), 3),
        "diastolic_diff_short_minus_adequate": round(short["diastolic"].mean() - adeq["diastolic"].mean(), 2),
        "diastolic_p": welch(short["diastolic"].to_numpy(), adeq["diastolic"].to_numpy()),
    }

    bmi_sub = df.dropna(subset=["bmi_category"])
    cats = [{"bmi_category": c, "n": int(len(s)), "mean_sleep_hours": round(s.mean(), 3),
             "sd_sleep_hours": round(s.std(), 3)}
            for c in ["Underweight", "Normal", "Overweight", "Obese"]
            for s in [bmi_sub[bmi_sub["bmi_category"] == c]["sleep_hours"]] if len(s)]
    pd.DataFrame(cats).to_csv(TABLES / "nhanes_sleep_by_bmi.csv", index=False)
    corr = df.dropna(subset=["bmi"])
    summary["B2_sleep_by_bmi"] = {
        "spearman_bmi_vs_sleep": round(float(corr["bmi"].corr(corr["sleep_hours"], method="spearman")), 3),
        "categories": cats}

    act_rows = [{"activity_group": g, "n": int(len(s)), "mean_sleep_hours": round(s["sleep_hours"].mean(), 3)}
                for g, s in df.dropna(subset=["activity_group"]).groupby("activity_group")]
    pd.DataFrame(act_rows).to_csv(TABLES / "nhanes_sleep_by_activity.csv", index=False)
    sed = df.dropna(subset=["sedentary_min"]).copy()
    sed["sedentary_quartile"] = pd.qcut(sed["sedentary_min"], 4, labels=["Q1 (least)", "Q2", "Q3", "Q4 (most)"])
    sed_rows = [{"sedentary_quartile": str(q), "n": int(len(s)), "mean_sleep_hours": round(s["sleep_hours"].mean(), 3)}
                for q, s in sed.groupby("sedentary_quartile", observed=True)]
    pd.DataFrame(sed_rows).to_csv(TABLES / "nhanes_sleep_by_sedentary.csv", index=False)
    summary["B3_sleep_by_activity"] = {
        "active_groups": act_rows, "sedentary_quartiles": sed_rows,
        "spearman_sedentary_vs_sleep": round(float(sed["sedentary_min"].corr(sed["sleep_hours"], method="spearman")), 3)}

    _figures(bp_tbl, pd.DataFrame(cats), pd.DataFrame(sed_rows))
    for target in (PUBLIC / "nhanes_summary.json", TABLES / "nhanes_summary.json"):
        target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _figures(bp_tbl, bmi_tbl, sed_tbl) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, accent, accent2 = "#0b1020", "#4c6ef5", "#e8590c"
    plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.color": "#33415522", "figure.facecolor": "white"})
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    x = np.arange(len(bp_tbl))
    ax[0].bar(x - 0.2, bp_tbl["mean_systolic"], 0.4, label="Systolic", color=accent)
    ax[0].bar(x + 0.2, bp_tbl["mean_diastolic"], 0.4, label="Diastolic", color=accent2)
    ax[0].set_xticks(x); ax[0].set_xticklabels(bp_tbl["sleep_group"], fontsize=9)
    ax[0].set_title("B1 · Blood pressure by sleep group"); ax[0].set_ylabel("mmHg"); ax[0].legend()
    ax[1].bar(bmi_tbl["bmi_category"], bmi_tbl["mean_sleep_hours"], color=accent)
    ax[1].set_title("B2 · Usual sleep by BMI category"); ax[1].set_ylabel("hours")
    ax[1].set_ylim(bmi_tbl["mean_sleep_hours"].min() - 0.4, bmi_tbl["mean_sleep_hours"].max() + 0.3)
    ax[2].bar(sed_tbl["sedentary_quartile"], sed_tbl["mean_sleep_hours"], color=accent2)
    ax[2].set_title("B3 · Sleep by sedentary-time quartile"); ax[2].set_ylabel("hours")
    ax[2].set_ylim(sed_tbl["mean_sleep_hours"].min() - 0.4, sed_tbl["mean_sleep_hours"].max() + 0.3)
    for a in ax:
        a.tick_params(axis="x", labelrotation=15)
    fig.suptitle("NHANES 2021-2023 · Independent population-health evidence (associations only)",
                 color=ink, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(FIGS / "16_nhanes_evidence.png", dpi=130)
    fig.savefig(ASSETS / "16_nhanes_evidence.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, default=str))
