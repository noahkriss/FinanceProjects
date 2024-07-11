# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 09:24:56 2024

@author: noahk
"""

# import packages
import numpy as np

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

print(f"American Option Binomial Tree Estimation:   ${option_price:.2f}")

#%%

# Pricing an Options Contract By Ticker

import yfinance as yf
from datetime import datetime

def parse_option_contract(contract_name):
    # Extract ticker symbol (assumes ticker is the first part and is alphabetic)
    ticker = ''.join([char for char in contract_name if char.isalpha()])
    ticker = ticker[:-1] # Remove C/P
    
    # Extract expiration date (assumes it's the 6 digits following the ticker)
    date_start = len(ticker)
    exp_date = contract_name[date_start:date_start + 6]
    exp_date = datetime.strptime(exp_date, '%y%m%d').strftime('%Y-%m-%d')
    
    # Extract option type (the character following the date)
    option_type = contract_name[date_start + 6]
    
    # Extract strike price (the rest of the contract name)
    strike_price = contract_name[date_start + 7:]
    strike_price = float(strike_price) / 1000
    
    return {
        'ticker': ticker,
        'exp_date': exp_date,
        'strike_price': strike_price,
        'option_type': 'call' if option_type == 'C' else 'put'
    }


def AmericanBinomialTree(contract_name, N):	
    
    parsed_data = parse_option_contract(contract_name)
    
    ticker = parsed_data['ticker']
    exp_date = parsed_data['exp_date']
    strike_price = parsed_data['strike_price']
    option_type = parsed_data['option_type']

    tk = yf.Ticker(ticker)
    
    # get stock price
    last_stock_price = tk.history(period='1d')['Close'].iloc[-1]
    
    # get options contract data
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
        
    # get time to expiry (years)
    time_to_expiry = datetime.fromisoformat(exp_date) - datetime.today()
    time_to_expiry = (time_to_expiry.days + 1)/365
    
    # get T-bill rate (use 1 year)
    treasury_ticker = yf.Ticker('^IRX')
    treasury_data = treasury_ticker.history(period='1d')
    treasury_rate = treasury_data['Close'].iloc[-1]
    treasury_rate = treasury_rate/100

    S0 = last_stock_price
    K = strike_price
    T = time_to_expiry
    r = treasury_rate
    sigma = volatility
    option_type = option_type
    
    bta_option = BinomialTreeAmerOption(S0, K, T, r, sigma, N, option_type)
    return bta_option.price()


# Example usage
N = 1000 # iterations
Option_Ticker = 'TSLA260618P00400000'

contract_price = AmericanBinomialTree(Option_Ticker, N)

print(f"{Option_Ticker} American Binomial Tree Price Estimation:            ${contract_price:.2f}")





















