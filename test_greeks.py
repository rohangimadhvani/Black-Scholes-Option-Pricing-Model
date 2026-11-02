"""Check each Greek against a numerical derivative of the option price.

Run with:  python3 test_greeks.py
"""
from blackscholes import BlackScholes

BASE = dict(
    time_to_maturity=2,
    strike=90,
    current_price=100,
    volatility=0.2,
    interest_rate=0.05,
)


def make(**overrides):
    """Build an option from the base inputs, changing only what is passed in."""
    return BlackScholes(**{**BASE, **overrides})


def slope(price_name, param, h=1e-4):
    """Numerical first derivative of a price with respect to one input."""
    up = getattr(make(**{param: BASE[param] + h}), price_name)
    down = getattr(make(**{param: BASE[param] - h}), price_name)
    return (up - down) / (2 * h)


def curvature(price_name, param, h=1e-2):
    """Numerical second derivative of a price with respect to one input."""
    up = getattr(make(**{param: BASE[param] + h}), price_name)
    mid = getattr(make(), price_name)
    down = getattr(make(**{param: BASE[param] - h}), price_name)
    return (up - 2 * mid + down) / h ** 2


def check(name, formula, numeric, tolerance=1e-6):
    """Compare a formula to its numerical derivative, allowing a small relative error."""
    close = abs(formula - numeric) <= tolerance * max(1.0, abs(formula))
    status = "PASS" if close else "FAIL"
    print(f"{status}  {name:<12} formula={formula:.9f}  numeric={numeric:.9f}")
    assert status == "PASS", f"{name} does not match its numerical derivative"


if __name__ == "__main__":
    option = make()

    check("call delta", option.call_delta, slope("call_price", "current_price"))
    check("put delta", option.put_delta, slope("put_price", "current_price"))
    check("gamma (call)", option.gamma, curvature("call_price", "current_price"))
    check("gamma (put)", option.gamma, curvature("put_price", "current_price"))
    check("vega (call)", option.vega, slope("call_price", "volatility"))
    check("vega (put)", option.vega, slope("put_price", "volatility"))
    # Theta is the change in price as time PASSES, i.e. as time_to_maturity shrinks,
    # so it is minus the slope with respect to time_to_maturity.
    check("theta (call)", option.call_theta, -slope("call_price", "time_to_maturity"))
    check("theta (put)", option.put_theta, -slope("put_price", "time_to_maturity"))
    check("rho (call)", option.call_rho, slope("call_price", "interest_rate"))
    check("rho (put)", option.put_rho, slope("put_price", "interest_rate"))
    
    print("All checks passed.")