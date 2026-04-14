"""
MACRO/SIGNAL Dashboard v3.1
============================================================
1. pip install streamlit pandas plotly fredapi yfinance
2. Get free FRED key: https://fred.stlouisfed.org/docs/api/api_key.html
3. streamlit run macro_dashboard.py
   (or paste key in sidebar when running on Streamlit Cloud)
============================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fredapi import Fred
import yfinance as yf
from datetime import datetime, timedelta

# ============================================================
# PASTE YOUR FRED API KEY HERE (or use the sidebar input)
# ============================================================
FRED_API_KEY = st.secrets.get("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE") if hasattr(st, "secrets") else "YOUR_FRED_API_KEY_HERE"

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MACRO/SIGNAL",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background: #070d18 !important;
    color: #c9d8eb !important;
}
.stApp { background: #070d18 !important; }
.main .block-container { padding: 1.2rem 1.6rem 2rem; max-width: 1700px; }

[data-testid="stSidebar"] {
    background: #0a1220 !important;
    border-right: 1px solid #1a2840;
}
[data-testid="stMetric"] {
    background: #0d1b2a;
    border: 1px solid #1a2840;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: #22d3ee;
}
[data-testid="stMetricLabel"] {
    color: #3a5a7a !important;
    font-size: 0.68rem !important;
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
[data-testid="stMetricValue"] {
    color: #e8f4ff !important;
    font-size: 1.55rem !important;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
}
[data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem !important;
}
[data-testid="stTabs"] button {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #3a5a7a;
}
[data-testid="stTabs"] button[aria-selected="true"] { color: #22d3ee !important; }
.stTabs [data-baseweb="tab-border"]    { background: #1a2840 !important; }
.stTabs [data-baseweb="tab-highlight"] { background: #22d3ee !important; }
hr { border-color: #1a2840 !important; }
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.7rem !important;
    color: #e8f4ff !important;
}
h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    color: #3a5a7a !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}
[data-testid="stAlert"] {
    background: #0d1b2a !important;
    border: 1px solid #1a2840 !important;
    border-radius: 8px;
    font-family: 'IBM Plex Mono', monospace;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d1b2a; }
::-webkit-scrollbar-thumb { background: #1a2840; border-radius: 3px; }

.regime-banner {
    display: flex; align-items: center; gap: 12px;
    background: #0d1b2a; border: 1px solid #1a2840;
    border-radius: 8px; padding: 11px 18px; margin-bottom: 1rem;
}
.regime-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.regime-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem; font-weight: 600; letter-spacing: 0.08em;
}
.regime-desc { font-size: 0.78rem; color: #7a9bbf; margin-left: auto; text-align: right; max-width: 540px; }
.live-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 10px; border-radius: 20px;
    background: rgba(34,211,238,0.07);
    border: 1px solid rgba(34,211,238,0.18);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; color: #22d3ee;
}
.live-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #22d3ee; display: inline-block;
    animation: blink 1.8s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.sig-pill {
    display: inline-block; padding: 2px 9px; border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.05em;
}
.sow { background: rgba(34,197,94,0.13);   color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.ow  { background: rgba(134,239,172,0.1);  color: #86efac; border: 1px solid rgba(134,239,172,0.2); }
.n   { background: rgba(148,163,184,0.08); color: #64748b; border: 1px solid rgba(148,163,184,0.15);}
.uw  { background: rgba(252,165,165,0.1);  color: #fca5a5; border: 1px solid rgba(252,165,165,0.2); }
.suw { background: rgba(239,68,68,0.13);   color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.hm-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 7px; }
.hm-cell { border-radius: 6px; padding: 9px 7px; text-align: center; }
.hm-name { font-size: 0.72rem; font-weight: 500; margin-bottom: 3px; }
.hm-sig  { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; font-weight: 600; }
.scorecard-wrap { background: #0d1b2a; border: 1px solid #1a2840; border-radius: 8px; padding: 12px 14px; }
.sc-row {
    display: grid; grid-template-columns: 120px 68px 22px 1fr;
    gap: 5px; align-items: center;
    padding: 5px 0; border-bottom: 1px solid rgba(26,40,64,0.5);
}
.sc-row:last-child { border-bottom: none; }
</style>
""", unsafe_allow_html=True)

