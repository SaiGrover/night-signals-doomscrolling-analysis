import pandas as pd
import plotly.express as px
import streamlit as st

from night_signals.data import apply_filters, load_summaries, load_survey
from night_signals.statistics import exposure_gradient
from night_signals.ui import cohort_filter_bar, evidence_note, footer, hero
from night_signals.viz import COLORS, exposure_outcome_chart, finish

hero(
    "Night Signals · Research atlas",
    "What happens after the screen should have gone dark?",
    "A multi-dataset investigation of nighttime digital behaviour, sleep outcomes, resilient exceptions, and objective health signals. The atlas separates observed association, prediction, and external evidence by design.",
)

st.html('<div class="ns-section-kicker">Dashboard / primary survey</div>')
cohort_filter_bar()

df = apply_filters(
    load_survey(),
    st.session_state.get("global_gender"),
    st.session_state.get("global_occupation"),
    st.session_state.get("global_exposure"),
)
analysis, model = load_summaries()

with st.container(horizontal=True):
    st.metric("Respondents in view", f"{len(df):,}", border=True, chart_data=df.groupby("exposure_quartile", observed=True).size().tolist())
    st.metric("Poor-sleep prevalence", f"{df['poor_sleep'].mean():.1%}", border=True)
    st.metric("Median bedtime exposure", f"{df['bedtime_screen_time_minutes'].median():.0f} min", border=True)
    st.metric("High-exposure exceptions", f"{int((df['high_exposure'] & df['favorable_sleep']).sum())}", border=True)
    st.metric("Holdout ROC AUC", f"{model['holdout']['roc_auc']:.3f}", border=True)

evidence_note(
    "Primary evidence: a 1,000-row public Kaggle survey with incompletely documented sampling and collection methods. External NHANES and PhysioNet analyses are independent evidence layers and are never row-merged with survey respondents."
)

left, right = st.columns([1.15, 0.85])
with left.container(border=True, height="stretch"):
    st.subheader("Exposure gradient", icon=":material/ssid_chart:")
    outcome = st.segmented_control(
        "Sleep outcome",
        ["sleep_latency_minutes", "weekly_sleep_debt_hours", "sleep_hours_per_night"],
        format_func=lambda value: value.replace("_", " ").capitalize(),
        key="overview_outcome",
        bind="query-params",
    ) or "sleep_latency_minutes"
    gradient = exposure_gradient(df)
    st.plotly_chart(
        exposure_outcome_chart(gradient, outcome),
        alt=f"Mean {outcome.replace('_', ' ')} with 95 percent confidence intervals across bedtime screen exposure quartiles",
        config={"displaylogo": False, "responsive": True},
    )

with right.container(border=True, height="stretch"):
    st.subheader("Sleep outcome profile", icon=":material/bedroom_parent:")
    grouped = (
        df.groupby("sleep_quality_category", observed=True)[
            ["sleep_latency_minutes", "weekly_sleep_debt_hours", "daytime_fatigue_score"]
        ]
        .mean()
        .reset_index()
    )
    long = grouped.melt(id_vars="sleep_quality_category", var_name="outcome", value_name="mean")
    fig = px.bar(
        long,
        x="sleep_quality_category",
        y="mean",
        color="outcome",
        barmode="group",
        color_discrete_sequence=COLORS,
        labels={"sleep_quality_category": "Sleep quality", "mean": "Group mean", "outcome": "Outcome"},
    )
    st.plotly_chart(
        finish(fig),
        alt="Mean sleep latency, weekly sleep debt, and fatigue by sleep quality category",
        config={"displaylogo": False},
    )

st.html('<div class="ns-section-kicker">The research frame</div>')
st.subheader("Five research questions", icon=":material/quiz:")
questions = [
    ("RQ1 · Association", "How are nighttime screen exposure and doomscrolling associated with duration, latency, awakenings, debt, and fatigue?"),
    ("RQ2 · Exposure gradient", "Do sleep outcomes differ systematically across increasing exposure levels?"),
    ("RQ3 · Resilience", "What distinguishes high-exposure respondents with comparatively favorable sleep?"),
    ("RQ4 · Prediction", "Can pre-outcome variables estimate poor-sleep risk without leakage and with useful calibration?"),
    ("RQ5 · External evidence", "What independent population-health and physiological patterns appear in NHANES and PhysioNet?"),
]
for column, (title, body) in zip(st.columns(5, border=True), questions):
    with column:
        st.markdown(f"**{title}**")
        st.caption(body)

st.warning(
    "The primary survey is cross-sectional and self-reported. The dashboard does not establish causality, diagnose a sleep disorder, or provide personal medical advice.",
    title="Interpretation boundary",
    icon=":material/warning:",
)

st.html('<div class="ns-section-kicker">A second look at the signal</div>')
st.subheader("Exposure distribution and protective context", icon=":material/insights:")
left, right = st.columns(2)
with left.container(border=True, height="stretch"):
    distribution = px.histogram(
        df,
        x="doomscroll_load_minutes",
        color="sleep_quality_category",
        nbins=28,
        marginal="box",
        color_discrete_sequence=COLORS,
        labels={"doomscroll_load_minutes": "Nightly doomscroll load (minutes)", "sleep_quality_category": "Sleep quality"},
    )
    st.plotly_chart(distribution, alt="Distribution of nightly doomscroll load by sleep quality", config={"displaylogo": False, "responsive": True})
with right.container(border=True, height="stretch"):
    protective = df.groupby("sleep_quality_category", observed=True)["protective_habit_count"].mean().reset_index()
    protective_fig = px.bar(
        protective,
        x="sleep_quality_category",
        y="protective_habit_count",
        color="sleep_quality_category",
        color_discrete_sequence=COLORS,
        labels={"sleep_quality_category": "Sleep quality", "protective_habit_count": "Mean protective habits"},
    )
    st.plotly_chart(protective_fig, alt="Mean protective habit count by sleep quality category", config={"displaylogo": False, "responsive": True})
footer()
