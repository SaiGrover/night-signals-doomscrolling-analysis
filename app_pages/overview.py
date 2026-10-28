import plotly.express as px
import streamlit as st

from night_signals.data import apply_filters, load_survey
from night_signals.ui import cohort_filter_bar, footer, hero
from night_signals.viz import COLORS, finish


hero(
    "Night Signals  ·  Research atlas",
    'What happens after<br>the screen should<br><span class="ns-hero-accent">have gone dark?</span>',
    "A multi-dataset investigation of nighttime digital behaviour, sleep outcomes, resilient exceptions, and objective health signals. The atlas separates observed association, prediction, and external evidence by design.",
    class_name="ns-overview-hero",
)

cohort_filter_bar()

df = apply_filters(
    load_survey(),
    st.session_state.get("global_gender"),
    st.session_state.get("global_occupation"),
    st.session_state.get("global_exposure"),
)
st.html('<div class="ns-section-kicker ns-explore-bar">Explore the data</div>')

with st.container(horizontal=True, gap="small"):
    st.metric(
        "Respondents in view",
        f"{len(df):,}",
        border=True,
        chart_data=df.groupby("exposure_quartile", observed=True).size().tolist(),
    )
    st.metric("Poor-sleep prevalence", f"{df['poor_sleep'].mean():.1%}", border=True)
    st.metric("Median bedtime exposure", f"{df['bedtime_screen_time_minutes'].median():.0f} min", border=True)
    st.metric("High-exposure exceptions", f"{int((df['high_exposure'] & df['favorable_sleep']).sum())}", border=True)

left, middle, right = st.columns([1.08, 1.08, 0.82], gap="small")

with left.container(border=True, height="stretch"):
    st.html('<div class="ns-panel-label">▥ &nbsp; Exposure distribution</div>')
    st.caption("Distribution of nightly screen exposure in the selected cohort.")
    fig = px.histogram(
        df,
        x="bedtime_screen_time_minutes",
        nbins=24,
        color_discrete_sequence=[COLORS[0]],
        labels={"bedtime_screen_time_minutes": "Nightly screen exposure (minutes)", "count": "Respondents"},
    )
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(finish(fig, height=300), width="stretch", config={"displaylogo": False, "responsive": True})

with middle.container(border=True, height="stretch"):
    st.html('<div class="ns-panel-label">◐ &nbsp; Sleep outcomes</div>')
    st.caption("Proportion of poor sleep across exposure quartiles.")
    quartiles = (
        df.groupby("exposure_quartile", observed=True)["poor_sleep"]
        .mean()
        .mul(100)
        .rename("Poor sleep prevalence")
        .reset_index()
    )
    fig = px.bar(
        quartiles,
        x="exposure_quartile",
        y="Poor sleep prevalence",
        color_discrete_sequence=[COLORS[1]],
        labels={"exposure_quartile": "Exposure quartile", "Poor sleep prevalence": "Poor sleep (%)"},
    )
    fig.update_traces(marker_line_width=0, texttemplate="%{y:.1f}%", textposition="outside")
    st.plotly_chart(finish(fig, height=300), width="stretch", config={"displaylogo": False, "responsive": True})

with right:
    st.html(
        '<section class="ns-takeaway"><div class="ns-panel-label">♧ &nbsp; Key takeaway</div>'
        '<p>Higher nighttime screen exposure is associated with worse sleep outcomes, but a subset of individuals show resilience. Exploring behavioural, demographic, and physiological factors helps identify these exceptions.</p></section>'
    )
    if st.button("Explore the analysis  →", type="primary", width="stretch"):
        st.switch_page("app_pages/associations.py")

st.warning(
    "The primary survey is cross-sectional and self-reported. This atlas does not establish causality, diagnose a sleep disorder, or provide personal medical advice.",
    title="Interpretation boundary",
    icon=":material/warning:",
)

footer()
