"""
MACRO ANALYZER — app.py
Framework Top-Down: Mattone 1 (Macro) + Mattone 2 (Settori)
Navigazione multipage via st.session_state
"""

import streamlit as st
import requests
import pandas as pd
import io
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Macro Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── STILE GLOBALE ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background-color:#f8f7f4;color:#1a1a2e;}
.stApp{background-color:#f8f7f4;}
h1,h2,h3{font-family:'DM Serif Display',serif;color:#1a1a2e;}
.metric-card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px 22px;margin:6px 0;box-shadow:0 1px 4px rgba(0,0,0,.06);transition:border-color .2s,box-shadow .2s;}
.metric-card:hover{border-color:#b8922a;box-shadow:0 4px 12px rgba(0,0,0,.1);}
.metric-label{font-family:'DM Mono',monospace;font-size:11px;color:#9ca3af;letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px;}
.metric-value{font-family:'DM Serif Display',serif;font-size:30px;color:#1a1a2e;line-height:1;}
.metric-delta{font-family:'DM Mono',monospace;font-size:12px;margin-top:5px;}
.metric-source{font-family:'DM Mono',monospace;font-size:9px;color:#d1d5db;margin-top:4px;}
.regime-badge{display:inline-block;padding:8px 20px;border-radius:50px;font-family:'DM Mono',monospace;font-size:13px;font-weight:500;letter-spacing:.05em;margin:4px;}
.regime-expansion{background:#dcfce7;color:#166534;border:1px solid #86efac;}
.regime-peak{background:#fef9c3;color:#854d0e;border:1px solid #fde047;}
.regime-contraction{background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;}
.regime-recovery{background:#dbeafe;color:#1e40af;border:1px solid #93c5fd;}
.regime-stagflation{background:#ede9fe;color:#5b21b6;border:1px solid #c4b5fd;}
.regime-unknown{background:#f3f4f6;color:#6b7280;border:1px solid #d1d5db;}
.section-title{font-family:'DM Mono',monospace;font-size:11px;color:#b8922a;letter-spacing:.15em;text-transform:uppercase;border-bottom:1px solid #e5e7eb;padding-bottom:8px;margin:28px 0 16px 0;}
.sidebar-header{font-family:'DM Serif Display',serif;font-size:22px;color:#b8922a;margin-bottom:4px;}
.info-box{background:#fff;border-left:3px solid #b8922a;border-radius:0 8px 8px 0;padding:14px 18px;margin:12px 0;font-size:14px;color:#6b7280;box-shadow:0 1px 4px rgba(0,0,0,.05);}
.sector-tag{display:inline-block;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:5px 12px;margin:3px;font-family:'DM Mono',monospace;font-size:12px;color:#b8922a;}
.sector-tag-fav{display:inline-block;background:#dcfce7;border:1px solid #86efac;border-radius:6px;padding:5px 12px;margin:3px;font-family:'DM Mono',monospace;font-size:12px;color:#166534;}
.sector-tag-ev{display:inline-block;background:#fee2e2;border:1px solid #fca5a5;border-radius:6px;padding:5px 12px;margin:3px;font-family:'DM Mono',monospace;font-size:12px;color:#991b1b;}
.warn-box{background:#fffbeb;border-left:3px solid #f59e0b;border-radius:0 8px 8px 0;padding:10px 16px;margin:8px 0;font-size:13px;color:#92400e;}
.sector-card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:16px 20px;margin:8px 0;box-shadow:0 1px 4px rgba(0,0,0,.06);cursor:pointer;transition:all .2s;}
.sector-card:hover{border-color:#b8922a;box-shadow:0 4px 12px rgba(0,0,0,.1);}
.sector-card-selected{background:#fffbeb;border:2px solid #b8922a;border-radius:12px;padding:16px 20px;margin:8px 0;box-shadow:0 4px 12px rgba(184,146,42,.15);}
.perf-positive{color:#16a34a;font-weight:600;}
.perf-negative{color:#dc2626;font-weight:600;}
.nav-btn{font-family:'DM Mono',monospace;}
footer{visibility:hidden;}

/* ── OTTIMIZZAZIONI MOBILE / PWA ── */
@media (max-width: 768px) {
    .metric-card { padding: 12px 14px !important; }
    .metric-value { font-size: 22px !important; }
    .section-title { font-size: 10px !important; margin: 18px 0 10px !important; }
    .regime-badge { font-size: 11px !important; padding: 6px 14px !important; }
    .sector-tag, .sector-tag-fav, .sector-tag-ev { font-size: 11px !important; padding: 4px 8px !important; }
    .sector-card, .sector-card-selected { padding: 12px 14px !important; }
    [data-testid="stSidebar"] { min-width: 80vw !important; }
    [data-testid="column"] { min-width: 0 !important; }
}
/* Nasconde footer e hamburger menu su mobile */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
/* Touch targets più grandi */
button[kind="primary"], button[kind="secondary"] {
    min-height: 48px !important;
    font-size: 15px !important;
}
/* Scrollbar più sottile su mobile */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 4px; }

</style>
""", unsafe_allow_html=True)

# ─── COSTANTI GLOBALI ──────────────────────────────────────────────────────────

COUNTRIES = {
    "🇺🇸 Stati Uniti":"US","🇩🇪 Germania":"DE","🇯🇵 Giappone":"JP",
    "🇬🇧 Regno Unito":"GB","🇫🇷 Francia":"FR","🇮🇹 Italia":"IT",
    "🇨🇳 Cina":"CN","🇧🇷 Brasile":"BR","🇮🇳 India":"IN","🇨🇦 Canada":"CA",
    "🇦🇺 Australia":"AU","🇰🇷 Corea del Sud":"KR","🇪🇸 Spagna":"ES",
    "🇳🇱 Paesi Bassi":"NL","🇨🇭 Svizzera":"CH","🇸🇪 Svezia":"SE",
    "🇲🇽 Messico":"MX","🇿🇦 Sudafrica":"ZA","🇹🇷 Turchia":"TR","🇵🇱 Polonia":"PL",
}

FALLBACK = {
    "US":(2.5,4.1,3.7),"DE":(-0.2,5.9,3.0),"JP":(1.9,3.3,2.6),
    "GB":(0.1,7.3,4.2),"FR":(0.9,5.7,7.3),"IT":(0.9,5.9,6.7),
    "CN":(5.2,0.2,5.2),"BR":(2.9,4.6,7.8),"IN":(8.2,5.4,3.2),
    "CA":(1.2,3.9,5.4),"AU":(2.0,5.6,3.7),"KR":(1.4,3.6,2.7),
    "ES":(2.5,3.5,12.2),"NL":(0.1,4.1,3.6),"CH":(1.3,2.1,2.1),
    "SE":(-0.1,8.6,8.5),"MX":(3.2,5.5,2.8),"ZA":(0.6,6.0,32.1),
    "TR":(4.5,53.9,9.4),"PL":(0.2,10.9,2.9),
}

# ─── ETF SETTORIALI PER AREA GEOGRAFICA ────────────────────────────────────────
# USA: SPDR Sector ETFs
# Europa: iShares STOXX Europe 600 sector ETFs (quotati su Xetra/LSE)
# Emerging/Global: ETF iShares MSCI sector

USA_SECTORS = {
    "Tecnologia":            {"ticker":"XLK",  "desc":"S&P 500 Tech"},
    "Finanziari":            {"ticker":"XLF",  "desc":"S&P 500 Financials"},
    "Energia":               {"ticker":"XLE",  "desc":"S&P 500 Energy"},
    "Healthcare":            {"ticker":"XLV",  "desc":"S&P 500 Health Care"},
    "Industriali":           {"ticker":"XLI",  "desc":"S&P 500 Industrials"},
    "Beni di prima necessità":{"ticker":"XLP", "desc":"S&P 500 Consumer Staples"},
    "Ciclici":               {"ticker":"XLY",  "desc":"S&P 500 Consumer Discret."},
    "Utilities":             {"ticker":"XLU",  "desc":"S&P 500 Utilities"},
    "Materiali":             {"ticker":"XLB",  "desc":"S&P 500 Materials"},
    "Real Estate":           {"ticker":"XLRE", "desc":"S&P 500 Real Estate"},
    "Comunicazioni":         {"ticker":"XLC",  "desc":"S&P 500 Comm. Services"},
}

EUROPE_SECTORS = {
    "Tecnologia":            {"ticker":"EXV3.DE","desc":"iShares STOXX Eu600 Tech"},
    "Finanziari":            {"ticker":"EXV1.DE","desc":"iShares STOXX Eu600 Banks"},
    "Energia":               {"ticker":"EXV6.DE","desc":"iShares STOXX Eu600 Oil&Gas"},
    "Healthcare":            {"ticker":"EXV4.DE","desc":"iShares STOXX Eu600 H.Care"},
    "Industriali":           {"ticker":"EXH2.DE","desc":"iShares STOXX Eu600 Industr."},
    "Beni di prima necessità":{"ticker":"EXH8.DE","desc":"iShares STOXX Eu600 Food&Bev"},
    "Ciclici":               {"ticker":"EXH3.DE","desc":"iShares STOXX Eu600 Retail"},
    "Utilities":             {"ticker":"EXH7.DE","desc":"iShares STOXX Eu600 Utilities"},
    "Materiali":             {"ticker":"EXV5.DE","desc":"iShares STOXX Eu600 Basic Res."},
    "Real Estate":           {"ticker":"EPRA.MI","desc":"iShares EU Property Yield"},
    "Comunicazioni":         {"ticker":"EXH9.DE","desc":"iShares STOXX Eu600 Telecom"},
}

GLOBAL_SECTORS = {
    "Tecnologia":            {"ticker":"IXN",  "desc":"iShares Global Tech"},
    "Finanziari":            {"ticker":"IXG",  "desc":"iShares Global Financials"},
    "Energia":               {"ticker":"IXC",  "desc":"iShares Global Energy"},
    "Healthcare":            {"ticker":"IXJ",  "desc":"iShares Global Healthcare"},
    "Industriali":           {"ticker":"EXI",  "desc":"iShares Global Industrials"},
    "Beni di prima necessità":{"ticker":"KXI", "desc":"iShares Global Cons.Staples"},
    "Ciclici":               {"ticker":"RXI",  "desc":"iShares Global Cons.Discret."},
    "Utilities":             {"ticker":"JXI",  "desc":"iShares Global Utilities"},
    "Materiali":             {"ticker":"MXI",  "desc":"iShares Global Materials"},
    "Real Estate":           {"ticker":"IFGL", "desc":"iShares Intl Dev.Real Estate"},
    "Comunicazioni":         {"ticker":"IXP",  "desc":"iShares Global Telecom"},
}

EUROPE_COUNTRIES = {"DE","FR","IT","GB","ES","NL","CH","SE","PL"}
AMERICAS_COUNTRIES = {"US","CA","MX","BR"}

def get_sector_map(cc: str) -> dict:
    if cc == "US":         return USA_SECTORS
    if cc in EUROPE_COUNTRIES: return EUROPE_SECTORS
    return GLOBAL_SECTORS

def get_region_label(cc: str) -> str:
    if cc == "US":              return "USA (SPDR S&P 500)"
    if cc in EUROPE_COUNTRIES:  return "Europa (iShares STOXX 600)"
    return "Globale (iShares MSCI)"

# ─── DATI TEORICI: performance per regime (letteratura finanziaria) ─────────────
# Basato su: Fidelity Sector Investing, BofA Regime framework,
#            Merrill Lynch Investment Clock, MSCI factor research

THEORETICAL_PERF = {
    "Espansione": {
        "Tecnologia":5,"Finanziari":4,"Industriali":4,"Ciclici":5,
        "Materiali":3,"Energia":2,"Healthcare":1,"Beni di prima necessità":-1,
        "Utilities":-2,"Real Estate":2,"Comunicazioni":3,
    },
    "Surriscaldamento": {
        "Energia":5,"Materiali":4,"Real Estate":3,"Finanziari":2,
        "Industriali":1,"Comunicazioni":0,"Tecnologia":-1,"Healthcare":0,
        "Ciclici":-2,"Beni di prima necessità":-1,"Utilities":-3,
    },
    "Contrazione": {
        "Utilities":4,"Healthcare":5,"Beni di prima necessità":4,"Comunicazioni":2,
        "Finanziari":-2,"Industriali":-3,"Ciclici":-5,"Materiali":-3,
        "Energia":-1,"Tecnologia":-2,"Real Estate":-2,
    },
    "Ripresa": {
        "Ciclici":5,"Finanziari":4,"Tecnologia":4,"Industriali":3,
        "Materiali":3,"Real Estate":2,"Comunicazioni":2,"Energia":1,
        "Healthcare":0,"Beni di prima necessità":-1,"Utilities":-2,
    },
    "Stagflazione": {
        "Energia":5,"Materiali":3,"Beni di prima necessità":3,"Utilities":2,
        "Healthcare":2,"Comunicazioni":0,"Real Estate":-1,"Finanziari":-3,
        "Ciclici":-4,"Industriali":-2,"Tecnologia":-3,
    },
    "Surriscaldamento": {
        "Energia":5,"Materiali":4,"Real Estate":3,"Finanziari":2,
        "Industriali":1,"Comunicazioni":0,"Tecnologia":-1,"Healthcare":0,
        "Ciclici":-2,"Beni di prima necessità":-1,"Utilities":-3,
    },
    "Fase incerta": {
        "Healthcare":2,"Utilities":2,"Beni di prima necessità":2,"Comunicazioni":1,
        "Finanziari":0,"Real Estate":0,"Tecnologia":0,"Industriali":0,
        "Materiali":0,"Energia":0,"Ciclici":0,
    },
}

SCORE_LABELS = {5:"Molto favorevole",4:"Favorevole",3:"Leggermente positivo",
                2:"Neutro positivo",1:"Neutro",0:"Neutro",
                -1:"Cautela",-2:"Sfavorevole",-3:"Molto sfavorevole",
                -4:"Fortemente negativo",-5:"Evitare"}

# ─── FETCH HELPERS ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def wb(country, ind, n=22):
    url=(f"https://api.worldbank.org/v2/country/{country}/indicator/{ind}"
         f"?format=json&per_page={n}&mrv={n}")
    try:
        r=requests.get(url,timeout=12); p=r.json()
        if len(p)<2 or not p[1]: return pd.DataFrame()
        rows=[{"year":int(d["date"]),"value":d["value"]} for d in p[1] if d["value"] is not None]
        return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)
    except: return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner=False)
def fred(series):
    url=f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    try:
        r=requests.get(url,timeout=12)
        df=pd.read_csv(io.StringIO(r.text),names=["date","value"],skiprows=1)
        df["date"]=pd.to_datetime(df["date"],errors="coerce")
        df["value"]=pd.to_numeric(df["value"],errors="coerce")
        df=df.dropna(); df["year"]=df["date"].dt.year
        return df.groupby("year")["value"].mean().reset_index().sort_values("year")
    except: return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner=False)
def get_gdp(cc):
    if cc=="US":
        df=fred("A191RL1A225NBEA")
        if not df.empty: return df
    return wb(cc,"NY.GDP.MKTP.KD.ZG")

@st.cache_data(ttl=86400, show_spinner=False)
def get_inf(cc):
    if cc=="US":
        df=fred("CPIAUCSL")
        if not df.empty:
            df["value"]=df["value"].pct_change()*100
            return df.dropna().reset_index(drop=True)
    return wb(cc,"FP.CPI.TOTL.ZG")

@st.cache_data(ttl=86400, show_spinner=False)
def get_unemp(cc):
    if cc=="US":
        df=fred("UNRATE")
        if not df.empty: return df
    return wb(cc,"SL.UEM.TOTL.ZS")

@st.cache_data(ttl=86400, show_spinner=False)
def get_ca(cc):   return wb(cc,"BN.CAB.XOKA.GD.ZS")
@st.cache_data(ttl=86400, show_spinner=False)
def get_debt(cc): return wb(cc,"GC.DOD.TOTL.GD.ZS")
@st.cache_data(ttl=86400, show_spinner=False)
def get_fdi(cc):  return wb(cc,"BX.KLT.DINV.WD.GD.ZS")

def latest(df):
    if df is None or df.empty: return None,None
    v=df.iloc[-1]["value"]; p=df.iloc[-2]["value"] if len(df)>1 else None
    return v,(v-p if p is not None else None)

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_etf_data(ticker: str, period_years: int = 5) -> pd.DataFrame:
    """Scarica dati ETF via yfinance e calcola rendimenti annuali."""
    try:
        end   = datetime.now()
        start = end - timedelta(days=period_years * 365)
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        # Rendimento annuale
        df_annual = df["Close"].resample("YE").last()
        returns   = df_annual.pct_change().dropna() * 100
        result    = pd.DataFrame({"year": returns.index.year, "return_pct": returns.values.flatten()})
        return result
    except: return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_etf_ytd(ticker: str) -> tuple:
    """Rendimento YTD e ultimo prezzo."""
    try:
        t   = yf.Ticker(ticker)
        hist= t.history(period="1y")
        if hist.empty: return None, None, None
        last_price = hist["Close"].iloc[-1]
        ytd_start  = hist[hist.index >= f"{datetime.now().year}-01-01"]["Close"]
        ytd_ret    = ((ytd_start.iloc[-1]/ytd_start.iloc[0])-1)*100 if len(ytd_start)>1 else None
        ret_1y     = ((hist["Close"].iloc[-1]/hist["Close"].iloc[0])-1)*100
        return round(last_price,2), round(ytd_ret,2) if ytd_ret else None, round(ret_1y,2)
    except: return None, None, None

# ─── REGIME ────────────────────────────────────────────────────────────────────

def classify_regime(gdp,inf,un):
    if gdp>2.5 and inf<4.0 and un<6.0:
        return {"name":"Espansione","css":"regime-expansion","icon":"🚀",
                "desc":"Crescita solida, inflazione contenuta, occupazione forte.",
                "fav":["Tecnologia","Finanziari","Industriali","Ciclici","Materiali"],
                "ev":["Utilities","Beni di prima necessità"]}
    if gdp>0.5 and inf>=4.0 and un<7.0:
        return {"name":"Surriscaldamento","css":"regime-peak","icon":"⚡",
                "desc":"Crescita positiva ma inflazione elevata. Possibile stretta monetaria.",
                "fav":["Energia","Materiali","Finanziari","Real Estate"],
                "ev":["Tecnologia growth","Bond lunghi"]}
    if gdp<0 and inf>3.5:
        return {"name":"Stagflazione","css":"regime-stagflation","icon":"⚠️",
                "desc":"Scenario difficile: PIL negativo + inflazione alta.",
                "fav":["Energia","Materiali","Beni di prima necessità"],
                "ev":["Tecnologia","Finanziari","Ciclici"]}
    if gdp<0.5 or un>8.5:
        return {"name":"Contrazione","css":"regime-contraction","icon":"📉",
                "desc":"Crescita debole o negativa. Mercato in risk-off.",
                "fav":["Utilities","Healthcare","Beni di prima necessità"],
                "ev":["Ciclici","Finanziari","Industriali"]}
    if gdp>0.5 and un>6.5:
        return {"name":"Ripresa","css":"regime-recovery","icon":"🌱",
                "desc":"PIL in risalita, mercato del lavoro ancora in recupero.",
                "fav":["Ciclici","Finanziari","Tecnologia","Industriali"],
                "ev":["Utilities pure"]}
    return {"name":"Fase incerta","css":"regime-unknown","icon":"❓",
            "desc":"Segnali misti. Diversificare e monitorare.",
            "fav":["Diversificazione"],"ev":[]}

# ─── CHART HELPERS ─────────────────────────────────────────────────────────────

CLRS={"gdp":"#3b82f6","inf":"#ef4444","unemp":"#f97316","ca":"#10b981","debt":"#8b5cf6","fdi":"#eab308"}

def h2r(h,a):
    h=h.lstrip("#"); r,g,b=int(h[:2],16),int(h[2:4],16),int(h[4:],16)
    return f"rgba({r},{g},{b},{a})"

def line_chart(df,color,unit="%"):
    fig=go.Figure()
    if df is not None and not df.empty:
        fig.add_trace(go.Scatter(x=df["year"],y=df["value"].round(2),mode="lines+markers",
            line=dict(color=color,width=2.5),marker=dict(size=5,color=color),
            fill="tozeroy",fillcolor=h2r(color,.07),
            hovertemplate=f"<b>%{{x}}</b>: %{{y:.1f}}{unit}<extra></extra>"))
    else:
        fig.add_annotation(text="Dati non disponibili",showarrow=False,font=dict(color="#9ca3af",size=12))
    fig.update_layout(height=175,margin=dict(l=0,r=0,t=6,b=0),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono",color="#9ca3af",size=10),showlegend=False,
        xaxis=dict(showgrid=False,zeroline=False,tickfont=dict(size=10)),
        yaxis=dict(showgrid=True,gridcolor="#f0f0f0",zeroline=True,
                   zerolinecolor="#e5e7eb",tickfont=dict(size=10)))
    return fig

def bar_chart_returns(df: pd.DataFrame, color: str, title: str):
    """Grafico a barre rendimenti annuali ETF."""
    if df.empty:
        fig=go.Figure()
        fig.add_annotation(text="Dati ETF non disponibili",showarrow=False,font=dict(color="#9ca3af",size=12))
        fig.update_layout(height=180,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=0,t=20,b=0))
        return fig
    colors_bar=[("#16a34a" if v>=0 else "#dc2626") for v in df["return_pct"]]
    fig=go.Figure(go.Bar(
        x=df["year"], y=df["return_pct"].round(1),
        marker_color=colors_bar,
        hovertemplate="<b>%{x}</b>: %{y:.1f}%<extra></extra>",
        text=df["return_pct"].round(1).astype(str)+"%",
        textposition="outside", textfont=dict(size=9,family="DM Mono"),
    ))
    fig.update_layout(height=200,margin=dict(l=0,r=0,t=30,b=0),title=dict(text=title,font=dict(family="DM Mono",size=11,color="#9ca3af"),x=0),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono",color="#9ca3af",size=10),showlegend=False,
        xaxis=dict(showgrid=False,zeroline=False,type="category"),
        yaxis=dict(showgrid=True,gridcolor="#f0f0f0",zeroline=True,zerolinecolor="#e5e7eb"),)
    return fig

def radar_chart(regime_name: str, sector_map: dict):
    """Radar chart score teorici per regime."""
    scores = THEORETICAL_PERF.get(regime_name, THEORETICAL_PERF["Fase incerta"])
    sectors = list(sector_map.keys())
    vals    = [scores.get(s, 0) for s in sectors]
    vals_norm = [(v + 5) / 10 for v in vals]   # normalizza 0-1

    fig = go.Figure(go.Scatterpolar(
        r=vals_norm + [vals_norm[0]],
        theta=sectors + [sectors[0]],
        fill='toself',
        fillcolor=h2r("#b8922a", 0.15),
        line=dict(color="#b8922a", width=2),
        hovertemplate="<b>%{theta}</b><br>Score: " +
            "<br>".join([f"{s}: {v:+d}" for s,v in zip(sectors,vals)]) + "<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1], showticklabels=False, gridcolor="#e5e7eb"),
            angularaxis=dict(tickfont=dict(size=10, family="DM Mono"), gridcolor="#e5e7eb"),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40,r=40,t=40,b=40),
        height=340,showlegend=False,
    )
    return fig

def fmt(v): return f"{v:.1f}%" if v is not None else "N/D"
def dhtml(d):
    if d is None: return '<span style="color:#d1d5db;">—</span>'
    c="#16a34a" if d>=0 else "#dc2626"; a="▲" if d>=0 else "▼"
    return f'<span style="color:{c};">{a} {abs(d):.2f}%</span>'

# ─── SESSION STATE INIT ────────────────────────────────────────────────────────

if "page" not in st.session_state:         st.session_state.page = "mattone1"
if "country_name" not in st.session_state: st.session_state.country_name = "🇺🇸 Stati Uniti"
if "cc" not in st.session_state:           st.session_state.cc = "US"
if "regime" not in st.session_state:       st.session_state.regime = None
if "years_back" not in st.session_state:   st.session_state.years_back = 10
if "selected_sector" not in st.session_state: st.session_state.selected_sector = None

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-header">📊 Macro Analyzer</div>',unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;margin-bottom:16px;">TOP-DOWN INVESTMENT FRAMEWORK</div>',unsafe_allow_html=True)

    # navigazione
    st.markdown("**Navigazione**")
    if st.button("📦 Mattone 1 — Macro", use_container_width=True,
                 type="primary" if st.session_state.page=="mattone1" else "secondary"):
        st.session_state.page = "mattone1"
        st.rerun()

    m2_disabled = st.session_state.regime is None
    if st.button("📦 Mattone 2 — Settori", use_container_width=True,
                 type="primary" if st.session_state.page=="mattone2" else "secondary",
                 disabled=m2_disabled):
        st.session_state.page = "mattone2"
        st.rerun()
    if m2_disabled:
        st.caption("⚠️ Completa il Mattone 1 prima")

    m3_disabled = st.session_state.regime is None
    if st.button("📦 Mattone 3 — Screening", use_container_width=True,
                 type="primary" if st.session_state.page=="mattone3" else "secondary",
                 disabled=m3_disabled):
        st.session_state.page = "mattone3"
        st.rerun()
    if m3_disabled:
        st.caption("⚠️ Completa il Mattone 1 prima")

    m4_disabled = st.session_state.regime is None
    if st.button("📦 Mattone 4 — Fair Value", use_container_width=True,
                 type="primary" if st.session_state.page=="mattone4" else "secondary",
                 disabled=m4_disabled):
        st.session_state.page = "mattone4"
        st.rerun()
    if m4_disabled:
        st.caption("⚠️ Completa il Mattone 1 prima")

    st.markdown("---")

    if st.session_state.page == "mattone1":
        st.markdown("**Impostazioni**")
        cn = st.selectbox("Paese", list(COUNTRIES.keys()),
                          index=list(COUNTRIES.keys()).index(st.session_state.country_name))
        if cn != st.session_state.country_name:
            st.session_state.country_name = cn
            st.session_state.cc = COUNTRIES[cn]
            st.session_state.regime = None
            st.rerun()
        st.session_state.years_back = st.slider("Anni di storico",5,20,st.session_state.years_back)

    st.markdown("---")
    # stato sessione visibile
    if st.session_state.regime:
        reg = st.session_state.regime
        st.markdown(f"""<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;line-height:2;">
        SESSIONE CORRENTE<br>
        🌍 {st.session_state.country_name}<br>
        {reg['icon']} Regime: {reg['name']}<br>
        {'📌 Settore: '+st.session_state.selected_sector if st.session_state.selected_sector else ''}
        </div>""",unsafe_allow_html=True)

    st.markdown("""<div style="font-family:DM Mono;font-size:10px;color:#9ca3af;line-height:2;margin-top:12px;">
    FONTI<br>· FRED · World Bank<br>· yfinance · IMF/OCSE<br><br>
    MATTONI ATTIVI<br>📦 1 · Macro ✅<br>📦 2 · Settori ✅<br>📦 3 · Screening ✅<br>📦 4 · Fair Value (prossimo)
    </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MATTONE 1
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "mattone1":
    cc = st.session_state.cc
    country_name = st.session_state.country_name
    years_back   = st.session_state.years_back

    st.markdown(f"## {country_name} — Analisi Macroeconomica")
    st.markdown('<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:24px;">MATTONE 1 · STEP 1 DEL FRAMEWORK TOP-DOWN</div>',unsafe_allow_html=True)

    with st.spinner("Carico dati macro... (prima volta ~5s, poi in cache 24h)"):
        df_gdp=get_gdp(cc); df_inf=get_inf(cc); df_unemp=get_unemp(cc)
        df_ca=get_ca(cc);   df_debt=get_debt(cc); df_fdi=get_fdi(cc)

    gv,gd=latest(df_gdp); iv,id_=latest(df_inf); uv,ud=latest(df_unemp)
    cv,cd=latest(df_ca);  dv,dd=latest(df_debt); fv,fd=latest(df_fdi)

    used_fb=False
    if cc in FALLBACK:
        fb=FALLBACK[cc]
        if gv is None: gv,gd=fb[0],None; used_fb=True
        if iv is None: iv,id_=fb[1],None; used_fb=True
        if uv is None: uv,ud=fb[2],None; used_fb=True

    # ── REGIME ──
    st.markdown('<div class="section-title">🔍 Regime Economico Corrente</div>',unsafe_allow_html=True)

    if gv is not None and iv is not None and uv is not None:
        reg = classify_regime(gv,iv,uv)
        st.session_state.regime = reg   # salva in session state per Mattone 2

        if used_fb:
            st.markdown('<div class="warn-box">⚠️ Alcuni dati integrati con stime IMF/OCSE 2023 — classificazione indicativa.</div>',unsafe_allow_html=True)

        c1,c2=st.columns([1,2])
        with c1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Regime identificato</div>
                <div style="margin:10px 0;"><span class="regime-badge {reg['css']}">{reg['icon']} {reg['name']}</span></div>
                <div style="font-size:13px;color:#9ca3af;line-height:1.6;">{reg['desc']}</div>
                <div style="margin-top:12px;font-family:DM Mono;font-size:10px;color:#d1d5db;">PIL:{gv:.1f}% · Inf:{iv:.1f}% · Disoc:{uv:.1f}%</div>
            </div>""",unsafe_allow_html=True)
        with c2:
            ca,cb=st.columns(2)
            with ca:
                st.markdown('<div style="font-family:DM Mono;font-size:10px;color:#16a34a;letter-spacing:.1em;margin-bottom:8px;">✅ SETTORI FAVORITI</div>',unsafe_allow_html=True)
                st.markdown("".join([f'<span class="sector-tag-fav">{s}</span>' for s in reg["fav"]]),unsafe_allow_html=True)
            with cb:
                st.markdown('<div style="font-family:DM Mono;font-size:10px;color:#dc2626;letter-spacing:.1em;margin-bottom:8px;">⛔ DA EVITARE</div>',unsafe_allow_html=True)
                avoid="".join([f'<span class="sector-tag-ev">{s}</span>' for s in reg["ev"]]) or "—"
                st.markdown(avoid,unsafe_allow_html=True)

        st.markdown("")
        if st.button(f"▶️ Vai al Mattone 2 — Analisi Settoriale ({reg['name']})", type="primary"):
            st.session_state.page = "mattone2"
            st.rerun()
    else:
        st.error("Dati insufficienti anche dopo fallback.")

    # ── KPI ──
    st.markdown('<div class="section-title">📈 Indicatori Chiave</div>',unsafe_allow_html=True)
    kpis=[("📈","PIL reale",gv,gd,"FRED/WB"),("🔥","Inflazione CPI",iv,id_,"FRED/WB"),
          ("👷","Disoccupazione",uv,ud,"FRED/WB"),("🌐","Conto Corrente",cv,cd,"World Bank"),
          ("🏛️","Debito / PIL",dv,dd,"World Bank"),("💼","FDI netti",fv,fd,"World Bank")]
    cols=st.columns(3)
    for i,(icon,name,val,dlt,src) in enumerate(kpis):
        with cols[i%3]:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">{icon} {name}</div>
                <div class="metric-value">{fmt(val)}</div>
                <div class="metric-delta">{dhtml(dlt)}</div>
                <div class="metric-source">fonte: {src}</div>
            </div>""",unsafe_allow_html=True)

    # ── GRAFICI ──
    st.markdown('<div class="section-title">📉 Serie Storiche</div>',unsafe_allow_html=True)
    def fy(df,n):
        if df is None or df.empty: return df
        return df[df["year"]>=datetime.now().year-n].copy()
    charts_cfg=[
        (df_gdp,CLRS["gdp"],"Crescita PIL (%)","gdp"),
        (df_inf,CLRS["inf"],"Inflazione CPI (%)","inf"),
        (df_unemp,CLRS["unemp"],"Disoccupazione (%)","unemp"),
        (df_ca,CLRS["ca"],"Conto Corrente (% PIL)","ca"),
        (df_debt,CLRS["debt"],"Debito Pubblico (% PIL)","debt"),
        (df_fdi,CLRS["fdi"],"FDI netti (% PIL)","fdi"),
    ]
    cl,cr=st.columns(2)
    for i,(df_r,color,label,kid) in enumerate(charts_cfg):
        with (cl if i%2==0 else cr):
            st.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#6b7280;margin:14px 0 2px;">{label}</div>',unsafe_allow_html=True)
            st.plotly_chart(line_chart(fy(df_r,years_back),color),use_container_width=True,
                            config={"displayModeBar":False},key=f"m1_{kid}_{cc}")

    st.markdown('<div style="font-family:DM Mono;font-size:10px;color:#d1d5db;text-align:center;margin-top:40px;">MACRO ANALYZER · MATTONE 1 · FRED + WORLD BANK + IMF/OCSE</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MATTONE 2
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "mattone2":
    cc          = st.session_state.cc
    country_name= st.session_state.country_name
    reg         = st.session_state.regime
    sector_map  = get_sector_map(cc)
    region_lbl  = get_region_label(cc)
    reg_name    = reg["name"]
    theo_scores = THEORETICAL_PERF.get(reg_name, THEORETICAL_PERF["Fase incerta"])

    st.markdown(f"## {country_name} — Analisi Settoriale")
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
        st.plotly_chart(radar_chart(reg_name, sector_map), use_container_width=True,
                        config={"displayModeBar":False}, key="radar_main")

    # ── TABELLA SETTORI + DATI REALI ──
    st.markdown('<div class="section-title">📊 Performance Settoriale — Dati Reali vs Score Teorico</div>',unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Mono;font-size:11px;color:#9ca3af;margin-bottom:12px;">ETF utilizzati: {region_lbl} · Dati: yfinance · Score teorico: Fidelity/BofA/MSCI framework</div>',unsafe_allow_html=True)

    # Scarica tutti gli ETF
    with st.spinner("Scarico dati ETF... (in cache per 1h dopo il primo caricamento)"):
        etf_results = {}
        for sector, info in sector_map.items():
            price, ytd, ret_1y = fetch_etf_ytd(info["ticker"])
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
                df_hist = fetch_etf_data(ticker, period_years=10)

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
            fig_bar = bar_chart_returns(df_hist, "#b8922a", f"Rendimenti annuali {ticker} (ultimi 10 anni)")
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

# ══════════════════════════════════════════════════════════════════════════════
# MATTONE 3 — SCREENING FONDAMENTALE
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "mattone3":

    cc          = st.session_state.cc
    country_name= st.session_state.country_name
    reg         = st.session_state.regime
    sector      = st.session_state.selected_sector or "Tecnologia"

    st.markdown(f"## {country_name} — Screening Fondamentale")
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
            data_f = fetch_fundamentals(tkr)
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
                st.markdown(f"""<div style="padding:6px 0;border-bottom:1px solid #f3f4f6;">
                    <span style="background:{score_bg};color:{score_color};font-family:DM Mono;font-size:12px;font-weight:700;padding:3px 8px;border-radius:6px;">{score:.0f}</span>
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


# ══════════════════════════════════════════════════════════════════════════════
# MATTONE 4 — FAIR VALUE & RACCOMANDAZIONE FINALE
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "mattone4":

    import math

    cc           = st.session_state.cc
    country_name = st.session_state.country_name
    reg          = st.session_state.regime
    sector       = st.session_state.selected_sector or "Tecnologia"

    st.markdown(f"## {country_name} — Fair Value & Raccomandazione")
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
