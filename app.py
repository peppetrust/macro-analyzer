"""
app.py — Router principale Macro Analyzer v2
Architettura modulare: ogni pagina è un modulo separato
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Macro Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject CSS globale
from components.styles import inject
inject()

# ── Session state defaults ─────────────────────────────────────────────────────
defaults = {
    "page":           "home",
    "country_name":   "🇺🇸 Stati Uniti",
    "cc":             "US",
    "regime":         None,
    "selected_sector":None,
    "years_back":     10,
    "m3_data":        [],
    "m3_sector_loaded":None,
    "m4_loaded":      {},
    "m4_cache_key":   None,
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Routing ───────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    from pages.p5_dashboard import render; render()

elif page == "macro":
    from pages.p1_macro import render; render()

elif page == "sectors":
    from pages.p2_sectors import render; render()

elif page == "screening":
    from pages.p3_screening import render; render()

elif page == "fairvalue":
    from pages.p4_fairvalue import render; render()

elif page == "heatmap":
    from pages.p6_heatmap import render; render()

elif page == "calendar":
    from pages.p7_calendar import render; render()

else:
    st.error(f"Pagina '{page}' non trovata.")