# ─── Chart helpers ────────────────────────────────────────────────────────────
CHART_BG  = "rgba(0,0,0,0)"
GRID_CLR  = "rgba(26,40,64,0.7)"
MONO_FONT = "'IBM Plex Mono', monospace"
TICK_CLR  = "#3a5a7a"

def apply_theme(fig, height=340):
    """Apply dark theme to a plotly figure IN PLACE and return it."""
    fig.update_layout(
        height=height,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=MONO_FONT, color=TICK_CLR, size=10),
        legend=dict(
            bgcolor="rgba(13,27,42,0.9)", bordercolor="#1a2840",
            borderwidth=1, font=dict(size=9),
        ),
        margin=dict(l=8, r=12, t=36, b=28),
        xaxis=dict(gridcolor=GRID_CLR, zeroline=False, tickfont=dict(size=9),
                   showspikes=True, spikecolor="#1a2840", spikethickness=1),
        yaxis=dict(gridcolor=GRID_CLR, zeroline=False, tickfont=dict(size=9)),
    )
    return fig

def apply_theme_multi(fig, height=480):
    """Apply dark theme to a multi-subplot figure."""
    fig.update_layout(
        height=height,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family=MONO_FONT, color=TICK_CLR, size=10),
        legend=dict(
            bgcolor="rgba(13,27,42,0.9)", bordercolor="#1a2840",
            borderwidth=1, font=dict(size=9),
        ),
        margin=dict(l=8, r=12, t=36, b=28),
    )
    fig.update_xaxes(gridcolor=GRID_CLR, zeroline=False, tickfont=dict(size=9),
                     showspikes=True, spikecolor="#1a2840", spikethickness=1)
    fig.update_yaxes(gridcolor=GRID_CLR, zeroline=False, tickfont=dict(size=9))
    fig.update_annotations(font=dict(size=9, color=TICK_CLR))
    return fig

# ─── FRED series ─────────────────────────────────────────────────────────────
FRED_IDS = {
    "fed_rate": "FEDFUNDS",
    "cpi":      "CPIAUCSL",
    "core_cpi": "CPILFESL",
    "pce":      "PCEPI",
    "unrate":   "UNRATE",
    "gdp":      "GDP",
    "t10y":     "GS10",
    "t2y":      "GS2",
    "t3m":      "DTB3",
    "retail":   "RSAFS",
    "housing":  "HOUST",
    "m2":       "M2SL",
}

# ─── Sector ETFs ─────────────────────────────────────────────────────────────
SECTORS = {
    "Healthcare":    "XLV",
    "Consumer_Stap": "XLP",
    "Utilities":     "XLU",
    "Financials":    "XLF",
    "Energy":        "XLE",
    "Materials":     "XLB",
    "Industrials":   "XLI",
    "Technology":    "XLK",
    "Consumer_Disc": "XLY",
    "Real_Estate":   "XLRE",
    "Comm_Services": "XLC",
}
SECTOR_LABELS = {k: k.replace("_", " ") for k in SECTORS}

# ─── Data loaders ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_fred_data(api_key):
    fred  = Fred(api_key=api_key)
    end   = datetime.today()
    start = end - timedelta(days=365 * 5)
    raw   = {}
    for name, sid in FRED_IDS.items():
        try:
            s = fred.get_series(sid, start, end)
            if s is not None and not s.empty:
                raw[name] = s
        except Exception:
            pass

    df = pd.DataFrame(raw)

    # Derived columns — safe checks before computing
    if "cpi" in df.columns and len(df["cpi"].dropna()) > 12:
        df["cpi_yoy"] = df["cpi"].pct_change(12) * 100
    if "core_cpi" in df.columns and len(df["core_cpi"].dropna()) > 12:
        df["core_cpi_yoy"] = df["core_cpi"].pct_change(12) * 100
    if "pce" in df.columns and len(df["pce"].dropna()) > 12:
        df["pce_yoy"] = df["pce"].pct_change(12) * 100
    if "gdp" in df.columns and len(df["gdp"].dropna()) > 4:
        df["gdp_g"] = df["gdp"].pct_change(4) * 100
    if "m2" in df.columns and len(df["m2"].dropna()) > 12:
        df["m2_g"] = df["m2"].pct_change(12) * 100
    if "retail" in df.columns and len(df["retail"].dropna()) > 12:
        df["retail_g"] = df["retail"].pct_change(12) * 100
    if "t10y" in df.columns and "t2y" in df.columns:
        df["curve_10_2"] = df["t10y"] - df["t2y"]
    if "t10y" in df.columns and "t3m" in df.columns:
        df["curve_10_3m"] = df["t10y"] - df["t3m"]

    return df

