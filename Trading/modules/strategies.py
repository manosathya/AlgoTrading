import os
import pandas as pd

from modules.trading_helpers import place_market_order
from modules.trading_helpers import get_position_size
from modules.data import rsi

from modules.visualisation import DynamicPlotter
from alpaca.trading.client import TradingClient

from tqdm.notebook import tqdm
from datetime import datetime

import redis.asyncio as redis  
import asyncio
import nest_asyncio

nest_asyncio.apply()
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

import numpy as np
    
class BaseStrategy:
    """
    Base strategy class to be inherited from.
    
    Defines Subscriber model for tickers
        Takes historical data before switching to real time streaming.
        Initialises existing ticker positions (long/short)
    Awaits generate_signal function, defined by the subclass
    
    -> config: dict
        -> stream_key:  str
        -> period:      int 
        -> tickers:     list(str)
    -> mode: str
        -> paper, test, or backtest
    """
    
    def __init__(self, config, mode, dry_run=False):
        if mode not in {"paper", "test", "backtest"}: 
            raise ValueError(f"Invalid mode: {mode}. Allowed values: 'live', 'backtest', 'test'")
        self.mode = mode
        self.dry_run = dry_run
        self.config = config
        self.positions = {ticker: None for ticker in config['tickers']}  # Initialize empty positions
        
        if self.mode =='paper':
            self.trading_client = TradingClient(os.environ['API_KEY'],os.environ['SECRET_KEY'], paper=True)       
            asyncio.create_task(self._initialize_positions())
        print("Positions initialized:", self.positions) 
            
    async def _initialize_positions(self):
        """
        Update self.positions with position type for all tickers in config['tickers']
        """
        all_positions = self.trading_client.get_all_positions()  
        for position in all_positions:
            ticker = position.symbol
            if ticker in self.config['tickers']: 
                qty = float(position.qty)
                if qty > 0:
                    self.positions[ticker] = 'long'
                elif qty < 0:
                    self.positions[ticker] = 'short'
                else:
                    self.positions[ticker] = None  
                    
    async def run_subscribers(self):
        """
        Launch streaming for all tickers in the config.
        """ 
        tasks = []
        for ticker in self.config['tickers']:
            tasks.append(self._subscriber(ticker))
        await asyncio.gather(*tasks) 
        
    async def _subscriber(self, ticker):
        """ 
        Fetch historical data and then stream new data.
        """
        stream_key = f"{self.config['stream_key']}_{ticker}"
        progress_bar = tqdm(desc=f"{ticker}", bar_format="{n} {l_bar} {postfix}")
        
        df, entry_id = await self._load_historical_data(stream_key, ticker)
        progress_bar.update(len(df))
        
        # Switch to real-time streaming
        while True:
            new_messages = await redis_client.xread({stream_key: entry_id}, block=0)
            progress_bar.colour = '#33eef5'
            
            for stream, entries in new_messages:
                for entry_id, data in entries:
                    df.loc[len(df)] = self._parse_ticks(data)
                    progress_bar.update(1)
                    progress_bar.set_postfix({"Status": f"Streaming (last tick: {data['timestamp']})"})
                    
                    indicator_value = self.calculate_values(df)[-1]
                    signal = self.generate_signal(ticker, indicator_value)

                    if signal:
                        order_data = {'ticker':ticker, 'signal':signal, 'price':data['close']}
                        await self._execute_order(order_data)

                    if self.config['plot']:
                        self.plotting_data = [ticker, data['timestamp'], indicator_value, self.positions[ticker]]
                        self.plotter.update(*self.plotting_data)
                        
            await asyncio.sleep(0)
            
    async def _execute_order(self, order_data):
        order_data['position_size'] = await get_position_size(order_data)
        print(f"{order_data}")
        self.positions[order_data['ticker']] = place_market_order(order_data, self.mode, self.dry_run)
            
    async def _load_historical_data(self, stream_key, ticker):
        messages = await redis_client.xrevrange(stream_key, count=self.config['period'])
        messages.reverse()

        hist_data = []
        for entry_id, data in messages:
            parsed_data = self._parse_ticks(data)
            hist_data.append(parsed_data)
    
        return pd.DataFrame(hist_data), entry_id     
        
    def _parse_ticks(self, data):
        data['close'] = float(data['close'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return data      
        
    async def generate_signal(self, df: pd.DataFrame, ticker: str):
        """
        Abstract method to process new data.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

        
class Base_RSI(BaseStrategy):   
    """
    RSI Implentaion.
    
    Defines RSI strategy for a ticker
        Inherits from Base strategy
        Generates long/short/close signal from rsi value
            Input all ticker data: pd.DataFrame, ticker:str
    
    -> Config
        -> overbought_th:    dict(entry:, exit:)    (default, 'entry': 85, 'exit':50})
        -> oversold_th:      dict(entry:, exit:)    (default, 'entry': 15, 'exit':50})
        -> free_cash_perc:   float                  (default, 0.1)
        -> plot:             bool
    """
    def __init__(self, config, mode, dry_run):
        super().__init__(config, mode, dry_run)
        self.overbought_th = config.get("overbought_th", {'entry': 85, 'exit':50})
        self.oversold_th = config.get("oversold_th", {'entry': 15, 'exit':50})
        self.free_cash_perc = config.get("free_cash_perc", 0.1)
        
        if config['plot']:
            self.plotter = DynamicPlotter(config['tickers'])
            self.plotting_data = []

    def calculate_values(self, df: pd.DataFrame):   
        if len(df)<self.config['period']+1:
            return None
            
        if self.mode == 'backtest':
            close_prices = df.close.to_numpy()
        else:
            close_prices = df.close.iloc[-(self.config['period']):].to_numpy()
        rsi_list = rsi(close_prices, self.config['period'])
        return rsi_list        
        
    def generate_signal(self, ticker, rsi_value,):
        if not(rsi_value):
            return None
            
        signal = None
        position = self.positions[ticker]
        # Trading Logic
        if position == None:
            if rsi_value <= self.oversold_th['entry']:
                signal = 'long'
            elif rsi_value >= self.overbought_th['entry']:         
                signal = 'short'     
        elif position == 'short' and rsi_value <= self.overbought_th['exit']:
            signal = 'close'         
        elif position == 'long' and rsi_value >= self.oversold_th['exit']:
            signal = 'close'
            
        return signal
