import plotly.express as px
import streamlit as st

from night_signals.config import POST_OUTCOME_COLUMNS
from night_signals.config import TABLE_DIR
from night_signals.data import audit_table, load_survey, range_audit, read_json_artifact
from night_signals.ui import footer, page_intro
from night_signals.viz import COLORS, finish

page_intro(
    "Dataset provenance and quality audit",
    "The public synthetic dataset is preserved unchanged; this page documents structure, missingness, ranges, duplicates, target balance, and the variable-level leakage audit.",
    ":material/fact_check:",
)

df = load_survey()
raw_columns = [column for column in df.columns if column not in {"doomscroll_load_minutes", "poor_sleep", "favorable_sleep", "exposure_quartile", "habit_indicator_count", "high_exposure", "resilience_group"}]
raw = df[raw_columns]
audit = audit_table(raw)

with st.container(horizontal=True):
    st.metric("Raw observations", f"{len(raw):,}", border=True)
    st.metric("Raw variables", f"{raw.shape[1]:,}", border=True)
    st.metric("Missing cells", f"{int(raw.isna().sum().sum()):,}", border=True)
    st.metric("Duplicate rows", f"{int(raw.duplicated().sum()):,}", border=True)
    st.metric("Unique respondent IDs", f"{raw['respondent_id'].nunique():,}", border=True)

left, right = st.columns([1.15, 0.85])
with left.container(border=True, height="stretch"):
    st.subheader("Missingness by variable", icon=":material/grid_view:")
    missing = audit[audit["missing_n"] > 0].sort_values("missing_pct")
    fig = px.bar(
        missing,
        x="missing_pct",
        y="variable",
        orientation="h",
        color="missing_pct",
        color_continuous_scale=["#31445e", "#f6c177"],
        labels={"missing_pct": "Missing (%)", "variable": "Variable"},
    )
    st.plotly_chart(finish(fig, 390), alt="Percentage missing by survey variable", config={"displaylogo": False})

with right.container(border=True, height="stretch"):
    st.subheader("Target class distribution", icon=":material/donut_large:")
    counts = raw["sleep_quality_category"].value_counts().rename_axis("category").reset_index(name="count")
    fig = px.pie(counts, names="category", values="count", hole=.62, color_discrete_sequence=COLORS)
    st.plotly_chart(finish(fig, 390), alt="Distribution of good, fair, and poor sleep quality categories", config={"displaylogo": False})

st.subheader("Variable audit", icon=":material/table_chart:")
st.dataframe(
    audit,
    hide_index=True,
    alt="Variable types, missingness, and unique-value counts for the primary synthetic file",
    column_config={
        "missing_pct": st.column_config.ProgressColumn("Missing", min_value=0, max_value=100, format="%.1f%%"),
        "missing_n": st.column_config.NumberColumn("Missing n", format="%d"),
        "unique_n": st.column_config.NumberColumn("Unique n", format="%d"),
    },
)

st.subheader("Prediction-time leakage audit", icon=":material/verified_user:")
leakage = []
for column in raw.columns:
    if column in POST_OUTCOME_COLUMNS:
        leakage.append({"variable": column, "prediction use": "Excluded", "reason": "Outcome, post-outcome, identifier, or target field"})
    else:
        leakage.append({"variable": column, "prediction use": "Timing unverified", "reason": "The cross-sectional source supplies no observation timestamp or questionnaire wording"})
st.dataframe(leakage, hide_index=True, alt="Variable-level leakage audit for poor-sleep prediction")

st.subheader("Range and outlier audit", icon=":material/rule:")
st.caption("Bounds are semantic plausibility checks. Out-of-range values are reported for investigation and are not silently removed.")
st.dataframe(range_audit(raw), hide_index=True, alt="Semantic range checks for numeric survey variables")

target_check = read_json_artifact(TABLE_DIR / "target_sensitivity.json")
with st.container(border=True):
    st.subheader("Target validity sensitivity", icon=":material/fact_check:")
    st.metric("Label versus score-proxy agreement", f"{target_check['agreement']:.1%}", border=True)
    st.caption(f"{target_check['n_complete_score']} records have a numeric score. {target_check['note']} The category-generation rule is unavailable; this check cannot decide which field is correct.")

with st.container(border=True):
    st.subheader("Provenance statement", icon=":material/source:")
    st.markdown(
        """
        - **Primary:** *Sleep and Doomscrolling Habits Dataset*, Kaggle, dataset author Harpartap Singh; 1,000 public rows.
        - **Design:** the uploader describes the records as synthetic. This project did not conduct a survey.
        - **Unresolved:** exact generation procedure, source revision, item wording, and predictor timing.
        - **Interpretation:** associations and model scores describe this file, not a sampled population.
        """
    )
footer()