@st.cache_data(ttl=900, show_spinner=False)
def load_etf_data():
    rows = []
    for key, ticker in SECTORS.items():
        try:
            hist = yf.Ticker(ticker).history(period="1y")
            if hist.empty:
                continue
            closes = hist["Close"]
            now    = float(closes.iloc[-1])

            def pct(n):
                idx = max(0, len(closes) - n)
                base = float(closes.iloc[idx])
                return round((now / base - 1) * 100, 2) if base != 0 else None

            ys  = closes[closes.index >= f"{datetime.today().year}-01-01"]
            ytd = round((now / float(ys.iloc[0]) - 1) * 100, 2) if not ys.empty else None

            rows.append({
                "key":    key,
                "label":  SECTOR_LABELS[key],
                "ticker": ticker,
                "price":  round(now, 2),
                "d1":     pct(2),
                "m1":     pct(22),
                "ytd":    ytd,
            })
        except Exception:
            pass
    return rows

# ─── Signal engine ─────────────────────────────────────────────────────────────
def get_latest(df, col):
    if col not in df.columns:
        return None
    s = df[col].dropna()
    return float(s.iloc[-1]) if not s.empty else None

def get_prev(df, col, n=1):
    if col not in df.columns:
        return None
    s = df[col].dropna()
    return float(s.iloc[-1 - n]) if len(s) > n else None

def compute_signals(df):
    fed   = get_latest(df, "fed_rate")     or 0
    cpi   = get_latest(df, "cpi_yoy")      or 0
    core  = get_latest(df, "core_cpi_yoy") or 0
    unr   = get_latest(df, "unrate")       or 0
    gdpg  = get_latest(df, "gdp_g")        or 0
    cur   = get_latest(df, "curve_10_2")   or 0
    cur3m = get_latest(df, "curve_10_3m")  or 0
    m2g   = get_latest(df, "m2_g")         or 0
    retg  = get_latest(df, "retail_g")     or 0

    # Regime
    if cpi > 5 and fed > 4:
        regime = "HIGH INFLATION · TIGHT POLICY"
        color  = "#f87171"
        desc   = "Fed in active tightening. Risk assets under pressure. Energy, Materials and Financials tend to outperform."
    elif cpi > 3 and fed < 3:
        regime = "INFLATION RESURGENCE · POLICY LAG"
        color  = "#fb923c"
        desc   = "Inflation above target but policy is behind the curve. Watch commodities, TIPS and Materials."
    elif cur < 0 or cur3m < 0:
        regime = "INVERTED YIELD CURVE · RECESSION RISK"
        color  = "#f59e0b"
        desc   = f"Curve inverted at {cur:.2f}%. Historically precedes recession by 6-18 months. Rotate to defensives."
    elif cpi < 2.5 and fed < 3 and unr < 5 and gdpg > 1.5:
        regime = "GOLDILOCKS · SOFT LANDING"
        color  = "#4ade80"
        desc   = "Low inflation, easy policy, strong labour market. Ideal for broad risk-on. Tech and Consumer Disc lead."
    elif unr > 5.5 or gdpg < 0:
        regime = "RECESSION · RISK-OFF"
        color  = "#f87171"
        desc   = "Growth contracting. Defensive positioning is key. Healthcare, Staples, Utilities, cash preservation."
    else:
        regime = "MID-CYCLE EXPANSION"
        color  = "#22d3ee"
        desc   = "Normalised expansion. Balanced positioning with a tilt toward cyclicals and quality growth names."

    # Sector scores
    scores = {k: 0 for k in SECTORS}

    if cpi > 5:
        scores["Energy"] += 2; scores["Materials"] += 2
        scores["Real_Estate"] -= 2; scores["Technology"] -= 1; scores["Utilities"] -= 1
    elif cpi > 3:
        scores["Energy"] += 1; scores["Materials"] += 1; scores["Real_Estate"] -= 1

    if fed > 5:
        scores["Financials"] += 2; scores["Utilities"] -= 2
        scores["Real_Estate"] -= 2; scores["Consumer_Disc"] -= 1
    elif fed > 3:
        scores["Financials"] += 1; scores["Utilities"] -= 1; scores["Real_Estate"] -= 1
    elif fed < 2:
        scores["Real_Estate"] += 1; scores["Utilities"] += 1; scores["Technology"] += 1

    if cur < -0.5 or cur3m < -0.5:
        scores["Healthcare"] += 2; scores["Consumer_Stap"] += 2; scores["Utilities"] += 1
        scores["Industrials"] -= 1; scores["Consumer_Disc"] -= 2; scores["Technology"] -= 1
    elif cur > 1.5:
        scores["Financials"] += 1; scores["Industrials"] += 1

    if gdpg < 0:
        scores["Healthcare"] += 2; scores["Consumer_Stap"] += 2; scores["Utilities"] += 1
        scores["Technology"] -= 2; scores["Consumer_Disc"] -= 2
    elif gdpg > 3:
        scores["Technology"] += 1; scores["Industrials"] += 1; scores["Consumer_Disc"] += 1

    if unr < 4:
        scores["Consumer_Disc"] += 1; scores["Technology"] += 1
    elif unr > 6:
        scores["Consumer_Disc"] -= 2; scores["Real_Estate"] -= 1
        scores["Healthcare"] += 1; scores["Consumer_Stap"] += 1

    if m2g > 8:
        scores["Technology"] += 1; scores["Real_Estate"] += 1
    elif m2g < 0:
        scores["Technology"] -= 1; scores["Real_Estate"] -= 1

    if retg and retg > 5:   scores["Consumer_Disc"] += 1
    elif retg and retg < 0: scores["Consumer_Disc"] -= 1

    scores = {k: max(-2, min(2, v)) for k, v in scores.items()}
    conviction = min(100, int((abs(cpi - 2.5) + abs(fed - 3) + abs(unr - 4.5) + abs(cur)) * 12))

    return dict(
        regime=regime, color=color, desc=desc,
        scores=scores, conviction=conviction,
        fed=fed, cpi=cpi, core=core, unr=unr,
        gdpg=gdpg, cur=cur, cur3m=cur3m, m2g=m2g, retg=retg,
    )

