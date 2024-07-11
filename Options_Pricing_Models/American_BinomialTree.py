# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 09:24:56 2024

@author: noahk
"""

# import packages
import numpy as np
import pandas as pd

# class for a Binomial Tree - American Style Stock Option - price estimation
class BinomialTreeAmerOption:
    
    def __init__(self, S0, K, T, r, sigma, N, option_type="call"):
        
        self.S0 = S0 # Current Stock Price
        self.K = K # Strike Price
        self.T = T # Time until expiry (years)
        self.r = r # Risk Free Interest Rate
        self.sigma = sigma # Volatility
        self.N = N # Binomial Tree iterations
        self.option_type = option_type # 'call' or 'put'
        self.dt = T / N
        self.u = np.exp(sigma * np.sqrt(self.dt))
        self.d = 1 / self.u  
        self.p = (np.exp(r * self.dt) - self.d) / (self.u - self.d)
      
        
    def price(self):
        
        asset_values = np.zeros(self.N + 1)
        for i in range(self.N + 1):
            asset_values[i] = self.S0 * (self.u ** i) * (self.d ** (self.N - i))
        
        option_values = np.zeros(self.N + 1)
        for i in range(self.N + 1):
            if self.option_type == 'call':  
                option_values[i] = max(0, asset_values[i] - self.K)
            elif self.option_type == 'put':
                option_values[i] = max(0, self.K - asset_values[i])
                    
        for j in range(self.N - 1, -1, -1):
            for i in range(j + 1):
                hold_value = (self.p * option_values[i + 1] + (1 - self.p) * option_values[i]) * np.exp(-self.r * self.dt)

                if self.option_type == 'call':  
                    excercise_value = max(0, asset_values[i]  - self.K)
                elif self.option_type == 'put':
                    excercise_value = max(0, self.K - asset_values[i])
                    
                option_values[i] = max(hold_value, excercise_value)
                asset_values[i] = asset_values[i] * self.u
                
        

        return option_values[0]
    

S0 = 259.6 # [dollars]
K = 260 # [dollars]
T = 344/365 # [years]
r = 0.05
sigma = 0.4849
N = 5000
option_type = 'put'

option = BinomialTreeAmerOption(S0, K, T, r, sigma, N, option_type)
option_price = option.price()

print(f"American Option Binomial Tree Estimation: ${option_price:.2f}")

#%%

# for pricing a real options contract

import yfinance as yf
from datetime import datetime

ticker = "TSLA"
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

bt_option = BinomialTreeAmerOption(S0, K, T, r, sigma, N, option_type)
bt_option_price = bt_option.price()

print(f"American Option Binomial Tree Estimation:   ${bt_option_price:.2f}")
print(f"Last Contract Price:                        ${lastPrice:.2f}")
























