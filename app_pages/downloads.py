from pathlib import Path
import streamlit as st

from night_signals.config import NOTEBOOK_DIR, PRIMARY_DATA, PROJECT_ROOT
from night_signals.ui import footer, page_intro

page_intro("Downloads and limitations", "Inspect the report, notebooks, tables, and model card that support the atlas.", ":material/download:")

def offer(label: str, path: Path, mime: str, icon: str) -> None:
    if path.exists():
        st.download_button(label, path.read_bytes(), file_name=path.name, mime=mime, width="stretch", icon=icon)
    else:
        st.info(f"Not available in this checkout: {path.name}", icon=":material/info:")

left, right = st.columns(2)
with left.container(border=True):
    st.subheader("Research artifacts", icon=":material/description:")
    offer("Download report", PROJECT_ROOT / "platform" / "deliverables" / "Sleep_Doomscrolling_Report.pdf", "application/pdf", ":material/picture_as_pdf:")
    offer("Download primary survey", PRIMARY_DATA, "text/csv", ":material/table_view:")
with right.container(border=True):
    st.subheader("Methodology", icon=":material/menu_book:")
    for path in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        offer(path.stem.replace("_", " ").title(), path, "application/x-ipynb+json", ":material/code:")

st.subheader("Limitations", icon=":material/warning:")
st.markdown("""
- The primary survey is self-reported and cross-sectional; association is not causation.
- Sampling and recruitment details are incomplete, so population and clinical claims are out of scope.
- Sleep-quality scores show a strong ceiling effect and some exception subgroups are small.
- The model has internal validation only and must not be used for diagnosis, employment, insurance, or automated decisions.
- NHANES and PhysioNet are independent evidence layers, not linked respondent-level validation.
""")
footer()