# ─── Display helpers ──────────────────────────────────────────────────────────
PILL_CLS  = {2:"sow", 1:"ow", 0:"n", -1:"uw", -2:"suw"}
PILL_TXT  = {2:"STRONG OW", 1:"OVERWEIGHT", 0:"NEUTRAL", -1:"UNDERWEIGHT", -2:"STRONG UW"}
BAR_CLR   = {2:"#4ade80", 1:"#86efac", 0:"#475569", -1:"#fca5a5", -2:"#f87171"}
HM_BG     = {2:"rgba(74,222,128,0.14)", 1:"rgba(134,239,172,0.1)",
             0:"rgba(148,163,184,0.07)", -1:"rgba(252,165,165,0.1)",
             -2:"rgba(239,68,68,0.14)"}
HM_CLR    = {2:"#4ade80", 1:"#86efac", 0:"#64748b", -1:"#fca5a5", -2:"#f87171"}

def pill_html(score):
    return f'<span class="sig-pill {PILL_CLS[score]}">{PILL_TXT[score]}</span>'

def pct_html(val):
    if val is None:
        return '<span style="color:#3a5a7a">—</span>'
    color = "#4ade80" if val > 0 else "#f87171" if val < 0 else "#64748b"
    sign  = "+" if val > 0 else ""
    return (f'<span style="color:{color};font-family:{MONO_FONT};'
            f'font-size:0.78rem">{sign}{val:.1f}%</span>')

def trend_arrow(df, col):
    if col not in df.columns:
        return "→", "#64748b"
    s = df[col].dropna()
    if len(s) < 3:
        return "→", "#64748b"
    diff = s.iloc[-1] - s.iloc[-3]
    if diff > 0.05:  return "↑", "#4ade80"
    if diff < -0.05: return "↓", "#f87171"
    return "→", "#64748b"

