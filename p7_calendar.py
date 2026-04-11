"""pages/p7_calendar.py — Calendario economico con prossime uscite dati"""
import streamlit as st, requests, pandas as pd
from datetime import datetime, timedelta
from components.navbar import render as nav

IMPACT_COLOR = {"Alto":"#dc2626","Medio":"#f97316","Basso":"#16a34a"}
IMPACT_ICON  = {"Alto":"🔴","Medio":"🟡","Basso":"🟢"}

# ── Dati calendario da investing.com tramite scraping leggero ─────────────────
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

# ── Render ────────────────────────────────────────────────────────────────────

def render():
    nav()
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
