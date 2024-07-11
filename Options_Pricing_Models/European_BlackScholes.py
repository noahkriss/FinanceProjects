# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 22:22:24 2024

@author: noahk
"""
import numpy as np
from scipy.stats import norm

class European_BlackScholes:

    def __init__(self, S0, K, T, r, sigma, option_type = 'call'):
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.option_type = option_type
        
    def price(self):
        d1 = (np.log(self.S0/self.K)+0.5*self.T*(self.r+self.sigma**2))/(self.sigma*np.sqrt(self.T))
        d2 = (np.log(self.S0/self.K)+0.5*self.T*(self.r-self.sigma**2))/(self.sigma*np.sqrt(self.T))
    
        
        if self.option_type == 'call':
            price = self.S0*norm.cdf(d1)-self.K*np.exp(-self.r*self.T)*norm.cdf(d2)
        elif self.option_type == 'put':
            price = self.K*np.exp(-self.r*self.T)*norm.cdf(-d2)-self.S0*norm.cdf(-d1)
        
        return price

S0 = 100 # [dollars]
K = 120 # [dollars]
T = 1.5 # [years]
r = 0.05
sigma = 0.3

option = European_BlackScholes(S0, K, T, r, sigma, 'put')
option_price = option.price()

print(f"European Option Binomial Tree Estimation: ${option_price:.2f}")

#%%

# for pricing a real options contract

import yfinance as yf
from datetime import datetime

ticker = "TSLA"
exp_date = '2025-06-20'
strike_price = 240
option_type = 'call'

tk = yf.Ticker(ticker)

# get stock price
last_stock_price = tk.history(period='1d')['Close'].iloc[-1]

# get options contract data
exps = tk.options
option_chain = tk.option_chain(exp_date)
calls = option_chain.calls
puts = option_chain.puts

if option_type == 'call':
    specific_contract = calls[calls['strike'] == strike_price]
else:
    specific_contract = puts[puts['strike'] == strike_price]

if not specific_contract.empty:
    contract_metrics = specific_contract.iloc[0]
    
volatility = contract_metrics['impliedVolatility']
lastPrice = contract_metrics['lastPrice']
    
# get time to expiry (years)
time_to_expiry = datetime.fromisoformat(exp_date) - datetime.today()
time_to_expiry = time_to_expiry.days/365

# get T-bill rate (use 1 year)
treasury_ticker = yf.Ticker('^IRX')
treasury_data = treasury_ticker.history(period='1d')
treasury_rate = last_treasury_rate = treasury_data['Close'].iloc[-1]
treasury_rate = treasury_rate/100

S0 = last_stock_price
K = strike_price
T = time_to_expiry
r = treasury_rate
sigma = volatility
N = 1000
option_type = option_type

r = 0.1

bs_option = European_BlackScholes(S0, K, T, r, sigma, option_type)
bs_option_price = bs_option.price()

print(f"Black-Scholes Price Estimation:             ${bs_option_price:.2f}")
print(f"Last Contract Price:                        ${lastPrice:.2f}")