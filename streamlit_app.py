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
    "Call in the money": {**DEFAULTS, "current_price": 120.0},
    "Put in the money": {**DEFAULTS, "current_price": 80.0},
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
# Each option is "in", "at" or "out" of the money. One palette is used everywhere.
MONEYNESS_STYLE = {
    "in": ("In the money", "#3DD56D"),      # green
    "at": ("At the money", "#4C9AFF"),      # blue
    "out": ("Out of the money", "#FFA421"),  # orange
}


def moneyness(option_type, spot, strike):
    """Return "in", "at" or "out" for a call or put, given the spot and strike prices."""
    if abs(spot / strike - 1) < 0.01:
        return "at"
    in_the_money = spot > strike if option_type == "call" else spot < strike
    return "in" if in_the_money else "out"


# Pure-CSS hover tooltip (works without any Streamlit widget): the explanation
# sits in a hidden <span> that becomes visible while the mouse is over the icon.
TOOLTIP_CSS = (
    "<style>"
    ".opt-tip { position: relative; display: inline-block; cursor: help; margin-left: 4px; }"
    ".opt-tip .opt-tip-text { visibility: hidden; opacity: 0; position: absolute; z-index: 1000; "
    "top: 135%; left: 50%; transform: translateX(-50%); width: 230px; padding: 8px 10px; "
    "border-radius: 6px; background: #31333F; color: #FAFAFA; border: 1px solid #4A4D5A; "
    "font-size: 0.8rem; font-weight: 400; line-height: 1.35; text-align: left; "
    "transition: opacity 0.15s; }"
    ".opt-tip:hover .opt-tip-text { visibility: visible; opacity: 1; }"
    "</style>"
)


