import pandas as pd
import streamlit as st

from blackscholes import BlackScholes


# Page configuration
st.set_page_config(
    page_title="Black-Scholes Option Pricing Model",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Custom CSS for the CALL and PUT value boxes
st.markdown("""
<style>
.metric-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px;
    margin: 0 auto;
}

.metric-call {
    background-color: #90ee90;  /* light green */
    color: black;
    border-radius: 10px;
}

.metric-put {
    background-color: #ffcccb;  /* light red */
    color: black;
    border-radius: 10px;
}

.metric-label {
    font-size: 1rem;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)


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


# Table of the current inputs
input_df = pd.DataFrame({
    "Current Asset Price": [current_price],
    "Strike Price": [strike],
    "Time to Maturity (Years)": [time_to_maturity],
    "Volatility (σ)": [volatility],
    "Risk-Free Interest Rate": [interest_rate],
})
st.table(input_df)


# Build the model from the sidebar values and run the calculation
bs_model = BlackScholes(
    time_to_maturity=time_to_maturity,
    strike=strike,
    current_price=current_price,
    volatility=volatility,
    interest_rate=interest_rate,
)
bs_model.run()


# Show CALL and PUT values side by side
col1, col2 = st.columns([1, 1], gap="small")

with col1:
    st.markdown(f"""
        <div class="metric-container metric-call">
            <div>
                <div class="metric-label">CALL Value</div>
                <div class="metric-value">${bs_model.call_price:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-container metric-put">
            <div>
                <div class="metric-label">PUT Value</div>
                <div class="metric-value">${bs_model.put_price:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)