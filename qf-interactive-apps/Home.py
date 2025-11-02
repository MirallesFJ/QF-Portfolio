import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import genpareto
import altair as alt

st.set_page_config(
    page_title="Risk Dashboard",  # Title shown in browser tab
    page_icon="📊",  # Optional emoji/icon
)


# --------- Helpers
@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def compute_var(returns: pd.Series, alpha: float, method: str = "historical"):
    r = returns.dropna().values
    if method == "historical":
        # VaR as (1 - alpha) quantile of loss (-ret)
        return np.quantile(-r, 1 - alpha)
    elif method == "parametric":
        mu, sigma = np.mean(r), np.std(r, ddof=1)
        z = {0.90: 1.2816, 0.95: 1.6449, 0.99: 2.3263}[alpha]
        return -(mu - z * sigma)  # VaR on returns
    else:
        raise ValueError("Unknown method")


def fit_evt_tail(returns: pd.Series, threshold_q: float = 0.90):
    """Simple POT approach on losses."""
    losses = -returns.dropna().values
    u = np.quantile(losses, threshold_q)  # threshold
    excess = losses[losses > u] - u
    # Fit GPD to excesses
    c, loc, scale = genpareto.fit(excess, floc=0)
    return dict(threshold=u, shape=c, scale=scale)


def var_evt(returns: pd.Series, alpha: float, threshold_q: float = 0.90):
    """Approximate EVT VaR using fitted GPD on tail."""
    losses = -returns.dropna().values
    n = len(losses)
    u = np.quantile(losses, threshold_q)
    excess = losses[losses > u] - u
    m = len(excess)
    if m < 10:
        return np.nan  # not enough tail data
    c, loc, scale = genpareto.fit(excess, floc=0)
    # Tail prob level for exceedances
    p_u = m / n
    # Target tail prob (1 - alpha)
    p = 1 - alpha
    # VaR formula under GPD tail (POT)
    if c != 0:
        q = u + (scale / c) * ((p / p_u) ** (-c) - 1)
    else:
        q = u + scale * np.log(p_u / p)
    return q


# --------- Sidebar (controls)
st.sidebar.header("Controls")
source = st.sidebar.radio("Data source", ["Sample CSV", "Upload CSV"], horizontal=True)
alpha = st.sidebar.select_slider(
    "Confidence level (α)", options=[0.90, 0.95, 0.99], value=0.95
)
method = st.sidebar.selectbox("VaR method", ["historical", "parametric", "evt"])
evt_q = st.sidebar.slider("EVT threshold quantile", 0.80, 0.99, 0.90, 0.01)

if source == "Sample CSV":
    df = load_csv("data/AAPL.csv")
else:
    up = st.sidebar.file_uploader("Upload CSV with columns: date, ret", type=["csv"])
    if up:
        df = pd.read_csv(up, parse_dates=["date"]).sort_values("date")
    else:
        st.stop()

# --------- Main
st.title("📉 Risk Lab — VaR & EVT")
st.caption("Drop-in scaffold you can reuse for your quant projects.")

# Basic stats
colA, colB, colC, colD = st.columns(4)
r = df["ret"].astype(float)
colA.metric("Observations", f"{len(r):,}")
colB.metric("Mean (daily)", f"{r.mean():.4f}")
colC.metric("Std (daily)", f"{r.std(ddof=1):.4f}")
colD.metric("Skew", f"{pd.Series(r).skew():.2f}")

# Chart
c = (
    alt.Chart(df)
    .mark_line()
    .encode(x="date:T", y="ret:Q", tooltip=["date:T", "ret:Q"])
    .properties(height=250)
)
st.altair_chart(c, width="stretch")

# Tabs: VaR + Distribution
tab1, tab2 = st.tabs(["VaR", "Distribution"])

with tab1:
    if method in ("historical", "parametric"):
        var = compute_var(r, alpha=alpha, method=method)
    else:
        var = var_evt(r, alpha=alpha, threshold_q=evt_q)
    st.subheader(f"VaR @ {int(alpha*100)}% ({method})")
    st.code(f"VaR = {var:.6f}" if pd.notna(var) else "VaR = NaN (not enough tail data)")

    # Optional: simple PnL simulation with position size
    size = st.number_input("Position notional (€)", value=100000.0, step=1000.0)
    if pd.notna(var):
        loss_euro = size * var
        st.metric("One-day VaR (EUR)", f"{loss_euro:,.0f}")

with tab2:
    # Histogram of returns
    bins = st.slider("Bins", 10, 100, 40, 5)
    hist = (
        alt.Chart(pd.DataFrame({"ret": r}))
        .mark_bar()
        .encode(
            alt.X("ret:Q", bin=alt.Bin(maxbins=bins)), y="count()", tooltip=["count()"]
        )
        .properties(height=250)
    )
    st.altair_chart(hist, width="stretch")

# Session state demo (remember UI choices)
st.session_state.setdefault("alpha_history", [])
if st.button("Save current α to history"):
    st.session_state["alpha_history"].append(alpha)
st.write("α history:", st.session_state["alpha_history"])
