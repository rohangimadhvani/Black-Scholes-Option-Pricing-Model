"""Check every Greek against a numerical derivative of the option price, in many scenarios.

A Greek is defined as "how fast the price changes when one input changes", so we can measure it
directly: nudge the input up and down, reprice, and divide the price difference by the nudge.
If the formula in blackscholes.py agrees with that measurement, the formula is doing its job.

Run with:  python3 test_greeks.py     (or: pytest, if you have it installed)
"""
from blackscholes import BlackScholes
from scenarios import SCENARIOS

WORST = {}  # for each Greek, the largest share of the allowed error that was used


def make(base, **overrides):
    """Build an option from a scenario's inputs, changing only what is passed in."""
    return BlackScholes(**{**base, **overrides})


def slope(base, price_name, param, h):
    """Numerical first derivative of a price with respect to one input."""
    up = getattr(make(base, **{param: base[param] + h}), price_name)
    down = getattr(make(base, **{param: base[param] - h}), price_name)
    return (up - down) / (2 * h)


def curvature(base, price_name, param, h):
    """Numerical second derivative of a price with respect to one input."""
    up = getattr(make(base, **{param: base[param] + h}), price_name)
    mid = getattr(make(base), price_name)
    down = getattr(make(base, **{param: base[param] - h}), price_name)
    return (up - 2 * mid + down) / h ** 2


def check(scenario, greek, formula, numeric, rel_tol=1e-4, abs_tol=1e-7):
    """Fail if formula and measurement differ by more than the measurement error allows."""
    error = abs(formula - numeric)
    allowed = rel_tol * abs(formula) + abs_tol
    WORST[greek] = max(WORST.get(greek, 0.0), error / allowed)
    assert error <= allowed, (
        f"[{scenario}] {greek}: formula={formula:.10g} but measured={numeric:.10g}"
    )


def test_delta():
    for name, base in SCENARIOS.items():
        option, h = make(base), base["current_price"] * 1e-3
        check(name, "delta (call)", option.call_delta, slope(base, "call_price", "current_price", h))
        check(name, "delta (put)", option.put_delta, slope(base, "put_price", "current_price", h))


def test_gamma():
    for name, base in SCENARIOS.items():
        option, h = make(base), base["current_price"] * 1e-3
        check(name, "gamma (call)", option.gamma, curvature(base, "call_price", "current_price", h))
        check(name, "gamma (put)", option.gamma, curvature(base, "put_price", "current_price", h))


def test_vega():
    for name, base in SCENARIOS.items():
        option, h = make(base), 1e-5
        check(name, "vega (call)", option.vega, slope(base, "call_price", "volatility", h))
        check(name, "vega (put)", option.vega, slope(base, "put_price", "volatility", h))


def test_theta():
    # Theta is the change in price as time PASSES, i.e. as time_to_maturity shrinks,
    # so it is minus the slope with respect to time_to_maturity.
    for name, base in SCENARIOS.items():
        option, h = make(base), base["time_to_maturity"] * 1e-4
        check(name, "theta (call)", option.call_theta, -slope(base, "call_price", "time_to_maturity", h))
        check(name, "theta (put)", option.put_theta, -slope(base, "put_price", "time_to_maturity", h))


def test_rho():
    for name, base in SCENARIOS.items():
        option, h = make(base), 1e-6
        check(name, "rho (call)", option.call_rho, slope(base, "call_price", "interest_rate", h))
        check(name, "rho (put)", option.put_rho, slope(base, "put_price", "interest_rate", h))


def test_call_and_put_delta_differ_by_one():
    for name, base in SCENARIOS.items():
        option = make(base)
        assert abs((option.call_delta - option.put_delta) - 1) < 1e-12, name


if __name__ == "__main__":
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}  ({len(SCENARIOS)} scenarios)")
    print("\nLargest share of the allowed error used (100% would be the limit):")
    for greek, share in sorted(WORST.items()):
        print(f"  {greek:<14}{share:>7.2%}")
    print("\nAll checks passed.")

    