def safe_metric(val, prev_val, label, help_text="", delta_color="normal"):
    """Render a metric card, safely handling None values."""
    display = f"{val:.2f}%" if val is not None else "N/A"
    delta   = f"{val - prev_val:+.2f}" if val is not None and prev_val is not None else None
    st.metric(label, display, delta, delta_color=delta_color, help=help_text)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙ Settings")
    api_input = st.text_input(
        "FRED API Key", value=FRED_API_KEY, type="password",
        help="Free at fred.stlouisfed.org/docs/api/api_key.html",
    )
    if api_input and api_input != "YOUR_FRED_API_KEY_HERE":
        FRED_API_KEY = api_input
    st.divider()
    lookback_label = st.selectbox("Chart Lookback", ["1Y","2Y","3Y","5Y"], index=2)
    lookback_days  = {"1Y":365,"2Y":730,"3Y":1095,"5Y":1825}[lookback_label]
    st.divider()
    st.caption("Data: FRED (hourly) + yfinance (15 min)\nNot financial advice.")

# ─── API key guard ─────────────────────────────────────────────────────────────
if FRED_API_KEY == "YOUR_FRED_API_KEY_HERE":
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem">
      <div style="font-size:3rem;margin-bottom:1rem">📡</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-size:1.4rem;
                  font-weight:700;color:#e8f4ff;margin-bottom:0.5rem">
        Connect your data feed
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:#3a5a7a">
        Paste your FRED API key in the sidebar ←<br>
        Free key at <strong style="color:#22d3ee">fred.stlouisfed.org</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Loading live data feeds…"):
    df   = load_fred_data(FRED_API_KEY)
    sig  = compute_signals(df)
    etfs = load_etf_data()

cutoff = datetime.today() - timedelta(days=lookback_days)
dfc    = df[df.index >= cutoff]

# ─── Header ───────────────────────────────────────────────────────────────────
c_title, c_conv, c_count = st.columns([3, 1, 1])
with c_title:
    st.markdown("# 📡 MACRO/SIGNAL")
    st.markdown(
        f'<span class="live-chip"><span class="live-dot"></span>'
        f'LIVE &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y %H:%M")} SGT</span>',
        unsafe_allow_html=True,
    )
with c_conv:
    st.metric("Signal Conviction", f"{sig['conviction']}%",
              help="How many indicators agree on a clear directional signal")
with c_count:
    st.metric("Indicators Tracked", "12",
              help="Fed Rate, CPI, Core CPI, PCE, Unemployment, GDP, 10Y, 2Y, 3M, Yield Curve, M2, Retail")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Regime banner ────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="regime-banner" style="border-left:3px solid {sig["color"]}">'
    f'<div class="regime-dot" style="background:{sig["color"]}"></div>'
    f'<div class="regime-name" style="color:{sig["color"]}">{sig["regime"]}</div>'
    f'<div class="regime-desc">{sig["desc"]}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ─── KPI metrics ──────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1: safe_metric(sig["fed"],  get_prev(df,"fed_rate"),    "Fed Funds Rate",    FRED_IDS["fed_rate"])
with k2: safe_metric(sig["cpi"],  get_prev(df,"cpi_yoy"),     "CPI YoY",           "CPI year-over-year % change")
with k3: safe_metric(sig["core"], get_prev(df,"core_cpi_yoy"),"Core CPI YoY",      "Core CPI excl. food & energy")
with k4: safe_metric(sig["unr"],  get_prev(df,"unrate"),      "Unemployment",      FRED_IDS["unrate"], delta_color="inverse")
with k5: safe_metric(sig["cur"],  get_prev(df,"curve_10_2"),  "Yield Curve 10-2Y", "10Y minus 2Y Treasury yield")
with k6: safe_metric(sig["gdpg"], get_prev(df,"gdp_g"),       "GDP Growth YoY",    "Annualised GDP growth rate")

st.divider()

# ─── Sector signals + ETF table ───────────────────────────────────────────────
left, right = st.columns([1, 1.05], gap="large")

