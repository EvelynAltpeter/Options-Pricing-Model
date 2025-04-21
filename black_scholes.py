import numpy as np
from scipy.stats import norm

def black_scholes(current_stock_price, strike_price, risk_free_rate, time_to_expiry, sigma, option_type='call'):
    d1 = (np.log(current_stock_price / strike_price) + (risk_free_rate + 0.5 * sigma ** 2) * time_to_expiry) / (sigma * np.sqrt(time_to_expiry))
    d2 = d1 - sigma * np.sqrt(time_to_expiry)
    # Call
    if option_type == 'call':
        price = current_stock_price * norm.cdf(d1) - strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
    # Put
    else:
        price = strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - current_stock_price * norm.cdf(-d1)

    return price

'''
# Example case
current_stock_price = 1000
strike_price = 1010
risk_free_rate = 0.05 # Rate of 5%
time_to_expiry = 1    # Time in years
sigma = 0.15          # Volatility of 15%

call_price = black_scholes(current_stock_price, strike_price, risk_free_rate, time_to_expiry, sigma, 'call')
put_price = black_scholes(current_stock_price, strike_price, risk_free_rate, time_to_expiry, sigma, 'put')
print(f"Call Price: {call_price}, Put Price: {put_price}")
'''



