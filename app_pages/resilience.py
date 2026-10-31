import plotly.express as px
import streamlit as st

from night_signals.data import apply_filters, load_survey, read_csv_artifact
from night_signals.statistics import resilience_effects
from night_signals.ui import cohort_filter_bar, footer, page_intro

page_intro("Resilience and protective context", "The small high-exposure group with favorable sleep is shown as a counter-pattern, not a clinical phenotype.", ":material/health_and_safety:")
cohort_filter_bar()
df = apply_filters(load_survey(), st.session_state.get("global_gender"), st.session_state.get("global_occupation"), st.session_state.get("global_exposure"))
high = df[df["high_exposure"]]
good = high[high["favorable_sleep"]]
poor = high[high["poor_sleep"]]

with st.container(horizontal=True):
    st.metric("High exposure", f"{len(high):,}", border=True)
    st.metric("Favorable sleep", f"{len(good):,}", border=True)
    st.metric("Poor sleep", f"{len(poor):,}", border=True)
    st.metric("Favorable share", f"{len(good) / len(high):.1%}" if len(high) else "—", border=True)

with st.container(border=True):
    st.subheader("Exploratory behavioral contrasts", icon=":material/compare_arrows:")
    st.caption("Sleep duration, latency, debt and fatigue define or closely track the outcome and are excluded from protective-factor interpretation. Small favorable group; no causal inference.")

test = resilience_effects(df)
st.dataframe(test, hide_index=True, alt="Behavioral contrasts with group sizes and false-discovery-rate adjusted p-values")
st.subheader("Adjusted routine associations", icon=":material/analytics:")
st.caption("Full synthetic file, complete cases; logistic model adjusts for bedtime screen minutes, self-label, news, age, gender and occupation. Odds ratios and intervals describe model fit only. No routine contrast survives FDR correction.")
st.dataframe(read_csv_artifact("adjusted_habit_associations.csv"), hide_index=True, alt="Exploratory adjusted habit odds ratios, confidence intervals and FDR p-values")
st.subheader("Exploratory factor comparison", icon=":material/science:")
fig = px.bar(test, x="cohens_d", y="factor", orientation="h", color="p_fdr_bh", color_continuous_scale=["#f6c177", "#5eead4"], labels={"cohens_d": "Cohen's d", "factor": "Factor", "p_fdr_bh": "FDR-adjusted p"})
st.plotly_chart(fig, alt="Exploratory standardized differences between favorable and poor high-exposure respondents", config={"displaylogo": False})
st.warning("Only a small number of high-exposure respondents report favorable sleep. Estimates are unstable and should motivate follow-up research, not individualized recommendations.", title="Small subgroup boundary", icon=":material/warning:")
footer()
