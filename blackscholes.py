"""Black-Scholes pricing and Greeks for European options (no dividends)."""

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
        """Store the five inputs. Time is in years; volatility and rate are yearly decimals."""
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
        """Black-Scholes price of a European call."""
        return (
            self.current_price * norm.cdf(self.d1)
            - self.strike * self.discount_factor * norm.cdf(self.d2)
        )

    @property
    def put_price(self) -> float:
        """Black-Scholes price of a European put."""
        return (
            self.strike * self.discount_factor * norm.cdf(-self.d2)
            - self.current_price * norm.cdf(-self.d1)
        )

    # ---- Greeks ----

    @property
    def call_delta(self) -> float:
        """Change in call price per $1 move in the asset price."""
        return norm.cdf(self.d1)

    @property
    def put_delta(self) -> float:
        """Change in put price per $1 move in the asset price (negative for puts)."""
        return norm.cdf(self.d1) - 1

    @property
    def gamma(self) -> float:
        """Change in delta per $1 move in the asset price (same for calls and puts)."""
        return norm.pdf(self.d1) / (
            self.current_price * self.volatility * sqrt(self.time_to_maturity)
        )

    @property
    def vega(self) -> float:
        """Change in option price per 1.00 (100 percentage points) change in volatility. 
        
        Same for calls and puts.
        """
        return self.current_price * norm.pdf(self.d1) * sqrt(self.time_to_maturity)

    @property
    def call_theta(self) -> float:
        """Change in call price per year that passes (usually negative: value decays).

        Divide by 365 for the change per calendar day.
        """
        decay = (
            self.current_price * norm.pdf(self.d1) * self.volatility
            / (2 * sqrt(self.time_to_maturity))
        )
        carry = self.interest_rate * self.strike * self.discount_factor * norm.cdf(self.d2)
        return -decay - carry

    @property
    def put_theta(self) -> float:
        """Change in put price per year that passes. 
        
        Divide by 365 for the change per day.
        """
        decay = (
            self.current_price * norm.pdf(self.d1) * self.volatility
            / (2 * sqrt(self.time_to_maturity))
        )
        carry = self.interest_rate * self.strike * self.discount_factor * norm.cdf(-self.d2)
        return -decay + carry

    @property
    def call_rho(self) -> float:
        """Change in call price per 1.00 (100 percentage points) change in the interest rate."""
        return (
            self.strike * self.time_to_maturity * self.discount_factor * norm.cdf(self.d2)
        )

    @property
    def put_rho(self) -> float:
        """Change in put price per 1.00 (100 percentage points) change in the interest rate."""
        return (
            -self.strike * self.time_to_maturity * self.discount_factor * norm.cdf(-self.d2)
        )


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
    print("Call theta:", option.call_theta)
    print("Put theta:", option.put_theta)
    print("Call rho:", option.call_rho)
    print("Put rho:", option.put_rho)