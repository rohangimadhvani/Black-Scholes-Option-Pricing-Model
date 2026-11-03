"""Options Lab: a Streamlit dashboard for Black-Scholes prices, Greeks and heatmaps."""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st

from blackscholes import BlackScholes


# ---------- Page setup ----------
st.set_page_config(
    page_title="Options Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------- Input defaults and quick scenarios ----------
DEFAULTS = {
    "current_price": 100.0,
    "strike": 100.0,
    "time_to_maturity": 1.0,
    "volatility": 0.20,
    "interest_rate": 0.05,
}

PRESETS = {
    "At the money": {**DEFAULTS},
    "In the money call": {**DEFAULTS, "current_price": 120.0},
    "Short-dated": {**DEFAULTS, "time_to_maturity": 0.1},
    "High volatility": {**DEFAULTS, "volatility": 0.60},
}

# Give each input a starting value the first time the page loads.
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def apply_preset(values):
    """Overwrite the input boxes with a preset scenario (runs when a button is clicked)."""
    st.session_state.update(values)


# ---------- Helpers ----------
def describe_moneyness(spot, strike):
    """Return a (label, color) pair saying where the spot price sits relative to the strike."""
    if abs(spot / strike - 1) < 0.01:
        return "At the money", "blue"
    if spot > strike:
        return "Call in the money · Put out of the money", "green"
    return "Put in the money · Call out of the money", "gray"


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


# ---------- Header ----------
st.title("Options Lab")
st.caption("Explore how Black-Scholes prices a European call and put.")


# ---------- Option setup (inputs) ----------
with st.expander("Option setup", expanded=True):
    input_cols = st.columns(5)
    current_price = input_cols[0].number_input("Asset price", key="current_price", min_value=0.01)
    strike = input_cols[1].number_input("Strike price", key="strike", min_value=0.01)
    time_to_maturity = input_cols[2].number_input("Years to expiry", key="time_to_maturity", min_value=0.01)
    volatility = input_cols[3].number_input("Volatility (σ)", key="volatility", min_value=0.01)
    interest_rate = input_cols[4].number_input("Risk-free rate", key="interest_rate")

    st.caption("Quick scenarios")
    preset_cols = st.columns(len(PRESETS))
    for col, (name, values) in zip(preset_cols, PRESETS.items()):
        col.button(name, on_click=apply_preset, args=(values,))


# ---------- Results strip (visible above every tab) ----------
bs_model = BlackScholes(
    time_to_maturity=time_to_maturity,
    strike=strike,
    current_price=current_price,
    volatility=volatility,
    interest_rate=interest_rate,
)

st.write(
    f"A {time_to_maturity:g}-year call and put struck at \\${strike:,.2f}, "
    f"on an asset trading at \\${current_price:,.2f}."
)
label, color = describe_moneyness(current_price, strike)
st.badge(label, color=color)

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


# ---------- Tabs ----------
tab_greeks, tab_heatmaps = st.tabs(["📈 Greeks", "🔥 Heatmaps"])

with tab_greeks:
    st.info("The Greeks are coming in the next step.")

with tab_heatmaps:
    st.write(
        "Each cell shows the option price for one combination of spot price "
        "(horizontal) and volatility (vertical), with the strike held fixed."
    )

    range_cols = st.columns(4)
    spot_min = range_cols[0].number_input(
        "Min spot price", min_value=0.01, value=current_price * 0.8, step=0.01
    )
    spot_max = range_cols[1].number_input(
        "Max spot price", min_value=0.01, value=current_price * 1.2, step=0.01
    )
    vol_min = range_cols[2].number_input(
        "Min volatility", min_value=0.01, value=max(volatility * 0.5, 0.01), step=0.01
    )
    vol_max = range_cols[3].number_input(
        "Max volatility", min_value=0.01, value=max(volatility * 1.5, 0.02), step=0.01
    )

    if spot_min >= spot_max or vol_min >= vol_max:
        st.error("Each minimum must be smaller than its maximum.")
    else:
        spot_range = np.linspace(spot_min, spot_max, 10)
        vol_range = np.linspace(vol_min, vol_max, 10)
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
linkedin_url = "https://www.linkedin.com/in/rohangimadhvani/"
st.markdown(
    f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;">'
    '<img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" '
    'style="vertical-align: middle; margin-right: 10px;">'
    'Created by Rohangi Madhvani</a>',
    unsafe_allow_html=True,
)
st.caption(
    "Layout concept inspired by "
    "[Prudhvi Reddy Muppala's Black-Scholes app](https://github.com/prudhvi-reddy-m/BlackScholes). "
    "Built step by step as a learning project."
)