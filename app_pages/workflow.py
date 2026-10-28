import streamlit as st

from night_signals.config import NOTEBOOK_DIR
from night_signals.ui import footer, page_intro

page_intro("Research workflow", "The dashboard is a read-only presentation layer over validated, versioned analytical artifacts.", ":material/account_tree:")
steps = [
    ("01", "Acquire and audit", "Preserve source files, provenance notes, IDs, missingness, ranges, and data-quality flags."),
    ("02", "Prepare features", "Create exposure measures, protective counts, age groups, and prediction-time eligibility without mutating raw data."),
    ("03", "Describe and test", "Use EDA, confidence intervals, Spearman associations, effect sizes, bootstrap intervals, and FDR correction."),
    ("04", "Validate models", "Keep pre-outcome inputs separate, tune within folds, use nested CV, calibrate, optimize thresholds, and audit subgroups."),
    ("05", "Synthesize evidence", "Keep NHANES and PhysioNet independent; combine interpretation, not respondent rows."),
]
for code, title, body in steps:
    with st.container(border=True):
        st.caption(code)
        st.subheader(title)
        st.write(body)

st.subheader("Executed notebooks", icon=":material/menu_book:")
for path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
    st.caption(path.name)
st.info("The migration includes ten stage-specific research notebooks plus the original executed analysis, modeling, and external-evidence notebooks. Each generated notebook reads the saved project artifacts and keeps interpretation boundaries explicit.", title="Reproducibility note", icon=":material/info:")
footer()
