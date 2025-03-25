"""
Logic:

Base Strategy imports BacktestEngine.
Each strategy can call strategy.run_backtest()
    Needs input params to initialise on run backtest call:
        Historical Data. Initial Balance.

run backtest:
Pass through rolling dataframe defined by strategy.config[hist_period] + 1 to strategy.generate_signal()
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
        self.hist_period = self.strategy.config.get('hist_period',0)
        self.rolling_window = {ticker:deque(maxlen=self.hist_period+1) for ticker in self.strategy.config['tickers']}
        
        self.historical_data = historical_data.sort_values(by='timestamp', ascending=True)
        
        self.current_cash = initial_balance
        self.balance_hist = [initial_balance]  
        self.portfolio = {ticker:0 for ticker in self.strategy.config['tickers']}
        self.latest_price = {ticker:0 for ticker in self.strategy.config['tickers']}
        
    def process_row(self, row, ticker):
        if ticker not in self.rolling_window:
            return 
            
        self.rolling_window[ticker].append(row)
           
        if len(self.rolling_window[ticker]) < self.hist_period+1:
            return 
            
        return pd.DataFrame(self.rolling_window[ticker])
                
    def run_backtest(self): 
        for group_id, group_df in self.historical_data.groupby('timestamp'):
            for row in group_df.itertuples(index=False):
                ticker = row.ticker
                df_window = row
                
                if self.hist_period > 0:
                    df_window = self.process_row(df_window, ticker)
                if df_window is None:
                    continue
                #print(group_id)
                order_data = self.strategy.generate_signal(df_window, ticker)

                if not order_data:
                    continue    
    
                order_data['position_size'] = self.get_position_size(order_data)
                self.strategy.positions[ticker] = self.place_market_order_backtest(order_data)    
                
                self.latest_price[ticker] = (order_data['price'])  
            self.balance_hist.append(self.get_portfolio_value() + self.current_cash)

    

    def place_market_order_backtest(self, order_data):
        ticker, signal, price, position_size = order_data['ticker'], order_data['signal'], order_data['price'], order_data['position_size']
        if signal == 'long':
            self.current_cash -= position_size
            self.portfolio[ticker] += position_size/price
        elif signal == 'short':     
            self.current_cash -= price*position_size
            self.portfolio[ticker] -= position_size
        elif signal == 'close':     
            self.current_cash += price*position_size
            self.portfolio[ticker] = 0
            return None
        return signal
        
    #def get_portfolio_value(self):
        #total_value = 0
        #for ticker, qty in self.portfolio.items():
            #total_value += abs(qty)*self.latest_price[ticker][0]
        #return total_value
        
    def get_portfolio_value(self):
        tickers = list(self.portfolio.keys())
        quantities = np.array([self.portfolio[ticker] for ticker in tickers])
        prices = np.array([self.latest_price[ticker] for ticker in tickers])
        total_value = np.sum(np.abs(quantities) * prices)  
        return total_value
        
    def get_position_size(self, order_data):
        ticker, signal, price = order_data['ticker'], order_data['signal'], order_data['price']
        
        if signal =='close':
            return abs(self.portfolio[ticker])
            
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