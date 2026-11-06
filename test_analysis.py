"""Check the analysis calculations against simple one-at-a-time pricing.

Run with:  python3 test_analysis.py     (or: pytest, if you have it installed)
"""
import numpy as np

from analysis import pnl_grid
from blackscholes import BlackScholes
from scenarios import SCENARIOS


def make(base):
    return BlackScholes(**base)


def test_pnl_grid_matches_pricing_one_option_at_a_time():
    for name, base in SCENARIOS.items():
        model = make(base)
        prices = np.linspace(base["current_price"] * 0.7, base["current_price"] * 1.3, 7)
        for option_type in ("call", "put"):
            paid = model.call_price if option_type == "call" else model.put_price
            years_left, pnl = pnl_grid(option_type, model, paid, prices, rows=6)
            for i, years in enumerate(years_left[:-1]):
                for j, price in enumerate(prices):
                    single = BlackScholes(**{**base, "time_to_maturity": years, "current_price": price})
                    value = single.call_price if option_type == "call" else single.put_price
                    assert abs(pnl[i, j] - (value - paid)) < 1e-9, (name, option_type, i, j)


def test_pnl_grid_last_row_is_the_expiry_payoff():
    for name, base in SCENARIOS.items():
        model = make(base)
        prices = np.linspace(base["strike"] * 0.6, base["strike"] * 1.4, 9)
        _, call_pnl = pnl_grid("call", model, 3.0, prices)
        _, put_pnl = pnl_grid("put", model, 2.0, prices)
        assert np.allclose(call_pnl[-1], np.maximum(prices - base["strike"], 0) - 3.0), name
        assert np.allclose(put_pnl[-1], np.maximum(base["strike"] - prices, 0) - 2.0), name


def test_pnl_grid_starts_at_zero_when_you_pay_the_model_price():
    # Pay the fair price today, and at today's asset price you have made nothing yet.
    for name, base in SCENARIOS.items():
        model = make(base)
        prices = np.array([base["current_price"] * 0.9, base["current_price"], base["current_price"] * 1.1])
        years_left, call_pnl = pnl_grid("call", model, model.call_price, prices)
        _, put_pnl = pnl_grid("put", model, model.put_price, prices)
        assert years_left[0] == base["time_to_maturity"] and years_left[-1] == 0, name
        assert abs(call_pnl[0, 1]) < 1e-9 and abs(put_pnl[0, 1]) < 1e-9, name


def test_pnl_grid_shape():
    model = make(SCENARIOS["at the money"])
    years_left, pnl = pnl_grid("call", model, 1.0, np.linspace(80, 120, 9), rows=10)
    assert len(years_left) == 10 and pnl.shape == (10, 9)


if __name__ == "__main__":
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print("\nAll checks passed.")