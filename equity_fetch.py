"""
data/equity_fetch.py
Fetch fondamentali e prezzi azionari con TTL intelligente.
Cascade: yfinance → FMP free → calcoli derivati
"""
import streamlit as st
import requests, pandas as pd, numpy as np, yfinance as yf
from datetime import datetime, timedelta
from config import TTL, SECTOR_TO_GICS, CURATED_STOCKS

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
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_KEY}"
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
