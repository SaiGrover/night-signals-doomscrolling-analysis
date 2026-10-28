import plotly.express as px
import streamlit as st

from night_signals.config import OUTPUT_DIR
from night_signals.data import read_json_artifact
from night_signals.ui import footer, page_intro

page_intro("PhysioNet physiological evidence", "Wearable heart-rate dynamics across PSG-scored sleep stages, analysed as an independent evidence layer.", ":material/ecg_heart:")
summary = read_json_artifact(OUTPUT_DIR / "tables" / "physionet_summary.json")
with st.container(horizontal=True):
    st.metric("Subjects analysed", f"{summary['subjects_analysed']:,}", border=True)
    st.metric("Scored epochs", f"{summary['total_scored_epochs']:,}", border=True)
    st.metric("Wake minus deep HR", f"{summary['wake_minus_deep_hr']:.1f} bpm", border=True)
    st.metric("Median awakenings", f"{summary['median_awakenings_after_onset']:,}", border=True)

left, right = st.columns(2)
with left.container(border=True):
    fig = px.bar(summary["hr_by_stage"], x="stage_name", y="mean_hr", error_y="mean_hr_variability", labels={"stage_name": "Sleep stage", "mean_hr": "Mean heart rate (bpm)"})
    st.plotly_chart(fig, alt="Mean heart rate and variability by sleep stage", config={"displaylogo": False})
with right.container(border=True):
    composition = [{"stage": key, "share": value} for key, value in summary["mean_stage_composition_pct"].items()]
    fig = px.bar(composition, x="stage", y="share", labels={"stage": "Sleep stage", "share": "Scored epochs (%)"})
    st.plotly_chart(fig, alt="Mean composition of scored sleep stages", config={"displaylogo": False})
st.warning(summary["note"], title="Interpretation boundary", icon=":material/warning:")
multi = summary.get("multi_night_dataset", {})
with st.container(border=True):
    st.subheader("Multi-night evidence layer", icon=":material/timeline:")
    st.write(
        f"{multi.get('name', 'Specified multi-night PhysioNet dataset')} is registered as an independent source "
        f"({multi.get('expected_subjects', 47)} adults / {multi.get('expected_nights', 253)} nights). "
        "Raw files are intentionally not bundled because the source is multi-gigabyte; the local reproducible "
        "pipeline is available in `scripts/build_bidsleep_evidence.py`."
    )
    st.link_button("Open PhysioNet source", multi.get("physionet_url", "https://physionet.org/content/bidsleep-dataset/1.0.0/"), icon=":material/open_in_new:")
footer()
