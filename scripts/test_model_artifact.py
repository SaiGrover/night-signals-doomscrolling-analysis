import json
from pathlib import Path
import joblib
import pandas as pd

root = Path(__file__).resolve().parents[1]
summary = json.loads((root / "outputs/tables/production_model_summary.json").read_text())
artifact = joblib.load(root / "outputs/models/poor_sleep_preoutcome_model.joblib")
portable = json.loads((root / "outputs/models/poor_sleep_preoutcome_model.json").read_text())
assert summary["untouched_holdout_rows"] == 250
assert abs(summary["majority_baseline_accuracy"] - 0.67) < 1e-9
assert summary["holdout"]["balanced_accuracy"] > summary["majority_baseline_accuracy"]
assert summary["external_validation"].startswith("Not performed")
assert artifact["version"] == summary["model_version"]
assert "drift_baseline" in artifact
assert portable["format"] == "night-signals-logistic-ensemble-v1"
for forbidden in ["sleep_hours_per_night", "sleep_latency_minutes", "number_of_night_wakeups", "daytime_fatigue_score", "weekly_sleep_debt_hours", "sleep_quality_score"]:
    assert forbidden not in artifact["features"]
row = pd.read_csv(root / "data/sleep_doomscrolling_habits.csv").iloc[0].to_dict()
expected = float(artifact["model"].predict_proba(pd.DataFrame([{name: row.get(name, artifact["defaults"][name]) for name in artifact["features"]}]))[0, 1])
predictions = []
for estimator in portable["estimators"]:
    values = [(float(row.get(field["name"], field["impute"])) - field["mean"]) / field["scale"] for field in estimator["numeric"]]
    for field in estimator["categorical"]:
        value = str(row.get(field["name"], field["impute"]))
        values.extend(float(value == category) for category in field["categories"])
    score = estimator["intercept"] + sum(coefficient * value for coefficient, value in zip(estimator["coefficients"], values))
    import math
    predictions.append(1 / (1 + math.exp(estimator["calibration"]["a"] * score + estimator["calibration"]["b"])))
assert abs(sum(predictions) / len(predictions) - expected) < 1e-10
print("model artifact checks passed")
