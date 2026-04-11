"""components/navbar.py — Navigazione mobile a 7 pagine"""
import streamlit as st

PAGES = [
    ("🏠", "Home",      "home"),
    ("🌍", "Macro",     "macro"),
    ("📊", "Settori",   "sectors"),
    ("🔍", "Screening", "screening"),
    ("🎯", "FairValue", "fairvalue"),
    ("🔥", "Heatmap",   "heatmap"),
    ("📅", "Calendario","calendar"),
]

def render():
    cur  = st.session_state.get("page","home")
    rdy  = st.session_state.get("regime") is not None
    cols = st.columns(len(PAGES))
    for col,(icon,label,pg) in zip(cols, PAGES):
        enabled = True if pg in ("home","macro") else rdy
        with col:
            if st.button(
                f"{icon}\n{label}",
                key=f"nav_{pg}",
                use_container_width=True,
                disabled=not enabled,
                type="primary" if cur==pg else "secondary",
            ):
                st.session_state.page = pg
                st.rerun()
    st.markdown(
        "<hr style='border:none;border-top:1px solid #e5e7eb;margin:4px 0 16px'>",
        unsafe_allow_html=True,
    )
