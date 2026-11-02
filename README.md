# Black-Scholes Option Pricing Dashboard

An interactive Streamlit app that prices European call and put options with the
Black-Scholes model, and shows how prices change with spot price and volatility.

Built as a learning project, replicating the layout of an existing Streamlit
dashboard and re-deriving the math and code step by step.

## Features

- Call and put prices from five inputs: asset price, strike, time to maturity,
  volatility and risk-free interest rate
- Greeks (delta and gamma) calculated in the `BlackScholes` class
- Interactive heatmaps of call and put prices across a range of spot prices
  and volatilities

## Project structure

- `blackscholes.py`: the `BlackScholes` class (pricing and Greeks)
- `streamlit_app.py`: the Streamlit dashboard
- `requirements.txt`: Python dependencies

## Run it locally

```
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Limitations

Black-Scholes assumes European options (exercisable only at expiry), constant
volatility and interest rate, and no dividends. Real markets violate these
assumptions, so treat the output as a model, not a market quote.