from modules.data import load_yaml_config
from modules.strategies import Base_RSI

import json
import asyncio
import redis.asyncio as redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
strategy_configs = load_yaml_config('configs/strategy_configs.yaml')
strategy_name = 'RSI'
mode = 'test'
submit_orders = False
plot_type = 'dash'

async def run_strategy():
    try:
        strategy = Base_RSI(strategy_configs[strategy_name], mode=mode,submit_orders=submit_orders, plot_type=plot_type)
        await strategy.run_subscribers()
    except:
        print('keyboard interrupt')
        await strategy.stop()

asyncio.run(run_strategy())
