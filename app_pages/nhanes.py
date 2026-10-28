import plotly.express as px
import streamlit as st

from night_signals.config import OUTPUT_DIR
from night_signals.data import read_json_artifact
from night_signals.ui import footer, page_intro

page_intro("NHANES independent evidence", "A separately analysed population-health layer. It is not linked or row-merged with the primary survey.", ":material/public:")
summary = read_json_artifact(OUTPUT_DIR / "tables" / "nhanes_summary.json")
with st.container(horizontal=True):
    st.metric("Analytic adults", f"{summary['analytic_adults']:,}", border=True)
    st.metric("Short-sleep systolic difference", f"{summary['B1_sleep_blood_pressure']['systolic_diff_short_minus_adequate']:.1f} mmHg", border=True)
    st.metric("Short-sleep diastolic difference", f"{summary['B1_sleep_blood_pressure']['diastolic_diff_short_minus_adequate']:.2f} mmHg", border=True)
    st.metric("BMI–sleep Spearman rho", f"{summary['B2_sleep_by_bmi']['spearman_bmi_vs_sleep']:.2f}", border=True)

left, right = st.columns(2)
with left.container(border=True):
    fig = px.bar(summary["B2_sleep_by_bmi"]["categories"], x="bmi_category", y="mean_sleep_hours", error_y="sd_sleep_hours", labels={"bmi_category": "BMI category", "mean_sleep_hours": "Mean sleep (hours)"})
    st.plotly_chart(fig, alt="Mean sleep hours by BMI category in NHANES", config={"displaylogo": False})
with right.container(border=True):
    fig = px.bar(summary["B3_sleep_by_activity"]["active_groups"], x="activity_group", y="mean_sleep_hours", labels={"activity_group": "Activity group", "mean_sleep_hours": "Mean sleep (hours)"})
    st.plotly_chart(fig, alt="Mean sleep hours by activity group in NHANES", config={"displaylogo": False})
st.warning(summary["note"], title="Interpretation boundary", icon=":material/warning:")
footer()
