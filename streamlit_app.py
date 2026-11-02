"""Streamlit dashboard for the Black-Scholes model: prices, Greeks and heatmaps."""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st

from blackscholes import BlackScholes


# ---------- Page setup ----------
st.set_page_config(
    page_title="Black-Scholes Option Pricing Model",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Sidebar: inputs ----------
with st.sidebar:
    st.title("📊 Black-Scholes Model")

    st.write("`Created by:`")
    linkedin_url = "https://www.linkedin.com/in/rohangimadhvani/"
    st.markdown(
        f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;">'
        '<img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" '
        'style="vertical-align: middle; margin-right: 10px;">'
        'Rohangi Madhvani</a>',
        unsafe_allow_html=True,
    )

    current_price = st.number_input("Current Asset Price", value=100.0)
    strike = st.number_input("Strike Price", value=100.0)
    time_to_maturity = st.number_input("Time to Maturity (Years)", value=1.0)
    volatility = st.number_input("Volatility (σ)", value=0.2)
    interest_rate = st.number_input("Risk-Free Interest Rate", value=0.05)

    st.markdown("---")
    st.subheader("Heatmap Parameters")
    spot_min = st.number_input("Min Spot Price", min_value=0.01, value=current_price * 0.8, step=0.01)
    spot_max = st.number_input("Max Spot Price", min_value=0.01, value=current_price * 1.2, step=0.01)
    vol_min = st.slider("Min Volatility for Heatmap", min_value=0.01, max_value=1.0, value=volatility * 0.5, step=0.01)
    vol_max = st.slider("Max Volatility for Heatmap", min_value=0.01, max_value=1.0, value=volatility * 1.5, step=0.01)

    spot_range = np.linspace(spot_min, spot_max, 10)
    vol_range = np.linspace(vol_min, vol_max, 10)


# ---------- Helpers ----------
def compute_price_grids(time_to_maturity, strike, interest_rate, spot_range, vol_range):
    """Calculate call and put prices for every (volatility, spot price) pair."""
    call_prices = np.zeros((len(vol_range), len(spot_range)))
    put_prices = np.zeros((len(vol_range), len(spot_range)))

    for i, vol in enumerate(vol_range):
        for j, spot in enumerate(spot_range):
            option = BlackScholes(
                time_to_maturity=time_to_maturity,
                strike=strike,
                current_price=spot,
                volatility=vol,
                interest_rate=interest_rate,
            )

            call_prices[i, j] = option.call_price
            put_prices[i, j] = option.put_price

    return call_prices, put_prices


def plot_heatmap(prices, spot_range, vol_range, title):
    """Draw one heatmap of option prices (rows = volatility, columns = spot price)."""
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        prices,
        xticklabels=np.round(spot_range, 2),
        yticklabels=np.round(vol_range, 2),
        annot=True,
        fmt=".2f",
        cmap="viridis",
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel("Spot Price")
    ax.set_ylabel("Volatility")
    return fig


# ---------- Main page ----------
st.title("Black-Scholes Option Pricing")
st.caption(
    f"Spot \\${current_price:,.2f}  ·  Strike \\${strike:,.2f}  ·  "
    f"{time_to_maturity:g} yr to expiry  ·  Volatility {volatility:.0%}  ·  "
    f"Rate {interest_rate:.1%}"
)

# Build the model from the sidebar values
bs_model = BlackScholes(
    time_to_maturity=time_to_maturity,
    strike=strike,
    current_price=current_price,
    volatility=volatility,
    interest_rate=interest_rate,
)

tab_pricing, tab_greeks, tab_heatmaps = st.tabs(["Pricing", "Greeks", "Heatmaps"])


# ---------- Tab 1: Pricing ----------
with tab_pricing:
    call_col, put_col = st.columns(2)
    call_col.metric(
        "Call option",
        f"${bs_model.call_price:.2f}",
        help="The right to BUY the asset at the strike price on the expiry date.",
        border=True,
    )
    put_col.metric(
        "Put option",
        f"${bs_model.put_price:.2f}",
        help="The right to SELL the asset at the strike price on the expiry date.",
        border=True,
    )


# ---------- Tab 2: Greeks (coming in the next step) ----------
with tab_greeks:
    st.info("The Greeks are coming in the next step.")


# ---------- Tab 3: Heatmaps ----------
with tab_heatmaps:
    st.write(
        "Each cell shows the option price for one combination of spot price "
        "(horizontal) and volatility (vertical), with the strike held fixed. "
        "Change the ranges in the sidebar to zoom in on a region."
    )

    call_prices, put_prices = compute_price_grids(
        time_to_maturity, strike, interest_rate, spot_range, vol_range
    )

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Call prices")
        fig_call = plot_heatmap(call_prices, spot_range, vol_range, "CALL")
        st.pyplot(fig_call)
        plt.close(fig_call)

    with right_col:
        st.subheader("Put prices")
        fig_put = plot_heatmap(put_prices, spot_range, vol_range, "PUT")
        st.pyplot(fig_put)
        plt.close(fig_put)


# ---------- Footer ----------
st.markdown("---")
st.caption(
    "Dashboard layout and project idea based on "
    "[Prudhvi Reddy Muppala's Black-Scholes app](https://github.com/prudhvi-reddy-m/BlackScholes). "
    "Rebuilt step by step as a learning project."
)