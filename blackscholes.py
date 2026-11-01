from numpy import exp, sqrt, log
from scipy.stats import norm

class BlackScholes:
    def __init__(
        self,
        time_to_maturity: float,
        strike: float,
        current_price: float,
        volatility: float,
        interest_rate: float,
    ):
        self.time_to_maturity = time_to_maturity
        self.strike = strike
        self.current_price = current_price
        self.volatility = volatility
        self.interest_rate = interest_rate


    def run(self):
        time_to_maturity = self.time_to_maturity
        strike = self.strike
        current_price = self.current_price
        volatility = self.volatility
        interest_rate = self.interest_rate

        d1 = (
            log(current_price / strike) +
            (interest_rate + 0.5 * volatility ** 2) * time_to_maturity
        ) / (
            volatility * sqrt(time_to_maturity)
        )
        d2 = d1 - volatility * sqrt(time_to_maturity)

        call_price = current_price * norm.cdf(d1) - (
            strike * exp(-(interest_rate * time_to_maturity)) * norm.cdf(d2)
        )
        put_price = (
            strike * exp(-(interest_rate * time_to_maturity)) * norm.cdf(-d2)
        ) - current_price * norm.cdf(-d1)

        self.call_price = call_price
        self.put_price = put_price

        # GREEKS
        # Delta: how much the option price changes per $1 move in the asset
        self.call_delta = norm.cdf(d1)
        self.put_delta = norm.cdf(d1) - 1

        # Gamma: how much delta itself changes per $1 move in the asset
        self.call_gamma = norm.pdf(d1) / (
            current_price * volatility * sqrt(time_to_maturity)
        )
        self.put_gamma = self.call_gamma


if __name__ == "__main__":
    option = BlackScholes(
        time_to_maturity=2,
        strike=90,
        current_price=100,
        volatility=0.2,
        interest_rate=0.05,
    )

    option.run()
    print("Call price:", option.call_price)
    print("Put price:", option.put_price)
    print("Call delta:", option.call_delta)
    print("Put delta:", option.put_delta)
    print("Gamma:", option.call_gamma)