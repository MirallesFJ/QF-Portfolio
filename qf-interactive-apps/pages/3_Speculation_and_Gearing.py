import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Speculation & Gearing", layout="wide")

st.title("📈 Speculation & Gearing (Leverage) — Call Options")

st.markdown(
    r"""
**Idea (Wilmott):** Buying a far out-of-the-money call can give a **large % return** for a small premium if the underlying moves a lot.  
Downside: the option can expire worthless → **100 % loss** of premium.

We compare **buying the stock** vs **buying the call** and then simulate outcomes.

**Formulas**

- Stock % return: $R_S = \frac{S_T - S_0}{S_0} \times 100\%$
- Call payoff: $\max(S_T - K, 0)$
- Call profit: $\max(S_T - K, 0) - C$
- Call % return: $R_C = \frac{\max(S_T - K, 0) - C}{C} \times 100\%$

**Gearing (leverage)** at a scenario $S_T$: $\text{Gearing} = \frac{R_C}{R_S}$
"""
)


# ---------- Sidebar inputs (Wilmott example defaults)
st.sidebar.header("Scenario (deterministic)")
S0 = st.sidebar.number_input("Spot S₀", value=666.0, step=1.0, format="%.2f")
K = st.sidebar.number_input("Strike K", value=680.0, step=1.0, format="%.2f")
C = st.sidebar.number_input("Call premium C", value=39.0, step=1.0, format="%.2f")
S_T = st.sidebar.number_input("Future price S_T", value=730.0, step=1.0, format="%.2f")

st.sidebar.header("Monte-Carlo (GBM)")
years = st.sidebar.number_input(
    "Time to expiry (years)", value=0.35, step=0.05, format="%.2f"
)
mu = st.sidebar.number_input("Drift μ (annual)", value=0.10, step=0.01, format="%.2f")
sigma = st.sidebar.number_input("Vol σ (annual)", value=0.25, step=0.01, format="%.2f")
nsim = st.sidebar.slider("Simulations", 1000, 100_000, 20_000, step=1000)

# ---------- Deterministic example (like the book)
stock_ret = (S_T - S0) / S0 * 100
call_payoff = max(S_T - K, 0.0)
call_profit = call_payoff - C
call_ret = (call_profit / C) * 100

gearing = np.nan
if stock_ret != 0:
    gearing = call_ret / stock_ret

c1, c2, c3, c4 = st.columns(4)
c1.metric("Stock % return", f"{stock_ret:.2f}%")
c2.metric("Call payoff", f"{call_payoff:.2f}")
c3.metric("Call % return", f"{call_ret:.2f}%")
c4.metric("Gearing (R_c / R_s)", "∞" if np.isinf(gearing) else f"{gearing:.2f}×")

# Payoff diagrams
x = np.linspace(0.5 * S0, 1.5 * S0, 400)
stock_pnl = x - S0
call_pnl = np.maximum(x - K, 0.0) - C

df_pay = pd.DataFrame({"S_T": x, "Stock_PnL": stock_pnl, "Call_PnL": call_pnl})
base = alt.Chart(df_pay).properties(height=280)

payoff_chart = alt.layer(
    base.mark_line().encode(x="S_T:Q", y=alt.Y("Stock_PnL:Q", title="PnL")),
    base.mark_line().encode(x="S_T:Q", y="Call_PnL:Q"),
).resolve_scale(y="shared")

st.subheader("Payoff at expiry")
st.altair_chart(payoff_chart, width="stretch")
st.caption("Stock PnL = S_T − S₀.  Call PnL = max(S_T − K, 0) − C.")

# ---------- Monte-Carlo simulation (GBM)
st.subheader("Monte-Carlo outcomes (GBM on S)")
with st.spinner("Simulating paths…"):
    Z = np.random.randn(nsim)
    ST = S0 * np.exp((mu - 0.5 * sigma**2) * years + sigma * np.sqrt(years) * Z)
    stock_ret_sim = (ST - S0) / S0 * 100
    call_pnl_sim = np.maximum(ST - K, 0.0) - C
    call_ret_sim = (call_pnl_sim / C) * 100

    df_sim = pd.DataFrame({"S_T": ST, "Stock_%": stock_ret_sim, "Call_%": call_ret_sim})
    p_zero = (call_pnl_sim <= -C + 1e-12).mean()  # approx worthless
    exp_stock = stock_ret_sim.mean()
    exp_call = call_ret_sim.mean()

c1, c2, c3 = st.columns(3)
c1.metric("P(option worthless)", f"{p_zero*100:.1f}%")
c2.metric("E[Stock % return]", f"{exp_stock:.2f}%")
c3.metric("E[Call % return]", f"{exp_call:.2f}%")

# Histograms
bins = st.slider("Histogram bins", 20, 150, 60, 10)

hist_stock = (
    alt.Chart(df_sim)
    .mark_bar()
    .encode(
        alt.X("Stock_%:Q", bin=alt.Bin(maxbins=bins), title="Stock % return"),
        y="count()",
    )
    .properties(height=220)
)

hist_call = (
    alt.Chart(df_sim)
    .mark_bar()
    .encode(
        alt.X("Call_%:Q", bin=alt.Bin(maxbins=bins), title="Call % return"), y="count()"
    )
    .properties(height=220)
)

colA, colB = st.columns(2)
with colA:
    st.altair_chart(hist_stock, width="stretch")
with colB:
    st.altair_chart(hist_call, width="stretch")

# Optional download
csv_bytes = df_sim.to_csv(index=False).encode()
st.download_button(
    "Download simulation results (CSV)",
    data=csv_bytes,
    file_name="gearing_sim.csv",
    mime="text/csv",
)

st.caption(
    """
**Interpretation:** Calls magnify percentage outcomes: large upside in favorable moves (high gearing),
but a high probability of total loss of premium. This is why buyers face small limited downside
and potentially large % upside, while writers face the opposite risk profile.
"""
)
