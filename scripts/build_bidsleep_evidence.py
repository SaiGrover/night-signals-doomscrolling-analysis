"""Build the optional multi-night PhysioNet BIDSleep evidence layer.

The raw dataset is intentionally not committed: PhysioNet reports about 27.9 GB
uncompressed. Run without arguments to write a source manifest. After downloading
the dataset into external/physionet/bidsleep-dataset/1.0.0, run this script again
to generate subject/night summaries from local files.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "external" / "physionet" / "bidsleep-dataset" / "1.0.0"
TABLES = ROOT / "outputs" / "tables"
BASE_URL = "https://physionet.org/files/bidsleep-dataset/1.0.0/"
LICENSE = "Open Data Commons Attribution License v1.0"
STAGES = {0: "Wake", 1: "N1 (light)", 2: "N2", 3: "N3 (deep)", 4: "REM", 5: "Unknown"}


def source_manifest() -> dict:
    return {
        "dataset": "A Multi-Night Instantaneous Heart Rate and Accelerometry Dataset with EEG Sleep Stage Labels",
        "physionet_url": "https://physionet.org/content/bidsleep-dataset/1.0.0/",
        "download_url": BASE_URL,
        "version": "1.0.0",
        "doi": "10.13026/a0sy-7t69",
        "license": LICENSE,
        "expected_subjects": 47,
        "expected_nights": 253,
        "files_per_night": ["motion.csv", "hr.csv", "labels.mat"],
        "analysis_role": "Independent physiological evidence; never merged with Night Signals respondents and not external validation of the classifier.",
        "raw_data_policy": "Not committed to Git; download locally because the source reports approximately 27.9 GB uncompressed.",
    }


def summarize_local(root: Path) -> dict:
    rows = []
    for labels_path in sorted(root.glob("Bidslab*/**/labels.mat")):
        night_dir = labels_path.parent
        subject = night_dir.parent.name
        night = night_dir.name
        labels = loadmat(labels_path)
        raw_labels = np.asarray(labels.get("dreem_label")).reshape(-1)
        stage_values = pd.to_numeric(pd.Series(raw_labels), errors="coerce").dropna().astype(int)
        stage_values = stage_values[stage_values.isin(STAGES)]
        hr_path = night_dir / "hr.csv"
        motion_path = night_dir / "motion.csv"
        # PhysioNet v1.0.0 CSV rows are headerless: timestamp, value(s).
        hr = pd.read_csv(hr_path, header=None) if hr_path.exists() else pd.DataFrame()
        motion = pd.read_csv(motion_path, header=None) if motion_path.exists() else pd.DataFrame()
        hr_numeric = hr.select_dtypes(include=[np.number])
        hr_values = hr_numeric.iloc[:, -1] if not hr_numeric.empty else pd.Series(dtype=float)
        hr_values = pd.to_numeric(hr_values, errors="coerce")
        accel_numeric = motion.select_dtypes(include=[np.number])
        accel_rms = float("nan")
        if accel_numeric.shape[1] >= 3:
            xyz = accel_numeric.iloc[:, -3:].apply(pd.to_numeric, errors="coerce").dropna().to_numpy()
            if len(xyz):
                accel_rms = float(np.sqrt(np.square(xyz).sum(axis=1)).mean())
        rows.append({
            "subject": subject,
            "night": night,
            "label_epochs": int(len(stage_values)),
            "hr_samples": int(hr_values.notna().sum()),
            "motion_samples": int(len(motion)),
            "mean_hr": float(hr_values.mean()) if hr_values.notna().any() else np.nan,
            "mean_acceleration_magnitude": accel_rms,
            "wake_share": float((stage_values == 0).mean()) if len(stage_values) else np.nan,
            "deep_share": float((stage_values == 3).mean()) if len(stage_values) else np.nan,
            "rem_share": float((stage_values == 4).mean()) if len(stage_values) else np.nan,
        })
    if not rows:
        raise FileNotFoundError(f"No local labels.mat files found under {root}")
    frame = pd.DataFrame(rows)
    TABLES.mkdir(parents=True, exist_ok=True)
    frame.to_csv(TABLES / "bidsleep_subject_night_summary.csv", index=False)
    result = source_manifest()
    result.update({
        "local_status": "analysed",
        "subjects_analysed": int(frame["subject"].nunique()),
        "nights_analysed": int(len(frame)),
        "subject_night_table": "outputs/tables/bidsleep_subject_night_summary.csv",
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    manifest = summarize_local(args.root) if args.root.exists() else source_manifest() | {
        "local_status": "manifest-only",
        "local_root": str(args.root),
        "next_step": f"Download the PhysioNet dataset into {args.root} and rerun this script.",
    }
    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / "bidsleep_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
