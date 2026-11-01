import streamlit as st

from blackscholes import BlackScholes

# Page configuration
st.set_page_config(
    page_title="Black-Scholes Option Pricing Model",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Sidebar for user inputs
with st.sidebar:
    st.title("📊 Black-Scholes Model")

    current_price = st.number_input("Current Asset Price", value=100.0)
    strike = st.number_input("Strike Price", value=100.0)
    time_to_maturity = st.number_input("Time to Maturity (Years)", value=1.0)
    volatility = st.number_input("Volatility (σ)", value=0.2)
    interest_rate = st.number_input("Risk-Free Interest Rate", value=0.05)


# Main page
st.title("Black-Scholes Pricing Model")


# Build the model from the sidebar values and run the calculation
bs_model = BlackScholes(
    time_to_maturity=time_to_maturity,
    strike=strike,
    current_price=current_price,
    volatility=volatility,
    interest_rate=interest_rate,
)
bs_model.run()

# Temporary display 
st.write("Call price:", bs_model.call_price)
st.write("Put price:", bs_model.put_price)