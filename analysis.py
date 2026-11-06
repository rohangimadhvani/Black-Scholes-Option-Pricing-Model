"""Calculations built on top of the Black-Scholes model.

This file has no Streamlit or plotting code, so everything in it can be tested on its own.
"""
import numpy as np

from blackscholes import BlackScholes


def pnl_grid(option_type, model, price_paid, prices, rows=10):
    """Profit or loss per share for every (time left, asset price) pair.

    This is for someone who bought the option today at `price_paid` and looks at its value
    later, keeping volatility and the interest rate as they are now.

    Returns (years_left, pnl). `years_left` has one entry per row, from today down to zero
    (expiry day). `pnl` has one row per entry of `years_left` and one column per price.
    """
    years_left = model.time_to_maturity * (1 - np.linspace(0, 1, rows))

    # Rows before expiry are priced with Black-Scholes. Arrays of different shapes combine
    # automatically: times of shape (rows, 1) against prices of shape (1, columns) price
    # every combination at once.
    before_expiry = BlackScholes(
        time_to_maturity=years_left[:-1, None],
        strike=model.strike,
        current_price=prices[None, :],
        volatility=model.volatility,
        interest_rate=model.interest_rate,
    )
    if option_type == "call":
        value = before_expiry.call_price
        payoff = np.maximum(prices - model.strike, 0)
    else:
        value = before_expiry.put_price
        payoff = np.maximum(model.strike - prices, 0)

    # The last row is expiry day, where the option is worth exactly its payoff.
    return years_left, np.vstack([value, payoff[None, :]]) - price_paid