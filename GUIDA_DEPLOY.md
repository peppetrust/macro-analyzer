# 🚀 Guida Completa — Deploy Macro Analyzer come PWA Android

---

## FASE 1 — Crea account GitHub (5 minuti)

1. Vai su **https://github.com** dal tuo PC
2. Clicca **"Sign up"** in alto a destra
3. Inserisci:
   - Email
   - Password (almeno 8 caratteri)
   - Username (es. `tuonome-analyzer`)
4. Verifica l'email che ti arriva
5. Scegli il piano **Free** (è sufficiente)

---

## FASE 2 — Crea il Repository (3 minuti)

1. Una volta loggato su GitHub, clicca il **"+"** in alto a destra → **"New repository"**
2. Imposta:
   - **Repository name:** `macro-analyzer`
   - **Visibility:** `Public` ✅ (obbligatorio per Streamlit Cloud gratuito)
   - **Add a README file:** spunta ✅
3. Clicca **"Create repository"**

---

## FASE 3 — Carica i File (5 minuti)

Devi caricare questi 4 file/cartelle nel repository:

```
macro-analyzer/
├── app.py                    ← il file principale
├── requirements.txt          ← le dipendenze Python
├── README.md                 ← descrizione progetto
└── .streamlit/
    └── config.toml           ← configurazione tema
```

### Come caricare i file:

1. Nella pagina del tuo repository clicca **"Add file"** → **"Upload files"**
2. Trascina i file `app.py`, `requirements.txt`, `README.md`
3. Clicca **"Commit changes"**

### Per la cartella .streamlit/config.toml:
La cartella che inizia con `.` è nascosta — caricala così:
1. Clicca **"Add file"** → **"Create new file"**
2. Nel campo nome scrivi: `.streamlit/config.toml`
3. Copia e incolla il contenuto del file config.toml
4. Clicca **"Commit new file"**

---

## FASE 4 — Deploy su Streamlit Cloud (5 minuti)

1. Vai su **https://streamlit.io/cloud**
2. Clicca **"Sign up"** → scegli **"Continue with GitHub"**
   - Autorizza Streamlit ad accedere al tuo GitHub
3. Clicca **"New app"**
4. Imposta:
   - **Repository:** `tuousername/macro-analyzer`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Clicca **"Deploy!"**
6. Aspetta 2-3 minuti mentre installa le dipendenze
7. L'app sarà disponibile a un URL tipo:
   `https://tuousername-macro-analyzer-app-xxxxx.streamlit.app`

---

## FASE 5 — Installa come PWA su Android (2 minuti)

1. Sul tuo telefono Android apri **Chrome**
2. Vai all'URL della tua app (quello di Streamlit Cloud)
3. Aspetta che l'app carichi completamente
4. Tocca i **3 puntini** (⋮) in alto a destra in Chrome
5. Seleziona **"Aggiungi alla schermata Home"**
   *(oppure "Installa app" se appare il banner automatico)*
6. Dai un nome: `Macro Analyzer`
7. Tocca **"Aggiungi"**

✅ Ora hai l'icona sulla home screen — si apre come un'app nativa, schermo intero!

---

## TROUBLESHOOTING COMUNE

| Problema | Soluzione |
|---|---|
| "Module not found" al deploy | Controlla che `requirements.txt` sia caricato correttamente |
| App lenta al primo avvio | Normale — Streamlit Cloud "dorme" dopo inattività, si risveglia in ~30s |
| Dati non caricano | yfinance può avere rate limiting — ricarica la pagina |
| CSS non si vede | Svuota cache Chrome sul telefono |
| Repository deve essere Public | Streamlit Cloud gratuito richiede repo pubblici |

---

## AGGIORNARE L'APP IN FUTURO

Quando vuoi aggiornare il codice:
1. Vai su GitHub → tuo repository
2. Clicca su `app.py` → matita ✏️ (Edit)
3. Modifica il codice
4. Clicca **"Commit changes"**
5. Streamlit Cloud si aggiorna automaticamente in ~1 minuto

---

## LIMITI DEL PIANO GRATUITO STREAMLIT CLOUD

| Risorsa | Limite |
|---|---|
| App pubbliche | 1 |
| RAM | 1 GB |
| CPU | Condivisa |
| Sleep dopo inattività | ~7 giorni |
| Bandwidth | Illimitata |

Per uso personale è più che sufficiente. ✅

---

*Guida generata per Macro Analyzer — Framework Top-Down per analisi azionaria*
