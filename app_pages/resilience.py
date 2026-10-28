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

effects = read_csv_artifact("exception_effect_sizes.csv")
with st.container(border=True):
    st.subheader("High-exposure exception profile", icon=":material/compare_arrows:")
    st.dataframe(effects, hide_index=True, alt="Effect sizes comparing favorable and poor sleepers within the high-exposure group")

test = resilience_effects(df)
st.subheader("Exploratory factor comparison", icon=":material/science:")
fig = px.bar(test, x="cohens_d", y="factor", orientation="h", color="p_fdr_bh", color_continuous_scale=["#f6c177", "#5eead4"], labels={"cohens_d": "Cohen's d", "factor": "Factor", "p_fdr_bh": "FDR-adjusted p"})
st.plotly_chart(fig, alt="Exploratory standardized differences between favorable and poor high-exposure respondents", config={"displaylogo": False})
st.warning("Only a small number of high-exposure respondents report favorable sleep. Estimates are unstable and should motivate follow-up research, not individualized recommendations.", title="Small subgroup boundary", icon=":material/warning:")
footer()