with left:
    st.markdown("### Sector rotation signals")

    sorted_sc  = sorted(sig["scores"].items(), key=lambda x: x[1])
    bar_names  = [SECTOR_LABELS[k] for k, _ in sorted_sc]
    bar_scores = [v for _, v in sorted_sc]
    bar_colors = [BAR_CLR[v] for v in bar_scores]
    bar_labels = [PILL_TXT[v] for v in bar_scores]

    fig_bar = go.Figure(go.Bar(
        x=bar_scores, y=bar_names, orientation="h",
        marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,0.04)", width=1)),
        text=bar_labels, textposition="outside",
        textfont=dict(family=MONO_FONT, size=9, color="#7a9bbf"),
        hovertemplate="<b>%{y}</b><br>Score: %{x}<extra></extra>",
        cliponaxis=False,
    ))
    fig_bar.add_vline(x=0, line_color="rgba(148,163,184,0.2)", line_width=1)

    # Apply theme then update layout separately — no chaining
    apply_theme(fig_bar, height=380)
    fig_bar.update_layout(
        xaxis=dict(
            range=[-3.2, 3.2],
            tickvals=[-2, -1, 0, 1, 2],
            ticktext=["Strong UW","UW","Neutral","OW","Strong OW"],
            gridcolor=GRID_CLR, tickfont=dict(size=9),
        ),
        yaxis=dict(tickfont=dict(size=10, family=MONO_FONT)),
        margin=dict(l=8, r=105, t=12, b=28),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    st.markdown("### Live ETF performance")
    if etfs:
        tbl = (
            "<table style='width:100%;border-collapse:collapse;"
            "font-family:IBM Plex Mono,monospace' "
            "role='table' aria-label='Sector ETF live performance and signals'>"
            "<thead><tr style='border-bottom:1px solid #1a2840'>"
            "<th scope='col' style='padding:5px 6px;color:#243a52;font-size:0.68rem;text-align:left'>SECTOR</th>"
            "<th scope='col' style='padding:5px 6px;color:#243a52;font-size:0.68rem;text-align:right'>PRICE</th>"
            "<th scope='col' style='padding:5px 6px;color:#243a52;font-size:0.68rem;text-align:right'>1D</th>"
            "<th scope='col' style='padding:5px 6px;color:#243a52;font-size:0.68rem;text-align:right'>1M</th>"
            "<th scope='col' style='padding:5px 6px;color:#243a52;font-size:0.68rem;text-align:right'>YTD</th>"
            "<th scope='col' style='padding:5px 6px;color:#243a52;font-size:0.68rem;text-align:left'>SIGNAL</th>"
            "</tr></thead><tbody>"
        )
        for e in etfs:
            score = sig["scores"].get(e["key"], 0)
            tbl += (
                f"<tr style='border-bottom:1px solid rgba(26,40,64,0.5)'>"
                f"<td style='padding:5px 6px'>"
                f"<span style='color:#c9d8eb;font-size:0.78rem'>{e['label']}</span>"
                f"<span style='color:#243a52;font-size:0.68rem;margin-left:5px'>{e['ticker']}</span>"
                f"</td>"
                f"<td style='padding:5px 6px;text-align:right;color:#22d3ee;"
                f"font-family:IBM Plex Mono,monospace;font-size:0.78rem'>${e['price']}</td>"
                f"<td style='padding:5px 6px;text-align:right'>{pct_html(e['d1'])}</td>"
                f"<td style='padding:5px 6px;text-align:right'>{pct_html(e['m1'])}</td>"
                f"<td style='padding:5px 6px;text-align:right'>{pct_html(e['ytd'])}</td>"
                f"<td style='padding:5px 6px'>{pill_html(score)}</td>"
                f"</tr>"
            )
        tbl += "</tbody></table>"
        st.markdown(tbl, unsafe_allow_html=True)
    else:
        st.warning("ETF data unavailable. Check your internet connection.")

st.divider()

# ─── Historical charts ────────────────────────────────────────────────────────
st.markdown("### Historical macro charts")

COLORS = dict(
    blue="#22d3ee", red="#f87171", orange="#fb923c",
    green="#4ade80", purple="#a78bfa", yellow="#f59e0b",
    teal="#2dd4bf",  pink="#f472b6",
)

tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Rates & Inflation",
    "📉  Yield Curve",
    "💼  Labour & Growth",
    "💧  Liquidity",
])

