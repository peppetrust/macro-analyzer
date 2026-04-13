# ══════════════════════════════════════════════════════════════════════
# MACRO ANALYZER v2 — file unico, avvio: py -m streamlit run app.py
# ══════════════════════════════════════════════════════════════════════
import streamlit as st
import requests, io, pandas as pd, numpy as np
import yfinance as yf, plotly.graph_objects as go, math
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Macro Analyzer", page_icon="📊",
    layout="wide", initial_sidebar_state="collapsed",
)

from datetime import datetime

# ── PAESI ─────────────────────────────────────────────────────────────────────

COUNTRIES = {
    "🇺🇸 Stati Uniti":   "US",
    "🇩🇪 Germania":      "DE",
    "🇯🇵 Giappone":      "JP",
    "🇬🇧 Regno Unito":   "GB",
    "🇫🇷 Francia":       "FR",
    "🇮🇹 Italia":        "IT",
    "🇨🇳 Cina":          "CN",
    "🇧🇷 Brasile":       "BR",
    "🇮🇳 India":         "IN",
    "🇨🇦 Canada":        "CA",
    "🇦🇺 Australia":     "AU",
    "🇰🇷 Corea del Sud": "KR",
    "🇪🇸 Spagna":        "ES",
    "🇳🇱 Paesi Bassi":   "NL",
    "🇨🇭 Svizzera":      "CH",
    "🇸🇪 Svezia":        "SE",
    "🇲🇽 Messico":       "MX",
    "🇿🇦 Sudafrica":     "ZA",
    "🇹🇷 Turchia":       "TR",
    "🇵🇱 Polonia":       "PL",
}

EUROPE_CC  = {"DE","FR","IT","GB","ES","NL","CH","SE","PL"}
OECD_CC    = {"US","DE","JP","GB","FR","IT","CA","AU","KR","ES","NL","CH","SE","MX","PL"}

# ── FALLBACK DATI IMF/OCSE 2023 ───────────────────────────────────────────────
FALLBACK = {
    "US":(2.5,4.1,3.7),"DE":(-0.2,5.9,3.0),"JP":(1.9,3.3,2.6),
    "GB":(0.1,7.3,4.2),"FR":(0.9,5.7,7.3),"IT":(0.9,5.9,6.7),
    "CN":(5.2,0.2,5.2),"BR":(2.9,4.6,7.8),"IN":(8.2,5.4,3.2),
    "CA":(1.2,3.9,5.4),"AU":(2.0,5.6,3.7),"KR":(1.4,3.6,2.7),
    "ES":(2.5,3.5,12.2),"NL":(0.1,4.1,3.6),"CH":(1.3,2.1,2.1),
    "SE":(-0.1,8.6,8.5),"MX":(3.2,5.5,2.8),"ZA":(0.6,6.0,32.1),
    "TR":(4.5,53.9,9.4),"PL":(0.2,10.9,2.9),
}

# ── TTL CACHE PER TIPO DI DATO ────────────────────────────────────────────────
# Ogni valore è in secondi
TTL = {
    "gdp":          60 * 60 * 24 * 90,   # trimestrale  (90 giorni)
    "debt":         60 * 60 * 24 * 90,   # trimestrale
    "inflation":    60 * 60 * 24 * 30,   # mensile      (30 giorni)
    "unemployment": 60 * 60 * 24 * 30,   # mensile
    "current_acc":  60 * 60 * 24 * 90,   # trimestrale
    "fdi":          60 * 60 * 24 * 90,   # trimestrale
    "equity_price": 60 * 60 * 4,         # 4 ore
    "fundamentals": 60 * 60 * 24 * 7,    # settimanale  (7 giorni)
    "etf":          60 * 60 * 4,         # 4 ore
    "news":         60 * 60,              # 1 ora
    "calendar":     60 * 60 * 6,         # 6 ore
}

# ── ISO2 → ISO3 PER IMF ───────────────────────────────────────────────────────
ISO2_TO_ISO3 = {
    "US":"USA","DE":"DEU","JP":"JPN","GB":"GBR","FR":"FRA","IT":"ITA",
    "CN":"CHN","BR":"BRA","IN":"IND","CA":"CAN","AU":"AUS","KR":"KOR",
    "ES":"ESP","NL":"NLD","CH":"CHE","SE":"SWE","MX":"MEX","ZA":"ZAF",
    "TR":"TUR","PL":"POL",
}

# ── ETF SETTORIALI PER AREA ───────────────────────────────────────────────────
USA_SECTORS = {
    "Tecnologia":             {"ticker":"XLK",  "desc":"SPDR S&P 500 Tech"},
    "Finanziari":             {"ticker":"XLF",  "desc":"SPDR S&P 500 Financials"},
    "Energia":                {"ticker":"XLE",  "desc":"SPDR S&P 500 Energy"},
    "Healthcare":             {"ticker":"XLV",  "desc":"SPDR S&P 500 Health Care"},
    "Industriali":            {"ticker":"XLI",  "desc":"SPDR S&P 500 Industrials"},
    "Beni di prima necessità":{"ticker":"XLP",  "desc":"SPDR S&P 500 Cons. Staples"},
    "Ciclici":                {"ticker":"XLY",  "desc":"SPDR S&P 500 Cons. Discret."},
    "Utilities":              {"ticker":"XLU",  "desc":"SPDR S&P 500 Utilities"},
    "Materiali":              {"ticker":"XLB",  "desc":"SPDR S&P 500 Materials"},
    "Real Estate":            {"ticker":"XLRE", "desc":"SPDR S&P 500 Real Estate"},
    "Comunicazioni":          {"ticker":"XLC",  "desc":"SPDR S&P 500 Comm. Services"},
}
EUROPE_SECTORS = {
    "Tecnologia":             {"ticker":"EXV3.DE","desc":"iShares STOXX Eu600 Tech"},
    "Finanziari":             {"ticker":"EXV1.DE","desc":"iShares STOXX Eu600 Banks"},
    "Energia":                {"ticker":"EXV6.DE","desc":"iShares STOXX Eu600 Oil&Gas"},
    "Healthcare":             {"ticker":"EXV4.DE","desc":"iShares STOXX Eu600 H.Care"},
    "Industriali":            {"ticker":"EXH2.DE","desc":"iShares STOXX Eu600 Industr."},
    "Beni di prima necessità":{"ticker":"EXH8.DE","desc":"iShares STOXX Eu600 Food&Bev"},
    "Ciclici":                {"ticker":"EXH3.DE","desc":"iShares STOXX Eu600 Retail"},
    "Utilities":              {"ticker":"EXH7.DE","desc":"iShares STOXX Eu600 Utilities"},
    "Materiali":              {"ticker":"EXV5.DE","desc":"iShares STOXX Eu600 Basic Res."},
    "Real Estate":            {"ticker":"EPRA.MI","desc":"iShares EU Property Yield"},
    "Comunicazioni":          {"ticker":"EXH9.DE","desc":"iShares STOXX Eu600 Telecom"},
}
GLOBAL_SECTORS = {
    "Tecnologia":             {"ticker":"IXN",  "desc":"iShares Global Tech"},
    "Finanziari":             {"ticker":"IXG",  "desc":"iShares Global Financials"},
    "Energia":                {"ticker":"IXC",  "desc":"iShares Global Energy"},
    "Healthcare":             {"ticker":"IXJ",  "desc":"iShares Global Healthcare"},
    "Industriali":            {"ticker":"EXI",  "desc":"iShares Global Industrials"},
    "Beni di prima necessità":{"ticker":"KXI",  "desc":"iShares Global Cons.Staples"},
    "Ciclici":                {"ticker":"RXI",  "desc":"iShares Global Cons.Discret."},
    "Utilities":              {"ticker":"JXI",  "desc":"iShares Global Utilities"},
    "Materiali":              {"ticker":"MXI",  "desc":"iShares Global Materials"},
    "Real Estate":            {"ticker":"IFGL", "desc":"iShares Intl Dev.Real Estate"},
    "Comunicazioni":          {"ticker":"IXP",  "desc":"iShares Global Telecom"},
}

def get_sector_map(cc: str) -> dict:
    if cc == "US":             return USA_SECTORS
    if cc in EUROPE_CC:        return EUROPE_SECTORS
    return GLOBAL_SECTORS

def get_region_label(cc: str) -> str:
    if cc == "US":             return "USA (SPDR S&P 500)"
    if cc in EUROPE_CC:        return "Europa (iShares STOXX 600)"
    return "Globale (iShares MSCI)"

# ── SCORE TEORICI SETTORE × REGIME ────────────────────────────────────────────
THEORETICAL_PERF = {
    "Espansione":      {"Tecnologia":5,"Finanziari":4,"Industriali":4,"Ciclici":5,"Materiali":3,"Energia":2,"Healthcare":1,"Beni di prima necessità":-1,"Utilities":-2,"Real Estate":2,"Comunicazioni":3},
    "Surriscaldamento":{"Energia":5,"Materiali":4,"Real Estate":3,"Finanziari":2,"Industriali":1,"Comunicazioni":0,"Tecnologia":-1,"Healthcare":0,"Ciclici":-2,"Beni di prima necessità":-1,"Utilities":-3},
    "Contrazione":     {"Utilities":4,"Healthcare":5,"Beni di prima necessità":4,"Comunicazioni":2,"Finanziari":-2,"Industriali":-3,"Ciclici":-5,"Materiali":-3,"Energia":-1,"Tecnologia":-2,"Real Estate":-2},
    "Ripresa":         {"Ciclici":5,"Finanziari":4,"Tecnologia":4,"Industriali":3,"Materiali":3,"Real Estate":2,"Comunicazioni":2,"Energia":1,"Healthcare":0,"Beni di prima necessità":-1,"Utilities":-2},
    "Stagflazione":    {"Energia":5,"Materiali":3,"Beni di prima necessità":3,"Utilities":2,"Healthcare":2,"Comunicazioni":0,"Real Estate":-1,"Finanziari":-3,"Ciclici":-4,"Industriali":-2,"Tecnologia":-3},
    "Fase incerta":    {"Healthcare":2,"Utilities":2,"Beni di prima necessità":2,"Comunicazioni":1,"Finanziari":0,"Real Estate":0,"Tecnologia":0,"Industriali":0,"Materiali":0,"Energia":0,"Ciclici":0},
}

SCORE_LABELS = {
    5:"Molto favorevole", 4:"Favorevole", 3:"Leggermente positivo",
    2:"Neutro positivo",  1:"Neutro",     0:"Neutro",
    -1:"Cautela",        -2:"Sfavorevole",-3:"Molto sfavorevole",
    -4:"Fortemente negativo",-5:"Evitare",
}

# ── COLORI ─────────────────────────────────────────────────────────────────────
COLORS = {
    "gold":    "#b8922a",
    "green":   "#16a34a",
    "red":     "#dc2626",
    "blue":    "#3b82f6",
    "orange":  "#f97316",
    "purple":  "#8b5cf6",
    "yellow":  "#eab308",
    "teal":    "#10b981",
    "gray":    "#9ca3af",
    "bg":      "#f8f7f4",
    "white":   "#ffffff",
    "dark":    "#1a1a2e",
    "border":  "#e5e7eb",
}

CHART_COLORS = {
    "gdp":    "#3b82f6",
    "inf":    "#ef4444",
    "unemp":  "#f97316",
    "ca":     "#10b981",
    "debt":   "#8b5cf6",
    "fdi":    "#eab308",
}

# ── AZIONI PER PAESE/SETTORE ──────────────────────────────────────────────────
SECTOR_TO_GICS = {
    "Tecnologia":             "Information Technology",
    "Finanziari":             "Financials",
    "Energia":                "Energy",
    "Healthcare":             "Health Care",
    "Industriali":            "Industrials",
    "Beni di prima necessità":"Consumer Staples",
    "Ciclici":                "Consumer Discretionary",
    "Utilities":              "Utilities",
    "Materiali":              "Materials",
    "Real Estate":            "Real Estate",
    "Comunicazioni":          "Communication Services",
}

