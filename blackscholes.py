from numpy import exp, log, sqrt
from scipy.stats import norm


class BlackScholes:
    """Black-Scholes pricing for a European option on an asset with no dividends."""

    def __init__(
        self,
        time_to_maturity: float,
        strike: float,
        current_price: float,
        volatility: float,
        interest_rate: float,
    ):
        self.time_to_maturity = time_to_maturity  # T, in years
        self.strike = strike                      # K
        self.current_price = current_price        # S
        self.volatility = volatility              # sigma, yearly (0.2 = 20%)
        self.interest_rate = interest_rate        # r, yearly (0.05 = 5%)

    # ---- Building blocks ----

    @property
    def d1(self) -> float:
        """Standardized distance between the current price and the strike."""
        return (
            log(self.current_price / self.strike)
            + (self.interest_rate + 0.5 * self.volatility ** 2) * self.time_to_maturity
        ) / (self.volatility * sqrt(self.time_to_maturity))

    @property
    def d2(self) -> float:
        """d1 shifted down by one total-volatility step."""
        return self.d1 - self.volatility * sqrt(self.time_to_maturity)

    @property
    def discount_factor(self) -> float:
        """Today's value of $1 received at expiry: e^(-rT)."""
        return exp(-self.interest_rate * self.time_to_maturity)

    # ---- Prices ----

    @property
    def call_price(self) -> float:
        return (
            self.current_price * norm.cdf(self.d1)
            - self.strike * self.discount_factor * norm.cdf(self.d2)
        )

    @property
    def put_price(self) -> float:
        return (
            self.strike * self.discount_factor * norm.cdf(-self.d2)
            - self.current_price * norm.cdf(-self.d1)
        )

    # ---- Greeks ----

    @property
    def call_delta(self) -> float:
        return norm.cdf(self.d1)

    @property
    def put_delta(self) -> float:
        return norm.cdf(self.d1) - 1

    @property
    def gamma(self) -> float:
        return norm.pdf(self.d1) / (
            self.current_price * self.volatility * sqrt(self.time_to_maturity)
        )

    @property
    def vega(self) -> float:
        """Change in option price per 1.00 (100 percentage points) change in volatility."""
        return self.current_price * norm.pdf(self.d1) * sqrt(self.time_to_maturity)


if __name__ == "__main__":
    option = BlackScholes(
        time_to_maturity=2,
        strike=90,
        current_price=100,
        volatility=0.2,
        interest_rate=0.05,
    )

    print("Call price:", option.call_price)
    print("Put price:", option.put_price)
    print("Call delta:", option.call_delta)
    print("Put delta:", option.put_delta)
    print("Gamma:", option.gamma)
    print("Vega:", option.vega)