with tab1:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.45], vertical_spacing=0.08,
        subplot_titles=("Policy rate vs inflation", "PCE inflation & 10Y yield"),
    )
    if "fed_rate" in dfc.columns:
        fig.add_trace(go.Scatter(x=dfc.index, y=dfc["fed_rate"], name="Fed Rate",
            line=dict(color=COLORS["blue"], width=2),
            fill="tozeroy", fillcolor="rgba(34,211,238,0.05)"), row=1, col=1)
    if "cpi_yoy" in dfc.columns:
        fig.add_trace(go.Scatter(x=dfc.index, y=dfc["cpi_yoy"], name="CPI YoY",
            line=dict(color=COLORS["red"], width=2)), row=1, col=1)
    if "core_cpi_yoy" in dfc.columns:
        fig.add_trace(go.Scatter(x=dfc.index, y=dfc["core_cpi_yoy"], name="Core CPI",
            line=dict(color=COLORS["orange"], width=1.5, dash="dot")), row=1, col=1)
    fig.add_hline(y=2, line_dash="dash", line_color="rgba(148,163,184,0.25)",
                  annotation_text="2% target", annotation_font_size=9, row=1, col=1)
    if "pce_yoy" in dfc.columns:
        fig.add_trace(go.Scatter(x=dfc.index, y=dfc["pce_yoy"], name="PCE YoY",
            line=dict(color=COLORS["purple"], width=1.5)), row=2, col=1)
    if "t10y" in dfc.columns:
        fig.add_trace(go.Scatter(x=dfc.index, y=dfc["t10y"], name="10Y Yield",
            line=dict(color=COLORS["teal"], width=1.5)), row=2, col=1)
    apply_theme_multi(fig, height=480)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.5, 0.5], vertical_spacing=0.08,
        subplot_titles=("10Y – 2Y spread (inversion monitor)", "10Y – 3M spread"),
    )
    for col_key, row_num in [("curve_10_2", 1), ("curve_10_3m", 2)]:
        if col_key in dfc.columns:
            s   = dfc[col_key]
            pos = s.clip(lower=0)
            neg = s.clip(upper=0)
            fig2.add_trace(go.Scatter(x=s.index, y=pos, name="Normal",
                fill="tozeroy", fillcolor="rgba(74,222,128,0.1)",
                line=dict(color=COLORS["green"], width=2)), row=row_num, col=1)
            fig2.add_trace(go.Scatter(x=s.index, y=neg, name="Inverted",
                fill="tozeroy", fillcolor="rgba(248,113,113,0.12)",
                line=dict(color=COLORS["red"], width=2)), row=row_num, col=1)
            fig2.add_hline(y=0, line_color="rgba(148,163,184,0.3)",
                           line_width=1, row=row_num, col=1)
    apply_theme_multi(fig2, height=480)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("⚠ Yield curve inversion has preceded every US recession since 1955, typically by 6-18 months.")

