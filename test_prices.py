"""Check the option prices themselves, independently of the Greek formulas.

The Greek tests prove the Greeks match the prices. These tests prove the prices are right:
against a completely different calculation, against textbook values, and against rules that
any sensible option price must obey.

Run with:  python3 test_prices.py     (or: pytest, if you have it installed)
"""
import numpy as np
from scipy.integrate import quad
from scipy.stats import norm

from blackscholes import BlackScholes
from scenarios import SCENARIOS


def make(base, **overrides):
    return BlackScholes(**{**base, **overrides})


def price_by_integration(base):
    """Price a call and a put without any Black-Scholes formula.

    Under the model, the asset price at expiry is lognormal. The option price is the average
    discounted payoff over all possible outcomes, which we add up numerically.
    """
    T, K, S = base["time_to_maturity"], base["strike"], base["current_price"]
    sigma, r = base["volatility"], base["interest_rate"]

    def discounted_payoff(z, sign):
        asset_at_expiry = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * z)
        return np.exp(-r * T) * sign * (asset_at_expiry - K) * norm.pdf(z)

    # The payoff has a corner where the asset finishes exactly at the strike; integrate up to it.
    corner = (np.log(K / S) - (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    call = quad(discounted_payoff, corner, 12, args=(1,), epsabs=1e-13, epsrel=1e-13)[0]
    put = quad(discounted_payoff, -12, corner, args=(-1,), epsabs=1e-13, epsrel=1e-13)[0]
    return call, put


def test_matches_independent_integration():
    for name, base in SCENARIOS.items():
        option = make(base)
        call, put = price_by_integration(base)
        assert abs(option.call_price - call) < 1e-8, f"[{name}] call {option.call_price} vs {call}"
        assert abs(option.put_price - put) < 1e-8, f"[{name}] put {option.put_price} vs {put}"


def test_put_call_parity():
    # A call minus a put always equals the asset price minus the discounted strike.
    for name, base in SCENARIOS.items():
        option = make(base)
        expected = base["current_price"] - base["strike"] * np.exp(
            -base["interest_rate"] * base["time_to_maturity"]
        )
        assert abs((option.call_price - option.put_price) - expected) < 1e-9, name


def test_textbook_values():
    # The standard example: S = K = 100, T = 1 year, sigma = 20%, r = 5%.
    option = make(SCENARIOS["at the money"])
    assert round(option.call_price, 4) == 10.4506
    assert round(option.put_price, 4) == 5.5735


def test_no_arbitrage_bounds():
    for name, base in SCENARIOS.items():
        option = make(base)
        S, K = base["current_price"], base["strike"]
        discounted_strike = K * option.discount_factor
        assert max(S - discounted_strike, 0) - 1e-12 <= option.call_price <= S + 1e-12, name
        assert max(discounted_strike - S, 0) - 1e-12 <= option.put_price <= discounted_strike + 1e-12, name


def test_prices_move_the_right_way():
    # A call gains as the asset rises and a put loses; both gain as volatility rises.
    for name, base in SCENARIOS.items():
        S, vol = base["current_price"], base["volatility"]
        assert make(base, current_price=S * 1.01).call_price > make(base).call_price, name
        assert make(base, current_price=S * 1.01).put_price < make(base).put_price, name
        assert make(base, volatility=vol * 1.1).call_price > make(base).call_price - 1e-12, name
        assert make(base, volatility=vol * 1.1).put_price > make(base).put_price - 1e-12, name


def test_converges_to_the_expiry_payoff():
    # With almost no time left, the price should collapse onto the "hockey stick" payoff.
    for name, base in SCENARIOS.items():
        K = base["strike"]
        prices = np.array([0.5 * K, 0.8 * K, 1.2 * K, 1.5 * K])  # kept away from the corner
        option = make(base, time_to_maturity=1e-8, current_price=prices)
        assert np.allclose(option.call_price, np.maximum(prices - K, 0), atol=1e-4), name
        assert np.allclose(option.put_price, np.maximum(K - prices, 0), atol=1e-4), name


def test_whole_arrays_match_single_values():
    # The charts price hundreds of asset prices at once, so arrays must give the same
    # answers as pricing each one separately.
    for name, base in SCENARIOS.items():
        prices = np.linspace(base["current_price"] * 0.5, base["current_price"] * 1.5, 25)
        together = make(base, current_price=prices)
        for i, price in enumerate(prices):
            single = make(base, current_price=float(price))
            assert abs(together.call_price[i] - single.call_price) < 1e-12, name
            assert abs(together.put_price[i] - single.put_price) < 1e-12, name
            assert abs(together.gamma[i] - single.gamma) < 1e-12, name
            assert abs(together.call_theta[i] - single.call_theta) < 1e-12, name


if __name__ == "__main__":
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print("\nAll checks passed.")