import redis.asyncio as redis  
import asyncio
import nest_asyncio
import json
nest_asyncio.apply()

from alpaca.data.live.stock import StockDataStream
from modules.data import load_yaml_config

import os 

stock_stream = StockDataStream(os.environ['API_KEY'], os.environ['SECRET_KEY'])
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
configs = load_yaml_config('configs/publisher_configs.yaml')

print(f"Available publisher configs - {list(configs.items())}")
key = None
while key not in configs.keys():
    key = input("Select config:")
    if key not in configs.keys():
        print("Invalid config name. Please choose from the list.")
        
stream_key = configs[key]['stream_key']
tickers = configs[key]['tickers']

async def push_ohlc_data(bar):
    bar = {k: v for k, v in bar}
    bar['timestamp'] = bar['timestamp'].isoformat()
    
    # Add the new OHLC tick to the Redis Stream
    await redis_client.xadd(f"{stream_key}:{bar['symbol']}", bar)
    await redis_client.xtrim(f"{stream_key}:{bar['symbol']}", maxlen=100)
    
    print(f"Pushed OHLC Tick: {bar}")

stock_stream.subscribe_bars(push_ohlc_data, *tickers)
    
async def main():
    await redis_client.hset('configs:publisher',mapping={'status':json.dumps(configs[key])})
    try:
        stock_stream.run()
    except:
        await redis_client.hset('configs:publisher',mapping={'status':json.dumps('inactive')})

asyncio.run(main())