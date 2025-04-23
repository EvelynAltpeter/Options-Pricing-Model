# Options-Pricing-Model

How to run it: streamlit run dashboard.py

Options Pricing Dashboard
Project Purpose
This dashboard provides a streamlined interface for analyzing options pricing using two fundamental quantitative models: the Black-Scholes analytical model and Monte Carlo simulations. The tool fetches real-time options chain data and computes theoretical prices, enabling traders and analysts to:
- Compare market prices with model valuations
- Assess implied volatility patterns
- Visualize option price sensitivity across strikes
- Evaluate model performance under different market conditions

Motivation
Options pricing is fundamental to modern financial markets, yet remains computationally intensive and data-heavy. This project addresses three key needs:
- Accessibility: Democratizing sophisticated pricing models through an intuitive interface
- Education: Demonstrating quantitative finance concepts in practice
- Efficiency: Automating complex calculations that would be time-consuming manually

The implementation combines financial theory with practical engineering, showcasing how Python can bridge academic models and real-world trading applications.

Theoretical Foundations

Black-Scholes Model
The Black-Scholes-Merton model (1973) provides a closed-form solution for European option pricing under these key assumptions:

Geometric Brownian Motion: 
Stock prices follow: 
dS = μSdt + σSdW

where:
μ = drift rate

σ = volatility

W = Wiener process

Key Inputs:
S = Current stock price

K = Strike price

T = Time to expiration (years)

r = Risk-free rate

σ = Volatility (annualized)

Pricing Formulas:

Call Price:
C = S*N(d1) - K*e^(-rT)*N(d2)

Put Price:
P = K*e^(-rT)*N(-d2) - S*N(-d1)

where:
d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
d2 = d1 - σ√T
and N() is the cumulative normal distribution

Limitations:
- Assumes constant volatility and interest rates
- Only valid for European options
- Ignores dividends and transaction costs

Monte Carlo Simulation
The Monte Carlo approach estimates option prices through statistical sampling:

Process:
- Simulate thousands of possible stock price paths
- Calculate payoff for each path
- Discount and average all payoffs

Price Evolution:
Each simulated path follows:
S_t = S_0 * exp((r - σ²/2)t + σ√t*Z)

where Z ~ N(0,1)

Option Payoff:

Call: max(S_T - K, 0)

Put: max(K - S_T, 0)

Final Price:
Price = e^(-rT) * average(payoffs)

Advantages:
- Handles path-dependent options
- Accommodates complex payoffs
- Can model stochastic volatility

Tradeoffs:
- Computationally intensive
- Requires careful random number generation
- Subject to sampling error


This implementation demonstrates both models' outputs simultaneously, allowing users to observe how they converge under different market conditions.


Technologies used (Streamlit, yfinance, NumPy)

![img.png](img.png)
![img_1.png](img_1.png)
