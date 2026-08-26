"""Layer C - PhysioNet objective physiological evidence (RQ5, synopsis 4.12).

Self-contained: downloads the public PhysioNet Sleep-Accel heart-rate and
sleep-label files if not already present under `external/physionet/`, then
summarises Apple Watch heart rate over polysomnography-scored sleep stages
across the 31 subjects. Used as an INDEPENDENT physiological evidence layer -
never row-merged with the survey or NHANES, and never used to claim that
doomscrolling changes heart rate.

Run from the repository root:  python scripts/build_physionet_evidence.py

Outputs (consumed by the Research Atlas Evidence Synthesis page):
  public/data/physionet_summary.json
  outputs/tables/physionet_*.csv
  outputs/figures/17_physionet_evidence.png (embedded into the external-evidence notebook)

The atlas Evidence Synthesis page renders the interactive Plotly specs stored under
the "charts" key of physionet_summary.json, not a static image.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "external" / "physionet"
TABLES = ROOT / "outputs" / "tables"
FIGS = ROOT / "outputs" / "figures"
PUBLIC = ROOT / "public" / "data"
ASSETS = ROOT / "public" / "assets"
for d in (RAW / "heart_rate", RAW / "labels", TABLES, FIGS, PUBLIC, ASSETS):
    d.mkdir(parents=True, exist_ok=True)

BASE = "https://physionet.org/files/sleep-accel/1.0.0"
SUBJECTS = ["1066528", "1360686", "1449548", "1455390", "1818471", "2598705", "2638030",
            "3509524", "3997827", "4018081", "4314139", "4426783", "46343", "5132496",
            "5383425", "5498603", "5797046", "6220552", "759667", "7749105", "781756",
            "8000685", "8173033", "8258170", "844359", "8530312", "8686948", "8692923",
            "9106476", "9618981", "9961348"]
STAGE_NAMES = {0: "Wake", 1: "N1 (light)", 2: "N2", 3: "N3 (deep)", 5: "REM"}
STAGE_ORDER = ["Wake", "N1 (light)", "N2", "N3 (deep)", "REM"]


def ensure_data() -> None:
    for sid in SUBJECTS:
        for sub, suffix in (("heart_rate", "_heartrate.txt"), ("labels", "_labeled_sleep.txt")):
            dest = RAW / sub / f"{sid}{suffix}"
            if dest.exists() and dest.stat().st_size > 100:
                continue
            print(f"downloading {sub}/{sid}{suffix} ...")
            urllib.request.urlretrieve(f"{BASE}/{sub}/{sid}{suffix}", dest)


def load_subject(sid: str):
    lab_path = RAW / "labels" / f"{sid}_labeled_sleep.txt"
    hr_path = RAW / "heart_rate" / f"{sid}_heartrate.txt"
    if not (lab_path.exists() and hr_path.exists()):
        return None
    lab = pd.read_csv(lab_path, header=None, names=["time", "stage"], sep=r"\s+")
    hr = pd.read_csv(hr_path, header=None, names=["time", "bpm"])
    lab["time"] = lab["time"].astype(float)
    hr["time"] = hr["time"].astype(float)
    lab = lab[lab["stage"].isin(STAGE_NAMES)].sort_values("time").reset_index(drop=True)
    hr = hr[(hr["bpm"] > 25) & (hr["bpm"] < 220) & (hr["time"] >= 0)].sort_values("time").reset_index(drop=True)
    if lab.empty or hr.empty:
        return None
    merged = pd.merge_asof(hr, lab, on="time", direction="nearest", tolerance=30).dropna(subset=["stage"])
    merged["stage_name"] = merged["stage"].astype(int).map(STAGE_NAMES)
    merged["subject"] = sid
    return merged


def count_awakenings(seq: list[int]) -> int:
    started, awake = False, 0
    for i, s in enumerate(seq):
        if s != 0:
            started = True
        elif started and i > 0 and seq[i - 1] != 0:
            awake += 1
    return awake


def build() -> dict:
    ensure_data()
    per_hr, subj_rows, comp_rows = [], [], []
    for sid in SUBJECTS:
        m = load_subject(sid)
        if m is None:
            continue
        g = m.groupby("stage_name")["bpm"].agg(["mean", "std", "count"]).reset_index()
        g["subject"] = sid
        per_hr.append(g)
        lab = pd.read_csv(RAW / "labels" / f"{sid}_labeled_sleep.txt", header=None,
                          names=["time", "stage"], sep=r"\s+")
        lab = lab[lab["stage"].isin(STAGE_NAMES)].sort_values("time")
        comp = lab["stage"].map(STAGE_NAMES).value_counts(normalize=True)
        comp_rows.append({"subject": sid, **{s: round(float(comp.get(s, 0.0)) * 100, 2) for s in STAGE_ORDER}})
        transitions = int((lab["stage"].values[1:] != lab["stage"].values[:-1]).sum())
        subj_rows.append({"subject": sid, "epochs_scored": int(len(lab)),
                          "recording_hours": round(len(lab) * 30 / 3600, 2),
                          "mean_hr": round(float(m["bpm"].mean()), 1),
                          "stage_transitions": transitions,
                          "awakenings_after_onset": count_awakenings(lab["stage"].tolist())})

    hr_long = pd.concat(per_hr, ignore_index=True)
    by_stage = hr_long.groupby("stage_name").agg(subjects=("subject", "nunique"),
                                                 mean_hr=("mean", "mean"),
                                                 mean_hr_variability=("std", "mean")).reindex(STAGE_ORDER).reset_index()
    by_stage["mean_hr"] = by_stage["mean_hr"].round(1)
    by_stage["mean_hr_variability"] = by_stage["mean_hr_variability"].round(2)
    by_stage.to_csv(TABLES / "physionet_hr_by_stage.csv", index=False)
    comp = pd.DataFrame(comp_rows); comp.to_csv(TABLES / "physionet_stage_composition.csv", index=False)
    subj = pd.DataFrame(subj_rows); subj.to_csv(TABLES / "physionet_subject_summary.csv", index=False)

    wake_hr = float(by_stage.loc[by_stage["stage_name"] == "Wake", "mean_hr"].iloc[0])
    deep_hr = float(by_stage.loc[by_stage["stage_name"] == "N3 (deep)", "mean_hr"].iloc[0])
    summary = {"dataset": "PhysioNet Sleep-Accel (Walch et al., 2019)",
               "role": "Physiological evidence layer (Apple Watch HR vs PSG sleep stages); not linked to survey respondents",
               "subjects_analysed": int(subj["subject"].nunique()),
               "total_scored_epochs": int(subj["epochs_scored"].sum()),
               "hr_by_stage": by_stage.to_dict(orient="records"),
               "wake_minus_deep_hr": round(wake_hr - deep_hr, 1),
               "mean_stage_composition_pct": {s: round(float(comp[s].mean()), 2) for s in STAGE_ORDER},
               "median_awakenings_after_onset": int(subj["awakenings_after_onset"].median()),
               "note": "Objective physiology, associations only; no causal or clinical claims; "
                       "tri-axial acceleration is available in the source and summarised here via "
                       "wearable heart-rate dynamics to keep the analytical footprint light."}
    summary["charts"] = _chart_specs(by_stage, comp, subj)
    for target in (PUBLIC / "physionet_summary.json", TABLES / "physionet_summary.json"):
        target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _figure(by_stage, comp, subj)
    return summary


def _chart_specs(by_stage, comp, subj) -> dict:
    """Interactive Plotly specs ({data, layout}) rendered by the Research Atlas,
    matching public/data/plotly_charts.json; PlotRenderer applies shared styling."""
    stages = by_stage["stage_name"].tolist()
    comp_means = [round(float(comp[s].mean()), 2) for s in stages]
    return {
        "hr_stage": {"data": [
            {"type": "bar", "name": "Mean HR", "x": stages, "y": by_stage["mean_hr"].tolist(),
             "error_y": {"type": "data", "array": by_stage["mean_hr_variability"].tolist(), "visible": True,
                         "color": "rgba(170,160,181,.5)"},
             "marker": {"color": "#6f789f"}, "hovertemplate": "%{x}<br>%{y:.1f} bpm<extra></extra>"}],
            "layout": {"height": 380, "margin": {"l": 58, "r": 20, "t": 20, "b": 55},
                       "xaxis": {"title": "Sleep stage"}, "yaxis": {"title": "Heart rate (bpm)"}}},
        "stage_comp": {"data": [
            {"type": "bar", "name": "Composition", "x": stages, "y": comp_means, "marker": {"color": "#8d7baa"},
             "hovertemplate": "%{x}<br>%{y:.1f}% of scored epochs<extra></extra>"}],
            "layout": {"height": 380, "margin": {"l": 58, "r": 20, "t": 20, "b": 55},
                       "xaxis": {"title": "Sleep stage"}, "yaxis": {"title": "% of scored epochs"}}},
        "awakenings": {"data": [
            {"type": "scatter", "mode": "markers", "name": "Subject",
             "x": subj["recording_hours"].tolist(), "y": subj["awakenings_after_onset"].tolist(),
             "marker": {"color": "#74a08f", "size": 9},
             "hovertemplate": "%{x:.1f} h scored<br>%{y} awakenings<extra></extra>"}],
            "layout": {"height": 380, "margin": {"l": 55, "r": 20, "t": 20, "b": 52},
                       "xaxis": {"title": "Hours scored (per subject)"},
                       "yaxis": {"title": "Awakenings after onset"}}},
    }


def _figure(by_stage, comp, subj) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, accent, accent2 = "#0b1020", "#4c6ef5", "#e8590c"
    plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.color": "#33415522", "figure.facecolor": "white"})
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    ax[0].bar(by_stage["stage_name"], by_stage["mean_hr"], yerr=by_stage["mean_hr_variability"], color=accent, capsize=4)
    ax[0].set_title("C1 · Mean heart rate by sleep stage"); ax[0].set_ylabel("bpm"); ax[0].tick_params(axis="x", labelrotation=20)
    comp_means = [comp[s].mean() for s in STAGE_ORDER]
    ax[1].bar(STAGE_ORDER, comp_means, color=accent2)
    ax[1].set_title("C2 · Mean sleep-stage composition"); ax[1].set_ylabel("% of scored epochs"); ax[1].tick_params(axis="x", labelrotation=20)
    ax[2].scatter(subj["recording_hours"], subj["awakenings_after_onset"], color=accent, s=40, alpha=0.8)
    ax[2].set_title("C3 · Awakenings vs recording length"); ax[2].set_xlabel("hours scored"); ax[2].set_ylabel("awakenings after onset")
    fig.suptitle(f"PhysioNet Sleep-Accel · {int(subj['subject'].nunique())} subjects · objective wearable physiology (associations only)",
                 color=ink, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(FIGS / "17_physionet_evidence.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, default=str))
