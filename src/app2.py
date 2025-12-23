from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Trading Backtester", layout="wide")
st.title("Trading Backtester")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO_ROOT / "data" / "omxs.csv"

csv_path_str = st.sidebar.text_input("CSV path", value=str(DEFAULT_CSV))
csv_path = Path(csv_path_str)

st.sidebar.header("Time resolution")
resolution = st.sidebar.selectbox("Resample to", ["D", "H", "15T", "5T"], index=0)

# Toggle indicators
st.sidebar.header("Indicators")
show_sma = st.sidebar.checkbox("SMA", value=True)
sma_len = st.sidebar.slider("SMA length", 2, 300, 50)
sma_color = st.sidebar.color_picker("SMA color", "#1f77b4")

show_ema = st.sidebar.checkbox("EMA", value=False)
ema_len = st.sidebar.slider("EMA length", 2, 300, 20)
ema_color = st.sidebar.color_picker("EMA color", "#ff7f0e")

show_volume = st.sidebar.checkbox("Volume bars", value=False)
vol_color = st.sidebar.color_picker("Volume color", "#7f7f7f")

# RSI (oscillator in the lower panel)
show_rsi = st.sidebar.checkbox("RSI", value=True)
rsi_len = st.sidebar.slider("RSI length", 2, 100, 14)
rsi_color = st.sidebar.color_picker("RSI color", "#9467bd")  # purple-ish default
show_rsi_levels = st.sidebar.checkbox("RSI levels (30/70)", value=True)
level_color = st.sidebar.color_picker("RSI level color", "#aaaaaa")


# Chart style
st.sidebar.header("Chart")
candle_up = st.sidebar.color_picker("Candle up color", "#2ca02c")
candle_down = st.sidebar.color_picker("Candle down color", "#d62728")

@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    df_try = pd.read_csv(path)
    if df_try.shape[1] == 1:
        df_try = pd.read_csv(path, sep=";")
    return df_try

if not csv_path.exists():
    st.error(f"File not found: {csv_path}")
    st.stop()

df = load_csv(str(csv_path))

# ---- Column detection for OHLC ----
# We assume the first column is time.
time_col = df.columns[0]
df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
df = df.dropna(subset=[time_col]).sort_values(time_col)

# Try common OHLC column names.
def pick_col(candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None

open_col = pick_col(["Open", "open", "OPEN"])
high_col = pick_col(["High", "high", "HIGH"])
low_col = pick_col(["Low", "low", "LOW"])
close_col = pick_col(["Close", "close", "CLOSE", "Last", "last", "PRICE", "Price", "price"])
vol_col = pick_col(["Volume", "volume", "VOL", "vol"])

# If we do not have full OHLC, we cannot do true candlesticks.
has_ohlc = all([open_col, high_col, low_col, close_col])

# Coerce numeric columns
for c in [open_col, high_col, low_col, close_col, vol_col]:
    if c is not None:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ---- Resample to OHLC (and volume if available) ----
df = df.set_index(time_col)

if has_ohlc:
    ohlc = df[[open_col, high_col, low_col, close_col]].resample(resolution).agg({
        open_col: "first",
        high_col: "max",
        low_col: "min",
        close_col: "last",
    }).dropna()

    ohlc = ohlc.rename(columns={
        open_col: "open",
        high_col: "high",
        low_col: "low",
        close_col: "close",
    })

else:
    # Fallback: if we only have one price column, build a "pseudo candle" from that.
    # This is not real OHLC, but it lets you keep the same UI while you fix your dataset later.
    if close_col is None:
        st.error("Could not find a Close/Price column. Check your CSV headers.")
        st.write("Columns:", df.columns.tolist())
        st.stop()

    price = df[close_col].resample(resolution).last().dropna()
    ohlc = pd.DataFrame({
        "open": price.shift(1),
        "high": price,
        "low": price,
        "close": price,
    }).dropna()

volume = None
if vol_col is not None:
    volume = df[vol_col].resample(resolution).sum().dropna()

ohlc = ohlc.reset_index().rename(columns={time_col: "time"})

st.sidebar.caption(f"Detected time column: {time_col}")
if has_ohlc:
    st.sidebar.caption("Detected OHLC columns: yes")
else:
    st.sidebar.caption("Detected OHLC columns: no. Using pseudo candles from Close/Price.")
if vol_col is not None:
    st.sidebar.caption(f"Detected volume column: {vol_col}")

# ---- Indicator calculations (based on close) ----
close = ohlc["close"]

sma = close.rolling(sma_len).mean() if show_sma else None
ema = close.ewm(span=ema_len, adjust=False).mean() if show_ema else None

# ---- Build figure with two panels ----
# Row 1: candles
# Row 2: indicator panel (we will place volume here or leave it for future oscillators)
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=[0.75, 0.25],
)

# Candlesticks
fig.add_trace(
    go.Candlestick(
        x=ohlc["time"],
        open=ohlc["open"],
        high=ohlc["high"],
        low=ohlc["low"],
        close=ohlc["close"],
        name="Candles",
        increasing_line_color=candle_up,
        increasing_fillcolor=candle_up,
        decreasing_line_color=candle_down,
        decreasing_fillcolor=candle_down,
    ),
    row=1, col=1
)

# Overlay indicators on price panel
if show_sma and sma is not None:
    fig.add_trace(
        go.Scatter(
            x=ohlc["time"],
            y=sma,
            mode="lines",
            name=f"SMA {sma_len}",
            line=dict(color=sma_color),
        ),
        row=1, col=1
    )

if show_ema and ema is not None:
    fig.add_trace(
        go.Scatter(
            x=ohlc["time"],
            y=ema,
            mode="lines",
            name=f"EMA {ema_len}",
            line=dict(color=ema_color),
        ),
        row=1, col=1
    )

# Volume in the lower panel if enabled and available
if show_volume and volume is not None:
    vol_df = pd.DataFrame({"time": volume.index, "volume": volume.values})
    fig.add_trace(
        go.Bar(
            x=vol_df["time"],
            y=vol_df["volume"],
            name="Volume",
            marker=dict(color=vol_color),
        ),
        row=2, col=1
    )
else:
    # Placeholder line so the panel is visible
    fig.add_trace(
        go.Scatter(
            x=ohlc["time"],
            y=[0] * len(ohlc),
            mode="lines",
            name="Indicator placeholder",
        ),
        row=2, col=1
    )

# Hover and layout. "x unified" feels closer to TradingView.
fig.update_layout(
    height=750,
    margin=dict(l=20, r=20, t=40, b=20),
    hovermode="x unified",
)

# TradingView-like navigation
fig.update_xaxes(
    rangeslider=dict(visible=True),
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(count=5, label="5Y", step="year", stepmode="backward"),
            dict(step="all", label="All"),
        ])
    ),
    row=2, col=1
)

fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="Indicators", row=2, col=1)

# Draw tools via modebar and scroll zoom.
# These tools let you draw lines and shapes on the chart.
config = {
    "displayModeBar": True,
    "scrollZoom": True,
    "displaylogo": False,
    "modeBarButtonsToAdd": [
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawrect",
        "drawcircle",
        "eraseshape",
        "zoomIn2d",
        "zoomOut2d",
        "resetScale2d",
        "pan2d",
    ],
}

st.plotly_chart(fig, use_container_width=True, config=config)

with st.expander("Show OHLC preview"):
    st.dataframe(ohlc.head(50))

