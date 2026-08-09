import json
from pathlib import Path
import joblib

root = Path(__file__).resolve().parents[1]
summary = json.loads((root / "outputs/tables/production_model_summary.json").read_text())
artifact = joblib.load(root / "outputs/models/poor_sleep_preoutcome_model.joblib")
assert summary["untouched_holdout_rows"] == 250
assert abs(summary["majority_baseline_accuracy"] - 0.67) < 1e-9
assert summary["holdout"]["balanced_accuracy"] > summary["majority_baseline_accuracy"]
assert summary["external_validation"].startswith("Not performed")
assert artifact["version"] == summary["model_version"]
assert "drift_baseline" in artifact
for forbidden in ["sleep_hours_per_night", "sleep_latency_minutes", "number_of_night_wakeups", "daytime_fatigue_score", "weekly_sleep_debt_hours", "sleep_quality_score"]:
    assert forbidden not in artifact["features"]
print("model artifact checks passed")
