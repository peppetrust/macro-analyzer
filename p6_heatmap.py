"""pages/p6_heatmap.py — Heatmap settoriale stile Finviz"""
import streamlit as st, yfinance as yf, pandas as pd, numpy as np
import plotly.graph_objects as go
from datetime import datetime
from components.navbar import render as nav
from config import USA_SECTORS, EUROPE_SECTORS, GLOBAL_SECTORS, get_sector_map, THEORETICAL_PERF

PERIOD_OPTIONS = {"1 giorno":"1d","1 settimana":"5d","1 mese":"1mo","3 mesi":"3mo","YTD":"ytd","1 anno":"1y"}

@st.cache_data(ttl=3600, show_spinner=False)
def get_etf_returns(sector_map: dict, period: str) -> dict:
    results = {}
    for sec, info in sector_map.items():
        try:
            hist = yf.Ticker(info["ticker"]).history(period=period)
            if len(hist)<2:
                results[sec] = None; continue
            ret = ((hist["Close"].iloc[-1]/hist["Close"].iloc[0])-1)*100
            results[sec] = round(float(ret),2)
        except: results[sec] = None
    return results

def color_for_return(ret):
    if ret is None: return "#f3f4f6","#6b7280"
    if ret >=  5:  return "#14532d","#bbf7d0"
    if ret >=  2:  return "#16a34a","#ffffff"
    if ret >=  0:  return "#86efac","#166534"
    if ret >= -2:  return "#fca5a5","#991b1b"
    if ret >= -5:  return "#dc2626","#ffffff"
    return "#7f1d1d","#fecaca"

def render():
    nav()
    st.markdown("## 🔥 Heatmap Settoriale")
    st.markdown('<div class="label" style="margin-bottom:16px;">PERFORMANCE ETF PER SETTORE · STILE FINVIZ</div>', unsafe_allow_html=True)

    cc  = st.session_state.get("cc","US")
    reg = st.session_state.get("regime")

    cfg1, cfg2 = st.columns([2,1])
    with cfg1:
        period_label = st.selectbox("Periodo", list(PERIOD_OPTIONS.keys()), index=2, key="hm_period")
        period = PERIOD_OPTIONS[period_label]
    with cfg2:
        show_regime = st.toggle("Mostra score regime", value=True)

    sector_map = get_sector_map(cc)
    regime_scores = THEORETICAL_PERF.get(reg["name"],{}) if reg else {}

    with st.spinner("Carico performance ETF..."):
        returns = get_etf_returns(sector_map, period)

    # ── HEATMAP GRIGLIA ──
    st.markdown('<div class="section">📊 Performance per Settore</div>', unsafe_allow_html=True)

    sectors = list(sector_map.keys())
    n_cols  = 3
    rows    = [sectors[i:i+n_cols] for i in range(0, len(sectors), n_cols)]

    for row in rows:
        cols = st.columns(n_cols)
        for col, sec in zip(cols, row):
            if not sec: continue
            ret   = returns.get(sec)
            score = regime_scores.get(sec, 0)
            bg, tc = color_for_return(ret)
            ticker = sector_map[sec]["ticker"]
            fav_icon = "✅" if reg and sec in reg.get("fav",[]) else ("⛔" if reg and sec in reg.get("ev",[]) else "")
            ret_str = f"{ret:+.2f}%" if ret is not None else "N/D"
            score_str = f"Score: {score:+d}" if show_regime and score!=0 else ""
            with col:
                st.markdown(f'''
                <div style="background:{bg};color:{tc};border-radius:10px;padding:16px 12px;
                            text-align:center;margin:4px 0;min-height:90px;">
                    <div style="font-family:DM Mono;font-size:10px;opacity:.8;margin-bottom:4px;">{fav_icon} {ticker}</div>
                    <div style="font-family:\'DM Serif Display\',serif;font-size:14px;font-weight:600;margin-bottom:4px;">{sec}</div>
                    <div style="font-family:DM Mono;font-size:20px;font-weight:700;">{ret_str}</div>
                    <div style="font-family:DM Mono;font-size:10px;opacity:.8;margin-top:4px;">{score_str}</div>
                </div>''', unsafe_allow_html=True)

    # ── BAR CHART RIEPILOGO ──
    st.markdown('<div class="section">📈 Riepilogo Rendimenti</div>', unsafe_allow_html=True)
    valid = {s:r for s,r in returns.items() if r is not None}
    if valid:
        sorted_s = sorted(valid.items(), key=lambda x: x[1], reverse=True)
        names = [s[:12] for s,_ in sorted_s]
        vals  = [v for _,v in sorted_s]
        colors= ["#16a34a" if v>=0 else "#dc2626" for v in vals]
        fig = go.Figure(go.Bar(
            y=names[::-1], x=vals[::-1], orientation="h",
            marker_color=colors[::-1],
            text=[f"{v:+.2f}%" for v in vals[::-1]],
            textposition="outside", textfont=dict(family="DM Mono",size=10),
            hovertemplate="<b>%{y}</b>: %{x:+.2f}%<extra></extra>",
        ))
        fig.add_vline(x=0, line_color="#e5e7eb", line_width=1)
        fig.update_layout(
            height=350, margin=dict(l=0,r=60,t=10,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Mono",color="#9ca3af",size=10), showlegend=False,
            xaxis=dict(showgrid=True,gridcolor="#f0f0f0",zeroline=False,
                       title=f"Rendimento {period_label}"),
            yaxis=dict(showgrid=False,tickfont=dict(size=11,color="#1a1a2e")),
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar":False}, key="heatmap_bar")

    # ── LEGENDA REGIME ──
    if reg:
        st.markdown(f'''<div class="info">
        <b>Regime attuale: {reg["icon"]} {reg["name"]}</b> — Le celle con ✅ sono i settori favoriti,
        ⛔ quelli da evitare. Lo score teorico (da -5 a +5) indica l'allineamento storico
        tra il settore e il regime economico corrente.
        </div>''', unsafe_allow_html=True)

    st.markdown(
        '<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:32px;">'
        'MACRO ANALYZER · HEATMAP · ETF via yfinance</div>',
        unsafe_allow_html=True)
