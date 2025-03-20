import os
import pandas as pd
from pandas_ta.momentum import rsi
from modules.trading_helpers import place_market_order
from alpaca.trading.client import TradingClient

from tqdm.notebook import tqdm
from datetime import datetime

import redis.asyncio as redis  
import asyncio
import nest_asyncio

nest_asyncio.apply()
trading_client = TradingClient(os.environ['API_KEY'],os.environ['SECRET_KEY'], paper=True)
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

class BaseStrategy:
    def __init__(self,config):
        self.config = config
        self.positions = {ticker: None for ticker in config['tickers']}  # Initialize empty positions

        asyncio.run(self.initialize_positions())


    async def initialize_positions(self):
        """Fetch current positions from the API for tickers in config and update self.positions."""
        try:
            all_positions = trading_client.get_all_positions()  # Fetch all positions from API

            # Filter only positions for tickers in config
            for position in all_positions:
                ticker = position.symbol
                if ticker in self.config['tickers']:  # Only update if the ticker is in our config
                    qty = float(position.qty)

                    # Determine if it's long or short
                    if qty > 0:
                        self.positions[ticker] = 'long'
                    elif qty < 0:
                        self.positions[ticker] = 'short'
                    else:
                        self.positions[ticker] = None

            print("Positions initialized:", self.positions)

        except Exception as e:
            print(f"Error fetching positions: {e}")
            
    async def subscriber(self, ticker):
        """
        Fetch historical data and then stream new data.
        """
        stream_key = f"{self.config['stream_key']}_{ticker}"
        messages = await redis_client.xrevrange(stream_key, count=self.config['n_hist'])
        messages.reverse()
        hist_data = []
        progress_bar = tqdm(desc=f"{ticker}", bar_format="{n} {l_bar} {postfix}") 

        for entry_id, data in messages:
            data['close'] = float(data['close'])
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            hist_data.append(data)
            last_id = entry_id
            progress_bar.update(1)
            
        progress_bar.refresh()
        df = pd.DataFrame(hist_data)

        # Switch to real-time streaming
        while True:
            new_messages = await redis_client.xread({stream_key: last_id}, block=0)
            for stream, entries in new_messages:
                for entry_id, data in entries:
                    data['close'] = float(data['close'])
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    df.loc[len(df)] = data
                    last_id = entry_id
                    progress_bar.colour = '#33eef5'
                    progress_bar.update(1)
                    progress_bar.set_postfix({"Status": f"Streaming (last tick: {data['timestamp']})"})    
                    await self.generate_signal(df, ticker)
            await asyncio.sleep(0)

    async def run_multiple_subscribers(self):
        """
        Launch streaming for all tickers in the config.
        """
        tasks = []
        for ticker in self.config['tickers']:
            tasks.append(self.subscriber(ticker))
        await asyncio.gather(*tasks)
        
    async def generate_signal(self, df: pd.DataFrame, ticker: str):
        """
        Abstract method to process new data.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

class Base_RSI(BaseStrategy):    
    def __init__(self, config):
        super().__init__(config)
        self.overbought_th = config.get("overbought_th", {'entry': 85, 'exit':50})
        self.oversold_th = config.get("oversold_th", {'entry': 15, 'exit':50})
        self.free_cash_perc = config.get("free_cash_perc", 0.1)
        
    async def generate_signal(self, df: pd.DataFrame, ticker: str):
        if len(df)<15:
            print('HOLD')
            return
            
        # Calculate Latest RSI
        rsi_value = rsi(df.close.iloc[-15:]).iloc[-1]
        
        price = df.close.iloc[-1]
        notional = round(float(trading_client.get_account().buying_power) * self.free_cash_perc,2)
        qty = round(notional/price)
        # Trading Logic
        if rsi_value <= self.oversold_th['entry'] and self.positions[ticker] == None:
            print('buy:', ticker)
            await place_market_order(ticker,'buy', notional)
            self.positions[ticker] = 'long'
            
        elif rsi_value >= self.overbought_th['entry'] and self.positions[ticker] == None:
            await place_market_order(ticker, 'short', qty) 
            print('short:', ticker, f"qty: {qty}")
            self.positions[ticker] = 'short'
            
        if self.positions[ticker] == 'short' and rsi_value <= self.overbought_th['exit']:
            print('close short:', ticker)
            await place_market_order(ticker,'close')
            self.positions[ticker] = None
            
        elif self.positions[ticker] == 'long' and rsi_value >= self.oversold_th['exit']:
            await place_market_order(ticker, 'close') 
            print('close long:', ticker)
            self.positions[ticker] = None

