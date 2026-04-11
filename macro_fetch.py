"""
data/macro_fetch.py
Cache intelligente con TTL diverso per ogni indicatore.
Cascade: FRED → IMF WEO → OECD → World Bank → Fallback statico
"""
import streamlit as st
import requests, io, pandas as pd
from datetime import datetime
from config import TTL, ISO2_TO_ISO3, FALLBACK

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

# ── Fonte 4: World Bank ───────────────────────────────────────────────────────

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

# ── Classificazione regime ────────────────────────────────────────────────────

def classify_regime(gdp: float, inf: float, un: float) -> dict:
    if gdp>2.5 and inf<4.0 and un<6.0:
        return {"name":"Espansione","css":"b-expansion","icon":"🚀",
                "desc":"Crescita solida, inflazione contenuta, occupazione forte.",
                "fav":["Tecnologia","Finanziari","Industriali","Ciclici","Materiali"],
                "ev":["Utilities","Beni di prima necessità"]}
    if gdp>0.5 and inf>=4.0 and un<7.0:
        return {"name":"Surriscaldamento","css":"b-peak","icon":"⚡",
                "desc":"Crescita positiva ma inflazione elevata. Possibile stretta monetaria.",
                "fav":["Energia","Materiali","Finanziari","Real Estate"],
                "ev":["Tecnologia growth","Bond lunghi"]}
    if gdp<0 and inf>3.5:
        return {"name":"Stagflazione","css":"b-stagflation","icon":"⚠️",
                "desc":"Scenario difficile: PIL negativo + inflazione alta.",
                "fav":["Energia","Materiali","Beni di prima necessità"],
                "ev":["Tecnologia","Finanziari","Ciclici"]}
    if gdp<0.5 or un>8.5:
        return {"name":"Contrazione","css":"b-contraction","icon":"📉",
                "desc":"Crescita debole o negativa. Mercato in risk-off.",
                "fav":["Utilities","Healthcare","Beni di prima necessità"],
                "ev":["Ciclici","Finanziari","Industriali"]}
    if gdp>0.5 and un>6.5:
        return {"name":"Ripresa","css":"b-recovery","icon":"🌱",
                "desc":"PIL in risalita, mercato del lavoro ancora in recupero.",
                "fav":["Ciclici","Finanziari","Tecnologia","Industriali"],
                "ev":["Utilities pure"]}
    return {"name":"Fase incerta","css":"b-unknown","icon":"❓",
            "desc":"Segnali misti. Diversificare e monitorare.",
            "fav":["Diversificazione"],"ev":[]}
