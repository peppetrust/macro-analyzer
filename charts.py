"""components/charts.py — Grafici riutilizzabili"""
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

def radar_chart(scores: dict, height: int = 300) -> go.Figure:
    sectors = list(scores.keys())
    vals    = [scores[s] for s in sectors]
    vals_n  = [(v+5)/10 for v in vals]
    fig = go.Figure(go.Scatterpolar(
        r=vals_n+[vals_n[0]], theta=sectors+[sectors[0]],
        fill="toself", fillcolor=hex_rgba("#b8922a",.15),
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
