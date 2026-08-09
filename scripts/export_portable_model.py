import json
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]


def export_bundle(bundle, destination):
    estimators = []
    for calibrated in bundle["model"].calibrated_classifiers_:
        pipeline = calibrated.estimator
        preprocess = pipeline.named_steps["preprocess"]
        numeric = preprocess.named_transformers_["numeric"]
        categorical = preprocess.named_transformers_["categorical"]
        numeric_columns = preprocess.transformers_[0][2]
        categorical_columns = preprocess.transformers_[1][2]
        numeric_imputer = numeric.named_steps["impute"]
        scaler = numeric.named_steps["scale"]
        categorical_imputer = categorical.named_steps["impute"]
        encoder = categorical.named_steps["onehot"]
        model = pipeline.named_steps["model"]
        estimators.append({
            "numeric": [{"name": name, "impute": float(numeric_imputer.statistics_[index]),
                         "mean": float(scaler.mean_[index]), "scale": float(scaler.scale_[index])}
                        for index, name in enumerate(numeric_columns)],
            "categorical": [{"name": name, "impute": str(categorical_imputer.statistics_[index]),
                             "categories": [str(value) for value in encoder.categories_[index]]}
                            for index, name in enumerate(categorical_columns)],
            "coefficients": model.coef_[0].tolist(), "intercept": float(model.intercept_[0]),
            "calibration": {"a": float(calibrated.calibrators[0].a_), "b": float(calibrated.calibrators[0].b_)},
        })
    portable = {key: bundle[key] for key in ["threshold", "features", "defaults", "ranges", "categories", "drift_baseline", "version"]}
    portable["format"] = "night-signals-logistic-ensemble-v1"
    portable["estimators"] = estimators
    Path(destination).write_text(json.dumps(portable, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    bundle = joblib.load(ROOT / "outputs/models/poor_sleep_preoutcome_model.joblib")
    export_bundle(bundle, ROOT / "outputs/models/poor_sleep_preoutcome_model.json")
