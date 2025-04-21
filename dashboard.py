import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from monte_carlo import monte_carlo_simulation, n_simulations
from black_scholes import black_scholes, risk_free_rate

SYMBOL = "NVDA" # NVIDIA

# Configure page
st.set_page_config(layout="wide", page_title="Options Pricing Dashboard")

# Sidebar control
st.sidebar.header("Parameters")
symbol = st.sidebar.text_input("Ticker Symbol", SYMBOL)
risk_free_rate = st.sidebar.slider("Risk-Free Rate (%)", 0.0, 10.0, 2.5) / 100
n_simulations = st.sidebar.number_input("Monte Carlo Simulations", min_value=1000, value=10000, max_value=100000, step=1000)

# Main dashboard
st.title(f"Options Pricing Dashboard - {symbol}")

@st.cache_data(ttl=3600) # Cache for 1hr
def fetch_options_data(symbol, risk_free_rate, n_simulations):

    # Fetch current stock price
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    current_price = hist["Close"].iloc[-1]

    # Fetch options chain (next expiry by default)
    options_chain = ticker.option_chain()

    # Get expiration date from chain (timezone-naive)
    expiry_date = pd.to_datetime(options_chain.calls['lastTradeDate'].iloc[0])
    if expiry_date.tz:  # Remove timezone if present
        expiry_date = expiry_date.tz_localize(None)

    # Process calls and puts
    calls = options_chain.calls.assign(type="call")
    puts = options_chain.puts.assign(type="put")
    options = pd.concat([calls, puts])

    # Add calculated fields
    options['current_stock_price'] = current_price
    options['time_to_expiry'] = (expiry_date - pd.Timestamp.now()).days / 365

    # Filter out expired options
    valid_options = options[options['time_to_expiry'] > 0].copy()

    if not valid_options.empty:
        # Add debug prints
        print("\nCalculating Black-Scholes prices...")
        valid_options['BS Price'] = valid_options.apply(
            lambda row: black_scholes(
                S=row['current_stock_price'],
                K=row['strike'],
                T=row['time_to_expiry'],
                r=risk_free_rate,
                sigma=row['impliedVolatility'],
                option_type=row['type']
            ), axis=1
        )

        print("Calculating Monte Carlo prices...")
        valid_options['MC Price'] = valid_options.apply(
            lambda row: monte_carlo_simulation(
                current_stock_price=row['current_stock_price'],
                strike_price=row['strike'],
                risk_free_rate=risk_free_rate,
                time_to_expiry=row['time_to_expiry'],
                sigma=row['impliedVolatility'],
                n_simulations=n_simulations,
                option_type=row['type']
            ), axis=1
        )

        print("Sample calculated prices:")
        print(valid_options[['strike', 'BS Price', 'MC Price']].head())

    return valid_options

# Fetch data
options_data = fetch_options_data(symbol, risk_free_rate, n_simulations)

# Display results
if not options_data.empty:
    # Verify calculations are happening
    if 'BS Price' not in options_data.columns or 'MC Price' not in options_data.columns:
        st.error("Price calculations failed - check terminal for errors")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Call Option")
            calls = options_data[options_data['type'] == 'call'].sort_values('strike')
            st.dataframe(calls.style.format({
                'bid': '{:.2f}',
                'ask': '{:.2f}',
                'impliedVolatility': '{:.2%}',
                'BS Price': '{:.2f}',
                'MC Price': '{:.2f}',
                'time_to_expiry': '{:.3f}'
            }), height=400)

        with col2:
            st.subheader("Put Option")
            puts = options_data[options_data['type'] == 'put'].sort_values('strike')
            st.dataframe(puts.style.format({
                'bid': '{:.2f}',
                'ask': '{:.2f}',
                'impliedVolatility': '{:.2%}',
                'BS Price': '{:.2f}',
                'MC Price': '{:.2f}',
                'time_to_expiry': '{:.3f}'
            }), height=400)

        # Visualization
        st.subheader("Pricing Comparison")
        select_type = st.selectbox("Option Type", ['call', 'put'])
        filtered = options_data[options_data['type'] == select_type]

        chart_data = filtered.set_index('strike')[['bid', 'ask', 'BS Price', 'MC Price']])
        print("\nChart data sample:", chart_data.head())
        st.line_chart(chart_data)

else:
    st.warning("No options data available for this symbol")
