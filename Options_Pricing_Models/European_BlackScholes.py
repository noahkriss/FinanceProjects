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

print(f"European Option Binomial Tree Estimation:   ${option_price:.2f}")

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


def BlackScholes(contract_name):	
    
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
    
    bs_option = European_BlackScholes(S0, K, T, r, sigma, option_type)
    return bs_option.price()


# Example usage
Option_Ticker = 'TSLA260618P00400000'

contract_price = BlackScholes(Option_Ticker)

print(f"{Option_Ticker} Black-Scholes Price Estimation:                     ${contract_price:.2f}")