with tab3:
    fig3 = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Unemployment rate", "GDP growth YoY",
                        "Retail sales growth YoY", "Housing starts"),
        vertical_spacing=0.12, horizontal_spacing=0.08,
    )
    if "unrate" in dfc.columns:
        fig3.add_trace(go.Scatter(x=dfc.index, y=dfc["unrate"], name="Unemployment",
            line=dict(color=COLORS["purple"], width=2),
            fill="tozeroy", fillcolor="rgba(167,139,250,0.07)"), row=1, col=1)
    if "gdp_g" in dfc.columns:
        gd = dfc["gdp_g"].dropna()
        fig3.add_trace(go.Bar(x=gd.index, y=gd.values, name="GDP",
            marker_color=[COLORS["green"] if v >= 0 else COLORS["red"] for v in gd],
            opacity=0.75), row=1, col=2)
        fig3.add_hline(y=0, line_color="rgba(148,163,184,0.3)", row=1, col=2)
    if "retail_g" in dfc.columns:
        fig3.add_trace(go.Scatter(x=dfc.index, y=dfc["retail_g"], name="Retail",
            line=dict(color=COLORS["teal"], width=2)), row=2, col=1)
    if "housing" in dfc.columns:
        fig3.add_trace(go.Scatter(x=dfc.index, y=dfc["housing"], name="Housing",
            line=dict(color=COLORS["pink"], width=2),
            fill="tozeroy", fillcolor="rgba(244,114,182,0.06)"), row=2, col=2)
    apply_theme_multi(fig3, height=480)
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    fig4 = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.5, 0.5], vertical_spacing=0.08,
        subplot_titles=("M2 money supply growth YoY", "Fed rate vs 10Y-2Y spread"),
    )
    if "m2_g" in dfc.columns:
        m2d = dfc["m2_g"].dropna()
        fig4.add_trace(go.Scatter(x=m2d.index, y=m2d.values, name="M2 YoY",
            line=dict(color=COLORS["yellow"], width=2),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.07)"), row=1, col=1)
        fig4.add_hline(y=0, line_color="rgba(148,163,184,0.3)", row=1, col=1)
    if "curve_10_2" in dfc.columns:
        fig4.add_trace(go.Scatter(x=dfc.index, y=dfc["curve_10_2"], name="10Y-2Y",
            line=dict(color=COLORS["teal"], width=1.5)), row=2, col=1)
    if "fed_rate" in dfc.columns:
        fig4.add_trace(go.Scatter(x=dfc.index, y=dfc["fed_rate"], name="Fed Rate",
            line=dict(color=COLORS["blue"], width=1.5, dash="dot")), row=2, col=1)
        fig4.add_hline(y=0, line_color="rgba(148,163,184,0.3)", row=2, col=1)
    apply_theme_multi(fig4, height=480)
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("M2 contraction (negative YoY) is rare and has historically coincided with stress in credit markets.")

st.divider()

# ─── Heatmap + Scorecard ──────────────────────────────────────────────────────
hm_col, sc_col = st.columns([1.3, 1], gap="large")

with hm_col:
    st.markdown("### Sector regime heatmap")
    cells = ""
    for k, label in SECTOR_LABELS.items():
        v = sig["scores"][k]
        cells += (
            f'<div class="hm-cell" style="background:{HM_BG[v]};border:1px solid {HM_CLR[v]}28">'
            f'<div class="hm-name" style="color:{HM_CLR[v]}">{label}</div>'
            f'<div class="hm-sig" style="color:{HM_CLR[v]}">{PILL_TXT[v]}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="hm-grid">{cells}</div>', unsafe_allow_html=True)

with sc_col:
    st.markdown("### Macro scorecard")
    sc_items = [
        ("Fed Funds",    "fed_rate",      "fed",  "Tight" if sig["fed"] > 4 else "Easy" if sig["fed"] < 2 else "Neutral"),
        ("CPI YoY",      "cpi_yoy",       "cpi",  "Hot" if sig["cpi"] > 4 else "Elevated" if sig["cpi"] > 2.5 else "Anchored"),
        ("Core CPI",     "core_cpi_yoy",  "core", "Sticky" if sig["core"] > 3 else "Softening"),
        ("Unemployment", "unrate",        "unr",  "Tight" if sig["unr"] < 4.5 else "Loose"),
        ("GDP Growth",   "gdp_g",         "gdpg", "Expanding" if sig["gdpg"] and sig["gdpg"] > 2 else "Slowing"),
        ("Yield Curve",  "curve_10_2",    "cur",  "Inverted" if sig["cur"] < 0 else "Normal"),
        ("M2 Growth",    "m2_g",          "m2g",  "Contracting" if sig["m2g"] and sig["m2g"] < 0 else "Expanding"),
        ("Retail Sales", "retail_g",      "retg", "Strong" if sig["retg"] and sig["retg"] > 4 else "Resilient"),
    ]
    rows = ""
    for label, col_key, sig_key, reading in sc_items:
        v            = sig.get(sig_key)
        arr, ac      = trend_arrow(df, col_key)
        val          = f"{v:.2f}%" if v is not None else "N/A"
        rows += (
            f'<div class="sc-row">'
            f'<span style="color:#7a9bbf;font-family:{MONO_FONT};font-size:0.72rem">{label}</span>'
            f'<span style="color:#22d3ee;font-family:{MONO_FONT};font-size:0.78rem;font-weight:600;text-align:right">{val}</span>'
            f'<span style="color:{ac};font-size:0.95rem;text-align:center">{arr}</span>'
            f'<span style="color:#3a5a7a;font-size:0.7rem">{reading}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="scorecard-wrap">{rows}</div>', unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    f"""<div style="display:flex;justify-content:space-between;padding-top:10px;
                    border-top:1px solid #1a2840;margin-top:1rem">
      <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#1e3552">
        Data: Federal Reserve Economic Data (FRED) · yfinance</span>
      <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#1e3552">
        Educational only — not financial advice</span>
      <span style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#1e3552">
        MACRO/SIGNAL v3.1 · {datetime.now().year}</span>
    </div>""",
    unsafe_allow_html=True,
)
