"""
Explosive Growth Candidate — Framework di valutazione qualitativa
==================================================================
App Streamlit standalone. Dati oggettivi via yfinance (gratuito, no API key).
I criteri che richiedono giudizio restano a compilazione manuale — il framework
struttura la decisione, non la prende al posto tuo.

Avvio:
    pip install streamlit yfinance
    streamlit run explosive_candidate_framework.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Explosive Candidate Framework", page_icon="📊", layout="centered")

# ---------------------------------------------------------------------------
# Stile minimo, coerente con registro "sala controllo analitica"
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0F1210; color: #E8E4DA; }
    h1, h2, h3 { font-family: 'Georgia', serif; }
    .stMetric { background-color: #171B18; padding: 12px; border-radius: 8px; }
    .verdict-box {
        padding: 24px; border-radius: 10px; margin-top: 20px;
    }
    .criterion-box {
        background-color: #171B18; padding: 18px; border-radius: 8px;
        margin-bottom: 16px; border: 1px solid #22261F;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("**FRAMEWORK · EXPLOSIVE GROWTH CANDIDATE**")
st.title("Non stai cercando conferme. Stai cercando dove ti sbagli.")
st.caption(
    "Dati oggettivi recuperati automaticamente da Yahoo Finance. "
    "I criteri interpretativi restano a tua valutazione — il framework struttura, non decide."
)

ticker_input = st.text_input("Ticker", value="MSFT", placeholder="es. MSFT, MU, AAPL").upper().strip()

if not ticker_input:
    st.stop()

# ---------------------------------------------------------------------------
# Recupero dati automatico (criteri oggettivi)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_data(ticker: str):
    t = yf.Ticker(ticker)
    info = t.info
    return {
        "shortName": info.get("shortName", ticker),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "revenueGrowth": info.get("revenueGrowth"),
        "earningsGrowth": info.get("earningsGrowth"),
        "grossMargins": info.get("grossMargins"),
        "operatingMargins": info.get("operatingMargins"),
        "freeCashflow": info.get("freeCashflow"),
        "operatingCashflow": info.get("operatingCashflow"),
        "totalCash": info.get("totalCash"),
        "totalDebt": info.get("totalDebt"),
        "marketCap": info.get("marketCap"),
        "targetMeanPrice": info.get("targetMeanPrice"),
        "recommendationKey": info.get("recommendationKey"),
        "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
    }

try:
    with st.spinner(f"Recupero dati per {ticker_input}..."):
        data = fetch_data(ticker_input)
except Exception as e:
    st.error(f"Impossibile recuperare dati per '{ticker_input}'. Verifica il ticker. Dettaglio: {e}")
    st.stop()

st.subheader(data["shortName"])
st.caption(f"{data.get('sector', 'N/D')} · {data.get('industry', 'N/D')}")

col1, col2, col3 = st.columns(3)
col1.metric("Prezzo attuale", f"${data['currentPrice']:.2f}" if data["currentPrice"] else "N/D")
col2.metric("Target medio analisti", f"${data['targetMeanPrice']:.2f}" if data["targetMeanPrice"] else "N/D")
if data["currentPrice"] and data["targetMeanPrice"]:
    upside = (data["targetMeanPrice"] / data["currentPrice"] - 1) * 100
    col3.metric("Upside implicito", f"{upside:+.1f}%")
else:
    col3.metric("Upside implicito", "N/D")

st.divider()

# ---------------------------------------------------------------------------
# Criterio 2 — Backlog / crescita ricavi (semi-automatico: dato + tua conferma)
# ---------------------------------------------------------------------------
st.markdown("### 02 · Domanda contrattualizzata")
st.caption("*È già firmato, o solo promesso?*")

rev_growth = data["revenueGrowth"]
earn_growth = data["earningsGrowth"]

c1, c2 = st.columns(2)
c1.metric("Crescita ricavi (YoY)", f"{rev_growth*100:.1f}%" if rev_growth is not None else "N/D")
c2.metric("Crescita utili (YoY)", f"{earn_growth*100:.1f}%" if earn_growth is not None else "N/D")

st.info(
    "yfinance non espone il backlog contrattuale (RPO) direttamente: cercalo nell'ultimo "
    "10-Q/10-K o earnings call ('remaining performance obligations', 'commercial bookings')."
)
backlog_confirmed = st.radio(
    "In base a quanto trovato, la crescita è già contrattualizzata o solo guidance?",
    ["Contrattualizzata con backlog verificabile", "Solo guidance management", "Nessuna visibilità concreta"],
    index=None,
)
score_backlog = {"Contrattualizzata con backlog verificabile": 2, "Solo guidance management": 1,
                  "Nessuna visibilità concreta": 0}.get(backlog_confirmed)

st.divider()

# ---------------------------------------------------------------------------
# Criterio 3 — Multiplo disallineato (automatico)
# ---------------------------------------------------------------------------
st.markdown("### 03 · Multiplo disallineato")
st.caption("*Il forward P/E riflette già la crescita, o no?*")

trailing_pe = data["trailingPE"]
forward_pe = data["forwardPE"]

c1, c2 = st.columns(2)
c1.metric("P/E trailing", f"{trailing_pe:.1f}x" if trailing_pe else "N/D")
c2.metric("P/E forward", f"{forward_pe:.1f}x" if forward_pe else "N/D")

score_multiple = None
if trailing_pe and forward_pe:
    gap = trailing_pe - forward_pe
    gap_pct = (gap / trailing_pe) * 100
    if gap_pct > 25:
        st.success(f"Il forward P/E è {gap_pct:.0f}% più basso del trailing — disallineamento marcato, "
                    "segnale che il mercato non ha ancora aggiornato pienamente la view sulla crescita attesa.")
        score_multiple = 2
    elif gap_pct > 5:
        st.warning(f"Disallineamento moderato ({gap_pct:.0f}%). Non è il segnale netto di Micron 2025, "
                    "ma indica un minimo di margine.")
        score_multiple = 1
    else:
        st.error("Nessun disallineamento significativo: il mercato ha già prezzato la crescita attesa nel multiplo.")
        score_multiple = 0
else:
    st.info("Dati P/E incompleti per questo ticker.")

st.divider()

# ---------------------------------------------------------------------------
# Criterio 4 — Skin in the game (automatico su cash flow / debito)
# ---------------------------------------------------------------------------
st.markdown("### 04 · Skin in the game")
st.caption("*L'azienda investe soldi propri o si indebita/diluisce?*")

ocf = data["operatingCashflow"]
fcf = data["freeCashflow"]
cash = data["totalCash"]
debt = data["totalDebt"]

c1, c2 = st.columns(2)
c1.metric("Cash flow operativo", f"${ocf/1e9:.1f}B" if ocf else "N/D")
c2.metric("Free cash flow", f"${fcf/1e9:.1f}B" if fcf else "N/D")
c3, c4 = st.columns(2)
c3.metric("Cassa totale", f"${cash/1e9:.1f}B" if cash else "N/D")
c4.metric("Debito totale", f"${debt/1e9:.1f}B" if debt else "N/D")

score_skin = None
if ocf and debt is not None and cash is not None:
    net_cash_position = cash - debt
    if ocf > 0 and net_cash_position > 0:
        st.success("Cash flow operativo positivo e posizione di cassa netta positiva: capacità di "
                    "autofinanziare investimenti pesanti senza dipendere da debito o diluizione.")
        score_skin = 2
    elif ocf > 0:
        st.warning("Cash flow operativo positivo ma debito netto superiore alla cassa: capex parzialmente "
                    "sostenuto da leva finanziaria.")
        score_skin = 1
    else:
        st.error("Cash flow operativo debole o negativo: crescita a rischio di dipendere da debito/diluizione.")
        score_skin = 0

st.divider()

# ---------------------------------------------------------------------------
# Criterio 1 — Bottleneck competitivo (manuale, per natura qualitativo)
# ---------------------------------------------------------------------------
st.markdown("### 01 · Collo di bottiglia")
st.caption("*Chi altro può farlo?* — Nessun dato di mercato risponde a questa domanda: richiede la tua analisi competitiva.")
bottleneck = st.radio(
    "Quanti player credibili possono sostituire questo prodotto/servizio nei prossimi 2-3 anni?",
    ["Pochissimi (2-3 aziende al mondo)", "Alcuni competitor credibili, vantaggio ancora difendibile",
     "Molti: è sostituibile in tempi brevi"],
    index=None,
)
score_bottleneck = {
    "Pochissimi (2-3 aziende al mondo)": 2,
    "Alcuni competitor credibili, vantaggio ancora difendibile": 1,
    "Molti: è sostituibile in tempi brevi": 0,
}.get(bottleneck)

st.divider()

# ---------------------------------------------------------------------------
# Criterio 5 — Tesi di fallimento (obbligatoria, manuale)
# ---------------------------------------------------------------------------
st.markdown("### 05 · Tesi di fallimento — *obbligatoria*")
st.caption("In una frase: quando questo trade fallisce?")
thesis = st.text_area(
    "Es. Questo trade fallisce se il capex si mantiene a questi livelli per oltre 4 trimestri senza "
    "conversione in ricavo Azure/AI misurabile, comprimendo il free cash flow oltre la soglia che il mercato tollera.",
    height=90,
)

st.divider()

# ---------------------------------------------------------------------------
# Sizing e verdetto
# ---------------------------------------------------------------------------
sizing = st.slider("Size massima che ti sei dato per questa scommessa satellite (% portafoglio)", 2.0, 8.0, 5.0, 0.5)

scores = [s for s in [score_bottleneck, score_backlog, score_multiple, score_skin] if s is not None]
answered_all = len(scores) == 4
raw_score = sum(scores) if scores else 0

st.markdown("## Verdetto")

if not answered_all:
    st.warning(f"Valutazione incompleta: {4 - len(scores)} criteri ancora da compilare.")
elif len(thesis.strip()) < 15:
    st.error("**Verdetto bloccato.** Non puoi chiudere la valutazione senza una tesi di fallimento chiara. "
             "Questo non è un vincolo burocratico: se non riesci a scriverla, probabilmente non conosci "
             "abbastanza l'azienda per metterci sopra capitale.")
else:
    if raw_score >= 7:
        st.success(f"**Candidato solido** — punteggio {raw_score}/8. Supera la maggior parte dei filtri "
                    f"strutturali. Size indicata: **{sizing}%** del portafoglio.")
    elif raw_score >= 4:
        reduced = round(sizing * 0.5, 1)
        st.warning(f"**Convinzione parziale** — punteggio {raw_score}/8. Alcuni criteri deboli. "
                    f"Se procedi, size ridotta indicata: **{reduced}%** invece di {sizing}%.")
    else:
        st.error(f"**Non regge il framework** — punteggio {raw_score}/8. Troppi criteri strutturali mancanti: "
                 "questa non è una scommessa asimmetrica, è speranza. Size indicata: **0%**.")

    with st.expander("Riepilogo tesi di fallimento"):
        st.write(thesis)

st.caption(
    "⚠️ Questo strumento struttura il ragionamento, non lo sostituisce e non è consulenza finanziaria. "
    "I dati yfinance possono avere ritardi o imprecisioni: verifica sempre su fonti primarie (10-K, 10-Q, "
    "earnings call) prima di decidere."
)
