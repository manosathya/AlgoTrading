from modules.data import load_yaml_config
from modules.strategies import Base_RSI

import json
import asyncio
import redis.asyncio as redis

import argparse

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
strategy_configs = load_yaml_config('configs/strategy_configs.yaml')

parser = argparse.ArgumentParser()
parser.add_argument('--strategy', type=str, required=True, help='Name of strategy class (e.g., RSI)')
parser.add_argument('--mode', type=str, choices=['paper', 'backtest', 'test'], default='test')
parser.add_argument('--submit_orders', action='store_true')
parser.add_argument('--plot_type', type=str, choices=['dash', 'jupyter', 'None'], default='dash')

args = parser.parse_args()

strategy_name = args.strategy
mode = args.mode
submit_orders = args.submit_orders
plot_type = None if args.plot_type == 'None' else args.plot_type

async def run_strategy():
    try:
        strategy = Base_RSI(strategy_configs[strategy_name], mode=mode,submit_orders=submit_orders, plot_type=plot_type)
        await strategy.run_subscribers()
    except:
        print('keyboard interrupt')
        await strategy.stop()

asyncio.run(run_strategy())
