"""pages/p5_dashboard.py — Home Dashboard stile Bloomberg"""
import streamlit as st
import plotly.graph_objects as go
import yfinance as yf, pandas as pd, numpy as np
from datetime import datetime
from components.navbar import render as nav
from components.charts import line_chart, hex_rgba
from data.macro_fetch import get_gdp, get_inf, get_unemp, latest, freshness_badge, classify_regime
from config import COUNTRIES, FALLBACK, CHART_COLORS

# ── Indici globali da monitorare ──────────────────────────────────────────────
INDICES = {
    "S&P 500":   "^GSPC","NASDAQ":    "^IXIC","Euro Stoxx 50":"^STOXX50E",
    "FTSE MIB":  "FTSEMIB.MI","DAX":"^GDAXI","Nikkei 225":"^N225",
    "FTSE 100":  "^FTSE","Shanghai":  "000001.SS","BTC/USD":"BTC-USD",
    "Gold":      "GC=F","Oil (WTI)": "CL=F","EUR/USD":"EURUSD=X",
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_index_data(ticker: str) -> dict:
    try:
        t    = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if hist.empty: return {}
        last  = hist["Close"].iloc[-1]
        prev  = hist["Close"].iloc[-2] if len(hist)>1 else last
        chg   = ((last/prev)-1)*100
        ytd_s = t.history(period="ytd")
        ytd_r = ((ytd_s["Close"].iloc[-1]/ytd_s["Close"].iloc[0])-1)*100 if len(ytd_s)>1 else None
        return {"price":round(last,2),"chg":round(chg,2),"ytd":round(ytd_r,2) if ytd_r else None}
    except: return {}

@st.cache_data(ttl=3600, show_spinner=False)
def fear_greed() -> dict:
    """CNN Fear & Greed Index via API pubblica."""
    try:
        r = __import__("requests").get(
            "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
            timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code!=200: return {}
        d = r.json()
        score = d.get("fear_and_greed",{}).get("score")
        label = d.get("fear_and_greed",{}).get("rating","")
        return {"score":round(float(score),1) if score else None,"label":label}
    except: return {}

def render():
    nav()
    st.markdown("## 🏠 Dashboard — Overview Globale")
    st.markdown(
        f'<div class="label" style="margin-bottom:16px;">AGGIORNATO: {datetime.now().strftime("%d %b %Y %H:%M")}</div>',
        unsafe_allow_html=True)

    cc   = st.session_state.get("cc","US")
    reg  = st.session_state.get("regime")
    name = st.session_state.get("country_name","🇺🇸 Stati Uniti")

    # ── REGIME CORRENTE (se disponibile) ──
    if reg:
        st.markdown('<div class="section">📍 Regime Corrente</div>', unsafe_allow_html=True)
        rc1,rc2 = st.columns([1,2])
        with rc1:
            st.markdown(f'''<div class="card">
                <div class="label">Paese selezionato</div>
                <div style="font-size:18px;font-weight:600;margin:6px 0;">{name}</div>
                <span class="badge {reg['css']}">{reg['icon']} {reg['name']}</span>
                <div style="font-size:12px;color:#6b7280;margin-top:8px;">{reg['desc']}</div>
            </div>''', unsafe_allow_html=True)
        with rc2:
            fc1,fc2 = st.columns(2)
            with fc1:
                st.markdown('<div class="label" style="color:#16a34a;margin-bottom:6px;">✅ SETTORI FAVORITI</div>', unsafe_allow_html=True)
                st.markdown("".join([f'<span class="tag tag-green">{s}</span>' for s in reg["fav"]]), unsafe_allow_html=True)
            with fc2:
                st.markdown('<div class="label" style="color:#dc2626;margin-bottom:6px;">⛔ DA EVITARE</div>', unsafe_allow_html=True)
                st.markdown("".join([f'<span class="tag tag-red">{s}</span>' for s in reg["ev"]]) or "—", unsafe_allow_html=True)

    # ── FEAR & GREED ──
    st.markdown('<div class="section">🧠 Sentiment di Mercato</div>', unsafe_allow_html=True)
    fg = fear_greed()
    fg_score = fg.get("score")
    fg_label = fg.get("label","N/D")
    fg_color = ("#dc2626" if (fg_score or 50)<25 else "#f97316" if (fg_score or 50)<45
                else "#9ca3af" if (fg_score or 50)<55 else "#16a34a" if (fg_score or 50)<75
                else "#166534")
    fg_icon  = "😱" if (fg_score or 50)<25 else "😰" if (fg_score or 50)<45 else "😐" if (fg_score or 50)<55 else "😄" if (fg_score or 50)<75 else "🤑"

    fg_col, _ = st.columns([1,3])
    with fg_col:
        st.markdown(f'''<div class="card" style="text-align:center;">
            <div class="label">CNN Fear & Greed Index</div>
            <div style="font-size:40px;margin:6px 0;">{fg_icon}</div>
            <div style="font-family:\'DM Serif Display\',serif;font-size:32px;color:{fg_color};">{fg_score or "N/D"}</div>
            <div style="font-family:DM Mono;font-size:12px;color:{fg_color};margin-top:4px;">{fg_label.upper()}</div>
        </div>''', unsafe_allow_html=True)

    # ── INDICI GLOBALI ──
    st.markdown('<div class="section">📈 Indici & Asset Globali</div>', unsafe_allow_html=True)

    with st.spinner("Carico indici..."):
        index_data = {name: get_index_data(tkr) for name,tkr in INDICES.items()}

    cols = st.columns(4)
    for i,(name_idx,(tkr,)) in enumerate([(n,(t,)) for n,t in INDICES.items()]):
        d = index_data.get(name_idx,{})
        price = d.get("price")
        chg   = d.get("chg")
        ytd   = d.get("ytd")
        chg_color = "#16a34a" if (chg or 0)>=0 else "#dc2626"
        with cols[i%4]:
            st.markdown(f'''<div class="card" style="padding:12px 14px;">
                <div class="label">{name_idx}</div>
                <div style="font-family:\'DM Serif Display\',serif;font-size:18px;color:#1a1a2e;">{f"{price:,.2f}" if price else "N/D"}</div>
                <div style="font-family:DM Mono;font-size:11px;color:{chg_color};margin-top:3px;">
                    {"▲" if (chg or 0)>=0 else "▼"} {abs(chg):.2f}% oggi
                    {"  |  YTD "+("▲" if (ytd or 0)>=0 else "▼")+f" {abs(ytd):.1f}%" if ytd else ""}
                </div>
            </div>''', unsafe_allow_html=True)

    # ── GRAFICO S&P 500 1 ANNO ──
    st.markdown('<div class="section">📉 S&P 500 — Ultimo Anno</div>', unsafe_allow_html=True)
    try:
        sp_hist = yf.Ticker("^GSPC").history(period="1y")
        if not sp_hist.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sp_hist.index, y=sp_hist["Close"].round(2),
                mode="lines", line=dict(color="#3b82f6",width=2),
                fill="tozeroy", fillcolor=hex_rgba("#3b82f6",.06),
                hovertemplate="<b>%{x|%d %b %Y}</b>: %{y:,.0f}<extra></extra>",
            ))
            fig.update_layout(
                height=250, margin=dict(l=0,r=0,t=6,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Mono",color="#9ca3af",size=10), showlegend=False,
                xaxis=dict(showgrid=False,zeroline=False),
                yaxis=dict(showgrid=True,gridcolor="#f0f0f0",zeroline=False),
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar":False}, key="dash_sp500")
    except: pass

    st.markdown(
        '<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:32px;">'
        'MACRO ANALYZER · HOME DASHBOARD · yfinance · CNN Fear&Greed</div>',
        unsafe_allow_html=True)
