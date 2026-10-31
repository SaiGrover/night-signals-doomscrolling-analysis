"""Development-only, fixed 5-fold baseline and feature-ablation comparison.

These are diagnostic comparisons at threshold 0.5, not tuned or nested model
selection estimates. The historical 250-row holdout is never loaded here.
"""
from pathlib import Path

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
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
