import plotly.express as px
import streamlit as st

from night_signals.config import OUTCOME_COLUMNS
from night_signals.data import apply_filters, load_survey
from night_signals.statistics import association_matrix, exposure_gradient
from night_signals.ui import cohort_filter_bar, footer, page_intro
from night_signals.viz import correlation_heatmap, exposure_outcome_chart

page_intro(
    "Associations and exposure gradients",
    "A descriptive view of monotonic associations and mean outcome differences across bedtime-screen exposure quartiles.",
    ":material/query_stats:",
)
cohort_filter_bar()

df = apply_filters(load_survey(), st.session_state.get("global_gender"), st.session_state.get("global_occupation"), st.session_state.get("global_exposure"))
outcome = st.segmented_control(
    "Outcome",
    OUTCOME_COLUMNS,
    format_func=lambda value: value.replace("_", " ").capitalize(),
    key="association_outcome",
    bind="query-params",
) or OUTCOME_COLUMNS[0]

gradient = exposure_gradient(df)
left, right = st.columns([1.15, 0.85])
with left.container(border=True, height="stretch"):
    st.subheader("Dose-shaped view", icon=":material/ssid_chart:")
    st.plotly_chart(exposure_outcome_chart(gradient, outcome), alt=f"Mean {outcome.replace('_', ' ')} with 95 percent confidence intervals by exposure quartile", config={"displaylogo": False, "responsive": True})
with right.container(border=True, height="stretch"):
    st.subheader("What this means", icon=":material/info:")
    st.write("Each point is a group mean; whiskers are 95% confidence intervals. This is an association display, not a causal dose-response estimate.")
    st.metric("Rows in view", f"{len(df):,}", border=True)
    st.metric("Quartiles represented", f"{df['exposure_quartile'].nunique():,}", border=True)

associations = association_matrix(df)
st.subheader("Spearman association map", icon=":material/grid_on:")
st.plotly_chart(correlation_heatmap(associations), alt="Spearman correlations between digital-behaviour exposures and sleep outcomes", config={"displaylogo": False})
st.dataframe(associations.sort_values("p_fdr_bh"), hide_index=True, alt="Exposure and sleep-outcome associations with false-discovery-rate adjusted p-values")
footer()
