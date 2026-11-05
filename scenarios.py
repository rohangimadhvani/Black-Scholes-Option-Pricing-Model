"""Option scenarios shared by the test files."""

SCENARIOS = {
    "at the money": dict(
        time_to_maturity=1.0, strike=100.0, current_price=100.0, volatility=0.20, interest_rate=0.05
    ),
    "call in the money": dict(
        time_to_maturity=1.0, strike=100.0, current_price=120.0, volatility=0.20, interest_rate=0.05
    ),
    "put in the money": dict(
        time_to_maturity=1.0, strike=100.0, current_price=80.0, volatility=0.20, interest_rate=0.05
    ),
    "short-dated": dict(
        time_to_maturity=0.1, strike=100.0, current_price=100.0, volatility=0.20, interest_rate=0.05
    ),
    "high volatility": dict(
        time_to_maturity=1.0, strike=100.0, current_price=100.0, volatility=0.60, interest_rate=0.05
    ),
    "long-dated, out-of-the-money call": dict(
        time_to_maturity=3.0, strike=150.0, current_price=100.0, volatility=0.30, interest_rate=0.04
    ),
    "zero interest rate": dict(
        time_to_maturity=0.5, strike=100.0, current_price=105.0, volatility=0.25, interest_rate=0.0
    ),
    "negative interest rate": dict(
        time_to_maturity=2.0, strike=90.0, current_price=100.0, volatility=0.20, interest_rate=-0.01
    ),
    "original test case": dict(
        time_to_maturity=2.0, strike=90.0, current_price=100.0, volatility=0.20, interest_rate=0.05
    ),
    "very short, deep in the money": dict(
        time_to_maturity=0.05, strike=100.0, current_price=140.0, volatility=0.20, interest_rate=0.05
    ),
}