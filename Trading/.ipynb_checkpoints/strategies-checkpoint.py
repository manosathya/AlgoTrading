import pandas as pd

from tqdm.notebook import tqdm
from datetime import datetime

from pandas_ta.momentum import rsi

from trading_helpers import place_market_order


import redis.asyncio as redis  
import asyncio
import nest_asyncio
nest_asyncio.apply()

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

class BaseStrategy:
    def __init__(self,config):
        self.config = config

    async def subscriber(self, ticker):
        """
        Fetch historical data and then stream new data.
        """
        stream_key = f"alpaca_{ticker}"
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
        self.overbought_th = config.get("overbought_th", 50)
        self.oversold_th = config.get("oversold_th", 15)

    async def generate_signal(self, df: pd.DataFrame, ticker: str):
        if len(df)<15:
            print('HOLD')
            return
            
        # Calculate Latest RSI
        rsi_value = rsi(df.close.iloc[-15:]).iloc[-1]
        
        # Trading Logic
        if rsi_value <= self.oversold_th:
            print('buy', ticker)
            await place_market_order(ticker,'buy')
        elif rsi_value >= self.overbought_th:
            try:
                await place_market_order(ticker, 'sell')
                print('sell', ticker)
            except:
                pass