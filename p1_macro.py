"""pages/p1_macro.py — Mattone 1: Analisi Macroeconomica"""
import streamlit as st
import pandas as pd
from datetime import datetime
from components.navbar import render as nav
from components.charts import line_chart
from components.styles import inject
from data.macro_fetch import (get_gdp, get_inf, get_unemp, get_ca, get_debt, get_fdi,
                               latest, freshness_badge, classify_regime)
from config import COUNTRIES, FALLBACK, CHART_COLORS

def render():
    nav()

    # ── Selector paese inline ──
    c1,c2 = st.columns([2,1])
    with c1:
        new_cn = st.selectbox("🌍 Paese", list(COUNTRIES.keys()),
                              index=list(COUNTRIES.keys()).index(st.session_state.country_name),
                              key="p1_country")
        if new_cn != st.session_state.country_name:
            st.session_state.country_name = new_cn
            st.session_state.cc = COUNTRIES[new_cn]
            st.session_state.regime = None
            st.rerun()
    with c2:
        st.session_state.years_back = st.slider("Anni di storico", 5, 20,
                                                  st.session_state.years_back, key="p1_years")

    cc          = st.session_state.cc
    country_name= st.session_state.country_name
    years_back  = st.session_state.years_back

    st.markdown(f"## {country_name} — Analisi Macroeconomica")
    st.markdown('<div class="label" style="margin-bottom:20px;">MATTONE 1 · STEP 1 DEL FRAMEWORK TOP-DOWN</div>',
                unsafe_allow_html=True)

    # ── Fetch dati ──
    with st.spinner("Carico dati macro... (cache intelligente per tipo di dato)"):
        df_gdp,  fr_gdp,  src_gdp  = get_gdp(cc)
        df_inf,  fr_inf,  src_inf  = get_inf(cc)
        df_unemp,fr_un,   src_un   = get_unemp(cc)
        df_ca,   fr_ca,   src_ca   = get_ca(cc)
        df_debt, fr_debt, src_debt = get_debt(cc)
        df_fdi,  fr_fdi,  src_fdi  = get_fdi(cc)

    gv,gd = latest(df_gdp);  iv,id_= latest(df_inf);  uv,ud = latest(df_unemp)
    cv,cd = latest(df_ca);   dv,dd = latest(df_debt);  fv,fd = latest(df_fdi)

    # Fallback IMF 2023 se mancano i 3 chiave
    used_fb = False
    if cc in FALLBACK:
        fb = FALLBACK[cc]
        if gv is None: gv,gd=fb[0],None; used_fb=True
        if iv is None: iv,id_=fb[1],None; used_fb=True
        if uv is None: uv,ud=fb[2],None; used_fb=True

    # ── Regime ──
    st.markdown('<div class="section">🔍 Regime Economico Corrente</div>', unsafe_allow_html=True)

    if gv is not None and iv is not None and uv is not None:
        reg = classify_regime(gv, iv, uv)
        st.session_state.regime = reg

        if used_fb:
            st.markdown('<div class="warn">⚠️ Alcuni dati integrati con stime IMF/OCSE 2023 — classificazione indicativa.</div>',
                        unsafe_allow_html=True)

        rc1, rc2 = st.columns([1,2])
        with rc1:
            st.markdown(f'''<div class="card">
                <div class="label">Regime identificato</div>
                <div style="margin:10px 0;"><span class="badge {reg['css']}">{reg['icon']} {reg['name']}</span></div>
                <div style="font-size:13px;color:#6b7280;line-height:1.6;">{reg['desc']}</div>
                <div style="font-family:DM Mono;font-size:10px;color:#d1d5db;margin-top:10px;">
                    PIL:{gv:.1f}% · Inf:{iv:.1f}% · Disoc:{uv:.1f}%
                </div>
            </div>''', unsafe_allow_html=True)
        with rc2:
            ca,cb = st.columns(2)
            with ca:
                st.markdown('<div class="label" style="color:#16a34a;margin-bottom:6px;">✅ SETTORI FAVORITI</div>',unsafe_allow_html=True)
                st.markdown("".join([f'<span class="tag tag-green">{s}</span>' for s in reg["fav"]]),unsafe_allow_html=True)
            with cb:
                st.markdown('<div class="label" style="color:#dc2626;margin-bottom:6px;">⛔ DA EVITARE</div>',unsafe_allow_html=True)
                st.markdown("".join([f'<span class="tag tag-red">{s}</span>' for s in reg["ev"]]) or "—",unsafe_allow_html=True)

        st.markdown("")
        if st.button("▶️ Vai al Mattone 2 — Analisi Settoriale", type="primary"):
            st.session_state.page="sectors"; st.rerun()
    else:
        st.error("Dati insufficienti per classificare il regime.")

    # ── KPI ──
    st.markdown('<div class="section">📈 Indicatori Chiave</div>', unsafe_allow_html=True)

    def fmt(v): return f"{v:.1f}%" if v is not None else "N/D"
    def dhtml(d):
        if d is None: return '<span style="color:#d1d5db;">—</span>'
        c="#16a34a" if d>=0 else "#dc2626"; a="▲" if d>=0 else "▼"
        return f'<span style="color:{c};">{a} {abs(d):.2f}%</span>'

    kpis=[
        ("📈","PIL reale",       gv,gd, src_gdp,  fr_gdp),
        ("🔥","Inflazione CPI",  iv,id_,src_inf,  fr_inf),
        ("👷","Disoccupazione",  uv,ud, src_un,   fr_un),
        ("🌐","Conto Corrente",  cv,cd, src_ca,   fr_ca),
        ("🏛️","Debito / PIL",   dv,dd, src_debt, fr_debt),
        ("💼","FDI netti",       fv,fd, src_fdi,  fr_fdi),
    ]
    cols = st.columns(3)
    for i,(icon,name,val,dlt,src,fr) in enumerate(kpis):
        with cols[i%3]:
            st.markdown(f'''<div class="card">
                <div class="label">{icon} {name}</div>
                <div class="value">{fmt(val)}</div>
                <div class="delta">{dhtml(dlt)}</div>
                <div style="display:flex;justify-content:space-between;margin-top:4px;align-items:center;">
                    <span class="source">{src or "—"}</span>
                    {freshness_badge(fr)}
                </div>
            </div>''', unsafe_allow_html=True)

    # ── Grafici storici ──
    st.markdown('<div class="section">📉 Serie Storiche</div>', unsafe_allow_html=True)

    def fy(df):
        if df is None or df.empty: return df
        return df[df["year"] >= datetime.now().year - years_back].copy()

    charts = [
        (df_gdp,  CHART_COLORS["gdp"],  "Crescita PIL (%)","gdp"),
        (df_inf,  CHART_COLORS["inf"],  "Inflazione CPI (%)","inf"),
        (df_unemp,CHART_COLORS["unemp"],"Disoccupazione (%)","unemp"),
        (df_ca,   CHART_COLORS["ca"],   "Conto Corrente (% PIL)","ca"),
        (df_debt, CHART_COLORS["debt"], "Debito Pubblico (% PIL)","debt"),
        (df_fdi,  CHART_COLORS["fdi"],  "FDI netti (% PIL)","fdi"),
    ]
    cl,cr = st.columns(2)
    for i,(df_r,color,label,kid) in enumerate(charts):
        with (cl if i%2==0 else cr):
            st.markdown(f'<div class="label" style="margin:12px 0 2px;">{label}</div>',unsafe_allow_html=True)
            st.plotly_chart(line_chart(fy(df_r),color), use_container_width=True,
                            config={"displayModeBar":False}, key=f"p1_{kid}_{cc}")

    st.markdown(
        '<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:32px;">'
        'MATTONE 1 · FRED + IMF WEO + OECD + World Bank · Cache intelligente per tipo di dato</div>',
        unsafe_allow_html=True)
