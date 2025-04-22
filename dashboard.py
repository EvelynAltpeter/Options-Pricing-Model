import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from monte_carlo import monte_carlo_simulation
from black_scholes import black_scholes

SYMBOL = "AMZN"  # Amazon

# Configure page
st.set_page_config(layout="wide", page_title="Options Pricing Dashboard")

# Sidebar control
st.sidebar.header("Parameters")
symbol = st.sidebar.text_input("Ticker Symbol", SYMBOL)
risk_free_rate = st.sidebar.slider("Risk-Free Rate (%)", 0.0, 10.0, 2.5) / 100
n_simulations = st.sidebar.number_input("Monte Carlo Simulations",
                                        min_value=1000,
                                        max_value=100000,
                                        value=10000,
                                        step=1000)

# Main dashboard
st.title(f"Options Pricing Dashboard - {symbol}")



def fetch_options_data(symbol, risk_free_rate, n_simulations):
    try:
        # Fetch current stock price
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")

        if hist.empty:
            st.error("Failed to fetch stock price history")
            return pd.DataFrame()

        current_price = hist["Close"].iloc[-1]

        # Fetch options chain
        try:
            options_chain = ticker.option_chain()
        except Exception as e:
            st.error(f"Failed to fetch options chain: {str(e)}")
            return pd.DataFrame()

        # Process expiration date
        expiry_dates = ticker.options
        expiry_choice = st.sidebar.selectbox("Select Expiration", expiry_dates)
        options_chain = ticker.option_chain(expiry_choice)

        # Process calls and puts
        calls = options_chain.calls.assign(type="call")
        puts = options_chain.puts.assign(type="put")
        options = pd.concat([calls, puts])

        # Add calculated fields
        options['current_stock_price'] = current_price
        expiry_date = pd.to_datetime(str(expiry_choice))
        options['time_to_expiry'] = (expiry_date - pd.Timestamp.now()).days / 365

        # Filter out expired options (but less strict for debugging)
        valid_options = options[(options['time_to_expiry'] > -0.1)].copy()  # Allow slightly expired options

        if not valid_options.empty:
            # Corrected Black-Scholes calculation
            valid_options['BS Price'] = valid_options.apply(
                lambda row: black_scholes(
                    current_stock_price=row['current_stock_price'],
                    strike_price=row['strike'],
                    risk_free_rate=risk_free_rate,
                    time_to_expiry=max(0.001, row['time_to_expiry']),
                    sigma=row['impliedVolatility'],
                    option_type=row['type']
                ), axis=1
            )

            valid_options['MC Price'] = valid_options.apply(
                lambda row: monte_carlo_simulation(
                    current_stock_price=row['current_stock_price'],
                    strike_price=row['strike'],
                    risk_free_rate=risk_free_rate,
                    time_to_expiry=max(0.001, row['time_to_expiry']),
                    sigma=row['impliedVolatility'],
                    n_simulations=n_simulations,
                    option_type=row['type']
                ), axis=1
            )

        return valid_options

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return pd.DataFrame()


# Fetch data
options_data = fetch_options_data(symbol, risk_free_rate, n_simulations)

# Debug view
with st.expander("Debug View (Raw Data)"):
    if not options_data.empty:
        st.write("Options data sample:", options_data.head())
        st.write("Columns:", options_data.columns.tolist())
    else:
        st.write("No data fetched")

# Display results
if not options_data.empty:
    if 'BS Price' not in options_data.columns or 'MC Price' not in options_data.columns:
        st.error("Price calculations failed - showing raw options data")
        st.dataframe(options_data)
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Call Options")
            calls = options_data[options_data['type'] == 'call'].sort_values('strike')
            st.dataframe(calls[['strike', 'bid', 'ask', 'impliedVolatility',
                                'BS Price', 'MC Price', 'time_to_expiry']]
            .style.format({
                'bid': '{:.2f}',
                'ask': '{:.2f}',
                'impliedVolatility': '{:.2%}',
                'BS Price': '{:.2f}',
                'MC Price': '{:.2f}',
                'time_to_expiry': '{:.3f}'
            }), height=400)

        with col2:
            st.subheader("Put Options")
            puts = options_data[options_data['type'] == 'put'].sort_values('strike')
            st.dataframe(puts[['strike', 'bid', 'ask', 'impliedVolatility',
                               'BS Price', 'MC Price', 'time_to_expiry']]
            .style.format({
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

        chart_data = filtered.set_index('strike')[['bid', 'ask', 'BS Price', 'MC Price']]
        st.line_chart(chart_data)

        st.subheader("Implied Volatility Smile")
        iv_data = options_data[options_data['type'] == select_type][['strike', 'impliedVolatility']]
        st.line_chart(iv_data.set_index('strike'))


else:
    st.warning("No options data available for this symbol")
