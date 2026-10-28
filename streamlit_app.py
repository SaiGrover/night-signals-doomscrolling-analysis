import streamlit as st

from night_signals.data import load_survey
from night_signals.ui import inject_brand_surface

st.set_page_config(
    page_title="Night Signals research atlas",
    page_icon=":material/bedtime:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.session_state.setdefault("filters_enabled", True)
st.session_state.setdefault("selected_outcome", "sleep_latency_minutes")

inject_brand_surface()

pages = {
    "": [
        st.Page("app_pages/overview.py", title="Overview", icon=":material/bedtime:", default=True),
    ],
    "Start here": [
        st.Page("app_pages/landing.py", title="Landing page", icon=":material/auto_awesome:"),
    ],
    "Research atlas": [
        st.Page("app_pages/data_audit.py", title="Data audit", icon=":material/fact_check:"),
        st.Page("app_pages/associations.py", title="Associations & gradients", icon=":material/query_stats:"),
        st.Page("app_pages/resilience.py", title="Resilience", icon=":material/health_and_safety:"),
        st.Page("app_pages/modeling.py", title="Predictive modeling", icon=":material/model_training:"),
    ],
    "Independent evidence": [
        st.Page("app_pages/nhanes.py", title="NHANES", icon=":material/public:"),
        st.Page("app_pages/physionet.py", title="PhysioNet", icon=":material/ecg_heart:"),
    ],
    "Reproducibility": [
        st.Page("app_pages/workflow.py", title="Research workflow", icon=":material/account_tree:"),
        st.Page("app_pages/notebooks.py", title="Notebook studio", icon=":material/menu_book:"),
        st.Page("app_pages/downloads.py", title="Downloads & limitations", icon=":material/download:"),
    ],
}

with st.sidebar:
    st.html(
        '<div class="ns-sidebar-brand"><span class="ns-topbar-mark">◔</span><span><b>NIGHT SIGNALS</b><small>RESEARCH ATLAS</small></span></div>'
    )
    st.html('<div class="ns-sidebar-rule"></div>')

navigation = st.navigation(pages, position="sidebar")
navigation.run()

with st.sidebar:
    st.html('<div class="ns-sidebar-footer"><div class="ns-sidebar-status"><span class="ns-status-dot"></span><b>Dataset audited</b></div><span>Self-reported survey · 1,000 rows</span><div class="ns-sidebar-foot-rule"></div><b>Survey data</b><span>Descriptive patterns, not medical advice or causal estimates.</span></div>')
