# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 09:24:56 2024

@author: noahk
"""

import numpy as np

class BinomialTreeEuroOption:
    
    def __init__(self, S0, K, T, r, sigma, N, option_type="call"):
        
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.N = N
        self.option_type = option_type
        self.dt = T / N
        self.u = np.exp(sigma * np.sqrt(self.dt))
        self.d = 1 / self.u
        self.p = (np.exp(r * self.dt) - self.d) / (self.u - self.d)
      
        
    def price(self):
        
        ST = np.zeros(self.N + 1)
        for i in range(self.N + 1):
            ST[i] = self.S0 * (self.u ** (self.N - i)) * (self.d ** i)

        
        option_values = np.zeros(self.N + 1)
        for i in range(self.N + 1):
            if self.option_type == 'call':  
                option_values[i] = max(0, ST[i] - self.K)
            elif self.option_type == 'put':
                option_values[i] = max(0, self.K - ST[i])
            
        for j in range(self.N - 1, -1, -1):
            for i in range(j + 1):
                option_values[i] = (self.p * option_values[i] + (1 - self.p) * option_values[i + 1]) * np.exp(-self.r * self.dt)

        return option_values[0]
        
    
S0 = 100 # [dollars]
K = 120 # [dollars]
T = 1.5 # [years]
r = 0.05
sigma = 0.3
N = 3000

option = BinomialTreeEuroOption(S0, K, T, r, sigma, N, 'put')
option_price = option.price()

print(f"European Option Binomial Tree Estimation: ${option_price:.2f}")

#%%

# for pricing a real options contract

import yfinance as yf
from datetime import datetime

ticker = "AAPL"
exp_date = '2025-06-20'
strike_price = 240
option_type = 'call'

tk  = yf.Ticker(ticker)

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
N = 2000
option_type = option_type

bt_option = BinomialTreeEuroOption(S0, K, T, r, sigma, N, option_type)
bt_option_price = bt_option.price()

print(f"European Option Binomial Tree Estimation:   ${bt_option_price:.2f}")
print(f"Last Contract Price:                        ${lastPrice:.2f}")