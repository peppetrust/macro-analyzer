"""components/styles.py — CSS globale dell'app"""
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

def inject():
    st.markdown(CSS, unsafe_allow_html=True)
