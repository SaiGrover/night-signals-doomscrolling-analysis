import streamlit as st

from night_signals.ui import cinematic_media, footer

st.html("""
<style>
  [data-testid="stSidebar"] { display: none; }
  [data-testid="stMainBlockContainer"] { max-width: 1680px; padding-top: 1.35rem; }
  [data-testid="stHeader"] { background: transparent; }
</style>
""")

with st.container(horizontal=True, gap="large", vertical_alignment="center"):
    with st.container():
        cinematic_media(large=True)
    with st.container():
        st.html('<div class="ns-landing-kicker">[ evidence entry ]</div>')
        st.html('<div class="ns-landing-title">Night<br><em>Signals</em></div>')
        st.html('<div class="ns-landing-tagline">Your sleep, translated into the signal behind the scroll. An evidence-led atlas of nighttime digital behaviour, sleep quality, resilience, and independent health signals.</div>')
        st.html('<div class="ns-landing-stat">1,000 respondents <span>/</span> 29 analytic variables</div>')
        st.html('<div class="ns-landing-rule"></div>')
        with st.container(horizontal=True, gap="small"):
            if st.button("Proceed to analysis", type="primary", icon=":material/arrow_forward:", width="stretch"):
                st.switch_page("app_pages/overview.py")
            if st.button("Access methodology", icon=":material/menu_book:", width="stretch"):
                st.switch_page("app_pages/workflow.py")
        st.html('<div class="ns-landing-footnote">Self-reported survey · observational analysis · no causal or clinical claims</div>')

footer()
