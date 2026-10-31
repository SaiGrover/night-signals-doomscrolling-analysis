import streamlit as st

from night_signals.config import MODEL_SUMMARY
from night_signals.data import read_csv_artifact, read_json_artifact
from night_signals.modeling import load_portable_model, predict_probability, risk_band
from night_signals.ui import footer, page_intro
from night_signals.viz import model_comparison_chart, model_evaluation_dashboard

page_intro("Predictive modeling", "An internal label-recovery exercise on synthetic records, with outcome-column exclusion, nested validation, calibration, and explicit timing limits.", ":material/model_training:")
summary = read_json_artifact(MODEL_SUMMARY)
with st.container(horizontal=True):
    st.metric("Nested-CV balanced accuracy", f"{summary['nested_cv']['balanced_accuracy']:.1%}", border=True)
    st.metric("Historical holdout ROC AUC", f"{summary['holdout']['roc_auc']:.3f}", border=True)
    st.metric("Holdout balanced accuracy", f"{summary['holdout']['balanced_accuracy']:.1%}", border=True)
    st.metric("Decision threshold", f"{summary['decision_threshold']:.2f}", border=True)

comparison = read_csv_artifact("production_model_comparison.csv")
st.plotly_chart(model_comparison_chart(comparison), alt="Nested cross-validation comparison of candidate models", config={"displaylogo": False})
st.subheader("Simple baselines and feature ablations", icon=":material/compare:")
st.caption("Development rows only. Five-fold out-of-fold logistic comparisons use a fixed 0.5 threshold without tuning or calibration; they are diagnostic and not directly equivalent to the production nested-CV score.")
st.dataframe(read_csv_artifact("development_baselines_ablations.csv"), hide_index=True, alt="Majority and doomscroller-rule baselines compared with reduced and full logistic feature sets")

st.subheader("Interactive holdout diagnostics", icon=":material/insights:")
calibration = read_csv_artifact("production_calibration.csv")
roc = read_csv_artifact("production_roc_curve.csv")
precision_recall = read_csv_artifact("production_pr_curve.csv")
importance = read_csv_artifact("production_feature_importance.csv")
st.plotly_chart(
    model_evaluation_dashboard(
        calibration,
        roc,
        precision_recall,
        importance,
        summary["holdout"]["roc_auc"],
        summary["holdout"]["pr_auc"],
    ),
    alt="Interactive holdout calibration, ROC, precision-recall, and feature-importance diagnostics",
    config={"displaylogo": False, "responsive": True},
)
st.caption("Panels use saved historical holdout predictions. Earlier experiments may have accessed overlapping rows, so prospective holdout independence cannot be claimed.")
calibration_fit = read_json_artifact(MODEL_SUMMARY.parent / "holdout_calibration_slope.json")
st.caption(
    f"Retrospective calibration: intercept {calibration_fit['calibration_intercept']:.2f} "
    f"(95% CI {calibration_fit['calibration_intercept_95_ci'][0]:.2f} to {calibration_fit['calibration_intercept_95_ci'][1]:.2f}); "
    f"slope {calibration_fit['calibration_slope']:.2f} "
    f"(95% CI {calibration_fit['calibration_slope_95_ci'][0]:.2f} to {calibration_fit['calibration_slope_95_ci'][1]:.2f})."
)

with st.container(border=True):
    st.subheader("Subgroup audit", icon=":material/group:")
    subgroup = read_csv_artifact("subgroup_performance.csv")
    st.dataframe(subgroup[["attribute", "group", "n", "balanced_accuracy", "sensitivity", "specificity"]], hide_index=True, alt="Holdout performance by subgroup")

with st.container(border=True):
    st.subheader("Holdout decision audit", icon=":material/table_chart:")
    holdout = read_csv_artifact("production_holdout_predictions.csv")
    confusion = holdout.groupby(["y_true", "prediction"]).size().unstack(fill_value=0)
    confusion = confusion.reindex(index=[0, 1], columns=[0, 1], fill_value=0)
    confusion.index = ["Actual good", "Actual poor"]
    confusion.columns = ["Predicted good", "Predicted poor"]
    st.dataframe(confusion, alt="Confusion matrix for the untouched holdout")
    odds = read_csv_artifact("primary_model_odds_ratios.csv")
    st.caption("Logistic-model odds ratios are descriptive feature associations within the fitted model; they are not causal effects.")
    st.dataframe(odds[["feature_label", "odds_ratio", "direction"]].head(12), hide_index=True, alt="Primary logistic model odds ratios")

st.subheader("Transparent risk demo", icon=":material/insights:")
st.caption("This is recovery of a synthetic-file label, not a diagnosis or recommendation. The source does not establish when inputs were observed.")
model = load_portable_model()
defaults = model["defaults"]
categories = model["categories"]
with st.form("risk_demo", border=True):
    numeric = {}
    numeric_names = ["age", "bedtime_screen_time_minutes", "total_daily_screen_time_hours", "doomscroll_sessions_per_night", "avg_doomscroll_session_minutes", "anxiety_score", "stress_score", "phone_checks_per_night", "exercise_minutes_per_day", "days_since_last_digital_detox"]
    cols = st.columns(2)
    for index, name in enumerate(numeric_names):
        bounds = model["ranges"][name]
        step = 0.1 if "hours" in name else 1.0
        with cols[index % 2]:
            numeric[name] = st.number_input(name.replace("_", " ").capitalize(), min_value=float(bounds["min"]), max_value=float(bounds["max"]), value=float(defaults[name]), step=step)
    categorical = {}
    for index, name in enumerate(categories):
        with cols[index % 2]:
            categorical[name] = st.selectbox(name.replace("_", " ").capitalize(), categories[name], index=categories[name].index(defaults[name]))
    submitted = st.form_submit_button("Estimate model risk", type="primary", icon=":material/analytics:")

if submitted:
    probability, warnings = predict_probability({**numeric, **categorical}, model)
    with st.container(border=True):
        st.metric("Estimated probability", f"{probability:.1%}", border=True)
        st.write(risk_band(probability))
        st.caption(f"Threshold used for the published classifier: {model['threshold']:.2f}")
        for warning in warnings:
            st.warning(warning, icon=":material/warning:")
st.warning("The model has internal validation only and requires independent validation before any real-world use.", title="Model boundary", icon=":material/verified_user:")
footer()
