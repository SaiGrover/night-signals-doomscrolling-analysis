"""Development-only, fixed 5-fold baseline and feature-ablation comparison.

These are diagnostic comparisons at threshold 0.5, not tuned or nested model
selection estimates. The historical 250-row holdout is never loaded here.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
TARGET = "sleep_quality_category"
EXCLUDE = {"respondent_id", TARGET, "sleep_quality_score", "sleep_hours_per_night",
           "sleep_latency_minutes", "number_of_night_wakeups", "daytime_fatigue_score",
           "weekly_sleep_debt_hours"}


def main() -> None:
    df = pd.read_csv(ROOT / "data/sleep_doomscrolling_habits.csv")
    features = [name for name in df if name not in EXCLUDE]
    y = df[TARGET].eq("Poor").astype(int)
    development, _ = train_test_split(np.arange(len(df)), test_size=.25,
                                      stratify=y, random_state=42)
    x, y = df.iloc[development][features], y.iloc[development]
    folds = StratifiedKFold(5, shuffle=True, random_state=42)
    rows = []
    full_probability = None
    for name, subset in [
        ("bedtime minutes only", ["bedtime_screen_time_minutes"]),
        ("full minus self-label and phone checks", [f for f in features if f not in {"doomscroller", "phone_checks_per_night"}]),
        ("full minus self-label", [f for f in features if f != "doomscroller"]),
        ("full candidate features", features),
    ]:
        numeric = x[subset].select_dtypes(include=np.number).columns.tolist()
        categorical = [f for f in subset if f not in numeric]
        prep = ColumnTransformer([
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),
                                  ("scale", StandardScaler())]), numeric),
            ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                      ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ])
        model = Pipeline([("preprocess", prep), ("model", LogisticRegression(max_iter=3000))])
        prob = cross_val_predict(model, x[subset], y, cv=folds, method="predict_proba")[:, 1]
        if name == "full candidate features":
            full_probability = prob
        rows.append({"model": name, "features": len(subset), "n_development": len(y),
                     "oof_balanced_accuracy_0_5": balanced_accuracy_score(y, prob >= .5),
                     "oof_roc_auc": roc_auc_score(y, prob)})
    rule = x["doomscroller"].eq("Yes").astype(int)
    rows.insert(0, {"model": "doomscroller label rule", "features": 1, "n_development": len(y),
                    "oof_balanced_accuracy_0_5": balanced_accuracy_score(y, rule),
                    "oof_roc_auc": roc_auc_score(y, rule)})
    rows.insert(0, {"model": "majority class", "features": 0, "n_development": len(y),
                    "oof_balanced_accuracy_0_5": balanced_accuracy_score(y, np.zeros(len(y))),
                    "oof_roc_auc": .5})
    result = pd.DataFrame(rows)
    result.to_csv(ROOT / "outputs/tables/development_baselines_ablations.csv", index=False)
    assert full_probability is not None
    rule_probability = rule.to_numpy(dtype=float)
    truth = y.to_numpy()
    positive = np.flatnonzero(truth == 1)
    negative = np.flatnonzero(truth == 0)
    rng = np.random.default_rng(42)
    differences = []
    for _ in range(3000):
        sample = np.concatenate([
            rng.choice(positive, len(positive), replace=True),
            rng.choice(negative, len(negative), replace=True),
        ])
        differences.append({
            "balanced_accuracy": balanced_accuracy_score(truth[sample], full_probability[sample] >= .5)
            - balanced_accuracy_score(truth[sample], rule_probability[sample] >= .5),
            "roc_auc": roc_auc_score(truth[sample], full_probability[sample])
            - roc_auc_score(truth[sample], rule_probability[sample]),
        })
    frame = pd.DataFrame(differences)
    comparison = {
        "population": "750 development records; paired stratified bootstrap of fixed 5-fold OOF predictions",
        "settings": "Untuned logistic regression at threshold 0.5 versus deterministic doomscroller label rule",
        "balanced_accuracy_difference_full_minus_rule": float(
            balanced_accuracy_score(truth, full_probability >= .5)
            - balanced_accuracy_score(truth, rule_probability >= .5)
        ),
        "balanced_accuracy_difference_95_ci": frame.balanced_accuracy.quantile([.025, .975]).tolist(),
        "roc_auc_difference_full_minus_rule": float(
            roc_auc_score(truth, full_probability) - roc_auc_score(truth, rule_probability)
        ),
        "roc_auc_difference_95_ci": frame.roc_auc.quantile([.025, .975]).tolist(),
        "boundary": "Same development rows and folds; does not establish prospective or external generalization. Compared models differ from tuned/calibrated production model.",
    }
    (ROOT / "outputs/tables/development_paired_comparison.json").write_text(
        json.dumps(comparison, indent=2), encoding="utf-8"
    )
    print(result.to_string(index=False))
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
