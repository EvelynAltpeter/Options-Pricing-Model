import numpy as np
from scipy.stats import norm

def monte_carlo_simulation(current_stock_price, strike_price, risk_free_rate, time_to_expiry, sigma, n_simulations, option_type='call'):
    np.random.seed(0)

    Z = np.random.standard_normal(n_simulations)
    ST = current_stock_price * np.exp((risk_free_rate - 0.5 * sigma ** 2) * time_to_expiry + sigma *np.sqrt(time_to_expiry) * Z)

    # Calculate payoffs
    if option_type == 'call':
        payoffs = np.maximum(ST - strike_price, 0)
    # Put
    else:
        payoffs = np.maximum(strike_price - ST, 0)

    # Discount to present value
    option_price = np.exp(-risk_free_rate * time_to_expiry) * np.mean(payoffs)
    return option_price

# Example case
current_stock_price = 1000
strike_price = 1010
risk_free_rate = 0.05 # Rate of 5%
time_to_expiry = 1    # Time in years
sigma = 0.15          # Volatility of 15%
n_simulations = 10000

mc_call_price = monte_carlo_simulation(current_stock_price, strike_price, risk_free_rate, time_to_expiry, sigma, n_simulations, 'call')
mc_put_price = monte_carlo_simulation(current_stock_price, strike_price, risk_free_rate, time_to_expiry, sigma, n_simulations, 'put')
print(f"Monte Carlo Call Price: {mc_call_price}, Monte Carlo Put Price: {mc_put_price}")
