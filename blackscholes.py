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

if __name__ == "__main__":
    option = BlackScholes(
        time_to_maturity=2,
        strike=90,
        current_price=100,
        volatility=0.2,
        interest_rate=0.05,
    )
    print(option.strike)
    print(option.volatility)