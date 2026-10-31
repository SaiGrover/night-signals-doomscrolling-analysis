"""Retrospective calibration slope/intercept from saved historical predictions."""
from pathlib import Path
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"


def main() -> None:
    frame = pd.read_csv(TABLES / "production_holdout_predictions.csv")
    y = frame.y_true.astype(int)
    probability = frame.probability.clip(1e-6, 1 - 1e-6)
    logit = np.log(probability / (1 - probability))
    fit = sm.Logit(y, sm.add_constant(logit)).fit(disp=False)
    interval = fit.conf_int()
    result = {
        "n": len(frame),
        "calibration_intercept": float(fit.params.iloc[0]),
        "calibration_intercept_95_ci": [float(v) for v in interval.iloc[0]],
        "calibration_slope": float(fit.params.iloc[1]),
        "calibration_slope_95_ci": [float(v) for v in interval.iloc[1]],
        "interpretation": "Retrospective calibration in the saved historical holdout; earlier reuse cannot be excluded. No external calibration claim.",
    }
    (TABLES / "holdout_calibration_slope.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
