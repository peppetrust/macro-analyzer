"""
config.py — Costanti globali, paesi, ETF, colori, TTL cache
"""
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
