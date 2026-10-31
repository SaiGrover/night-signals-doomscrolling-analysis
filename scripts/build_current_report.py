"""Compile the editable LaTeX research report after checking its metric snapshot."""
from pathlib import Path
import json
import shutil
import subprocess

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "deliverables/Sleep_Doomscrolling_Report.tex"
DEST = SOURCE.with_suffix(".pdf")
BUILD = ROOT / "tmp/tex"
TABLES = ROOT / "outputs/tables"


def verify_snapshot(source: str) -> None:
    model = json.loads((TABLES / "production_model_summary.json").read_text())
    calibration = json.loads((TABLES / "holdout_calibration_slope.json").read_text())
    tests = pd.read_csv(TABLES / "habit_association_tests.csv")
    baseline = pd.read_csv(TABLES / "development_baselines_ablations.csv")
    values = [
        f"{model['nested_cv']['balanced_accuracy']:.3f}",
        f"{model['holdout']['balanced_accuracy']:.3f}",
        f"{model['holdout']['roc_auc']:.3f}",
        f"{model['decision_threshold']:.3f}",
        f"{calibration['calibration_slope']:.3f}",
        f"{tests.loc[tests.variable.eq('consumes_negative_news_content'), 'p_fdr_bh'].iloc[0]:.3f}",
        f"{baseline.loc[baseline.model.eq('doomscroller label rule'), 'oof_balanced_accuracy_0_5'].iloc[0]:.3f}",
    ]
    missing = [value for value in values if value not in source]
    if missing:
        raise RuntimeError(f"TeX report metric snapshot is stale: {missing}")


def main() -> None:
    verify_snapshot(SOURCE.read_text(encoding="utf-8"))
    BUILD.mkdir(parents=True, exist_ok=True)
    command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
               f"-output-directory={BUILD}", str(SOURCE)]
    for _ in range(2):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout[-3000:] + result.stderr[-1000:])
    shutil.copyfile(BUILD / DEST.name, DEST)
    print(f"Compiled {DEST} from {SOURCE}")


if __name__ == "__main__":
    main()