def option_card(container, title, help_text, price, status):
    """Show one option as a centered card whose color reflects its moneyness."""
    label, color = MONEYNESS_STYLE[status]
    container.markdown(
        TOOLTIP_CSS
        + f'<div style="border: 1px solid {color}66; border-radius: 12px; '
        f'padding: 14px 8px; text-align: center;">'
        f'<div style="font-size: 0.95rem;"><span style="opacity: 0.8;">{title}</span>'
        f'<span class="opt-tip">ⓘ<span class="opt-tip-text">{help_text}</span></span></div>'
        f'<div style="font-size: 2.4rem; font-weight: 700; line-height: 1.25; '
        f'color: {color};">&#36;{price:,.2f}</div>'
        f'<span style="display: inline-block; margin-top: 4px; padding: 3px 12px; '
        f'border-radius: 6px; background-color: {color}26; color: {color}; '
        f'font-size: 0.85rem; font-weight: 600;">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

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


# Shared chart styling, so every chart on every tab uses the same size and fonts.
FIG_SIZE = (8, 5.5)
FONT_LABEL = 10  # axis labels
FONT_TICK = 9    # tick numbers, legends and small notes

# Colors for the payoff charts (they match the dark theme and the moneyness palette).
PAGE_BG = "#0E1117"
TEXT = "#FAFAFA"
MUTED = "#9AA0AE"
GREEN = "#3DD56D"
ORANGE = "#FFA421"
BLUE = "#4C9AFF"


def plot_heatmap(prices, spot_range, vol_range):
    """Draw one heatmap of option prices (rows = volatility, columns = spot price)."""
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    sns.heatmap(
        prices,
        xticklabels=np.round(spot_range, 2),
        yticklabels=np.round(vol_range, 2),
        annot=True,
        fmt=".2f",
        cmap="viridis",
        annot_kws={"size": FONT_TICK - 1},
        ax=ax,
    )
    ax.set_xlabel("Spot price ($)", fontsize=FONT_LABEL)
    ax.set_ylabel("Volatility", fontsize=FONT_LABEL)
    ax.tick_params(labelsize=FONT_TICK)
    ax.collections[0].colorbar.ax.tick_params(labelsize=FONT_TICK)
    return fig


def plot_payoff(option_type, bs_model, show_profit):
    """Draw the value (or profit/loss) of one option at expiry and today, versus the asset price."""
    strike = bs_model.strike
    spot = bs_model.current_price
    prices = np.linspace(min(spot, strike) * 0.5, max(spot, strike) * 1.5, 300)

    # The class works on whole arrays of prices, so no loop is needed.
    curve = BlackScholes(
        time_to_maturity=bs_model.time_to_maturity,
        strike=strike,
        current_price=prices,
        volatility=bs_model.volatility,
        interest_rate=bs_model.interest_rate,
    )

    if option_type == "call":
        at_expiry = np.maximum(prices - strike, 0)
        today = curve.call_price
        premium = bs_model.call_price
        breakeven = strike + premium
    else:
        at_expiry = np.maximum(strike - prices, 0)
        today = curve.put_price
        premium = bs_model.put_price
        breakeven = strike - premium

    # Fix the y-axis so it never moves when the profit / loss toggle changes.
    # The lowest possible point is -premium (the most you can lose); the highest is
    # the top of the "value" curves.
    y_low = -premium
    y_high = max(at_expiry.max(), today.max())
    padding = 0.06 * (y_high - y_low)

    if show_profit:
        at_expiry = at_expiry - premium
        today = today - premium

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    fig.patch.set_facecolor(PAGE_BG)
    ax.set_facecolor(PAGE_BG)
    ax.set_ylim(y_low - padding, y_high + padding)

    ax.axhline(0, color=MUTED, linewidth=0.8)
    if show_profit:
        ax.fill_between(prices, at_expiry, 0, where=at_expiry >= 0, color=GREEN, alpha=0.18)
        ax.fill_between(prices, at_expiry, 0, where=at_expiry < 0, color=ORANGE, alpha=0.18)


    ax.plot(prices, at_expiry, color=BLUE, linewidth=2.5, label="At expiry")
    ax.plot(prices, today, color=TEXT, linewidth=1.8, linestyle="--", label="Today (includes time value)")

    ax.axvline(spot, color=MUTED, linestyle=":", linewidth=1)
    ax.axvline(strike, color=MUTED, linestyle=":", linewidth=1, alpha=0.5)
    ax.text(spot, 1.02, "Current price", transform=ax.get_xaxis_transform(),
            ha="center", va="bottom", color=MUTED, fontsize=FONT_TICK)
    ax.text(strike, 0.02, "Strike", transform=ax.get_xaxis_transform(),
            ha="center", va="bottom", color=MUTED, fontsize=FONT_TICK,
            bbox=dict(facecolor=PAGE_BG, edgecolor="none", pad=1.5))

    if show_profit and prices[0] <= breakeven <= prices[-1]:
        ax.plot(breakeven, 0, "o", color=TEXT, markersize=7)
        ax.annotate(f"Breakeven ${breakeven:,.2f}", (breakeven, 0), textcoords="offset points",
                    xytext=(0, 14), ha="center", color=TEXT, fontsize=FONT_TICK,
                    bbox=dict(facecolor=PAGE_BG, edgecolor="none", pad=1.5))

    ax.set_xlabel("Asset price ($)", color=TEXT, fontsize=FONT_LABEL)
    ax.set_ylabel(
        "Profit / loss per share ($)" if show_profit else "Option value per share ($)",
        color=TEXT, fontsize=FONT_LABEL,
    )
    ax.tick_params(colors=TEXT, labelsize=FONT_TICK)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.grid(True, color=MUTED, alpha=0.15)
    ax.legend(facecolor=PAGE_BG, edgecolor=MUTED, labelcolor=TEXT, fontsize=FONT_TICK)
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
        is_active = all(st.session_state[key] == value for key, value in values.items())
        col.button(
            name,
            on_click=apply_preset,
            args=(values,),
            width="stretch",
            type="primary" if is_active else "secondary",
        )


# ---------- Results strip (visible above every tab) ----------
bs_model = BlackScholes(
    time_to_maturity=time_to_maturity,
    strike=strike,
    current_price=current_price,
    volatility=volatility,
    interest_rate=interest_rate,
)

years = f"{time_to_maturity:g} year" + ("" if time_to_maturity == 1 else "s")
st.write(
    f"Options expiring in {years}, with a \\${strike:,.2f} strike, "
    f"on an asset trading at \\${current_price:,.2f} "
    f"(assuming {volatility * 100:g}% volatility and a {interest_rate * 100:g}% risk-free rate)."
)


call_col, put_col = st.columns(2)
option_card(
    call_col,
    "Call option",
    "The right to BUY the asset at the strike price on the expiry date.",
    bs_model.call_price,
    moneyness("call", current_price, strike),
)
option_card(
    put_col,
    "Put option",
    "The right to SELL the asset at the strike price on the expiry date.",
    bs_model.put_price,
    moneyness("put", current_price, strike),
)


# ---------- Tabs ----------
tab_payoff, tab_heatmaps, tab_greeks = st.tabs(["Payoff", "Heatmaps", "Greeks"])

with tab_payoff:
    show_profit = st.toggle("Show profit / loss (subtracts the price you paid today)")

    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("Call option")
        fig_call_payoff = plot_payoff("call", bs_model, show_profit)
        st.pyplot(fig_call_payoff)
        plt.close(fig_call_payoff)
    with right_col:
        st.subheader("Put option")
        fig_put_payoff = plot_payoff("put", bs_model, show_profit)
        st.pyplot(fig_put_payoff)
        plt.close(fig_put_payoff)

    st.caption(
        "The solid line is what the option is worth on expiry day. The dashed line is what "
        "the model says it is worth today, and the gap between them is time value. "
        "(A deep in-the-money put can dip slightly below its expiry value, because the "
        "strike you would receive is paid later and is worth less today.) "
        "Profit / loss assumes you buy at today's price shown above and hold to expiry."
    )

with tab_heatmaps:
    st.write(
        "Each cell shows the option price for one combination of spot price "
        "(x-axis) and volatility (y-axis), with the strike held fixed."
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
            st.subheader("Call option")
            fig_call = plot_heatmap(call_prices, spot_range, vol_range)
            st.pyplot(fig_call)
            plt.close(fig_call)

        with right_col:
            st.subheader("Put option")
            fig_put = plot_heatmap(put_prices, spot_range, vol_range)
            st.pyplot(fig_put)
            plt.close(fig_put)

with tab_greeks:
    st.info("The Greeks are coming in the next step.")


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
    "Inspired by "
    "[Prudhvi Reddy Muppala's Black-Scholes app](https://github.com/prudhvi-reddy-m/BlackScholes)."
)