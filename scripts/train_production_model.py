"""Train and audit the pre-outcome poor-sleep risk model.

The final holdout is split before model comparison. Candidate selection and
hyperparameter tuning happen only inside the development partition.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                             brier_score_loss, confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import (RandomizedSearchCV, StratifiedKFold, cross_val_predict,
                                     cross_validate, train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public/data/sleep_doomscrolling_habits.csv"
OUT = ROOT / "outputs"
TABLES, FIGURES, MODELS = OUT / "tables", OUT / "figures", OUT / "models"
for path in (TABLES, FIGURES, MODELS): path.mkdir(parents=True, exist_ok=True)
RANDOM_STATE = 42
TARGET = "sleep_quality_category"
OUTCOME_OR_POST_SLEEP = {
    "respondent_id", TARGET, "sleep_quality_score", "sleep_hours_per_night",
    "sleep_latency_minutes", "number_of_night_wakeups", "daytime_fatigue_score",
    "weekly_sleep_debt_hours",
}


def metric_row(y_true, probability, threshold=.5):
    pred = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "accuracy": accuracy_score(y_true, pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, pred),
        "roc_auc": roc_auc_score(y_true, probability),
        "pr_auc": average_precision_score(y_true, probability),
        "f1": f1_score(y_true, pred),
        "precision": precision_score(y_true, pred, zero_division=0),
        "sensitivity": recall_score(y_true, pred, zero_division=0),
        "specificity": tn / (tn + fp),
        "brier": brier_score_loss(y_true, probability),
        "false_negatives": int(fn), "false_positives": int(fp),
    }


def bootstrap_ci(y_true, probability, threshold, repeats=1000):
    rng = np.random.default_rng(RANDOM_STATE)
    rows = []
    y_array = np.asarray(y_true)
    for _ in range(repeats):
        idx = rng.integers(0, len(y_array), len(y_array))
        if len(np.unique(y_array[idx])) < 2: continue
        rows.append(metric_row(y_array[idx], probability[idx], threshold))
    frame = pd.DataFrame(rows)
    return {name: {"low": float(frame[name].quantile(.025)), "high": float(frame[name].quantile(.975))}
            for name in ["balanced_accuracy", "roc_auc", "pr_auc", "brier", "sensitivity", "specificity"]}


def main():
    df = pd.read_csv(DATA)
    features = [column for column in df.columns if column not in OUTCOME_OR_POST_SLEEP]
    X, y = df[features].copy(), df[TARGET].eq("Poor").astype(int)
    X_dev, X_holdout, y_dev, y_holdout = train_test_split(
        X, y, test_size=.25, stratify=y, random_state=RANDOM_STATE)
    categorical = X.select_dtypes(exclude=np.number).columns.tolist()
    numeric = [column for column in features if column not in categorical]
    preprocess = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),
                              ("scale", StandardScaler())]), numeric),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    candidates = {
        "Logistic Regression": (LogisticRegression(max_iter=3000, class_weight="balanced", random_state=RANDOM_STATE),
                                {"model__C": np.logspace(-2, 1, 10)}),
        "Random Forest": (RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=1),
                          {"model__n_estimators": [300, 500, 800], "model__max_depth": [None, 6, 10, 14],
                           "model__min_samples_leaf": [1, 2, 4, 8], "model__max_features": ["sqrt", "log2", .7]}),
        "Extra Trees": (ExtraTreesClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=1),
                        {"model__n_estimators": [300, 500, 800], "model__max_depth": [None, 6, 10, 14],
                         "model__min_samples_leaf": [1, 2, 4, 8], "model__max_features": ["sqrt", "log2", .7]}),
        "RBF SVM": (SVC(class_weight="balanced", probability=True, random_state=RANDOM_STATE),
                    {"model__C": [.1, .5, 1, 2, 5, 10], "model__gamma": ["scale", "auto", .01, .03, .1]}),
    }
    outer = StratifiedKFold(5, shuffle=True, random_state=RANDOM_STATE)
    inner = StratifiedKFold(3, shuffle=True, random_state=RANDOM_STATE + 1)
    rows = []
    for index, (name, (model, params)) in enumerate(candidates.items()):
        pipeline = Pipeline([("preprocess", clone(preprocess)), ("model", model)])
        search = RandomizedSearchCV(pipeline, params, n_iter=min(12, int(np.prod([len(v) for v in params.values()]))),
                                    scoring="balanced_accuracy", cv=inner, n_jobs=-1,
                                    random_state=RANDOM_STATE + index, refit=True)
        scores = cross_validate(search, X_dev, y_dev, cv=outer, n_jobs=1,
                                scoring=["accuracy", "balanced_accuracy", "roc_auc", "average_precision", "f1", "neg_brier_score"])
        rows.append({"model": name, **{key.removeprefix("test_"): float(value.mean())
                                      for key, value in scores.items() if key.startswith("test_")},
                     "balanced_accuracy_sd": float(scores["test_balanced_accuracy"].std())})
    comparison = pd.DataFrame(rows).rename(columns={"average_precision": "pr_auc", "neg_brier_score": "neg_brier"})
    comparison["brier"] = -comparison.pop("neg_brier")
    comparison = comparison.sort_values("balanced_accuracy", ascending=False).reset_index(drop=True)
    selected_name = comparison.iloc[0].model
    selected_model, selected_params = candidates[selected_name]
    selected_pipeline = Pipeline([("preprocess", clone(preprocess)), ("model", selected_model)])
    final_search = RandomizedSearchCV(selected_pipeline, selected_params,
                                      n_iter=min(20, int(np.prod([len(v) for v in selected_params.values()]))),
                                      scoring="balanced_accuracy", cv=StratifiedKFold(5, shuffle=True, random_state=44),
                                      n_jobs=-1, random_state=45, refit=True).fit(X_dev, y_dev)
    calibrated_template = CalibratedClassifierCV(final_search.best_estimator_, method="sigmoid", cv=5)
    oof_probability = cross_val_predict(calibrated_template, X_dev, y_dev, cv=outer,
                                        method="predict_proba", n_jobs=1)[:, 1]
    thresholds = np.linspace(.15, .75, 121)
    costs = []
    for threshold in thresholds:
        tn, fp, fn, tp = confusion_matrix(y_dev, oof_probability >= threshold, labels=[0, 1]).ravel()
        costs.append(2 * fn + fp)
    threshold = float(thresholds[int(np.argmin(costs))])
    calibrated = clone(calibrated_template).fit(X_dev, y_dev)
    holdout_probability = calibrated.predict_proba(X_holdout)[:, 1]
    holdout = metric_row(y_holdout, holdout_probability, threshold)
    intervals = bootstrap_ci(y_holdout, holdout_probability, threshold)

    subgroup_rows = []
    audit = X_holdout.copy()
    audit["age_group"] = pd.cut(audit.age, [-np.inf, 19, 29, np.inf], labels=["15–19", "20–29", "30+"])
    audit["truth"], audit["probability"] = y_holdout.values, holdout_probability
    for attribute in ["gender", "age_group", "occupation_status", "country_region"]:
        for group, part in audit.groupby(attribute, observed=True):
            if len(part) < 15 or part.truth.nunique() < 2: continue
            subgroup_rows.append({"attribute": attribute, "group": str(group), "n": len(part),
                                  **metric_row(part.truth, part.probability, threshold)})
    fairness = pd.DataFrame(subgroup_rows)

    calibrated.fit(X_dev, y_dev)
    result = permutation_importance(calibrated, X_holdout, y_holdout, scoring="balanced_accuracy",
                                    n_repeats=30, random_state=RANDOM_STATE, n_jobs=-1)
    importance = pd.DataFrame({"feature": features, "importance": result.importances_mean,
                               "sd": result.importances_std}).sort_values("importance", ascending=False)
    comparison.to_csv(TABLES / "production_model_comparison.csv", index=False)
    fairness.to_csv(TABLES / "subgroup_performance.csv", index=False)
    fairness.to_csv(ROOT / "public/data/subgroup_performance.csv", index=False)
    importance.to_csv(TABLES / "production_feature_importance.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
    axes[0].barh(comparison.model[::-1], comparison.balanced_accuracy[::-1], color="#b99aff")
    axes[0].axvline(.5, color="#888", ls="--"); axes[0].set(xlim=(0, 1), title="Nested CV on development data", xlabel="Balanced accuracy")
    observed, predicted = calibration_curve(y_holdout, holdout_probability, n_bins=7, strategy="quantile")
    axes[1].plot([0, 1], [0, 1], "--", color="#888"); axes[1].plot(predicted, observed, "o-", color="#56d0df")
    axes[1].set(xlim=(0, 1), ylim=(0, 1), title="Untouched-holdout calibration", xlabel="Predicted risk", ylabel="Observed rate")
    top = importance.head(10).sort_values("importance")
    axes[2].barh(top.feature, top.importance, xerr=top.sd, color="#7bd4b8")
    axes[2].set_title("Primary-model permutation importance")
    fig.tight_layout(); fig.savefig(FIGURES / "15_production_risk_model.png", dpi=170, bbox_inches="tight"); plt.close(fig)
    plot_path = ROOT / "public/data/plotly_charts.json"
    plot_specs = json.loads(plot_path.read_text(encoding="utf-8-sig"))
    plot_specs["15_production_risk_model.png"] = {
        "data": [
            {"type": "bar", "name": "Balanced accuracy", "x": comparison.model.tolist(), "y": comparison.balanced_accuracy.tolist(), "marker": {"color": "#b99aff"}},
            {"type": "bar", "name": "ROC AUC", "x": comparison.model.tolist(), "y": comparison.roc_auc.tolist(), "marker": {"color": "#56d0df"}},
            {"type": "bar", "name": "PR AUC", "x": comparison.model.tolist(), "y": comparison.pr_auc.tolist(), "marker": {"color": "#7bd4b8"}},
        ],
        "layout": {"barmode": "group", "title": {"text": "Development-only nested cross-validation"},
                   "yaxis": {"range": [0, 1], "title": {"text": "Cross-validated score"}},
                   "xaxis": {"tickangle": -12}, "legend": {"orientation": "h", "y": 1.13}}
    }
    plot_specs.pop("15_binary_risk_model.png", None)
    plot_path.write_text(json.dumps(plot_specs, separators=(",", ":")), encoding="utf-8")

    defaults = {column: (float(df[column].median()) if column in numeric else str(df[column].mode().iloc[0])) for column in features}
    ranges = {column: {"min": float(df[column].min()), "max": float(df[column].max())} for column in numeric}
    categories = {column: sorted(map(str, df[column].dropna().unique())) for column in categorical}
    drift_baseline = {
        "numeric": {column: {"mean": float(df[column].mean()), "sd": float(df[column].std())} for column in numeric},
        "categorical": {column: df[column].astype(str).value_counts(normalize=True).to_dict() for column in categorical},
        "policy": "Warn when a numeric input is more than 3 training standard deviations from the mean or a category was unseen. Aggregate production monitoring still requires a persistent event store."
    }
    version = "2.0.0"
    artifact = MODELS / "poor_sleep_preoutcome_model.joblib"
    joblib.dump({"model": calibrated, "threshold": threshold, "features": features,
                 "defaults": defaults, "ranges": ranges, "categories": categories,
                 "drift_baseline": drift_baseline, "version": version}, artifact, compress=3)
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    summary = {"model_version": version, "selected_model": selected_name,
               "prediction_moment": "At bedtime, before sleep outcomes occur",
               "development_rows": len(X_dev), "untouched_holdout_rows": len(X_holdout),
               "positive_prevalence": float(y.mean()), "majority_baseline_accuracy": float(1-y.mean()),
               "nested_cv": comparison.iloc[0].to_dict(), "decision_threshold": threshold,
               "false_negative_cost": 2, "holdout": holdout, "holdout_95_ci": intervals,
               "external_validation": "Not performed — independent real-world data required",
               "excluded_post_outcome_features": sorted(OUTCOME_OR_POST_SLEEP),
               "artifact_sha256": digest}
    (TABLES / "production_model_summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    (ROOT / "public/data/model_registry.json").write_text(json.dumps({"active": version, "models": [{"version": version,
        "status": "internal-validation-only", "artifact_sha256": digest, "metrics": holdout,
        "trained_on": "synthetic survey; n=750 development", "external_validation": False}]}, indent=2), encoding="utf-8")
    (ROOT / "public/data/prediction_schema.json").write_text(json.dumps({"version": version, "features": features,
        "defaults": defaults, "ranges": ranges, "categories": categories,
        "drift_baseline": drift_baseline}, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2, default=float))


if __name__ == "__main__": main()