CURATED_STOCKS = {
    "IT": [
        ("ENI.MI","Eni","Energia"),("ENEL.MI","Enel","Utilities"),
        ("ISP.MI","Intesa Sanpaolo","Finanziari"),("UCG.MI","UniCredit","Finanziari"),
        ("STM.MI","STMicroelectronics","Tecnologia"),("LDO.MI","Leonardo","Industriali"),
        ("MB.MI","Mediobanca","Finanziari"),("TIT.MI","Telecom Italia","Comunicazioni"),
        ("PRY.MI","Prysmian","Industriali"),("RACE.MI","Ferrari","Ciclici"),
        ("MONC.MI","Moncler","Ciclici"),("G.MI","Generali","Finanziari"),
        ("SRG.MI","Snam","Utilities"),("TRN.MI","Terna","Utilities"),
        ("BAMI.MI","Banco BPM","Finanziari"),("A2A.MI","A2A","Utilities"),
        ("PST.MI","Poste Italiane","Comunicazioni"),("STLAM.MI","Stellantis","Ciclici"),
        ("AZM.MI","Azimut","Finanziari"),("BMED.MI","Banca Mediolanum","Finanziari"),
    ],
    "DE": [
        ("SAP.DE","SAP","Tecnologia"),("SIE.DE","Siemens","Industriali"),
        ("ALV.DE","Allianz","Finanziari"),("DTE.DE","Deutsche Telekom","Comunicazioni"),
        ("BAYN.DE","Bayer","Healthcare"),("BMW.DE","BMW","Ciclici"),
        ("MBG.DE","Mercedes-Benz","Ciclici"),("VOW3.DE","Volkswagen","Ciclici"),
        ("DBK.DE","Deutsche Bank","Finanziari"),("BAS.DE","BASF","Materiali"),
        ("EOAN.DE","E.ON","Utilities"),("MRK.DE","Merck KGaA","Healthcare"),
        ("ADS.DE","Adidas","Ciclici"),("RWE.DE","RWE","Utilities"),
        ("HEN3.DE","Henkel","Beni di prima necessità"),("IFX.DE","Infineon","Tecnologia"),
        ("MUV2.DE","Munich Re","Finanziari"),("CON.DE","Continental","Ciclici"),
        ("FRE.DE","Fresenius","Healthcare"),("SHL.DE","Siemens Healthineers","Healthcare"),
    ],
    "FR": [
        ("OR.PA","L'Oréal","Beni di prima necessità"),("MC.PA","LVMH","Ciclici"),
        ("SAN.PA","Sanofi","Healthcare"),("TTE.PA","TotalEnergies","Energia"),
        ("AIR.PA","Airbus","Industriali"),("BNP.PA","BNP Paribas","Finanziari"),
        ("SU.PA","Schneider Electric","Industriali"),("AI.PA","Air Liquide","Materiali"),
        ("RI.PA","Pernod Ricard","Beni di prima necessità"),("KER.PA","Kering","Ciclici"),
        ("CAP.PA","Capgemini","Tecnologia"),("DG.PA","Vinci","Industriali"),
        ("GLE.PA","Société Générale","Finanziari"),("ACA.PA","Crédit Agricole","Finanziari"),
        ("VIV.PA","Vivendi","Comunicazioni"),("RNO.PA","Renault","Ciclici"),
        ("SGO.PA","Saint-Gobain","Materiali"),("WLN.PA","Worldline","Tecnologia"),
        ("EDF.PA","EDF","Utilities"),("SAF.PA","Safran","Industriali"),
    ],
    "GB": [
        ("SHEL.L","Shell","Energia"),("AZN.L","AstraZeneca","Healthcare"),
        ("HSBA.L","HSBC","Finanziari"),("ULVR.L","Unilever","Beni di prima necessità"),
        ("BP.L","BP","Energia"),("GSK.L","GSK","Healthcare"),
        ("LLOY.L","Lloyds Banking","Finanziari"),("DGE.L","Diageo","Beni di prima necessità"),
        ("RIO.L","Rio Tinto","Materiali"),("BATS.L","BAT","Beni di prima necessità"),
        ("GLEN.L","Glencore","Materiali"),("BT-A.L","BT Group","Comunicazioni"),
        ("VOD.L","Vodafone","Comunicazioni"),("BARC.L","Barclays","Finanziari"),
        ("NG.L","National Grid","Utilities"),("REL.L","RELX","Industriali"),
        ("CRH.L","CRH","Materiali"),("EXPN.L","Experian","Tecnologia"),
        ("LSEG.L","LSEG","Finanziari"),("IAG.L","IAG","Industriali"),
    ],
    "ES": [
        ("SAN.MC","Banco Santander","Finanziari"),("IBE.MC","Iberdrola","Utilities"),
        ("BBVA.MC","BBVA","Finanziari"),("ITX.MC","Inditex","Ciclici"),
        ("REP.MC","Repsol","Energia"),("TEF.MC","Telefónica","Comunicazioni"),
        ("CABK.MC","CaixaBank","Finanziari"),("AMS.MC","Amadeus","Tecnologia"),
        ("AENA.MC","AENA","Industriali"),("MAP.MC","MAPFRE","Finanziari"),
    ],
    "US": [],  # usa Wikipedia S&P500
}

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:#f8f7f4;color:#1a1a2e;}
.stApp{background:#f8f7f4;}
h1,h2,h3{font-family:'DM Serif Display',serif;color:#1a1a2e;}
#MainMenu,footer,header{visibility:hidden;}

/* Cards */
.card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px 22px;
      margin:6px 0;box-shadow:0 1px 4px rgba(0,0,0,.06);transition:all .2s;}
.card:hover{border-color:#b8922a;box-shadow:0 4px 12px rgba(0,0,0,.1);}
.card-gold{background:#fffbeb;border:1px solid #b8922a;}

/* Tipografia */
.label{font-family:'DM Mono',monospace;font-size:11px;color:#9ca3af;letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px;}
.value{font-family:'DM Serif Display',serif;font-size:28px;color:#1a1a2e;line-height:1;}
.delta{font-family:'DM Mono',monospace;font-size:12px;margin-top:4px;}
.source{font-family:'DM Mono',monospace;font-size:9px;color:#d1d5db;margin-top:3px;}
.section{font-family:'DM Mono',monospace;font-size:11px;color:#b8922a;letter-spacing:.15em;
         text-transform:uppercase;border-bottom:1px solid #e5e7eb;padding-bottom:8px;margin:24px 0 14px;}

/* Regime badges */
.badge{display:inline-block;padding:6px 16px;border-radius:50px;font-family:'DM Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.05em;}
.b-expansion  {background:#dcfce7;color:#166534;border:1px solid #86efac;}
.b-peak       {background:#fef9c3;color:#854d0e;border:1px solid #fde047;}
.b-contraction{background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;}
.b-recovery   {background:#dbeafe;color:#1e40af;border:1px solid #93c5fd;}
.b-stagflation{background:#ede9fe;color:#5b21b6;border:1px solid #c4b5fd;}
.b-unknown    {background:#f3f4f6;color:#6b7280;border:1px solid #d1d5db;}

/* Tags */
.tag{display:inline-block;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;
     padding:4px 10px;margin:2px;font-family:'DM Mono',monospace;font-size:11px;color:#b8922a;}
.tag-green{background:#dcfce7;border-color:#86efac;color:#166534;}
.tag-red  {background:#fee2e2;border-color:#fca5a5;color:#991b1b;}

/* Info/Warn boxes */
.info{background:#fff;border-left:3px solid #b8922a;border-radius:0 8px 8px 0;
      padding:12px 16px;margin:10px 0;font-size:13px;color:#6b7280;}
.warn{background:#fffbeb;border-left:3px solid #f59e0b;border-radius:0 8px 8px 0;
      padding:10px 14px;margin:8px 0;font-size:13px;color:#92400e;}
.success{background:#f0fdf4;border-left:3px solid #16a34a;border-radius:0 8px 8px 0;
         padding:10px 14px;margin:8px 0;font-size:13px;color:#166534;}

/* Freshness badge */
.fresh-green{background:#dcfce7;color:#166534;font-family:'DM Mono',monospace;font-size:9px;padding:2px 6px;border-radius:4px;}
.fresh-yellow{background:#fef9c3;color:#854d0e;font-family:'DM Mono',monospace;font-size:9px;padding:2px 6px;border-radius:4px;}
.fresh-red{background:#fee2e2;color:#991b1b;font-family:'DM Mono',monospace;font-size:9px;padding:2px 6px;border-radius:4px;}

/* Heatmap cells */
.heatmap-cell{border-radius:8px;padding:10px 8px;text-align:center;margin:2px;cursor:pointer;transition:transform .15s;}
.heatmap-cell:hover{transform:scale(1.03);}

/* Navbar */
.main .block-container{padding-bottom:20px !important;}
button[kind="primary"]{min-height:44px !important;}
button[kind="secondary"]{min-height:44px !important;}

/* Mobile */
@media(max-width:768px){
    .card{padding:12px 14px !important;}
    .value{font-size:22px !important;}
    .section{font-size:10px !important;margin:16px 0 10px !important;}
    [data-testid="stSidebar"]{min-width:80vw !important;}
}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-thumb{background:#e5e7eb;border-radius:4px;}
</style>
"""

def _inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

import plotly.graph_objects as go
import pandas as pd
import numpy as np

def hex_rgba(h: str, a: float) -> str:
    h = h.lstrip("#")
    r,g,b = int(h[:2],16),int(h[2:4],16),int(h[4:],16)
    return f"rgba({r},{g},{b},{a})"

def line_chart(df: pd.DataFrame, color: str, unit: str = "%", height: int = 180) -> go.Figure:
    fig = go.Figure()
    if df is not None and not df.empty:
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["value"].round(2),
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=5, color=color),
            fill="tozeroy", fillcolor=hex_rgba(color, .07),
            hovertemplate=f"<b>%{{x}}</b>: %{{y:.1f}}{unit}<extra></extra>",
        ))
    else:
        fig.add_annotation(text="Dati non disponibili", showarrow=False,
                           font=dict(color="#9ca3af", size=12))
    fig.update_layout(
        height=height, margin=dict(l=0,r=0,t=6,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono", color="#9ca3af", size=10), showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", zeroline=True,
                   zerolinecolor="#e5e7eb", tickfont=dict(size=10)),
    )
    return fig

def bar_chart(df: pd.DataFrame, height: int = 200) -> go.Figure:
    fig = go.Figure()
    if df is None or df.empty:
        fig.add_annotation(text="Dati non disponibili", showarrow=False, font=dict(color="#9ca3af"))
    else:
        colors = ["#16a34a" if v >= 0 else "#dc2626" for v in df["return_pct"]]
        fig.add_trace(go.Bar(
            x=df["year"], y=df["return_pct"].round(1),
            marker_color=colors,
            text=df["return_pct"].round(1).astype(str)+"%",
            textposition="outside", textfont=dict(size=9, family="DM Mono"),
            hovertemplate="<b>%{x}</b>: %{y:.1f}%<extra></extra>",
        ))
    fig.update_layout(
        height=height, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono", color="#9ca3af", size=10), showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, type="category"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", zeroline=True, zerolinecolor="#e5e7eb"),
    )
    return fig

def radar_chart(scores, height=300):
    # Protezione se l'input non è un dizionario (es. riceve una stringa di testo)
    if not isinstance(scores, dict):
        fig = go.Figure()
        fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        return fig
        
    sectors = list(scores.keys())
    vals    = [scores[s] for s in sectors]
    vals_n  = [(v+5)/10 for v in vals]
    
    fig = go.Figure(go.Scatterpolar(
        r=vals_n+[vals_n[0]], 
        theta=sectors+[sectors[0]],
        fill="toself", 
        fillcolor=hex_rgba("#b8922a",.15),
        line=dict(color="#b8922a", width=2),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1], showticklabels=False, gridcolor="#e5e7eb"),
            angularaxis=dict(tickfont=dict(size=9, family="DM Mono"), gridcolor="#e5e7eb"),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30,r=30,t=30,b=30),
        height=height, showlegend=False,
    )
    return fig

import streamlit as st
import requests, io, pandas as pd
from datetime import datetime

# ── Helpers ───────────────────────────────────────────────────────────────────

def _df_from_rows(rows):
    if not rows: return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)

def freshness_badge(year):
    if year is None:
        return '<span class="fresh-red">N/D</span>'
    lag = datetime.now().year - int(year)
    cls = "fresh-green" if lag<=1 else ("fresh-yellow" if lag<=2 else "fresh-red")
    return f'<span class="{cls}">{year}</span>'

def _latest_year(df):
    if df is None or df.empty: return None
    return int(df.iloc[-1]["year"])

# ── Fonte 1: FRED (solo USA) ──────────────────────────────────────────────────

@st.cache_data(ttl=TTL["inflation"], show_spinner=False)
def _fred(series: str) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code != 200: return pd.DataFrame()
        df = pd.read_csv(io.StringIO(r.text), names=["date","value"], skiprows=1)
        df["date"]  = pd.to_datetime(df["date"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
        df["year"] = df["date"].dt.year
        return df.groupby("year")["value"].mean().reset_index().sort_values("year")
    except: return pd.DataFrame()

# ── Fonte 2: IMF WEO ──────────────────────────────────────────────────────────

@st.cache_data(ttl=TTL["gdp"], show_spinner=False)
def _imf(cc: str, indicator: str) -> pd.DataFrame:
    iso3 = ISO2_TO_ISO3.get(cc)
    if not iso3: return pd.DataFrame()
    url = (f"https://www.imf.org/external/datamapper/api/v1/{indicator}/{iso3}"
           f"?periods=2019,2020,2021,2022,2023,2024,2025")
    try:
        r = requests.get(url, timeout=12)
        if r.status_code != 200: return pd.DataFrame()
        data   = r.json()
        values = data.get("values",{}).get(indicator,{}).get(iso3,{})
        if not values: return pd.DataFrame()
        rows = [{"year":int(k),"value":float(v)} for k,v in values.items() if v is not None]
        return _df_from_rows(rows)
    except: return pd.DataFrame()

# ── Fonte 3: OECD ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=TTL["gdp"], show_spinner=False)
def _oecd(cc: str, dataset: str) -> pd.DataFrame:
    DATASETS = {
        "GDP":   f"QNA/A.{cc}.B1_GE.GYSA.A",
        "CPI":   f"PRICES_CPI/A.{cc}.CPALTT01.GY",
        "UNEMP": f"ALFS_SUMTAB/A.{cc}.UNEMPSA_",
    }
    path = DATASETS.get(dataset,"")
    if not path: return pd.DataFrame()
    url = f"https://stats.oecd.org/SDMX-JSON/data/{path}?contentType=csv"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200: return pd.DataFrame()
        df = pd.read_csv(io.StringIO(r.text))
        yc = next((c for c in df.columns if any(k in c.lower() for k in ["year","time","period"])), None)
        vc = next((c for c in df.columns if any(k in c.lower() for k in ["value","obs"])), None)
        if not yc or not vc: return pd.DataFrame()
        df = df[[yc,vc]].copy(); df.columns=["year","value"]
        df["year"]  = pd.to_numeric(df["year"],  errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.dropna().sort_values("year").reset_index(drop=True)
    except: return pd.DataFrame()

@st.cache_data(ttl=TTL["gdp"], show_spinner=False)
def _oecd_quarterly(cc: str, dataset: str) -> pd.DataFrame:
    """Scarica dati OECD trimestrali per GDP e CPI."""
    QDATASETS = {
        "GDP":  f"QNA/Q.{cc}.B1_GE.GYSA.Q",
        "CPI":  f"PRICES_CPI/Q.{cc}.CPALTT01.GY",
    }
    path = QDATASETS.get(dataset, "")
    if not path: return pd.DataFrame()
    url = f"https://stats.oecd.org/SDMX-JSON/data/{path}?contentType=csv"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200: return pd.DataFrame()
        df = pd.read_csv(io.StringIO(r.text))
        tc = next((c for c in df.columns if any(k in c.lower() for k in ["time","period","quarter"])), None)
        vc = next((c for c in df.columns if any(k in c.lower() for k in ["value","obs"])), None)
        if not tc or not vc: return pd.DataFrame()
        df = df[[tc, vc]].copy(); df.columns = ["period", "value"]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
        # Normalizza formato periodo: "2024-Q1" o "2024Q1" o "2024-01"
        def _parse_period(p):
            p = str(p).strip()
            if "Q" in p.upper():
                p = p.upper().replace("-Q","Q").replace(" Q","Q")
                parts = p.split("Q")
                if len(parts) == 2:
                    return f"{parts[0]}-Q{parts[1]}"
            return p
        df["period"] = df["period"].apply(_parse_period)
        # Solo periodi con formato YYYY-QN
        mask = df["period"].str.match(r"^\d{4}-Q[1-4]$", na=False)
        return df[mask].sort_values("period").reset_index(drop=True)
    except: return pd.DataFrame()


@st.cache_data(ttl=TTL["gdp"], show_spinner=False)
def get_quarterly_data(cc: str):
    """Ritorna dati trimestrali (GDP e CPI) per il paese dato."""
    gdp_q = _oecd_quarterly(cc, "GDP")
    cpi_q = _oecd_quarterly(cc, "CPI")
    # Fallback FRED per USA (trimestrale)
    if cc == "US" and gdp_q.empty:
        try:
            url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=A191RL1Q225SBEA"
            r = requests.get(url, timeout=12)
            if r.status_code == 200:
                df = pd.read_csv(io.StringIO(r.text), names=["date","value"], skiprows=1)
                df["date"]  = pd.to_datetime(df["date"], errors="coerce")
                df["value"] = pd.to_numeric(df["value"], errors="coerce")
                df = df.dropna()
                df["period"] = df["date"].dt.year.astype(str) + "-Q" + df["date"].dt.quarter.astype(str)
                gdp_q = df[["period","value"]].tail(20).reset_index(drop=True)
        except: pass
    return gdp_q, cpi_q



@st.cache_data(ttl=TTL["gdp"], show_spinner=False)
def _wb(cc: str, ind: str, n: int = 25) -> pd.DataFrame:
    url = (f"https://api.worldbank.org/v2/country/{cc}/indicator/{ind}"
           f"?format=json&per_page={n}&mrv={n}")
    try:
        r = requests.get(url, timeout=12); p = r.json()
        if len(p)<2 or not p[1]: return pd.DataFrame()
        rows = [{"year":int(d["date"]),"value":d["value"]} for d in p[1] if d["value"] is not None]
        return _df_from_rows(rows)
    except: return pd.DataFrame()

# ── Cascade: prende il dato più fresco disponibile ────────────────────────────

def _best(*candidates) -> tuple:
    """
    candidates: lista di (df, source_name)
    Ritorna (df, freshness_year, source_name) del più aggiornato.
    """
    valid = [(df, _latest_year(df), src) for df,src in candidates
             if df is not None and not df.empty and _latest_year(df) is not None]
    if not valid: return pd.DataFrame(), None, "—"
    return max(valid, key=lambda x: x[1])

# ── API pubbliche per indicatori ──────────────────────────────────────────────

@st.cache_data(ttl=TTL["gdp"], show_spinner=False)
def get_gdp(cc: str):
    c = [(_wb(cc,"NY.GDP.MKTP.KD.ZG"), "World Bank"),
         (_imf(cc,"NGDP_RPCH"),         "IMF WEO"),
         (_oecd(cc,"GDP"),              "OECD")]
    if cc=="US":
        c.insert(0, (_fred("A191RL1A225NBEA"), "FRED"))
    return _best(*c)

@st.cache_data(ttl=TTL["inflation"], show_spinner=False)
def get_inf(cc: str):
    fred_df = pd.DataFrame()
    if cc=="US":
        raw=_fred("CPIAUCSL")
        if not raw.empty:
            raw=raw.copy(); raw["value"]=raw["value"].pct_change()*100
            fred_df=raw.dropna().reset_index(drop=True)
    c = [(_wb(cc,"FP.CPI.TOTL.ZG"),    "World Bank"),
         (_imf(cc,"PCPIPCH"),           "IMF WEO"),
         (_oecd(cc,"CPI"),              "OECD")]
    if not fred_df.empty: c.insert(0,(fred_df,"FRED"))
    return _best(*c)

@st.cache_data(ttl=TTL["unemployment"], show_spinner=False)
def get_unemp(cc: str):
    c = [(_wb(cc,"SL.UEM.TOTL.ZS"),    "World Bank"),
         (_imf(cc,"LUR"),               "IMF WEO"),
         (_oecd(cc,"UNEMP"),            "OECD")]
    if cc=="US": c.insert(0,(_fred("UNRATE"),"FRED"))
    return _best(*c)

@st.cache_data(ttl=TTL["current_acc"], show_spinner=False)
def get_ca(cc: str):
    return _best((_wb(cc,"BN.CAB.XOKA.GD.ZS"),"World Bank"))

@st.cache_data(ttl=TTL["debt"], show_spinner=False)
def get_debt(cc: str):
    return _best((_wb(cc,"GC.DOD.TOTL.GD.ZS"),"World Bank"))

@st.cache_data(ttl=TTL["fdi"], show_spinner=False)
def get_fdi(cc: str):
    return _best((_wb(cc,"BX.KLT.DINV.WD.GD.ZS"),"World Bank"))

# ── latest() utility ──────────────────────────────────────────────────────────

def latest(df):
    """Accetta DataFrame o tupla (df, fr, src)."""
    if isinstance(df, tuple): df = df[0]
    if df is None or df.empty: return None, None
    v = df.iloc[-1]["value"]
    p = df.iloc[-2]["value"] if len(df)>1 else None
    return v, (v-p if p is not None else None)

# ── Classificazione regime v2 ─ sistema a punteggio multi-dimensionale ─────────

def _regime_score(gdp, inf, un, ca=None, debt=None, gdp_trend=None, inf_trend=None):
    """
    Calcola i punteggi normalizzati [0-100] per ogni regime possibile.
    Ritorna un dict {nome_regime: score} e i segnali di dettaglio.
    
    Parametri:
      gdp       : crescita PIL reale (%)
      inf       : inflazione CPI (%)
      un        : disoccupazione (%)
      ca        : conto corrente (% PIL), opzionale
      debt      : debito pubblico (% PIL), opzionale
      gdp_trend : variazione PIL vs anno precedente, opzionale
      inf_trend : variazione inflazione vs anno precedente, opzionale
    """
    signals = {}  # nome → (icona, testo, colore)
    
    # ── Segnali per dimensione ────────────────────────────────────────────────
    # PIL
    if gdp >= 3.0:
        signals["pil"] = ("🟢", f"PIL forte ({gdp:.1f}%)", "green")
    elif gdp >= 1.5:
        signals["pil"] = ("🟡", f"PIL moderato ({gdp:.1f}%)", "yellow")
    elif gdp >= 0:
        signals["pil"] = ("🟠", f"PIL debole ({gdp:.1f}%)", "orange")
    else:
        signals["pil"] = ("🔴", f"PIL negativo ({gdp:.1f}%)", "red")

    # Inflazione
    if inf < 2.0:
        signals["inf"] = ("🟢", f"Inflazione bassa ({inf:.1f}%)", "green")
    elif inf < 4.0:
        signals["inf"] = ("🟡", f"Inflazione moderata ({inf:.1f}%)", "yellow")
    elif inf < 7.0:
        signals["inf"] = ("🟠", f"Inflazione elevata ({inf:.1f}%)", "orange")
    else:
        signals["inf"] = ("🔴", f"Inflazione molto alta ({inf:.1f}%)", "red")

    # Disoccupazione
    if un < 4.5:
        signals["un"] = ("🟢", f"Piena occupazione ({un:.1f}%)", "green")
    elif un < 6.5:
        signals["un"] = ("🟡", f"Occupazione accettabile ({un:.1f}%)", "yellow")
    elif un < 9.0:
        signals["un"] = ("🟠", f"Disoccupazione alta ({un:.1f}%)", "orange")
    else:
        signals["un"] = ("🔴", f"Disoccupazione critica ({un:.1f}%)", "red")

    # Trend PIL (accelerazione / decelerazione)
    if gdp_trend is not None:
        if gdp_trend >= 1.0:
            signals["gdp_trend"] = ("📈", f"PIL in accelerazione (+{gdp_trend:.1f}pp)", "green")
        elif gdp_trend <= -1.0:
            signals["gdp_trend"] = ("📉", f"PIL in decelerazione ({gdp_trend:.1f}pp)", "red")

    # Trend inflazione
    if inf_trend is not None:
        if inf_trend >= 1.0:
            signals["inf_trend"] = ("🔺", f"Inflazione in salita (+{inf_trend:.1f}pp)", "orange")
        elif inf_trend <= -1.0:
            signals["inf_trend"] = ("🔻", f"Inflazione in discesa ({inf_trend:.1f}pp)", "green")

    # Conto corrente
    if ca is not None:
        if ca >= 1.5:
            signals["ca"] = ("🟢", f"CC in surplus ({ca:.1f}% PIL)", "green")
        elif ca >= -1.0:
            signals["ca"] = ("🟡", f"CC equilibrato ({ca:.1f}% PIL)", "yellow")
        else:
            signals["ca"] = ("🔴", f"CC in deficit ({ca:.1f}% PIL)", "red")

    # Debito
    if debt is not None:
        if debt < 60:
            signals["debt"] = ("🟢", f"Debito sostenibile ({debt:.0f}% PIL)", "green")
        elif debt < 100:
            signals["debt"] = ("🟡", f"Debito moderato ({debt:.0f}% PIL)", "yellow")
        else:
            signals["debt"] = ("🔴", f"Debito elevato ({debt:.0f}% PIL)", "red")

    # ── Calcolo score per ciascun regime ─────────────────────────────────────
    # Ogni regime accumula punti da 0 a 100 in base a quante condizioni soddisfa
    scores = {}

    # --- ESPANSIONE: crescita alta, inflazione ok, bassa disoccupazione ---
    s = 0
    s += 35 if gdp >= 3.0 else (25 if gdp >= 2.0 else (10 if gdp >= 1.0 else 0))
    s += 30 if inf < 3.0 else (15 if inf < 4.5 else 0)
    s += 20 if un < 5.0 else (10 if un < 6.5 else 0)
    if gdp_trend and gdp_trend > 0: s += 8
    if inf_trend and inf_trend < 0: s += 7
    scores["Espansione"] = min(s, 100)

    # --- SURRISCALDAMENTO: crescita + inflazione alta ---
    s = 0
    s += 30 if gdp >= 2.0 else (15 if gdp >= 0.5 else 0)
    s += 40 if inf >= 5.0 else (30 if inf >= 3.5 else (10 if inf >= 2.5 else 0))
    s += 15 if un < 6.0 else (5 if un < 7.5 else 0)
    if gdp_trend and gdp_trend > 0: s += 5
    if inf_trend and inf_trend > 0: s += 10
    scores["Surriscaldamento"] = min(s, 100)

    # --- STAGFLAZIONE: PIL basso/negativo + inflazione alta ---
    s = 0
    s += 40 if gdp < 0 else (30 if gdp < 1.0 else (10 if gdp < 2.0 else 0))
    s += 40 if inf >= 5.0 else (25 if inf >= 3.5 else 0)
    s += 10 if un >= 7.0 else (5 if un >= 5.5 else 0)
    if gdp_trend and gdp_trend < 0: s += 5
    if inf_trend and inf_trend > 0: s += 5
    scores["Stagflazione"] = min(s, 100)

    # --- CONTRAZIONE / RECESSIONE: PIL negativo, alta disoccupazione ---
    s = 0
    s += 40 if gdp < 0 else (25 if gdp < 0.5 else (10 if gdp < 1.5 else 0))
    s += 30 if un >= 9.0 else (20 if un >= 7.0 else (10 if un >= 5.5 else 0))
    s += 15 if inf < 3.0 else 0   # contrazione tipicamente ha bassa inflazione
    if gdp_trend and gdp_trend < -0.5: s += 10
    if ca is not None and ca < -2: s += 5
    scores["Contrazione"] = min(s, 100)

    # --- RIPRESA: PIL in risalita, disoccupazione ancora alta ---
    s = 0
    s += 30 if 1.0 <= gdp <= 3.5 else (15 if 0.5 <= gdp < 1.0 else 0)
    s += 35 if 6.0 <= un <= 9.5 else (15 if 5.0 <= un < 6.0 else 0)
    s += 20 if inf < 4.0 else (5 if inf < 6.0 else 0)
    if gdp_trend and gdp_trend > 0.5: s += 15   # il trend in miglioramento è cruciale
    scores["Ripresa"] = min(s, 100)

    # --- DEFLAZIONE / STAGNAZIONE: PIL basso + inflazione < 0 ---
    s = 0
    s += 40 if inf < 0 else (20 if inf < 1.0 else 0)
    s += 30 if gdp < 1.0 else (10 if gdp < 2.0 else 0)
    s += 20 if un >= 7.0 else (10 if un >= 5.0 else 0)
    if gdp_trend and gdp_trend < 0: s += 10
    scores["Deflazione"] = min(s, 100)

    return scores, signals


# ── Dati storici del regime (multi-orizzonte) ─────────────────────────────────

def classify_regime_history(df_gdp: pd.DataFrame, df_inf: pd.DataFrame,
                             df_unemp: pd.DataFrame, horizon: int = 10) -> pd.DataFrame:
    """
    Classifica il regime economico anno per anno su un dato orizzonte storico.
    Ritorna un DataFrame con colonne: year, gdp, inf, un, regime, score_max
    """
    if any(df is None or df.empty for df in [df_gdp, df_inf, df_unemp]):
        return pd.DataFrame()

    cur_year = datetime.now().year
    start_y  = cur_year - horizon

    gdp_d  = df_gdp[df_gdp["year"]  >= start_y].set_index("year")["value"].to_dict()
    inf_d  = df_inf[df_inf["year"]   >= start_y].set_index("year")["value"].to_dict()
    un_d   = df_unemp[df_unemp["year"] >= start_y].set_index("year")["value"].to_dict()

    years = sorted(set(gdp_d.keys()) & set(inf_d.keys()) & set(un_d.keys()))
    rows  = []
    for i, yr in enumerate(years):
        g, v, u = gdp_d[yr], inf_d[yr], un_d[yr]
        prev_yr  = years[i-1] if i > 0 else None
        g_trend  = (g - gdp_d[prev_yr]) if prev_yr and prev_yr in gdp_d else None
        i_trend  = (v - inf_d[prev_yr]) if prev_yr and prev_yr in inf_d else None
        sc, _    = _regime_score(g, v, u, gdp_trend=g_trend, inf_trend=i_trend)
        best_reg = max(sc, key=sc.get)
        rows.append({"year": yr, "gdp": g, "inf": v, "un": u,
                     "regime": best_reg, "score": sc[best_reg]})
    return pd.DataFrame(rows)


def classify_regime(gdp: float, inf: float, un: float,
                    ca: float = None, debt: float = None,
                    gdp_trend: float = None, inf_trend: float = None) -> dict:
    """
    Classificazione avanzata con sistema a punteggio multi-dimensionale.
    Ritorna il regime con il punteggio più alto, la forza del segnale,
    e un secondo regime alternativo se lo scarto è piccolo.
    """
    REGIMES = {
        "Espansione": {
            "css":"b-expansion","icon":"🚀",
            "desc":"Crescita solida, inflazione contenuta, occupazione forte. Contesto ideale per asset rischiosi.",
            "fav":["Tecnologia","Finanziari","Industriali","Ciclici","Materiali"],
            "ev": ["Utilities","Beni di prima necessità"],
            "monitor": ["Ciclici","Tecnologia","Industriali"],
        },
        "Surriscaldamento": {
            "css":"b-peak","icon":"⚡",
            "desc":"Crescita positiva ma inflazione elevata. Attenzione alla stretta monetaria.",
            "fav":["Energia","Materiali","Finanziari","Real Estate"],
            "ev": ["Tecnologia","Bond lunghi","Ciclici"],
            "monitor": ["Energia","Materiali","Real Estate"],
        },
        "Stagflazione": {
            "css":"b-stagflation","icon":"⚠️",
            "desc":"Scenario difficile: PIL basso/negativo con inflazione alta. Capitale reale a rischio.",
            "fav":["Energia","Materiali","Beni di prima necessità","Utilities"],
            "ev": ["Tecnologia","Finanziari","Ciclici","Real Estate"],
            "monitor": ["Energia","Oro (GLD)","Beni di prima necessità"],
        },
        "Contrazione": {
            "css":"b-contraction","icon":"📉",
            "desc":"Crescita debole o negativa. Mercato in risk-off, liquidità preferita.",
            "fav":["Utilities","Healthcare","Beni di prima necessità","Comunicazioni"],
            "ev": ["Ciclici","Finanziari","Industriali","Real Estate"],
            "monitor": ["Utilities","Healthcare","Beni di prima necessità"],
        },
        "Ripresa": {
            "css":"b-recovery","icon":"🌱",
            "desc":"PIL in risalita, mercato del lavoro ancora in recupero. Opportunità nei ciclici.",
            "fav":["Ciclici","Finanziari","Tecnologia","Industriali","Materiali"],
            "ev": ["Utilities"],
            "monitor": ["Ciclici","Finanziari","Tecnologia"],
        },
        "Deflazione": {
            "css":"b-contraction","icon":"🧊",
            "desc":"Inflazione sotto zero, rischio stagnazione strutturale. Preferire qualità e dividendi.",
            "fav":["Utilities","Healthcare","Beni di prima necessità","Comunicazioni"],
            "ev": ["Materiali","Energia","Finanziari"],
            "monitor": ["Healthcare","Utilities","Tecnologia difensiva"],
        },
        "Fase incerta": {
            "css":"b-unknown","icon":"❓",
            "desc":"Segnali misti. Monitorare l'evoluzione dei principali indicatori.",
            "fav":["Healthcare","Utilities","Beni di prima necessità"],
            "ev": [],
            "monitor": ["Healthcare","Utilities","Beni di prima necessità","Comunicazioni"],
        },
    }

    scores, signals = _regime_score(gdp, inf, un, ca, debt, gdp_trend, inf_trend)
    sorted_regs     = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_name, best_score = sorted_regs[0]

    # Se il punteggio massimo è troppo basso → Fase incerta
    if best_score < 35:
        best_name = "Fase incerta"

    # Forza del regime
    if best_score >= 75:
        strength, strength_label, strength_color = 3, "FORTE", "#16a34a"
    elif best_score >= 50:
        strength, strength_label, strength_color = 2, "MODERATO", "#b8922a"
    else:
        strength, strength_label, strength_color = 1, "DEBOLE", "#dc2626"

    # Regime secondario: il secondo classificato se entro 20pt dal primo
    alt_name = None
    if len(sorted_regs) > 1:
        alt_nm, alt_sc = sorted_regs[1]
        if best_score - alt_sc <= 20 and alt_sc >= 25:
            alt_name = alt_nm

    reg = dict(REGIMES[best_name])
    reg.update({
        "name":           best_name,
        "score":          best_score,
        "strength":       strength,
        "strength_label": strength_label,
        "strength_color": strength_color,
        "all_scores":     scores,
        "signals":        signals,
        "alt_regime":     alt_name,
        "alt_score":      scores.get(alt_name, 0) if alt_name else 0,
    })
    return reg

import streamlit as st
import requests, pandas as pd, numpy as np, yfinance as yf
from datetime import datetime, timedelta

FMP_KEY = "nifHtWFpYxETOwULNyjRFzoqvrZHsqWo"   # ← sostituisci con key gratuita da financialmodelingprep.com

# ── Prezzi storici ETF ─────────────────────────────────────────────────────────

@st.cache_data(ttl=TTL["etf"], show_spinner=False)
def etf_history(ticker: str, years: int = 10) -> pd.DataFrame:
    try:
        end   = datetime.now()
        start = end - timedelta(days=years*365)
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        annual = df["Close"].resample("YE").last()
        ret    = annual.pct_change().dropna() * 100
        return pd.DataFrame({"year":ret.index.year,"return_pct":ret.values.flatten()})
    except: return pd.DataFrame()

@st.cache_data(ttl=TTL["etf"], show_spinner=False)
def etf_ytd(ticker: str) -> tuple:
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if hist.empty: return None,None,None
        price  = hist["Close"].iloc[-1]
        ytd_s  = hist[hist.index >= f"{datetime.now().year}-01-01"]["Close"]
        ytd_r  = ((ytd_s.iloc[-1]/ytd_s.iloc[0])-1)*100 if len(ytd_s)>1 else None
        r1y    = ((hist["Close"].iloc[-1]/hist["Close"].iloc[0])-1)*100
        return round(price,2), round(ytd_r,2) if ytd_r else None, round(r1y,2)
    except: return None,None,None

# ── Universo azioni ───────────────────────────────────────────────────────────

@st.cache_data(ttl=TTL["fundamentals"], show_spinner=False)
def sp500_list() -> pd.DataFrame:
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = tables[0][["Symbol","Security","GICS Sector"]]
        df.columns = ["ticker","name","sector_raw"]
        return df
    except: return pd.DataFrame()

def get_universe(cc: str, sector: str) -> pd.DataFrame:
    if cc=="US":
        df = sp500_list()
        if df.empty: return pd.DataFrame()
        gics = SECTOR_TO_GICS.get(sector, sector)
        return df[df["sector_raw"]==gics].copy().reset_index(drop=True)
    rows = CURATED_STOCKS.get(cc,[])
    if not rows: return pd.DataFrame()
    df = pd.DataFrame(rows, columns=["ticker","name","sector_raw"])
    return df[df["sector_raw"]==sector].reset_index(drop=True)

# ── Fondamentali multi-fonte ──────────────────────────────────────────────────

@st.cache_data(ttl=TTL["fundamentals"], show_spinner=False)
def _fmp(ticker: str) -> dict:
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={nifHtWFpYxETOwULNyjRFzoqvrZHsqWo}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code!=200: return {}
        d = r.json()
        if not d or not isinstance(d,list): return {}
        d=d[0]
        return {
            "name":d.get("companyName","—"),"price":d.get("price"),
            "mktcap":d.get("mktCap"),"pe":d.get("pe"),
            "profit_margin":(d.get("netProfitMargin") or 0)*100 if d.get("netProfitMargin") else None,
            "div_yield":(d.get("lastDiv")/d.get("price")*100) if (d.get("lastDiv") and d.get("price")) else None,
            "beta":d.get("beta"),"currency":d.get("currency","USD"),
            "sector":d.get("sector","—"),"_source":"FMP",
        }
    except: return {}

@st.cache_data(ttl=TTL["fundamentals"], show_spinner=False)
def get_fundamentals(ticker: str) -> dict:
    result = {}
    try:
        t    = yf.Ticker(ticker)
        info = t.info
        fcf    = info.get("freeCashflow")
        mktcap = info.get("marketCap")
        shares = info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")
        # Revenue growth
        try:
            fin = t.financials
            if fin is not None and not fin.empty and "Total Revenue" in fin.index:
                rev = fin.loc["Total Revenue"].dropna()
                rev_g = ((rev.iloc[0]/rev.iloc[1])-1)*100 if len(rev)>=2 else None
            else: rev_g = None
        except: rev_g = None
        # FCF per share
        try:
            cf = t.cashflow
            if cf is not None and not cf.empty:
                ocf = cf.loc["Operating Cash Flow"].dropna().iloc[0] if "Operating Cash Flow" in cf.index else None
                cap = cf.loc["Capital Expenditure"].dropna().iloc[0] if "Capital Expenditure" in cf.index else None
                fcf_act = float(ocf+cap) if (ocf is not None and cap is not None) else fcf
            else: fcf_act = fcf
        except: fcf_act = fcf

        result = {
            "name":         info.get("shortName") or info.get("longName","—"),
            "price":        info.get("currentPrice") or info.get("regularMarketPrice"),
            "mktcap":       mktcap,"shares":shares,
            "pe":           info.get("trailingPE"),
            "pb":           info.get("priceToBook"),
            "ps":           info.get("priceToSalesTrailing12Months"),
            "ev_ebitda":    info.get("enterpriseToEbitda"),
            "roe":          (info.get("returnOnEquity") or 0)*100    if info.get("returnOnEquity")  else None,
            "roa":          (info.get("returnOnAssets") or 0)*100    if info.get("returnOnAssets")  else None,
            "profit_margin":(info.get("profitMargins") or 0)*100     if info.get("profitMargins")   else None,
            "div_yield":    (info.get("dividendYield") or 0)*100     if info.get("dividendYield")   else None,
            "debt_equity":  info.get("debtToEquity"),
            "fcf_yield":    (fcf_act/mktcap*100) if (fcf_act and mktcap and mktcap>0) else None,
            "rev_growth":   rev_g,
            "beta":         info.get("beta"),
            "eps":          info.get("trailingEps"),
            "bvps":         info.get("bookValue"),
            "div_rate":     info.get("dividendRate") or 0,
            "payout_ratio": info.get("payoutRatio") or 0,
            "fcf_per_share":(fcf_act/shares) if (fcf_act and shares and shares>0) else None,
            "currency":     info.get("currency","USD"),
            "sector":       info.get("sector","—"),
            "analyst_target":info.get("targetMeanPrice"),
            "52w_high":     info.get("fiftyTwoWeekHigh"),
            "52w_low":      info.get("fiftyTwoWeekLow"),
            "longDesc":     (info.get("longBusinessSummary","")[:280]+"…") if info.get("longBusinessSummary") else "—",
            "_source":      "yfinance",
        }
    except: pass

    # Fallback FMP per campi mancanti
    missing = [k for k in ["pe","pb","roe","roa","profit_margin","price"] if not result.get(k)]
    if missing or not result.get("price"):
        fmp = _fmp(ticker)
        if fmp:
            for f in missing:
                if fmp.get(f) is not None and not result.get(f):
                    result[f] = fmp[f]
            if not result.get("price") and fmp.get("price"):
                result["price"] = fmp["price"]
            if result.get("_source"): result["_source"] += "+FMP"
            else: result["_source"] = "FMP"

    # P/S derivato
    if not result.get("ps") and result.get("mktcap"):
        try:
            rev = yf.Ticker(ticker).info.get("totalRevenue")
            if rev and rev>0: result["ps"] = result["mktcap"]/rev
        except: pass

    key_fields = ["pe","pb","ps","ev_ebitda","roe","roa","profit_margin",
                  "div_yield","debt_equity","fcf_yield","rev_growth"]
    filled = sum(1 for f in key_fields if result.get(f) is not None)
    result["_quality"] = round(filled/len(key_fields)*100)
    result["_missing"] = [f for f in key_fields if result.get(f) is None]
    return result

@st.cache_data(ttl=TTL["equity_price"], show_spinner=False)
def get_price_history(ticker: str, years: int = 5) -> pd.DataFrame:
    try:
        return yf.Ticker(ticker).history(period=f"{years}y")
    except: return pd.DataFrame()

# ── Indicatori tecnici ────────────────────────────────────────────────────────

def compute_technicals(hist: pd.DataFrame) -> dict:
    """Calcola RSI, MACD, SMA20/50/200, Bollinger Bands, Volume medio."""
    if hist is None or len(hist)<30: return {}
    close = hist["Close"].squeeze()
    out   = {}
    # SMA
    out["sma20"]  = close.rolling(20).mean().iloc[-1]
    out["sma50"]  = close.rolling(50).mean().iloc[-1]
    out["sma200"] = close.rolling(200).mean().iloc[-1] if len(close)>=200 else None
    # RSI 14
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain/loss
    out["rsi"] = float(100 - 100/(1+rs.iloc[-1]))
    # MACD
    ema12 = close.ewm(span=12,adjust=False).mean()
    ema26 = close.ewm(span=26,adjust=False).mean()
    macd  = ema12 - ema26
    signal= macd.ewm(span=9,adjust=False).mean()
    out["macd"]        = float(macd.iloc[-1])
    out["macd_signal"] = float(signal.iloc[-1])
    out["macd_hist"]   = float((macd-signal).iloc[-1])
    # Bollinger Bands (20, 2σ)
    sma20    = close.rolling(20).mean()
    std20    = close.rolling(20).std()
    out["bb_upper"] = float((sma20+2*std20).iloc[-1])
    out["bb_lower"] = float((sma20-2*std20).iloc[-1])
    out["bb_mid"]   = float(sma20.iloc[-1])
    # Volume
    if "Volume" in hist.columns:
        out["vol_avg20"] = float(hist["Volume"].rolling(20).mean().iloc[-1])
        out["vol_last"]  = float(hist["Volume"].iloc[-1])
    return out

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

def _navbar():
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

import streamlit as st
import pandas as pd
from datetime import datetime

def _page_macro():
    _navbar()

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
        # Calcola trend: variazione vs anno precedente
        def _prev_val(df):
            if df is None or df.empty or len(df) < 2: return None
            return df.iloc[-2]["value"] if isinstance(df, pd.DataFrame) else None

        gv_prev = _prev_val(df_gdp);  gdp_trend = (gv - gv_prev) if gv_prev is not None else None
        iv_prev = _prev_val(df_inf);  inf_trend = (iv - iv_prev) if iv_prev is not None else None

        reg = classify_regime(gv, iv, uv, ca=cv, debt=dv, gdp_trend=gdp_trend, inf_trend=inf_trend)
        st.session_state.regime = reg

        if used_fb:
            st.markdown('<div class="warn">⚠️ Alcuni dati integrati con stime IMF/OCSE 2023 — classificazione indicativa.</div>',
                        unsafe_allow_html=True)

        # ── CARD PRINCIPALE REGIME ──────────────────────────────────────────
        rc1, rc2 = st.columns([1, 2])
        with rc1:
            # Barra forza regime
            pct = reg["score"]
            bar_color = reg["strength_color"]
            st.markdown(f'''<div class="card">
                <div class="label">Regime identificato</div>
                <div style="margin:10px 0;"><span class="badge {reg['css']}">{reg['icon']} {reg['name']}</span></div>
                <div style="font-size:13px;color:#6b7280;line-height:1.6;">{reg['desc']}</div>
                <div style="margin:12px 0 4px;">
                    <div style="display:flex;justify-content:space-between;font-family:DM Mono;font-size:10px;color:#9ca3af;margin-bottom:4px;">
                        <span>FORZA DEL SEGNALE</span>
                        <span style="color:{bar_color};font-weight:600;">{reg["strength_label"]} ({pct:.0f}/100)</span>
                    </div>
                    <div style="background:#f3f4f6;border-radius:99px;height:8px;overflow:hidden;">
                        <div style="background:{bar_color};width:{pct}%;height:100%;border-radius:99px;transition:width .4s;"></div>
                    </div>
                </div>
                <div style="font-family:DM Mono;font-size:10px;color:#d1d5db;margin-top:8px;">
                    PIL:{gv:.1f}% · Inf:{iv:.1f}% · Disoc:{uv:.1f}%
                    {f"· CC:{cv:.1f}%" if cv is not None else ""}
                </div>
                {f'<div style="margin-top:8px;padding:6px 10px;background:#fffbeb;border-radius:6px;font-family:DM Mono;font-size:10px;color:#b8922a;">⚡ Possibile: {reg["alt_regime"]} ({reg["alt_score"]:.0f}pt)</div>' if reg.get("alt_regime") else ""}
            </div>''', unsafe_allow_html=True)

        with rc2:
            ca_col, cb_col, cc_col = st.columns(3)
            with ca_col:
                st.markdown('<div class="label" style="color:#16a34a;margin-bottom:6px;">✅ FAVORITI</div>', unsafe_allow_html=True)
                st.markdown("".join([f'<span class="tag tag-green">{s}</span>' for s in reg["fav"]]), unsafe_allow_html=True)
            with cb_col:
                st.markdown('<div class="label" style="color:#dc2626;margin-bottom:6px;">⛔ EVITARE</div>', unsafe_allow_html=True)
                st.markdown("".join([f'<span class="tag tag-red">{s}</span>' for s in reg["ev"]]) or '<span class="tag">—</span>', unsafe_allow_html=True)
            with cc_col:
                st.markdown('<div class="label" style="color:#3b82f6;margin-bottom:6px;">👁 MONITORARE</div>', unsafe_allow_html=True)
                st.markdown("".join([f'<span class="tag" style="background:#eff6ff;border-color:#93c5fd;color:#1d4ed8;">{s}</span>' for s in reg.get("monitor",[])]), unsafe_allow_html=True)

        # ── SEGNALI DETTAGLIO ────────────────────────────────────────────────
        if reg.get("signals"):
            sig_icons = {"green":"🟢","yellow":"🟡","orange":"🟠","red":"🔴"}
            st.markdown('<div style="margin:10px 0 4px;font-family:DM Mono;font-size:10px;color:#9ca3af;letter-spacing:.1em;">SEGNALI DIAGNOSTICI</div>', unsafe_allow_html=True)
            sig_html = " &nbsp;·&nbsp; ".join(
                f'<span style="font-family:DM Mono;font-size:11px;">{v[0]} {v[1]}</span>'
                for v in reg["signals"].values()
            )
            st.markdown(f'<div style="line-height:2;">{sig_html}</div>', unsafe_allow_html=True)

        # ── SCORE COMPARATIVO REGIMI ─────────────────────────────────────────
        with st.expander("📊 Punteggi comparativi tutti i regimi", expanded=False):
            all_sc = reg.get("all_scores", {})
            if all_sc:
                sorted_sc = sorted(all_sc.items(), key=lambda x: x[1], reverse=True)
                regime_icons = {"Espansione":"🚀","Surriscaldamento":"⚡","Stagflazione":"⚠️",
                                "Contrazione":"📉","Ripresa":"🌱","Deflazione":"🧊","Fase incerta":"❓"}
                score_cols = st.columns(len(sorted_sc))
                for col, (rn, rs) in zip(score_cols, sorted_sc):
                    ic = regime_icons.get(rn, "•")
                    bar_c = "#16a34a" if rs >= 65 else ("#b8922a" if rs >= 40 else "#d1d5db")
                    col.markdown(f'''
                    <div style="text-align:center;padding:8px 4px;">
                        <div style="font-size:16px;">{ic}</div>
                        <div style="font-family:DM Mono;font-size:9px;color:#9ca3af;margin:2px 0;">{rn}</div>
                        <div style="font-family:DM Mono;font-size:14px;font-weight:600;color:{bar_c};">{rs:.0f}</div>
                        <div style="background:#f3f4f6;border-radius:4px;height:4px;margin-top:3px;overflow:hidden;">
                            <div style="background:{bar_c};width:{rs}%;height:100%;"></div>
                        </div>
                    </div>''', unsafe_allow_html=True)

        # ── ANALISI STORICA MULTI-ORIZZONTE ──────────────────────────────────
        st.markdown('<div class="section">📅 Analisi Storica del Regime (multi-orizzonte)</div>', unsafe_allow_html=True)
        tab5, tab10, tab20 = st.tabs(["⏱ 5 anni", "📆 10 anni", "🗓 20 anni"])
        for tab_obj, horizon in [(tab5,5),(tab10,10),(tab20,20)]:
            with tab_obj:
                df_hist = classify_regime_history(df_gdp, df_inf, df_unemp, horizon=horizon)
                if df_hist.empty:
                    st.markdown('<div class="warn">Dati storici insufficienti per questo orizzonte.</div>', unsafe_allow_html=True)
                else:
                    # Distribuzione regimi
                    reg_counts = df_hist["regime"].value_counts()
                    st.markdown(f'<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;margin-bottom:8px;">Distribuzione regime su {len(df_hist)} anni disponibili</div>', unsafe_allow_html=True)
                    pie_cols = st.columns(len(reg_counts))
                    ric2 = {"Espansione":"#16a34a","Surriscaldamento":"#eab308","Stagflazione":"#8b5cf6",
                            "Contrazione":"#dc2626","Ripresa":"#3b82f6","Deflazione":"#6b7280","Fase incerta":"#9ca3af"}
                    for col_i, (rname, cnt) in zip(pie_cols, reg_counts.items()):
                        pct_h = cnt / len(df_hist) * 100
                        rc = ric2.get(rname, "#9ca3af")
                        col_i.markdown(f'''
                        <div style="text-align:center;padding:6px 2px;">
                            <div style="font-size:11px;color:{rc};font-family:DM Mono;font-weight:600;">{pct_h:.0f}%</div>
                            <div style="font-size:9px;color:#9ca3af;font-family:DM Mono;">{rname[:10]}</div>
                            <div style="font-size:9px;color:#d1d5db;font-family:DM Mono;">{cnt} ann{"o" if cnt==1 else "i"}</div>
                        </div>''', unsafe_allow_html=True)

                    # Timeline annuale
                    fig_tl = go.Figure()
                    reg_color_map = {"Espansione":"#16a34a","Surriscaldamento":"#eab308","Stagflazione":"#8b5cf6",
                                     "Contrazione":"#dc2626","Ripresa":"#3b82f6","Deflazione":"#6b7280","Fase incerta":"#9ca3af"}
                    for rn in df_hist["regime"].unique():
                        mask = df_hist["regime"] == rn
                        fig_tl.add_trace(go.Bar(
                            x=df_hist[mask]["year"],
                            y=df_hist[mask]["score"],
                            name=rn,
                            marker_color=reg_color_map.get(rn,"#9ca3af"),
                            text=df_hist[mask]["regime"],
                            textposition="inside",
                            textfont=dict(size=8, color="white", family="DM Mono"),
                            hovertemplate="<b>%{x}</b><br>Regime: " + rn + "<br>Score: %{y:.0f}<extra></extra>",
                        ))
                    fig_tl.update_layout(
                        barmode="stack", height=200,
                        margin=dict(l=0,r=0,t=6,b=0),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="DM Mono", color="#9ca3af", size=10),
                        xaxis=dict(showgrid=False, type="category"),
                        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="Score"),
                        showlegend=False,
                    )
                    st.plotly_chart(fig_tl, use_container_width=True,
                                    config={"displayModeBar": False}, key=f"hist_tl_{horizon}_{cc}")

                    # Tabella dati
                    with st.expander("Dati anno per anno", expanded=False):
                        df_show = df_hist[["year","regime","score","gdp","inf","un"]].copy()
                        df_show.columns = ["Anno","Regime","Score","PIL%","Inf%","Disoc%"]
                        df_show = df_show.sort_values("Anno", ascending=False).reset_index(drop=True)
                        st.dataframe(df_show.style.format({"Score":"{:.0f}","PIL%":"{:.1f}","Inf%":"{:.1f}","Disoc%":"{:.1f}"}),
                                     use_container_width=True, hide_index=True)

        st.markdown("")
        if st.button("▶️ Vai al Mattone 2 — Analisi Settoriale", type="primary"):
            st.session_state.page = "sectors"; st.rerun()
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

    # ── Analisi Trimestrale ──────────────────────────────────────────────────
    st.markdown('<div class="section">📅 Analisi Trimestrale (PIL & Inflazione)</div>', unsafe_allow_html=True)

    with st.spinner("Carico dati trimestrali OECD..."):
        gdp_q, cpi_q = get_quarterly_data(cc)

    if gdp_q.empty and cpi_q.empty:
        st.markdown('<div class="warn">⚠️ Dati trimestrali non disponibili per questo paese tramite OECD.</div>', unsafe_allow_html=True)
    else:
        n_qtrs = st.slider("Trimestri da mostrare", 8, 32, 16, 4, key="p1_qtrs")
        qcl, qcr = st.columns(2)

        def _qtrs_chart(df_q, color, title, unit="%"):
            df_q = df_q.tail(n_qtrs).copy() if not df_q.empty else df_q
            fig_q = go.Figure()
            if not df_q.empty:
                vals = df_q["value"].tolist()
                bar_colors = [color if v >= 0 else COLORS["red"] for v in vals]
                fig_q.add_trace(go.Bar(
                    x=df_q["period"], y=vals,
                    marker_color=bar_colors,
                    text=[f"{v:.1f}%" for v in vals],
                    textposition="outside",
                    textfont=dict(size=8, family="DM Mono"),
                    hovertemplate="<b>%{x}</b>: %{y:.2f}" + unit + "<extra></extra>",
                ))
                if len(vals) >= 4:
                    ma4 = pd.Series(vals).rolling(4).mean().tolist()
                    fig_q.add_trace(go.Scatter(
                        x=df_q["period"], y=ma4,
                        mode="lines", name="Media 4Q",
                        line=dict(color="#1a1a2e", width=1.5, dash="dot"),
                        hoverinfo="skip",
                    ))
            else:
                fig_q.add_annotation(text="N/D", showarrow=False, font=dict(color="#9ca3af", size=14))
            fig_q.update_layout(
                height=220, margin=dict(l=0,r=0,t=20,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Mono", color="#9ca3af", size=9),
                showlegend=False,
                xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=8)),
                yaxis=dict(showgrid=True, gridcolor="#f0f0f0", zeroline=True, zerolinecolor="#e5e7eb"),
                title=dict(text=title, font=dict(size=10, family="DM Mono", color="#9ca3af"), x=0),
            )
            return fig_q

        with qcl:
            st.plotly_chart(_qtrs_chart(gdp_q, CHART_COLORS["gdp"], "Crescita PIL Trimestrale (%)"),
                            use_container_width=True, config={"displayModeBar": False}, key=f"gdp_q_{cc}")
        with qcr:
            st.plotly_chart(_qtrs_chart(cpi_q, CHART_COLORS["inf"], "Inflazione CPI Trimestrale (%)"),
                            use_container_width=True, config={"displayModeBar": False}, key=f"cpi_q_{cc}")

        def _trend_diagnosis(df_q, label):
            if df_q.empty or len(df_q) < 2: return ""
            last2 = df_q["value"].tail(2).tolist()
            diff  = last2[-1] - last2[-2]
            if abs(diff) < 0.2: arrow, col = "→", "#9ca3af"
            elif diff > 0:      arrow, col = "▲", "#16a34a"
            else:               arrow, col = "▼", "#dc2626"
            return f'<span style="font-family:DM Mono;font-size:11px;color:{col};">{arrow} {label} ultimo trim: {last2[-1]:.1f}% ({diff:+.1f}pp vs trim prec.)</span>'

        diag_html = " &nbsp;|&nbsp; ".join(filter(None, [
            _trend_diagnosis(gdp_q, "PIL"),
            _trend_diagnosis(cpi_q, "CPI"),
        ]))
        if diag_html:
            st.markdown(f'<div style="margin-top:4px;">{diag_html}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:32px;">'
        'MATTONE 1 · FRED + IMF WEO + OECD + World Bank · Cache intelligente per tipo di dato</div>',
        unsafe_allow_html=True)

import streamlit as st
import plotly.graph_objects as go
import yfinance as yf, pandas as pd, numpy as np
from datetime import datetime

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

def _page_home():
    _navbar()
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

import streamlit as st, yfinance as yf, pandas as pd, numpy as np
import plotly.graph_objects as go
from datetime import datetime

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

def _page_heatmap():
    _navbar()
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

import streamlit as st, requests, pandas as pd
from datetime import datetime, timedelta

IMPACT_COLOR = {"Alto":"#dc2626","Medio":"#f97316","Basso":"#16a34a"}
IMPACT_ICON  = {"Alto":"🔴","Medio":"🟡","Basso":"🟢"}

@st.cache_data(ttl=3600*6, show_spinner=False)
def get_calendar_events(cc: str) -> list:
    """
    Usa l'API pubblica di Tradingeconomics (free tier limitato)
    o fallback con calendario statico aggiornato.
    """
    COUNTRY_MAP = {
        "US":"united states","DE":"germany","IT":"italy","FR":"france",
        "GB":"united kingdom","JP":"japan","CN":"china","ES":"spain",
        "CA":"canada","AU":"australia",
    }
    country_te = COUNTRY_MAP.get(cc,"united states")
    try:
        url = f"https://tradingeconomics.com/ws/calendar.aspx?c={country_te}&i=gdp,inflation+rate,unemployment+rate,interest+rate,retail+sales,pmi"
        headers = {"User-Agent":"Mozilla/5.0","Accept":"application/json"}
        r = requests.get(url, timeout=10, headers=headers)
        if r.status_code==200:
            data = r.json()
            events = []
            for d in data[:20]:
                events.append({
                    "date":      d.get("Date","")[:10],
                    "event":     d.get("Event","—"),
                    "actual":    d.get("Actual",""),
                    "forecast":  d.get("Forecast",""),
                    "previous":  d.get("Previous",""),
                    "impact":    "Alto" if any(k in d.get("Event","").lower()
                                               for k in ["gdp","cpi","inflation","nfp","unemployment","fomc","ecb","interest"])
                                 else "Medio",
                    "currency":  d.get("Currency",""),
                })
            return events
    except: pass
    # Fallback: calendario statico con i principali eventi ricorrenti
    return _static_calendar(cc)

def _static_calendar(cc: str) -> list:
    now   = datetime.now()
    month = now.month
    year  = now.year
    # Prossimi eventi standard per paese
    STANDARD_EVENTS = {
        "US":[
            {"event":"CPI (Inflazione USA)",      "impact":"Alto",  "freq":"Mensile",  "when":"~12 del mese"},
            {"event":"Non-Farm Payrolls",          "impact":"Alto",  "freq":"Mensile",  "when":"1° venerdì del mese"},
            {"event":"FOMC Meeting / Fed Rate",    "impact":"Alto",  "freq":"8x anno",  "when":"Vedi Fed calendar"},
            {"event":"GDP USA (stima)",            "impact":"Alto",  "freq":"Trimestrale","when":"Fine mese"},
            {"event":"Retail Sales",               "impact":"Medio", "freq":"Mensile",  "when":"~15 del mese"},
            {"event":"ISM Manufacturing PMI",      "impact":"Medio", "freq":"Mensile",  "when":"1° giorno lavorativo"},
            {"event":"Initial Jobless Claims",     "impact":"Medio", "freq":"Settimanale","when":"Ogni giovedì"},
            {"event":"University of Michigan Sentiment","impact":"Basso","freq":"Mensile","when":"~14 del mese"},
        ],
        "IT":[
            {"event":"PIL Italia (stima flash)",   "impact":"Alto",  "freq":"Trimestrale","when":"Fine trimestre"},
            {"event":"Inflazione CPI Italia",      "impact":"Alto",  "freq":"Mensile",  "when":"~20 del mese"},
            {"event":"BCE - Riunione tassi",       "impact":"Alto",  "freq":"8x anno",  "when":"Vedi BCE calendar"},
            {"event":"Disoccupazione Italia",      "impact":"Medio", "freq":"Mensile",  "when":"Fine mese"},
            {"event":"PMI Manifatturiero Italia",  "impact":"Medio", "freq":"Mensile",  "when":"1° giorno lavorativo"},
            {"event":"Inflazione Eurozona (flash)","impact":"Alto",  "freq":"Mensile",  "when":"~31 del mese"},
            {"event":"GDP Eurozona",               "impact":"Alto",  "freq":"Trimestrale","when":"Fine trimestre"},
        ],
        "DE":[
            {"event":"IFO Business Climate",       "impact":"Alto",  "freq":"Mensile",  "when":"~25 del mese"},
            {"event":"ZEW Economic Sentiment",     "impact":"Alto",  "freq":"Mensile",  "when":"~2° martedì"},
            {"event":"PIL Germania",               "impact":"Alto",  "freq":"Trimestrale","when":"Fine trimestre"},
            {"event":"Inflazione CPI Germania",    "impact":"Alto",  "freq":"Mensile",  "when":"~28 del mese"},
            {"event":"Disoccupazione Germania",    "impact":"Medio", "freq":"Mensile",  "when":"Fine mese"},
            {"event":"PMI Manifatturiero Germania","impact":"Medio", "freq":"Mensile",  "when":"1° giorno lavorativo"},
        ],
    }
    events = STANDARD_EVENTS.get(cc, STANDARD_EVENTS.get("US",[]))
    result = []
    for e in events:
        result.append({
            "date":     "Ricorrente",
            "event":    e["event"],
            "actual":   "—",
            "forecast": "—",
            "previous": "—",
            "impact":   e["impact"],
            "freq":     e.get("freq",""),
            "when":     e.get("when",""),
        })
    return result


def _page_calendar():
    _navbar()
    cc   = st.session_state.get("cc","US")
    name = st.session_state.get("country_name","🇺🇸 Stati Uniti")

    st.markdown(f"## 📅 Calendario Economico")
    st.markdown(f'<div class="label" style="margin-bottom:16px;">{name.upper()} · PROSSIME USCITE DATI RILEVANTI</div>',
                unsafe_allow_html=True)

    # ── Perché il calendario economico è importante ──
    st.markdown('''<div class="info">
    <b>Perché monitorare il calendario economico?</b><br>
    I dati macro (PIL, inflazione, lavoro) escono con cadenza fissa e possono
    <b>cambiare il regime economico</b> classificato nel Mattone 1.
    Un CPI più alto del previsto può spostare il regime da "Espansione" a "Surriscaldamento"
    e cambiare i settori favoriti nel Mattone 2.
    </div>''', unsafe_allow_html=True)

    # ── Frequenze di aggiornamento dati ──
    st.markdown('<div class="section">⏱️ Frequenza Aggiornamento Dati nell\'App</div>', unsafe_allow_html=True)
    freq_data = [
        ("🔵","PIL (GDP growth)",      "Trimestrale","90 giorni","World Bank / IMF WEO"),
        ("🔵","Debito Pubblico / PIL", "Trimestrale","90 giorni","World Bank"),
        ("🟡","Inflazione CPI",        "Mensile",    "30 giorni","FRED / IMF / OECD"),
        ("🟡","Disoccupazione",        "Mensile",    "30 giorni","FRED / IMF / OECD"),
        ("🟡","Conto Corrente",        "Trimestrale","90 giorni","World Bank"),
        ("🟢","Prezzi ETF e azioni",   "Giornaliero","4 ore",    "yfinance"),
        ("🟢","Fondamentali aziende",  "Trimestrale","7 giorni", "yfinance + FMP"),
        ("🟢","Notizie / Sentiment",   "Orario",     "1 ora",    "CNN F&G / RSS"),
    ]
    cols = st.columns([0.3,2,1.2,1,2])
    for h in ["","Indicatore","Frequenza reale","Cache app","Fonte"]:
        cols[["","Indicatore","Frequenza reale","Cache app","Fonte"].index(h)].markdown(
            f'<div class="label">{h}</div>', unsafe_allow_html=True)

    for dot,ind,freq,cache,fonte in freq_data:
        c1,c2,c3,c4,c5 = st.columns([0.3,2,1.2,1,2])
        c1.markdown(f'<div style="font-size:16px;margin:4px 0;">{dot}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="font-size:13px;font-weight:600;margin:4px 0;">{ind}</div>', unsafe_allow_html=True)
        c3.markdown(f'<div style="font-family:DM Mono;font-size:12px;color:#6b7280;margin:4px 0;">{freq}</div>', unsafe_allow_html=True)
        c4.markdown(f'<div style="font-family:DM Mono;font-size:12px;color:#b8922a;margin:4px 0;">{cache}</div>', unsafe_allow_html=True)
        c5.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin:4px 0;">{fonte}</div>', unsafe_allow_html=True)

    # ── Reset cache manuale ──
    st.markdown('<div class="section">🔄 Aggiornamento Manuale Cache</div>', unsafe_allow_html=True)
    st.markdown('''<div class="warn">
    I dati sono tenuti in cache per ridurre i tempi di caricamento.
    Se vuoi forzare un aggiornamento (es. dopo l'uscita di nuovi dati CPI),
    clicca il bottone qui sotto.
    </div>''', unsafe_allow_html=True)

    r1,r2,r3 = st.columns(3)
    with r1:
        if st.button("🔄 Svuota cache dati macro", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache svuotata! I dati verranno riscaricati al prossimo caricamento.")
    with r2:
        if st.button("📊 Svuota cache ETF/azioni", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache ETF svuotata!")
    with r3:
        if st.button("🗑️ Svuota tutta la cache", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.session_state.pop("m3_data",None)
            st.session_state.pop("m3_sector_loaded",None)
            st.session_state.pop("m4_loaded",None)
            st.session_state.pop("m4_cache_key",None)
            st.success("✅ Cache completa svuotata! Tutti i dati verranno riscaricati.")

    # ── Calendario eventi ──
    st.markdown('<div class="section">📋 Principali Appuntamenti Economici</div>', unsafe_allow_html=True)

    with st.spinner("Carico calendario..."):
        events = get_calendar_events(cc)

    if not events:
        st.info("Calendario non disponibile per questo paese.")
    else:
        for e in events:
            impact   = e.get("impact","Medio")
            ic       = IMPACT_COLOR.get(impact,"#9ca3af")
            ii       = IMPACT_ICON.get(impact,"⚪")
            actual   = e.get("actual","—")
            forecast = e.get("forecast","—")
            previous = e.get("previous","—")
            freq     = e.get("freq","")
            when     = e.get("when","")
            date_str = e.get("date","")

            # Colora actual vs forecast
            act_style = ""
            try:
                a_val = float(str(actual).replace("%","").replace(",","."))
                f_val = float(str(forecast).replace("%","").replace(",","."))
                act_style = f"color:{'#16a34a' if a_val>=f_val else '#dc2626'};font-weight:600;"
            except: pass

            st.markdown(f'''
            <div class="card" style="padding:12px 16px;margin:4px 0;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                    <div style="flex:1;min-width:180px;">
                        <div style="font-weight:600;font-size:14px;">{ii} {e["event"]}</div>
                        <div style="font-family:DM Mono;font-size:10px;color:#9ca3af;margin-top:3px;">
                            {date_str} {"· "+freq if freq else ""} {"· "+when if when else ""}
                        </div>
                    </div>
                    <div style="display:flex;gap:20px;font-family:DM Mono;font-size:12px;flex-wrap:wrap;">
                        <div style="text-align:center;">
                            <div style="font-size:9px;color:#9ca3af;margin-bottom:2px;">ATTUALE</div>
                            <div style="{act_style}">{actual if actual else "—"}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:9px;color:#9ca3af;margin-bottom:2px;">PREV.</div>
                            <div style="color:#b8922a;">{forecast if forecast else "—"}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:9px;color:#9ca3af;margin-bottom:2px;">PREC.</div>
                            <div style="color:#6b7280;">{previous if previous else "—"}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:9px;color:#9ca3af;margin-bottom:2px;">IMPATTO</div>
                            <div style="color:{ic};font-weight:600;">{impact}</div>
                        </div>
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)

    st.markdown(
        '<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:32px;">'
        'MACRO ANALYZER · CALENDARIO · TradingEconomics + Dati statici</div>',
        unsafe_allow_html=True)


def _page_sectors():
    _navbar()
    # ── Variabili di contesto da session state ──
    cc           = st.session_state.get("cc", "US")
    country_name = st.session_state.get("country_name", "🇺🇸 Stati Uniti")
    reg          = st.session_state.get("regime")
    sector       = st.session_state.get("selected_sector") or "Tecnologia"
    sector_map   = get_sector_map(cc)
    region_lbl   = get_region_label(cc)
    if reg is None:
        st.warning("⚠️ Completa prima il Mattone 1 per identificare il regime.")
        if st.button("◀️ Vai al Mattone 1"):
            st.session_state.page = "macro"; st.rerun()
        return
    reg_name     = reg["name"]
    theo_scores  = THEORETICAL_PERF.get(reg_name, THEORETICAL_PERF["Fase incerta"])
    # ── NAV RAPIDA MOBILE ──
    _nav_cols = st.columns(4)
    _pages    = [("🌍 Macro","mattone1"),("📊 Settori","mattone2"),("🔍 Screening","mattone3"),("🎯 Fair Value","mattone4")]
    _regime_ready = st.session_state.get("regime") is not None
    for _nc, (_lbl, _pg) in zip(_nav_cols, _pages):
        with _nc:
            _is_cur  = st.session_state.page == _pg
            _enabled = True if _pg == "mattone1" else _regime_ready
            if st.button(_lbl, key=f"topnav_{_pg}",
                         type="primary" if _is_cur else "secondary",
                         use_container_width=True,
                         disabled=not _enabled):
                st.session_state.page = _pg
                st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


    st.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:24px;">MATTONE 2 · REGIME: <span style="color:#b8922a;">{reg["icon"]} {reg_name}</span> · ETF: {region_lbl}</div>',unsafe_allow_html=True)

    # ── HEADER REGIME ──
    st.markdown('<div class="section-title">📍 Contesto di Regime</div>',unsafe_allow_html=True)
    col_reg, col_rad = st.columns([1, 1])
    with col_reg:
        fav_tags="".join([f'<span class="sector-tag-fav">{s}</span>' for s in reg["fav"]])
        ev_tags ="".join([f'<span class="sector-tag-ev">{s}</span>'  for s in reg["ev"]])
        st.markdown(f"""<div class="metric-card">
            <span class="regime-badge {reg['css']}">{reg['icon']} {reg_name}</span>
            <div style="font-size:13px;color:#6b7280;margin:12px 0 8px;">{reg['desc']}</div>
            <div style="font-family:DM Mono;font-size:10px;color:#16a34a;margin-bottom:4px;">✅ FAVORITI</div>
            {fav_tags}
            <div style="font-family:DM Mono;font-size:10px;color:#dc2626;margin:10px 0 4px;">⛔ DA EVITARE</div>
            {ev_tags}
        </div>""",unsafe_allow_html=True)
    with col_rad:
        st.markdown('<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;margin-bottom:4px;">SCORE TEORICO PER SETTORE (radar)</div>',unsafe_allow_html=True)
        st.plotly_chart(radar_chart(THEORETICAL_PERF.get(reg_name, {}), height=350), 
                use_container_width=True, key="radar_settori")

    # ── TABELLA SETTORI + DATI REALI ──
    st.markdown('<div class="section-title">📊 Performance Settoriale — Dati Reali vs Score Teorico</div>',unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:12px;">ETF utilizzati: {region_lbl} · Dati: yfinance · Score teorico: Fidelity/BofA/MSCI framework</div>',unsafe_allow_html=True)

    # Scarica tutti gli ETF
    with st.spinner("Scarico dati ETF... (in cache per 1h dopo il primo caricamento)"):
        etf_results = {}
        for sector, info in sector_map.items():
            price, ytd, ret_1y = etf_ytd(info["ticker"])
            etf_results[sector] = {
                "ticker": info["ticker"],
                "desc":   info["desc"],
                "price":  price,
                "ytd":    ytd,
                "ret_1y": ret_1y,
                "score":  theo_scores.get(sector, 0),
            }

    # Costruisce DataFrame di riepilogo
    rows=[]
    for sec,d in etf_results.items():
        rows.append({"Settore":sec,"Ticker":d["ticker"],"Descrizione":d["desc"],
                     "Prezzo":d["price"],"YTD %":d["ytd"],"1Y %":d["ret_1y"],
                     "Score":d["score"],"Label":SCORE_LABELS.get(d["score"],"—")})
    df_summary = pd.DataFrame(rows).sort_values("Score",ascending=False).reset_index(drop=True)

    # Render tabella custom
    for _, row in df_summary.iterrows():
        sec    = row["Settore"]
        score  = row["Score"]
        is_fav = sec in reg["fav"]
        is_ev  = sec in reg["ev"]
        is_sel = st.session_state.selected_sector == sec

        card_class = "sector-card-selected" if is_sel else "sector-card"
        border_extra = ""
        if is_fav:   border_extra = "border-left:4px solid #16a34a;"
        elif is_ev:  border_extra = "border-left:4px solid #dc2626;"

        score_color = "#16a34a" if score>0 else ("#dc2626" if score<0 else "#9ca3af")
        score_bar_w = int(abs(score)/5*100)
        score_bar_c = "#dcfce7" if score>0 else ("#fee2e2" if score<0 else "#f3f4f6")

        ytd_str = f"{row['YTD %']:+.1f}%" if row["YTD %"] is not None else "N/D"
        r1y_str = f"{row['1Y %']:+.1f}%"  if row["1Y %"]  is not None else "N/D"
        ytd_col = "#16a34a" if (row["YTD %"] or 0)>=0 else "#dc2626"
        r1y_col = "#16a34a" if (row["1Y %"]  or 0)>=0 else "#dc2626"

        regime_badge = ""
        if is_fav: regime_badge = '<span style="background:#dcfce7;color:#166534;border:1px solid #86efac;padding:2px 8px;border-radius:4px;font-size:10px;font-family:DM Mono;">✅ FAVORITO</span>'
        elif is_ev: regime_badge = '<span style="background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;padding:2px 8px;border-radius:4px;font-size:10px;font-family:DM Mono;">⛔ DA EVITARE</span>'

        st.markdown(f"""
        <div class="{card_class}" style="{border_extra}">
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
                <div style="flex:1;min-width:160px;">
                    <div style="font-family:'DM Serif Display',serif;font-size:16px;color:#1a1a2e;">{sec}</div>
                    <div style="font-family:DM Mono;font-size:10px;color:#9ca3af;margin-top:2px;">{row['Ticker']} · {row['Descrizione']}</div>
                    <div style="margin-top:6px;">{regime_badge}</div>
                </div>
                <div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap;">
                    <div style="text-align:center;">
                        <div style="font-family:DM Mono;font-size:9px;color:#9ca3af;">YTD</div>
                        <div style="font-family:'DM Serif Display',serif;font-size:18px;color:{ytd_col};">{ytd_str}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-family:DM Mono;font-size:9px;color:#9ca3af;">1 ANNO</div>
                        <div style="font-family:'DM Serif Display',serif;font-size:18px;color:{r1y_col};">{r1y_str}</div>
                    </div>
                    <div style="text-align:center;min-width:120px;">
                        <div style="font-family:DM Mono;font-size:9px;color:#9ca3af;">SCORE TEORICO</div>
                        <div style="font-family:DM Mono;font-size:13px;color:{score_color};font-weight:600;">{score:+d} · {row['Label']}</div>
                        <div style="background:#f3f4f6;border-radius:4px;height:6px;margin-top:4px;overflow:hidden;">
                            <div style="background:{score_color};width:{score_bar_w}%;height:100%;border-radius:4px;{'margin-left:auto;' if score<0 else ''}"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── SELEZIONE SETTORE ──
    st.markdown('<div class="section-title">🎯 Seleziona Settore per Approfondimento</div>',unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:12px;">Scegli un settore per vedere i rendimenti storici annuali dell\'ETF</div>',unsafe_allow_html=True)

    col_sel, col_btn = st.columns([3,1])
    with col_sel:
        sector_options = list(sector_map.keys())
        default_idx    = sector_options.index(st.session_state.selected_sector) if st.session_state.selected_sector in sector_options else 0
        chosen = st.selectbox("Settore da analizzare", sector_options, index=default_idx, key="sector_select")
    with col_btn:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("📈 Mostra storico", type="primary", use_container_width=True):
            st.session_state.selected_sector = chosen
            st.rerun()

    # ── STORICO ETF SELEZIONATO ──
    if st.session_state.selected_sector:
        sel = st.session_state.selected_sector
        if sel in sector_map:
            ticker = sector_map[sel]["ticker"]
            desc   = sector_map[sel]["desc"]
            score  = theo_scores.get(sel,0)
            score_lbl = SCORE_LABELS.get(score,"—")

            st.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#b8922a;margin:16px 0 8px;">📌 DETTAGLIO: {sel.upper()} · {ticker} · {desc}</div>',unsafe_allow_html=True)

            with st.spinner(f"Scarico storico {ticker}..."):
                df_hist = etf_history(ticker, years=10)

            dcol1, dcol2, dcol3 = st.columns(3)
            price, ytd, ret_1y  = etf_results.get(sel,{}).get("price",None), etf_results.get(sel,{}).get("ytd",None), etf_results.get(sel,{}).get("ret_1y",None)

            with dcol1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">💰 Ultimo prezzo</div>
                    <div class="metric-value">{"$"+str(price) if price else "N/D"}</div>
                </div>""",unsafe_allow_html=True)
            with dcol2:
                ytd_c="#16a34a" if (ytd or 0)>=0 else "#dc2626"
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">📅 Rendimento YTD</div>
                    <div class="metric-value" style="color:{ytd_c};">{f"{ytd:+.1f}%" if ytd else "N/D"}</div>
                </div>""",unsafe_allow_html=True)
            with dcol3:
                sc="#16a34a" if score>0 else ("#dc2626" if score<0 else "#9ca3af")
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">🧠 Score teorico (regime)</div>
                    <div class="metric-value" style="color:{sc};font-size:22px;">{score:+d} — {score_lbl}</div>
                </div>""",unsafe_allow_html=True)

            # grafico storico
            fig_bar = bar_chart(df_hist, height=250)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False}, key=f"bar_{sel}")

            # media storica
            if not df_hist.empty:
                avg = df_hist["return_pct"].mean()
                pos_years = (df_hist["return_pct"]>0).sum()
                tot_years = len(df_hist)
                st.markdown(f"""<div class="info-box">
                <b>📊 Statistiche storiche {ticker}:</b>&nbsp;&nbsp;
                Rendimento medio annuo: <b>{avg:+.1f}%</b> &nbsp;·&nbsp;
                Anni positivi: <b>{pos_years}/{tot_years}</b> &nbsp;·&nbsp;
                Rendimento 1 anno: <b>{f"{ret_1y:+.1f}%" if ret_1y else "N/D"}</b><br><br>
                <b>🧠 Interpretazione nel regime "{reg_name}":</b>&nbsp;
                Score teorico <b>{score:+d}</b> ({score_lbl}).
                {"Questo settore è storicamente favorito in questo regime." if score>=3 else
                 "Questo settore è neutro in questo regime." if score>=-1 else
                 "Questo settore è storicamente penalizzato in questo regime — valutare con cautela."}
                </div>""",unsafe_allow_html=True)

    st.markdown("")
    if st.button("◀️ Torna al Mattone 1", type="secondary"):
        st.session_state.page = "mattone1"
        st.rerun()

    st.markdown('<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:40px;">MACRO ANALYZER · MATTONE 2 · yfinance + Fidelity/BofA Sector Framework</div>',unsafe_allow_html=True)

def _page_screening():
    _navbar()
    # ── Variabili di contesto da session state ──
    cc           = st.session_state.get("cc", "US")
    country_name = st.session_state.get("country_name", "🇺🇸 Stati Uniti")
    reg          = st.session_state.get("regime")
    sector       = st.session_state.get("selected_sector") or "Tecnologia"
    if reg is None:
        st.warning("⚠️ Completa prima il Mattone 1 per identificare il regime.")
        if st.button("◀️ Vai al Mattone 1"):
            st.session_state.page = "macro"; st.rerun()
        return
    st.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:24px;">MATTONE 3 · SETTORE: <span style="color:#b8922a;">{sector}</span> · REGIME: {reg["icon"]} {reg["name"]}</div>', unsafe_allow_html=True)

    # ── UNIVERSO AZIONI PER PAESE ──────────────────────────────────────────────

    @st.cache_data(ttl=86400, show_spinner=False)
    def get_sp500_tickers() -> pd.DataFrame:
        """S&P 500 da Wikipedia con settore GICS."""
        try:
            tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
            df = tables[0][["Symbol","Security","GICS Sector"]]
            df.columns = ["ticker","name","sector_raw"]
            return df
        except:
            return pd.DataFrame()

    @st.cache_data(ttl=86400, show_spinner=False)
    def get_european_tickers(cc: str) -> pd.DataFrame:
        """Indici europei da Wikipedia."""
        urls = {
            "IT": ("https://en.wikipedia.org/wiki/FTSE_MIB",        0, ["ticker","name"],        ["Ticker","Company"]),
            "DE": ("https://en.wikipedia.org/wiki/DAX",              3, ["ticker","name"],        ["Ticker","Company"]),
            "FR": ("https://en.wikipedia.org/wiki/CAC_40",           2, ["ticker","name"],        ["Ticker","Company"]),
            "GB": ("https://en.wikipedia.org/wiki/FTSE_100_Index",   3, ["ticker","name"],        ["Ticker","Company"]),
            "ES": ("https://en.wikipedia.org/wiki/IBEX_35",          1, ["ticker","name"],        ["Ticker","Company"]),
            "NL": ("https://en.wikipedia.org/wiki/AEX_index",        1, ["ticker","name"],        ["Ticker","Company"]),
            "CH": ("https://en.wikipedia.org/wiki/Swiss_Market_Index",1,["ticker","name"],        ["Ticker","Company"]),
            "SE": ("https://en.wikipedia.org/wiki/OMX_Stockholm_30", 0, ["ticker","name"],        ["Ticker","Company"]),
        }
        # Fallback ticker lists curati per paese (suffisso borsa)
        CURATED = {
            "IT": [
                ("ENI.MI","Eni","Energia"),("ENEL.MI","Enel","Utilities"),
                ("ISP.MI","Intesa Sanpaolo","Finanziari"),("UCG.MI","UniCredit","Finanziari"),
                ("STM.MI","STMicroelectronics","Tecnologia"),("LDO.MI","Leonardo","Industriali"),
                ("MB.MI","Mediobanca","Finanziari"),("TIT.MI","Telecom Italia","Comunicazioni"),
                ("PRY.MI","Prysmian","Industriali"),("AZM.MI","Azimut","Finanziari"),
                ("RACE.MI","Ferrari","Ciclici"),("BMED.MI","Banca Mediolanum","Finanziari"),
                ("MONC.MI","Moncler","Ciclici"),("G.MI","Generali","Finanziari"),
                ("SRG.MI","Snam","Utilities"),("TRN.MI","Terna","Utilities"),
                ("BAMI.MI","Banco BPM","Finanziari"),("A2A.MI","A2A","Utilities"),
                ("PST.MI","Poste Italiane","Comunicazioni"),("STLAM.MI","Stellantis","Ciclici"),
            ],
            "DE": [
                ("SAP.DE","SAP","Tecnologia"),("SIE.DE","Siemens","Industriali"),
                ("ALV.DE","Allianz","Finanziari"),("DTE.DE","Deutsche Telekom","Comunicazioni"),
                ("BAYN.DE","Bayer","Healthcare"),("BMW.DE","BMW","Ciclici"),
                ("MBG.DE","Mercedes-Benz","Ciclici"),("VOW3.DE","Volkswagen","Ciclici"),
                ("DBK.DE","Deutsche Bank","Finanziari"),("BAS.DE","BASF","Materiali"),
                ("EOAN.DE","E.ON","Utilities"),("MRK.DE","Merck KGaA","Healthcare"),
                ("ADS.DE","Adidas","Ciclici"),("RWE.DE","RWE","Utilities"),
                ("HEN3.DE","Henkel","Beni di prima necessità"),("CON.DE","Continental","Ciclici"),
                ("FRE.DE","Fresenius","Healthcare"),("MUV2.DE","Munich Re","Finanziari"),
                ("IFX.DE","Infineon","Tecnologia"),("DHER.DE","Delivery Hero","Ciclici"),
            ],
            "FR": [
                ("OR.PA","L'Oréal","Beni di prima necessità"),("MC.PA","LVMH","Ciclici"),
                ("SAN.PA","Sanofi","Healthcare"),("TTE.PA","TotalEnergies","Energia"),
                ("AIR.PA","Airbus","Industriali"),("BNP.PA","BNP Paribas","Finanziari"),
                ("SU.PA","Schneider Electric","Industriali"),("AI.PA","Air Liquide","Materiali"),
                ("RI.PA","Pernod Ricard","Beni di prima necessità"),("KER.PA","Kering","Ciclici"),
                ("SGO.PA","Saint-Gobain","Materiali"),("CAP.PA","Capgemini","Tecnologia"),
                ("DG.PA","Vinci","Industriali"),("GLE.PA","Société Générale","Finanziari"),
                ("ACA.PA","Crédit Agricole","Finanziari"),("SG.PA","Stellantis","Ciclici"),
                ("VIV.PA","Vivendi","Comunicazioni"),("WLN.PA","Worldline","Tecnologia"),
                ("RNO.PA","Renault","Ciclici"),("EDF.PA","EDF","Utilities"),
            ],
            "GB": [
                ("SHEL.L","Shell","Energia"),("AZN.L","AstraZeneca","Healthcare"),
                ("HSBA.L","HSBC","Finanziari"),("ULVR.L","Unilever","Beni di prima necessità"),
                ("BP.L","BP","Energia"),("GSK.L","GSK","Healthcare"),
                ("LLOY.L","Lloyds Banking","Finanziari"),("DGE.L","Diageo","Beni di prima necessità"),
                ("RIO.L","Rio Tinto","Materiali"),("BATS.L","BAT","Beni di prima necessità"),
                ("GLEN.L","Glencore","Materiali"),("BT-A.L","BT Group","Comunicazioni"),
                ("VOD.L","Vodafone","Comunicazioni"),("BARC.L","Barclays","Finanziari"),
                ("AAL.L","Anglo American","Materiali"),("NG.L","National Grid","Utilities"),
                ("PRU.L","Prudential","Finanziari"),("REL.L","RELX","Industriali"),
                ("CCH.L","Coca-Cola HBC","Beni di prima necessità"),("CRH.L","CRH","Materiali"),
            ],
            "ES": [
                ("SAN.MC","Banco Santander","Finanziari"),("IBE.MC","Iberdrola","Utilities"),
                ("BBVA.MC","BBVA","Finanziari"),("ITX.MC","Inditex","Ciclici"),
                ("REP.MC","Repsol","Energia"),("TEF.MC","Telefónica","Comunicazioni"),
                ("CABK.MC","CaixaBank","Finanziari"),("AMS.MC","Amadeus","Tecnologia"),
                ("AENA.MC","AENA","Industriali"),("MAP.MC","MAPFRE","Finanziari"),
            ],
            "US": [],  # usa Wikipedia S&P500
        }

        rows = CURATED.get(cc, [])
        if rows:
            return pd.DataFrame(rows, columns=["ticker","name","sector_raw"])
        return pd.DataFrame()

    # Mapping settori nostri → GICS (per filtrare S&P 500)
    SECTOR_TO_GICS = {
        "Tecnologia":              "Information Technology",
        "Finanziari":              "Financials",
        "Energia":                 "Energy",
        "Healthcare":              "Health Care",
        "Industriali":             "Industrials",
        "Beni di prima necessità": "Consumer Staples",
        "Ciclici":                 "Consumer Discretionary",
        "Utilities":               "Utilities",
        "Materiali":               "Materials",
        "Real Estate":             "Real Estate",
        "Comunicazioni":           "Communication Services",
    }

    @st.cache_data(ttl=86400, show_spinner=False)
    def get_universe(cc: str, sector: str) -> pd.DataFrame:
        """Restituisce lista ticker filtrata per paese e settore."""
        if cc == "US":
            df = get_sp500_tickers()
            if df.empty: return pd.DataFrame()
            gics = SECTOR_TO_GICS.get(sector, sector)
            filtered = df[df["sector_raw"]==gics].copy()
            filtered["sector_raw"] = sector
            return filtered.reset_index(drop=True)
        else:
            df = get_european_tickers(cc)
            if df.empty: return pd.DataFrame()
            filtered = df[df["sector_raw"]==sector].copy()
            return filtered.reset_index(drop=True)

    # ── FETCH FONDAMENTALI ─────────────────────────────────────────────────────

    @st.cache_data(ttl=3600, show_spinner=False)
    def fetch_fundamentals(ticker: str) -> dict:
        """Scarica tutti i fondamentali via yfinance."""
        try:
            t    = yf.Ticker(ticker)
            info = t.info
            # Calcola FCF Yield
            fcf      = info.get("freeCashflow")
            mktcap   = info.get("marketCap")
            fcf_yield= (fcf / mktcap * 100) if (fcf and mktcap and mktcap > 0) else None
            # Revenue growth YoY
            try:
                fin = t.financials
                if fin is not None and not fin.empty and "Total Revenue" in fin.index:
                    rev = fin.loc["Total Revenue"].dropna()
                    rev_growth = ((rev.iloc[0]/rev.iloc[1])-1)*100 if len(rev)>=2 else None
                else:
                    rev_growth = None
            except:
                rev_growth = None

            return {
                "name":         info.get("shortName") or info.get("longName","—"),
                "price":        info.get("currentPrice") or info.get("regularMarketPrice"),
                "mktcap":       mktcap,
                "pe":           info.get("trailingPE"),
                "pb":           info.get("priceToBook"),
                "ps":           info.get("priceToSalesTrailing12Months"),
                "ev_ebitda":    info.get("enterpriseToEbitda"),
                "roe":          (info.get("returnOnEquity") or 0) * 100 if info.get("returnOnEquity") else None,
                "roa":          (info.get("returnOnAssets") or 0) * 100 if info.get("returnOnAssets") else None,
                "profit_margin":(info.get("profitMargins") or 0) * 100 if info.get("profitMargins") else None,
                "div_yield":    (info.get("dividendYield") or 0) * 100 if info.get("dividendYield") else None,
                "debt_equity":  info.get("debtToEquity"),
                "fcf_yield":    fcf_yield,
                "rev_growth":   rev_growth,
                "currency":     info.get("currency","USD"),
                "sector":       info.get("sector","—"),
            }
        except:
            return {}

    def score_stock(row: dict, medians: dict) -> float:
        """
        Score composito 0-100.
        Per ogni metrica: confronto col mediano di settore.
        Metriche "più basso è meglio": PE, PB, PS, EV/EBITDA, Debt/Equity
        Metriche "più alto è meglio": ROE, ROA, Profit Margin, FCF Yield, Div Yield, Rev Growth
        """
        points, total = 0.0, 0.0

        def add(val, med, higher_better=True, weight=1.0):
            nonlocal points, total
            if val is None or med is None or med == 0: return
            ratio = val / med
            if higher_better:
                score = min(ratio, 2.0) / 2.0   # 0-1
            else:
                score = min(1/ratio if ratio>0 else 0, 2.0) / 2.0
            points += score * weight
            total  += weight

        add(row.get("pe"),           medians.get("pe"),           higher_better=False, weight=1.5)
        add(row.get("pb"),           medians.get("pb"),           higher_better=False, weight=1.2)
        add(row.get("ps"),           medians.get("ps"),           higher_better=False, weight=1.0)
        add(row.get("ev_ebitda"),    medians.get("ev_ebitda"),    higher_better=False, weight=1.3)
        add(row.get("debt_equity"),  medians.get("debt_equity"),  higher_better=False, weight=0.8)
        add(row.get("roe"),          medians.get("roe"),          higher_better=True,  weight=1.5)
        add(row.get("roa"),          medians.get("roa"),          higher_better=True,  weight=1.2)
        add(row.get("profit_margin"),medians.get("profit_margin"),higher_better=True,  weight=1.2)
        add(row.get("fcf_yield"),    medians.get("fcf_yield"),    higher_better=True,  weight=1.3)
        add(row.get("div_yield"),    medians.get("div_yield"),    higher_better=True,  weight=0.8)
        add(row.get("rev_growth"),   medians.get("rev_growth"),   higher_better=True,  weight=1.0)

        return round((points / total) * 100, 1) if total > 0 else 0.0

    def fmt_val(v, decimals=1, suffix="", prefix=""):
        if v is None or (isinstance(v, float) and np.isnan(v)): return "—"
        return f"{prefix}{v:.{decimals}f}{suffix}"

    def color_vs_median(val, median, higher_better=True):
        if val is None or median is None: return "#9ca3af"
        better = val < median if not higher_better else val > median
        return "#16a34a" if better else "#dc2626"

    def fmt_mktcap(v):
        if v is None: return "—"
        if v >= 1e12: return f"${v/1e12:.1f}T"
        if v >= 1e9:  return f"${v/1e9:.1f}B"
        if v >= 1e6:  return f"${v/1e6:.1f}M"
        return f"${v:.0f}"

    # ── SIDEBAR MATTONE 3 ──────────────────────────────────────────────────────

    # Selezione settore (può cambiare qui)
    sector_list = list(SECTOR_TO_GICS.keys())
    if sector not in sector_list: sector_list.insert(0, sector)



    st.markdown('<div class="section-title">⚙️ Impostazioni Screening</div>', unsafe_allow_html=True)
    cfg1, cfg2, cfg3 = st.columns(3)
    with cfg1:
        sector = st.selectbox("Settore", sector_list,
                              index=sector_list.index(st.session_state.selected_sector)
                              if st.session_state.selected_sector in sector_list else 0,
                              key="m3_sector")
        st.session_state.selected_sector = sector
    with cfg2:
        show_undervalued = st.toggle("🔍 Solo sottovalutate", value=False)
    with cfg3:
        max_tickers = st.slider("Max azioni da analizzare", 5, 30, 15,
                                help="Più azioni = più tempo di caricamento")

    # ── CARICAMENTO UNIVERSO ──────────────────────────────────────────────────

    with st.spinner(f"Carico universo azioni — {sector} ({country_name})..."):
        universe = get_universe(cc, sector)

    if universe.empty:
        st.warning(f"Nessuna azione trovata per il settore **{sector}** in {country_name}. Prova un altro settore.")
        if st.button("◀️ Torna al Mattone 2", type="secondary"):
            st.session_state.page = "mattone2"
            st.rerun()
        st.stop()

    tickers_all = universe["ticker"].tolist()[:max_tickers]
    n_total     = len(tickers_all)

    st.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:8px;">Universo: <b style="color:#1a1a2e;">{n_total} azioni</b> · Settore: {sector} · Fonte: {"S&P 500 Wikipedia" if cc=="US" else "Indice locale"}</div>', unsafe_allow_html=True)

    # ── FETCH FONDAMENTALI CON PROGRESS BAR ───────────────────────────────────

    if "m3_data" not in st.session_state or st.session_state.get("m3_sector_loaded") != f"{cc}_{sector}_{max_tickers}":
        prog_bar  = st.progress(0, text="Scarico fondamentali...")
        fund_rows = []
        for i, tkr in enumerate(tickers_all):
            prog_bar.progress((i+1)/n_total, text=f"Scarico {tkr} ({i+1}/{n_total})...")
            data_f = fetch_fundamentals_enhanced(tkr)
            if data_f:
                data_f["ticker"] = tkr
                name_row = universe[universe["ticker"]==tkr]["name"].values
                data_f["display_name"] = name_row[0] if len(name_row) else data_f.get("name","—")
                fund_rows.append(data_f)
        prog_bar.empty()
        st.session_state.m3_data         = fund_rows
        st.session_state.m3_sector_loaded= f"{cc}_{sector}_{max_tickers}"
    else:
        fund_rows = st.session_state.m3_data

    if not fund_rows:
        st.error("Impossibile scaricare i fondamentali. Controlla la connessione e riprova.")
        st.stop()

    # ── CALCOLO MEDIANE DI SETTORE ────────────────────────────────────────────

    METRICS_NUM = ["pe","pb","ps","ev_ebitda","roe","roa","profit_margin",
                   "div_yield","debt_equity","fcf_yield","rev_growth"]

    def safe_median(rows, key):
        vals = [r[key] for r in rows if r.get(key) is not None and not (isinstance(r[key],float) and np.isnan(r[key]))]
        return float(np.median(vals)) if vals else None

    medians = {m: safe_median(fund_rows, m) for m in METRICS_NUM}

    # ── SCORE COMPOSITO ────────────────────────────────────────────────────────

    for r in fund_rows:
        r["score"] = score_stock(r, medians)

    # Ordina per score decrescente
    fund_rows_sorted = sorted(fund_rows, key=lambda x: x["score"], reverse=True)

    # Filtra sottovalutate (score >= 55)
    if show_undervalued:
        display_rows = [r for r in fund_rows_sorted if r["score"] >= 55]
    else:
        display_rows = fund_rows_sorted

    # ── MEDIANE DI SETTORE ─────────────────────────────────────────────────────

    st.markdown('<div class="section-title">📐 Mediane di Settore (benchmark di confronto)</div>', unsafe_allow_html=True)

    med_cols = st.columns(6)
    med_items = [
        ("P/E","pe","x"),("P/B","pb","x"),("P/S","ps","x"),
        ("EV/EBITDA","ev_ebitda","x"),("ROE","roe","%"),("ROA","roa","%"),
    ]
    for i,(label,key,suf) in enumerate(med_items):
        with med_cols[i]:
            v = medians.get(key)
            st.markdown(f"""<div class="metric-card" style="padding:12px 16px;">
                <div class="metric-label">{label} settore</div>
                <div style="font-family:'DM Serif Display',serif;font-size:22px;color:#b8922a;">{fmt_val(v,1,suf)}</div>
            </div>""", unsafe_allow_html=True)

    med_cols2 = st.columns(5)
    med_items2 = [
        ("Profit Margin","profit_margin","%"),("Div Yield","div_yield","%"),
        ("Debt/Equity","debt_equity","x"),("FCF Yield","fcf_yield","%"),
        ("Rev Growth","rev_growth","%"),
    ]
    for i,(label,key,suf) in enumerate(med_items2):
        with med_cols2[i]:
            v = medians.get(key)
            st.markdown(f"""<div class="metric-card" style="padding:12px 16px;">
                <div class="metric-label">{label} settore</div>
                <div style="font-family:'DM Serif Display',serif;font-size:22px;color:#b8922a;">{fmt_val(v,1,suf)}</div>
            </div>""", unsafe_allow_html=True)

    # ── TABELLA RISULTATI ──────────────────────────────────────────────────────

    n_shown = len(display_rows)
    n_under = len([r for r in fund_rows_sorted if r["score"] >= 55])

    st.markdown(f'<div class="section-title">{"🔍 Azioni Sottovalutate" if show_undervalued else "📋 Tabella Completa"} — {n_shown} titoli {"(filtrate)" if show_undervalued else ""}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:12px;">Score composito 0-100: confronto multimetrica vs mediana settore · 🟢 Verde = meglio del mediano · 🔴 Rosso = peggio del mediano</div>', unsafe_allow_html=True)

    if show_undervalued and n_shown == 0:
        st.info(f"Nessuna azione con score ≥ 55 nel settore {sector}. Prova a disattivare il filtro per vedere la tabella completa.")
    else:
        # Header tabella
        h = st.columns([2.2, 0.8, 0.7, 0.7, 0.7, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0])
        headers = ["Azienda","Mkt Cap","P/E","P/B","P/S","EV/EBITDA","ROE%","ROA%","Mrg%","DY%","D/E","FCF%","Score"]
        for col, hdr in zip(h, headers):
            col.markdown(f'<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;letter-spacing:.08em;padding:4px 0;border-bottom:1px solid #e5e7eb;">{hdr}</div>', unsafe_allow_html=True)

        for r in display_rows:
            score = r["score"]
            score_color = "#16a34a" if score >= 60 else ("#b8922a" if score >= 45 else "#dc2626")
            score_bg    = "#dcfce7" if score >= 60 else ("#fffbeb" if score >= 45 else "#fee2e2")

            def cv(val, key, hb=True):
                c = color_vs_median(val, medians.get(key), hb)
                return f'<span style="color:{c};font-family:DM Mono;font-size:12px;">{fmt_val(val,1)}</span>'

            cols_row = st.columns([2.2, 0.8, 0.7, 0.7, 0.7, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 1.0])
            with cols_row[0]:
                st.markdown(f"""<div style="padding:6px 0;border-bottom:1px solid #f3f4f6;">
                    <div style="font-family:'DM Sans',sans-serif;font-size:13px;font-weight:600;color:#1a1a2e;">{r.get('display_name','—')[:22]}</div>
                    <div style="font-family:DM Mono;font-size:10px;color:#9ca3af;">{r['ticker']}</div>
                </div>""", unsafe_allow_html=True)
            with cols_row[1]:
                st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #f3f4f6;font-family:DM Mono;font-size:11px;color:#6b7280;">{fmt_mktcap(r.get("mktcap"))}</div>', unsafe_allow_html=True)

            metric_pairs = [
                (cols_row[2],  r.get("pe"),           "pe",           False),
                (cols_row[3],  r.get("pb"),           "pb",           False),
                (cols_row[4],  r.get("ps"),           "ps",           False),
                (cols_row[5],  r.get("ev_ebitda"),    "ev_ebitda",    False),
                (cols_row[6],  r.get("roe"),          "roe",          True),
                (cols_row[7],  r.get("roa"),          "roa",          True),
                (cols_row[8],  r.get("profit_margin"),"profit_margin",True),
                (cols_row[9],  r.get("div_yield"),    "div_yield",    True),
                (cols_row[10], r.get("debt_equity"),  "debt_equity",  False),
                (cols_row[11], r.get("fcf_yield"),    "fcf_yield",    True),
            ]
            for col, val, key, hb in metric_pairs:
                with col:
                    st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #f3f4f6;">{cv(val,key,hb)}</div>', unsafe_allow_html=True)

            with cols_row[12]:
                _q = r.get("_quality",0)
                _q_color = "#16a34a" if _q>=70 else ("#b8922a" if _q>=40 else "#dc2626")
                st.markdown(f"""<div style="padding:6px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="background:{score_bg};color:{score_color};font-family:DM Mono;font-size:12px;font-weight:700;padding:3px 8px;border-radius:6px;">{score:.0f}</span>
                    <div style="font-family:DM Mono;font-size:9px;color:{_q_color};margin-top:3px;">dati {_q}%</div>
                </div>""", unsafe_allow_html=True)

    # ── CHART SCORE TOP 10 ─────────────────────────────────────────────────────

    st.markdown('<div class="section-title">🏆 Top 10 per Score Composito</div>', unsafe_allow_html=True)

    top10 = fund_rows_sorted[:10]
    if top10:
        names_top  = [r.get("display_name","—")[:18] for r in top10]
        scores_top = [r["score"] for r in top10]
        bar_colors = ["#16a34a" if s>=60 else ("#b8922a" if s>=45 else "#dc2626") for s in scores_top]

        fig_top = go.Figure(go.Bar(
            y=names_top[::-1], x=scores_top[::-1],
            orientation="h",
            marker_color=bar_colors[::-1],
            text=[f"{s:.0f}" for s in scores_top[::-1]],
            textposition="outside",
            textfont=dict(family="DM Mono", size=11),
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
        ))
        fig_top.add_vline(x=50, line_dash="dot", line_color="#d1d5db",
                          annotation_text="mediana", annotation_font_size=10,
                          annotation_font_color="#9ca3af")
        fig_top.update_layout(
            height=320, margin=dict(l=0,r=60,t=10,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Mono", color="#6b7280", size=11),
            xaxis=dict(range=[0,105], showgrid=True, gridcolor="#f0f0f0",
                       title="Score (0-100)", tickfont=dict(size=10)),
            yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#1a1a2e")),
            showlegend=False,
        )
        st.plotly_chart(fig_top, use_container_width=True,
                        config={"displayModeBar":False}, key="top10_bar")

    # ── SCATTER PE vs ROE ──────────────────────────────────────────────────────

    st.markdown('<div class="section-title">📈 Scatter P/E vs ROE — Mappa Valore/Qualità</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:8px;">In basso a destra = potenzialmente sottovalutate ad alta qualità · La dimensione della bolla = Market Cap</div>', unsafe_allow_html=True)

    scatter_rows = [r for r in fund_rows_sorted if r.get("pe") and r.get("roe") and r.get("mktcap")]
    if len(scatter_rows) >= 3:
        df_sc = pd.DataFrame(scatter_rows)
        fig_sc = go.Figure()
        for _, r in df_sc.iterrows():
            score = r["score"]
            color = "#16a34a" if score>=60 else ("#b8922a" if score>=45 else "#dc2626")
            size  = max(10, min(40, (np.log10(r["mktcap"]+1)-6)*8)) if r.get("mktcap") else 12
            fig_sc.add_trace(go.Scatter(
                x=[r["pe"]], y=[r["roe"]],
                mode="markers+text",
                marker=dict(size=size, color=color, opacity=0.75,
                            line=dict(width=1, color="white")),
                text=[r.get("display_name","")[:10]],
                textposition="top center",
                textfont=dict(size=9, family="DM Mono", color="#6b7280"),
                hovertemplate=(f"<b>{r.get('display_name','')}</b><br>"
                               f"P/E: {r['pe']:.1f}<br>ROE: {r['roe']:.1f}%<br>"
                               f"Score: {r['score']:.0f}<extra></extra>"),
                showlegend=False,
            ))

        # linee mediane
        if medians.get("pe"):
            fig_sc.add_vline(x=medians["pe"], line_dash="dot", line_color="#b8922a",
                             annotation_text=f"P/E med: {medians['pe']:.1f}",
                             annotation_font_size=10, annotation_font_color="#b8922a")
        if medians.get("roe"):
            fig_sc.add_hline(y=medians["roe"], line_dash="dot", line_color="#3b82f6",
                             annotation_text=f"ROE med: {medians['roe']:.1f}%",
                             annotation_font_size=10, annotation_font_color="#3b82f6")

        fig_sc.update_layout(
            height=380, margin=dict(l=0,r=0,t=10,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Mono", color="#9ca3af", size=10),
            xaxis=dict(title="P/E Ratio (< mediana = potenzialmente sottovalutata)",
                       showgrid=True, gridcolor="#f0f0f0", zeroline=False),
            yaxis=dict(title="ROE % (> mediana = alta qualità)",
                       showgrid=True, gridcolor="#f0f0f0", zeroline=False),
        )
        st.plotly_chart(fig_sc, use_container_width=True,
                        config={"displayModeBar":False}, key="scatter_pe_roe")

    # ── LEGENDA SCORE ──────────────────────────────────────────────────────────

    st.markdown("""<div class="info-box">
    <b>📖 Come leggere lo Score Composito (0-100):</b><br><br>
    <span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:4px;font-family:DM Mono;font-size:11px;">≥ 60 — Potenzialmente sottovalutata</span>&nbsp;
    <span style="background:#fffbeb;color:#854d0e;padding:2px 8px;border-radius:4px;font-family:DM Mono;font-size:11px;">45-59 — Nella norma</span>&nbsp;
    <span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:4px;font-family:DM Mono;font-size:11px;">&lt; 45 — Costosa o debole</span><br><br>
    Lo score confronta ogni metrica con la <b>mediana del settore</b>. I multipli (P/E, P/B, P/S, EV/EBITDA, Debt/Equity) premiano valori
    <i>inferiori</i> al mediano; la redditività (ROE, ROA, Profit Margin, FCF Yield, Rev Growth) premia valori <i>superiori</i>.<br><br>
    ⚠️ <b>Questo non è un consiglio di investimento.</b> Il fair value definitivo è nel Mattone 4.
    </div>""", unsafe_allow_html=True)

    # ── NAVIGAZIONE ───────────────────────────────────────────────────────────

    st.markdown("")
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("◀️ Torna al Mattone 2", type="secondary", use_container_width=True):
            st.session_state.page = "mattone2"
            st.rerun()
    with nav2:
        if st.button("▶️ Vai al Mattone 4 — Fair Value", type="primary", use_container_width=True):
            st.session_state.page = "mattone4"
            st.rerun()

    st.markdown('<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:40px;">MACRO ANALYZER · MATTONE 3 · yfinance · Score composito multimetrica vs mediana settore</div>', unsafe_allow_html=True)

def _page_fairvalue():
    _navbar()
    # ── Variabili di contesto da session state ──
    cc           = st.session_state.get("cc", "US")
    country_name = st.session_state.get("country_name", "🇺🇸 Stati Uniti")
    reg          = st.session_state.get("regime")
    sector       = st.session_state.get("selected_sector") or "Tecnologia"
    if reg is None:
        st.warning("⚠️ Completa prima il Mattone 1 per identificare il regime.")
        if st.button("◀️ Vai al Mattone 1"):
            st.session_state.page = "macro"; st.rerun()
        return
    st.markdown(
        f'''<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:24px;">'''
        f'''MATTONE 4 · SETTORE: <span style="color:#b8922a;">{sector}</span> · '''
        f'''REGIME: {reg["icon"]} {reg["name"]}</div>''',
        unsafe_allow_html=True)

    # ── HELPERS FONDAMENTALI (riusa fetch del Mattone 3) ──────────────────────

    @st.cache_data(ttl=3600, show_spinner=False)
    def get_full_data(ticker: str) -> dict:
        """Scarica info complete + financials + storia prezzi."""
        try:
            t    = yf.Ticker(ticker)
            info = t.info

            # Free Cash Flow
            fcf    = info.get("freeCashflow")
            mktcap = info.get("marketCap")
            shares = info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")

            # Financials per DCF e DDM
            try:
                fin   = t.financials
                cflow = t.cashflow
                # FCF per azione storico
                if cflow is not None and not cflow.empty:
                    ocf_row  = cflow.loc["Operating Cash Flow"]  if "Operating Cash Flow"  in cflow.index else None
                    capex_row= cflow.loc["Capital Expenditure"]  if "Capital Expenditure"  in cflow.index else None
                    if ocf_row is not None and capex_row is not None:
                        fcf_series = ocf_row + capex_row   # capex è negativo
                        fcf_latest = float(fcf_series.dropna().iloc[0]) if not fcf_series.dropna().empty else fcf
                    else:
                        fcf_latest = fcf
                else:
                    fcf_latest = fcf

                # Revenue growth
                if fin is not None and not fin.empty and "Total Revenue" in fin.index:
                    rev = fin.loc["Total Revenue"].dropna()
                    rev_growth = ((rev.iloc[0]/rev.iloc[1])-1) if len(rev)>=2 else 0.05
                else:
                    rev_growth = 0.05
            except:
                fcf_latest = fcf
                rev_growth = 0.05

            # Storico prezzi 5 anni
            hist = t.history(period="5y")

            # Dati dividendi
            div_rate = info.get("dividendRate") or 0.0
            div_yield= info.get("dividendYield") or 0.0

            return {
                "name":           info.get("shortName") or info.get("longName","—"),
                "ticker":         ticker,
                "price":          info.get("currentPrice") or info.get("regularMarketPrice"),
                "eps":            info.get("trailingEps"),
                "bvps":           info.get("bookValue"),
                "pe":             info.get("trailingPE"),
                "pb":             info.get("priceToBook"),
                "beta":           info.get("beta"),
                "mktcap":         mktcap,
                "shares":         shares,
                "fcf":            fcf_latest,
                "fcf_per_share":  (fcf_latest/shares) if (fcf_latest and shares and shares>0) else None,
                "div_rate":       div_rate,
                "div_yield":      div_yield * 100 if div_yield else 0,
                "payout_ratio":   info.get("payoutRatio") or 0,
                "roe":            (info.get("returnOnEquity") or 0)*100,
                "profit_margin":  (info.get("profitMargins") or 0)*100,
                "debt_equity":    info.get("debtToEquity"),
                "rev_growth":     float(rev_growth),
                "currency":       info.get("currency","USD"),
                "hist":           hist,
                "sector":         info.get("sector","—"),
                "longDesc":       info.get("longBusinessSummary","")[:300]+"…",
                "52w_high":       info.get("fiftyTwoWeekHigh"),
                "52w_low":        info.get("fiftyTwoWeekLow"),
                "analyst_target": info.get("targetMeanPrice"),
                "recommendation": info.get("recommendationMean"),   # 1=strong buy … 5=sell
            }
        except Exception as e:
            return {"error": str(e)}

    # ── MODELLI DI FAIR VALUE ─────────────────────────────────────────────────

    def dcf_model(fcf_per_share, growth_rate_5y, terminal_growth, wacc, years=5):
        """
        DCF a 2 stadi:
        - Fase 1: 5 anni con growth_rate_5y
        - Fase 2: crescita terminale perpetua
        """
        if not fcf_per_share or fcf_per_share <= 0:
            return None
        g1  = min(growth_rate_5y, 0.30)   # cap al 30%
        g2  = min(terminal_growth, 0.05)   # cap al 5%
        pv  = 0.0
        fcf = fcf_per_share
        for i in range(1, years+1):
            fcf *= (1 + g1)
            pv  += fcf / (1 + wacc)**i
        terminal_value = fcf * (1 + g2) / (wacc - g2)
        pv += terminal_value / (1 + wacc)**years
        return round(pv, 2)

    def graham_number(eps, bvps):
        """
        Graham Number = sqrt(22.5 * EPS * BVPS)
        Valido solo se EPS > 0 e BVPS > 0.
        """
        if not eps or not bvps or eps <= 0 or bvps <= 0:
            return None
        return round(math.sqrt(22.5 * eps * bvps), 2)

    def ddm_model(div_rate, roe, payout, cost_of_equity):
        """
        Gordon Growth Model (DDM):
        P = D1 / (Ke - g)
        g = ROE * retention_ratio
        Valido solo per azioni con dividendo.
        """
        if not div_rate or div_rate <= 0:
            return None
        retention = 1 - min(payout, 0.95)
        g = min((roe/100) * retention, 0.08)   # cap crescita 8%
        ke= cost_of_equity
        if ke <= g:
            ke = g + 0.02
        d1 = div_rate * (1 + g)
        return round(d1 / (ke - g), 2)

    def composite_fair_value(dcf_v, graham_v, ddm_v):
        """Media ponderata dei metodi disponibili."""
        vals, weights = [], []
        if dcf_v    and dcf_v > 0:    vals.append(dcf_v);    weights.append(3.0)
        if graham_v and graham_v > 0: vals.append(graham_v); weights.append(2.0)
        if ddm_v    and ddm_v > 0:    vals.append(ddm_v);    weights.append(1.5)
        if not vals: return None
        return round(sum(v*w for v,w in zip(vals,weights)) / sum(weights), 2)

    def get_recommendation(upside, beta, score_m3):
        """Raccomandazione finale basata su upside, rischio e score M3."""
        if upside is None: return "⚪ N/D", "#9ca3af", "#f3f4f6"
        risk = "alto" if (beta or 1) > 1.3 else ("medio" if (beta or 1) > 0.8 else "basso")
        if upside >= 30 and score_m3 >= 55:
            return "🟢 FORTE ACQUISTO", "#166534", "#dcfce7"
        elif upside >= 15 and score_m3 >= 45:
            return "🟢 ACQUISTO",       "#166534", "#dcfce7"
        elif upside >= 5:
            return "🟡 NEUTRO / ACCUMULA","#854d0e","#fef9c3"
        elif upside >= -10:
            return "🟠 MANTIENI",       "#92400e", "#ffedd5"
        elif upside < -10 and risk in ("alto","medio"):
            return "🔴 FORTE VENDITA",  "#991b1b", "#fee2e2"
        else:
            return "🔴 VENDITA",        "#991b1b", "#fee2e2"

    # ── SELEZIONE TICKER ──────────────────────────────────────────────────────



    st.markdown('<div class="section-title">🎯 Selezione Azioni da Analizzare</div>', unsafe_allow_html=True)

    # Top 5 dal Mattone 3
    m3_rows = st.session_state.get("m3_data", [])
    top5_auto = sorted(m3_rows, key=lambda x: x.get("score",0), reverse=True)[:5]
    top5_tickers = [r["ticker"] for r in top5_auto]

    col_auto, col_custom = st.columns([1,1])
    with col_auto:
        st.markdown('''<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;margin-bottom:8px;">TOP 5 DAL MATTONE 3 (per score composito)</div>''', unsafe_allow_html=True)
        if top5_auto:
            for r in top5_auto:
                st.markdown(
                    f'''<span style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;'''
                    f'''padding:4px 10px;margin:3px;font-family:DM Mono;font-size:12px;'''
                    f'''display:inline-block;color:#1a1a2e;">'''
                    f'''<b>{r["ticker"]}</b> · {r.get("display_name","")[:18]} · '''
                    f'''<span style="color:#16a34a;">Score {r.get("score",0):.0f}</span></span>''',
                    unsafe_allow_html=True)
        else:
            st.info("Completa il Mattone 3 per la selezione automatica.")

    with col_custom:
        st.markdown('''<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;margin-bottom:8px;">AGGIUNGI TICKER CUSTOM (separati da virgola)</div>''', unsafe_allow_html=True)
        custom_input = st.text_input("",
            placeholder="es. AAPL, MSFT, ENI.MI",
            label_visibility="collapsed", key="m4_custom")
        custom_tickers = [t.strip().upper() for t in custom_input.split(",") if t.strip()]

    # Unione ticker (deduplicati)
    all_tickers = list(dict.fromkeys(top5_tickers + custom_tickers))

    if not all_tickers:
        st.warning("Nessun ticker selezionato. Completa il Mattone 3 o inserisci ticker custom.")
        if st.button("◀️ Torna al Mattone 3", type="secondary"):
            st.session_state.page = "mattone3"
            st.rerun()
        st.stop()

    # ── PARAMETRI DCF ─────────────────────────────────────────────────────────

    st.markdown('<div class="section-title">⚙️ Parametri Valutazione</div>', unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        wacc = st.slider("WACC (%)", 6.0, 15.0, 9.0, 0.5,
                         help="Costo medio ponderato del capitale") / 100
    with p2:
        growth_5y = st.slider("Crescita FCF 5 anni (%)", 0.0, 30.0, 8.0, 0.5,
                               help="Tasso di crescita atteso nei prossimi 5 anni") / 100
    with p3:
        terminal_g = st.slider("Crescita terminale (%)", 1.0, 4.0, 2.5, 0.5,
                                help="Tasso di crescita perpetua dopo i 5 anni") / 100
    with p4:
        cost_equity = st.slider("Costo equity (%)", 6.0, 15.0, 10.0, 0.5,
                                 help="Usato nel DDM (Gordon Growth Model)") / 100

    st.markdown('''<div class="warn-box">⚠️ I parametri influenzano significativamente il fair value. WACC e crescita sono stime — modificali in base al settore e al regime macro corrente.</div>''', unsafe_allow_html=True)

    # ── CARICAMENTO DATI ──────────────────────────────────────────────────────

    cache_key = f"m4_{'_'.join(all_tickers)}"
    if st.session_state.get("m4_cache_key") != cache_key:
        prog = st.progress(0, text="Carico dati aziendali...")
        loaded = {}
        for i, tkr in enumerate(all_tickers):
            prog.progress((i+1)/len(all_tickers), text=f"Scarico {tkr}...")
            loaded[tkr] = get_full_data(tkr)
        prog.empty()
        st.session_state.m4_loaded    = loaded
        st.session_state.m4_cache_key = cache_key
    else:
        loaded = st.session_state.m4_loaded

    # ── DASHBOARD PER OGNI AZIONE ─────────────────────────────────────────────

    m3_scores = {r["ticker"]: r.get("score",0) for r in m3_rows}

    results_summary = []   # per tabella riepilogativa finale

    for tkr in all_tickers:
        d = loaded.get(tkr, {})
        if not d or "error" in d or not d.get("price"):
            st.warning(f"**{tkr}** — Dati non disponibili o ticker non valido.")
            continue

        price        = d["price"]
        score_m3     = m3_scores.get(tkr, 0)

        # ── Calcolo Fair Value ──
        dcf_fv     = dcf_model(d.get("fcf_per_share"), growth_5y, terminal_g, wacc)
        graham_fv  = graham_number(d.get("eps"), d.get("bvps"))
        ddm_fv     = ddm_model(d.get("div_rate"), d.get("roe"), d.get("payout_ratio"), cost_equity)
        comp_fv    = composite_fair_value(dcf_fv, graham_fv, ddm_fv)

        upside = ((comp_fv - price) / price * 100) if comp_fv and price > 0 else None
        rec_label, rec_text_color, rec_bg = get_recommendation(upside, d.get("beta"), score_m3)

        results_summary.append({
            "ticker": tkr, "name": d["name"], "price": price,
            "comp_fv": comp_fv, "upside": upside,
            "rec": rec_label, "rec_bg": rec_bg, "rec_tc": rec_text_color,
            "score_m3": score_m3,
        })

        # ── CARD INTESTAZIONE ──
        currency_sym = "€" if d.get("currency","USD") in ("EUR","GBP") else "$"
        upside_color = "#16a34a" if (upside or 0) > 5 else ("#dc2626" if (upside or 0) < -5 else "#b8922a")

        st.markdown(f'''
        <div style="background:#fff;border:2px solid #e5e7eb;border-radius:16px;
                    padding:20px 28px;margin:24px 0 12px;
                    box-shadow:0 2px 8px rgba(0,0,0,.07);">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                <div>
                    <div style="font-family:'DM Serif Display',serif;font-size:24px;color:#1a1a2e;">{d["name"]}</div>
                    <div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-top:2px;">{tkr} · {d["sector"]} · {d["currency"]}</div>
                    <div style="font-size:12px;color:#6b7280;margin-top:8px;max-width:500px;">{d.get("longDesc","")}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:DM Mono;font-size:10px;color:#9ca3af;">RACCOMANDAZIONE</div>
                    <div style="background:{rec_bg};color:{rec_text_color};font-family:DM Mono;
                                font-size:15px;font-weight:700;padding:8px 16px;border-radius:8px;margin-top:4px;">{rec_label}</div>
                    {f'<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;margin-top:6px;">Score M3: {score_m3:.0f}/100</div>' if score_m3 else ""}
                </div>
            </div>
        </div>''', unsafe_allow_html=True)

        # ── KPI ROW ──
        kpi_cols = st.columns(6)
        def kpi(col, label, val, suffix="", color="#1a1a2e", size="22px"):
            col.markdown(f'''<div class="metric-card" style="padding:12px 16px;text-align:center;">
                <div class="metric-label">{label}</div>
                <div style="font-family:'DM Serif Display',serif;font-size:{size};color:{color};">{val}{suffix}</div>
            </div>''', unsafe_allow_html=True)

        kpi(kpi_cols[0], "💰 Prezzo attuale",  f"{currency_sym}{price:.2f}")
        kpi(kpi_cols[1], "🎯 Fair Value comp.", f"{currency_sym}{comp_fv:.2f}" if comp_fv else "N/D", color="#b8922a")
        kpi(kpi_cols[2], "📈 Upside / Downside",
            f"{upside:+.1f}%" if upside is not None else "N/D",
            color=upside_color, size="20px")
        kpi(kpi_cols[3], "⚡ Beta",  f"{d['beta']:.2f}" if d.get("beta") else "N/D")
        kpi(kpi_cols[4], "🏛️ Mkt Cap",
            f"{d['mktcap']/1e12:.1f}T" if (d.get("mktcap") or 0)>=1e12
            else f"{d['mktcap']/1e9:.1f}B" if (d.get("mktcap") or 0)>=1e9
            else "N/D")
        kpi(kpi_cols[5], "📊 Score M3", f"{score_m3:.0f}/100" if score_m3 else "N/D",
            color="#16a34a" if score_m3>=60 else ("#b8922a" if score_m3>=45 else "#dc2626"))

        # ── DETTAGLIO FAIR VALUE ──
        st.markdown('<div class="section-title" style="margin-top:16px;">🧮 Dettaglio Metodi di Valutazione</div>', unsafe_allow_html=True)
        fv_cols = st.columns(4)

        def fv_card(col, method, value, desc, inputs, used):
            color  = "#b8922a" if used else "#9ca3af"
            bg     = "#fffbeb" if used else "#f9fafb"
            border = "#b8922a" if used else "#e5e7eb"
            val_str= f"{currency_sym}{value:.2f}" if value else "N/D (dati insuff.)"
            col.markdown(f'''<div style="background:{bg};border:1px solid {border};border-radius:10px;padding:14px 16px;height:100%;">
                <div style="font-family:DM Mono;font-size:10px;color:{color};letter-spacing:.1em;">{method}</div>
                <div style="font-family:'DM Serif Display',serif;font-size:22px;color:{color};margin:6px 0;">{val_str}</div>
                <div style="font-size:11px;color:#9ca3af;line-height:1.5;">{desc}</div>
                <div style="margin-top:8px;font-family:DM Mono;font-size:10px;color:#d1d5db;">{inputs}</div>
            </div>''', unsafe_allow_html=True)

        fcf_ps_str = f"{currency_sym}{d['fcf_per_share']:.2f}/sh" if d.get("fcf_per_share") else "FCF N/D"
        fv_card(fv_cols[0], "DCF — 2 STADI",
                dcf_fv,
                "Proietta FCF per 5 anni + valore terminale perpetuo. Metodo più completo.",
                f"FCF/sh: {fcf_ps_str} · g₁:{growth_5y*100:.1f}% · g∞:{terminal_g*100:.1f}% · WACC:{wacc*100:.1f}%",
                dcf_fv is not None)

        eps_str  = f"{currency_sym}{d['eps']:.2f}"  if d.get("eps")  else "N/D"
        bvps_str = f"{currency_sym}{d['bvps']:.2f}" if d.get("bvps") else "N/D"
        fv_card(fv_cols[1], "GRAHAM NUMBER",
                graham_fv,
                "√(22.5 × EPS × BVPS). Formula classica di Benjamin Graham per valore intrinseco.",
                f"EPS: {eps_str} · BVPS: {bvps_str}",
                graham_fv is not None)

        div_str = f"{currency_sym}{d['div_rate']:.2f}/yr" if d.get("div_rate") else "No dividendo"
        fv_card(fv_cols[2], "DDM — GORDON",
                ddm_fv,
                "D₁/(Ke−g). Valido per azioni con dividendo stabile. g = ROE × retention.",
                f"Div: {div_str} · ROE: {d.get('roe',0):.1f}% · Ke: {cost_equity*100:.1f}%",
                ddm_fv is not None)

        methods_used = sum([dcf_fv is not None, graham_fv is not None, ddm_fv is not None])
        fv_card(fv_cols[3], "FAIR VALUE COMPOSITO",
                comp_fv,
                f"Media ponderata dei {methods_used} metodi disponibili. DCF peso 3, Graham peso 2, DDM peso 1.5.",
                f"Upside: {upside:+.1f}%" if upside is not None else "",
                comp_fv is not None)

        # ── GRAFICO STORICO PREZZI + FAIR VALUE ──
        st.markdown('<div class="section-title" style="margin-top:16px;">📈 Storico Prezzi & Fair Value</div>', unsafe_allow_html=True)

        hist = d.get("hist", pd.DataFrame())
        if not hist.empty:
            fig_hist = go.Figure()

            # Prezzo storico
            fig_hist.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"].round(2),
                mode="lines", name="Prezzo",
                line=dict(color="#3b82f6", width=2),
                fill="tozeroy", fillcolor="rgba(59,130,246,0.05)",
                hovertemplate="<b>%{x|%d %b %Y}</b><br>Prezzo: " + currency_sym + "%{y:.2f}<extra></extra>",
            ))

            # Fair value composito
            if comp_fv:
                fig_hist.add_hline(y=comp_fv, line_dash="dash", line_color="#b8922a", line_width=2,
                                   annotation_text=f"Fair Value: {currency_sym}{comp_fv:.2f}",
                                   annotation_font_color="#b8922a", annotation_font_size=11,
                                   annotation_position="top right")

            # 52w high/low
            if d.get("52w_high"):
                fig_hist.add_hline(y=d["52w_high"], line_dash="dot", line_color="#dc2626", line_width=1,
                                   annotation_text=f"52W High: {currency_sym}{d['52w_high']:.2f}",
                                   annotation_font_color="#dc2626", annotation_font_size=10)
            if d.get("52w_low"):
                fig_hist.add_hline(y=d["52w_low"], line_dash="dot", line_color="#16a34a", line_width=1,
                                   annotation_text=f"52W Low: {currency_sym}{d['52w_low']:.2f}",
                                   annotation_font_color="#16a34a", annotation_font_size=10)

            # Analyst target
            if d.get("analyst_target"):
                fig_hist.add_hline(y=d["analyst_target"], line_dash="dot", line_color="#8b5cf6", line_width=1.5,
                                   annotation_text=f"Consensus: {currency_sym}{d['analyst_target']:.2f}",
                                   annotation_font_color="#8b5cf6", annotation_font_size=10,
                                   annotation_position="bottom right")

            fig_hist.update_layout(
                height=320, margin=dict(l=0,r=120,t=10,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Mono", color="#9ca3af", size=10), showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
                yaxis=dict(showgrid=True, gridcolor="#f0f0f0", zeroline=False,
                           tickprefix=currency_sym, tickfont=dict(size=10)),
            )
            st.plotly_chart(fig_hist, use_container_width=True,
                            config={"displayModeBar":False}, key=f"hist_{tkr}")

        # ── ANALISI RISCHIO ──
        st.markdown('<div class="section-title" style="margin-top:16px;">⚠️ Analisi del Rischio</div>', unsafe_allow_html=True)

        r1, r2, r3 = st.columns(3)

        # Volatilità storica
        if not hist.empty and len(hist) > 20:
            ret = hist["Close"].pct_change().dropna()
            vol_annual = ret.std() * np.sqrt(252) * 100
            sharpe_approx = ((ret.mean()*252)*100 - 4.5) / vol_annual if vol_annual > 0 else None
        else:
            vol_annual, sharpe_approx = None, None

        beta = d.get("beta")
        risk_level = "🟢 Basso" if (beta or 1) < 0.8 else ("🟡 Medio" if (beta or 1) < 1.3 else "🔴 Alto")

        with r1:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-label">📊 Volatilità Storica (ann.)</div>
                <div style="font-family:'DM Serif Display',serif;font-size:24px;color:#1a1a2e;">{f"{vol_annual:.1f}%" if vol_annual else "N/D"}</div>
                <div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-top:4px;">{"Alta" if (vol_annual or 0)>30 else "Media" if (vol_annual or 0)>15 else "Bassa"}</div>
            </div>''', unsafe_allow_html=True)

        with r2:
            beta_color = "#16a34a" if (beta or 1)<0.8 else ("#b8922a" if (beta or 1)<1.3 else "#dc2626")
            st.markdown(f'''<div class="metric-card">
                <div class="metric-label">⚡ Beta (vs mercato)</div>
                <div style="font-family:'DM Serif Display',serif;font-size:24px;color:{beta_color};">{f"{beta:.2f}" if beta else "N/D"}</div>
                <div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-top:4px;">Rischio: {risk_level}</div>
            </div>''', unsafe_allow_html=True)

        with r3:
            sharpe_color = "#16a34a" if (sharpe_approx or 0)>1 else ("#b8922a" if (sharpe_approx or 0)>0 else "#dc2626")
            st.markdown(f'''<div class="metric-card">
                <div class="metric-label">📐 Sharpe Ratio (approx.)</div>
                <div style="font-family:'DM Serif Display',serif;font-size:24px;color:{sharpe_color};">{f"{sharpe_approx:.2f}" if sharpe_approx else "N/D"}</div>
                <div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-top:4px;">Rf: 4.5% (approx)</div>
            </div>''', unsafe_allow_html=True)

        # Distribuzione rendimenti mensili
        if not hist.empty and len(hist) > 30:
            monthly = hist["Close"].resample("ME").last().pct_change().dropna() * 100
            fig_ret = go.Figure(go.Histogram(
                x=monthly.values, nbinsx=24,
                marker_color="#3b82f6", opacity=0.75,
                hovertemplate="Rendimento: %{x:.1f}%<br>Freq: %{y}<extra></extra>",
            ))
            fig_ret.add_vline(x=0, line_color="#dc2626", line_width=1.5, line_dash="dash")
            fig_ret.add_vline(x=float(monthly.mean()), line_color="#16a34a", line_width=1.5,
                              annotation_text=f"Media: {monthly.mean():.1f}%",
                              annotation_font_color="#16a34a", annotation_font_size=10)
            fig_ret.update_layout(
                height=200, margin=dict(l=0,r=0,t=10,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Mono", color="#9ca3af", size=10), showlegend=False,
                xaxis=dict(title="Rendimento mensile %", showgrid=False),
                yaxis=dict(title="Frequenza", showgrid=True, gridcolor="#f0f0f0"),
            )
            st.markdown('<div style="font-family:DM Mono;font-size:11px;color:#6b7280;margin:8px 0 2px;">Distribuzione Rendimenti Mensili (5 anni)</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_ret, use_container_width=True,
                            config={"displayModeBar":False}, key=f"ret_dist_{tkr}")

        # ── BOX RACCOMANDAZIONE FINALE ──
        st.markdown(f'''
        <div style="background:{rec_bg};border:2px solid {rec_text_color}33;border-radius:12px;
                    padding:20px 24px;margin:16px 0 32px;">
            <div style="font-family:DM Mono;font-size:10px;color:{rec_text_color};letter-spacing:.12em;margin-bottom:8px;">RACCOMANDAZIONE FINALE — {tkr}</div>
            <div style="font-family:'DM Serif Display',serif;font-size:26px;color:{rec_text_color};">{rec_label}</div>
            <div style="font-size:13px;color:#6b7280;margin-top:10px;line-height:1.7;">
                <b>Fair Value composito:</b> {f"{currency_sym}{comp_fv:.2f}" if comp_fv else "N/D"} &nbsp;|&nbsp;
                <b>Prezzo attuale:</b> {currency_sym}{price:.2f} &nbsp;|&nbsp;
                <b>Upside stimato:</b> <span style="color:{upside_color};font-weight:600;">{f"{upside:+.1f}%" if upside is not None else "N/D"}</span><br>
                <b>Rischio:</b> {risk_level} (Beta {f"{beta:.2f}" if beta else "N/D"}) &nbsp;|&nbsp;
                <b>Score fondamentale M3:</b> {score_m3:.0f}/100 &nbsp;|&nbsp;
                <b>Regime:</b> {reg["icon"]} {reg["name"]}<br><br>
                <span style="font-family:DM Mono;font-size:10px;color:#9ca3af;">
                ⚠️ Questo non è un consiglio di investimento. Il fair value è una stima basata su modelli quantitativi
                e parametri inseriti dall'utente. Effettua sempre una due diligence completa prima di investire.
                </span>
            </div>
        </div>''', unsafe_allow_html=True)

        st.markdown("<hr style='border:1px solid #f0f0f0;margin:8px 0;'>", unsafe_allow_html=True)

    # ── TABELLA RIEPILOGATIVA ─────────────────────────────────────────────────

    if len(results_summary) > 1:
        st.markdown('<div class="section-title">📋 Riepilogo Comparativo</div>', unsafe_allow_html=True)

        df_res = pd.DataFrame(results_summary)
        df_res = df_res.sort_values("upside", ascending=False).reset_index(drop=True)

        # Header
        hcols = st.columns([2, 1, 1, 1, 1, 1.5])
        for col, hdr in zip(hcols, ["Azienda","Prezzo","Fair Value","Upside","Score M3","Raccomandazione"]):
            col.markdown(f'<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;padding:4px 0;border-bottom:1px solid #e5e7eb;">{hdr}</div>', unsafe_allow_html=True)

        for _, row in df_res.iterrows():
            rc = st.columns([2, 1, 1, 1, 1, 1.5])
            up_c = "#16a34a" if (row["upside"] or 0)>5 else ("#dc2626" if (row["upside"] or 0)<-5 else "#b8922a")
            sc_c = "#16a34a" if row["score_m3"]>=60 else ("#b8922a" if row["score_m3"]>=45 else "#dc2626")
            with rc[0]:
                st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #f9fafb;font-size:13px;font-weight:600;">{row["name"][:20]}<br><span style="font-family:DM Mono;font-size:10px;color:#9ca3af;">{row["ticker"]}</span></div>', unsafe_allow_html=True)
            with rc[1]:
                st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #f9fafb;font-family:DM Mono;font-size:12px;">{f"{row['price']:.2f}" if row["price"] else "—"}</div>', unsafe_allow_html=True)
            with rc[2]:
                st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #f9fafb;font-family:DM Mono;font-size:12px;color:#b8922a;">{f"{row['comp_fv']:.2f}" if row["comp_fv"] else "—"}</div>', unsafe_allow_html=True)
            with rc[3]:
                st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #f9fafb;font-family:DM Mono;font-size:12px;color:{up_c};font-weight:600;">{f"{row['upside']:+.1f}%" if row["upside"] is not None else "—"}</div>', unsafe_allow_html=True)
            with rc[4]:
                st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #f9fafb;font-family:DM Mono;font-size:12px;color:{sc_c};">{row["score_m3"]:.0f}</div>', unsafe_allow_html=True)
            with rc[5]:
                st.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #f9fafb;background:{row["rec_bg"]};color:{row["rec_tc"]};font-family:DM Mono;font-size:11px;padding:4px 8px;border-radius:6px;">{row["rec"]}</div>', unsafe_allow_html=True)

        # Scatter upside vs score M3
        if len(df_res) >= 2:
            st.markdown('<div style="font-family:DM Mono;font-size:11px;color:#6b7280;margin:16px 0 4px;">Mappa Upside vs Score Fondamentale M3 — in alto a destra = le migliori opportunità</div>', unsafe_allow_html=True)
            fig_summary = go.Figure()
            for _, row in df_res.iterrows():
                if row["upside"] is None or not row["score_m3"]: continue
                color = "#16a34a" if row["upside"]>15 and row["score_m3"]>=55 else ("#b8922a" if row["upside"]>0 else "#dc2626")
                fig_summary.add_trace(go.Scatter(
                    x=[row["score_m3"]], y=[row["upside"]],
                    mode="markers+text",
                    marker=dict(size=18, color=color, opacity=0.85, line=dict(width=1.5,color="white")),
                    text=[row["ticker"]], textposition="top center",
                    textfont=dict(family="DM Mono", size=11, color="#1a1a2e"),
                    hovertemplate=f'<b>{row["name"]}</b><br>Score M3: {row["score_m3"]:.0f}<br>Upside: {row["upside"]:+.1f}%<extra></extra>',
                    showlegend=False,
                ))
            fig_summary.add_hline(y=0, line_dash="dash", line_color="#e5e7eb")
            fig_summary.add_vline(x=50, line_dash="dash", line_color="#e5e7eb")
            fig_summary.update_layout(
                height=300, margin=dict(l=0,r=0,t=10,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Mono", color="#9ca3af", size=10),
                xaxis=dict(title="Score M3 (fondamentali)", range=[0,105], showgrid=True, gridcolor="#f0f0f0"),
                yaxis=dict(title="Upside stimato %", showgrid=True, gridcolor="#f0f0f0", zeroline=False),
            )
            st.plotly_chart(fig_summary, use_container_width=True,
                            config={"displayModeBar":False}, key="summary_scatter")

    # ── NAVIGAZIONE ───────────────────────────────────────────────────────────

    st.markdown("")
    if st.button("◀️ Torna al Mattone 3", type="secondary"):
        st.session_state.page = "mattone3"
        st.rerun()

    st.markdown('<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:40px;">MACRO ANALYZER · MATTONE 4 · DCF + Graham + DDM · yfinance · Non è un consiglio di investimento</div>', unsafe_allow_html=True)


_inject_css()

for _k, _v in {
    "page":"home","country_name":"🇺🇸 Stati Uniti","cc":"US",
    "regime":None,"selected_sector":None,"years_back":10,
    "m3_data":[],"m3_sector_loaded":None,"m4_loaded":{},"m4_cache_key":None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

_p = st.session_state.page
if   _p == "home":      _page_home()
elif _p == "macro":     _page_macro()
elif _p == "sectors":   _page_sectors()
elif _p == "screening": _page_screening()
elif _p == "fairvalue": _page_fairvalue()
elif _p == "heatmap":   _page_heatmap()
elif _p == "calendar":  _page_calendar()
else: st.error(f"Pagina '{_p}' non trovata.")
