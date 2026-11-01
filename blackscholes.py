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

        print(d1, d2)
        
if __name__ == "__main__":
    option = BlackScholes(
        time_to_maturity=2,
        strike=100,
        current_price=100,
        volatility=0.2,
        interest_rate=0.05,
    )
    option.run()