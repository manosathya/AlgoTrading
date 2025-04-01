"""
Logic:

Base Strategy imports BacktestEngine.
Each strategy can call strategy.run_backtest()
    Needs input params to initialise on run backtest call:
        Historical Data. Initial Balance.

run backtest:
Pass through rolling dataframe defined by strategy.config[period] to strategy.generate_signal()
        Get all tickers in one, shuffle, sort by timestamp.
        Pass df.rolling and df.ticker

    return order type and value

-> pass into pmo_backtest?
calulate new cash balance.
update ticker position
update ticker value
store trade?
update ticker position value
get total portfolio value
    
"""

import pandas as pd
import numpy as np
from collections import deque

class BacktestEngine:
    def __init__(self, strategy, historical_data, initial_balance = 1000):
        self.strategy = strategy
        self.strategy.positions = {ticker:None for ticker in self.strategy.config['tickers']}
        self.period = self.strategy.config.get('period',0)
        
        self.historical_data = historical_data.sort_values(by=['ticker','timestamp'], ascending=True)
        
        self.current_cash = initial_balance
        self.balance_hist = [(self.historical_data.iloc[0].timestamp ,initial_balance)]

        self.portfolio_arr = np.zeros(len(self.strategy.config['tickers']))
        self.latest_price_arr = np.zeros(len(self.strategy.config['tickers']))
        self.ticker_index_map = {ticker: i for i, ticker in enumerate(self.strategy.config['tickers'])}
                    
    def run_backtest(self): 
        values = []
        for ticker, group_df in self.historical_data.groupby('ticker'):
            values.extend(self.strategy.calculate_values(group_df))
        self.historical_data['values'] = values
        
        self.historical_data.sort_values(by='timestamp', inplace=True)

        tickers, values, closes, timestamps = self.historical_data[['ticker', 'values', 'close', 'timestamp']].values.T
        for ticker, value, close, timestamp in zip(tickers, values, closes, timestamps):
            
            order_data = self.strategy.generate_signal(ticker, value)
            
            if order_data:
                order_data['price']= close
                order_data['position_size'] = self.get_position_size(order_data)
                           
                self.strategy.positions[ticker] = self.place_market_order_backtest(order_data)    
                self.latest_price_arr[self.ticker_index_map[ticker]] = order_data['price']
                self.balance_hist.append((timestamp, self.get_portfolio_value() + self.current_cash))

    def place_market_order_backtest(self, order_data):
        ticker, signal, price, position_size = self.ticker_index_map[order_data['ticker']], order_data['signal'], order_data['price'], order_data['position_size']
        if signal == 'long':
            self.current_cash -= position_size
            self.portfolio_arr[ticker] += position_size/price
        elif signal == 'short':     
            self.current_cash -= price*position_size
            self.portfolio_arr[ticker] -= position_size
        elif signal == 'close':     
            self.current_cash += price*position_size
            self.portfolio_arr[ticker] = 0
            return None
        return signal   

    def get_portfolio_value(self):
        return np.sum(np.abs(self.portfolio_arr) * self.latest_price_arr)

    def get_position_size(self, order_data):
        ticker, signal, price = self.ticker_index_map[order_data['ticker']], order_data['signal'], order_data['price']
        
        if signal =='close':
            return abs(self.portfolio_arr[ticker])
            
        buying_power = float(self.current_cash)
        free_cash_perc = 0.1
        notional = round(buying_power * free_cash_perc,2)
        
        if signal == 'short':
            #Whole QTY for short posns
            return round(notional/price)
        else:
            return notional 
                            
    def get_performance(self):
        pass