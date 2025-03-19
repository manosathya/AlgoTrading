import pandas as pd

import redis.asyncio as redis  
import asyncio
from datetime import datetime

from tqdm.notebook import tqdm

import nest_asyncio
nest_asyncio.apply()

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def ohlc_consume(ticker, strategy_config):
    """
    Fetch last N ticks, then listen for new OHLC data in real-time. Awaits strategy defined in strategy config
    """

    stream_key = f"alpaca_{ticker}"
    
    messages = await redis_client.xrevrange(stream_key, count=strategy_config['n_hist'])
    messages.reverse() 
    hist_data = []
    
    progress_bar = tqdm(desc=f"{ticker}", bar_format="{n} {l_bar} {postfix}") 
    
    for entry_id, data in messages:
        data['close'] = float(data['close'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        hist_data.append(data)
        last_id = entry_id
        progress_bar.update(1)
    progress_bar.set_postfix({"Status": "Processed"})
    df = pd.DataFrame(hist_data)  

    #Switch to real-time streaming
    while True:
        #Enter at the entry_id last found, i.e. the latest histroical id
        new_messages = await redis_client.xread({stream_key: last_id}, block=0)
        for stream, entries in new_messages:
            for entry_id, data in entries:
                data['close'] = float(data['close'])
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                
                df.loc[len(df)] = data
                last_id = entry_id  # Update last processed ID
                
                progress_bar.update(1)
                progress_bar.set_postfix({"Status": f"Streaming (last tick: {data['timestamp']})"})    
                progress_bar.colour = "#0cfade"
                
                await strategy_config['strategy'](df, ticker)
                
        await asyncio.sleep(0)            

async def gather_tickers(strategy_config):
    """
    Gather tasks for consuming OHLC data and applying the strategy. Tickers defined in strategy_config
    """
    tasks = []
    for ticker in strategy_config['tickers']:
        tasks.append(ohlc_consume(ticker, strategy_config))
    await asyncio.gather(*tasks)