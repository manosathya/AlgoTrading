import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide

API_KEY = os.environ['API_KEY']
SECRET_KEY = os.environ['SECRET_KEY']

trading_client = TradingClient(API_KEY,SECRET_KEY, paper=True)

async def place_market_order(ticker, order_type):
    free_cash_perc = 0.1
    try:
        hu = hus
        if order_type == 'buy':
            order_data = MarketOrderRequest(
                  symbol=ticker,
                  notional=round(float(trading_client.get_account().buying_power) * free_cash_perc,2),
                  side=OrderSide.BUY,
                  time_in_force='day')       
            return trading_client.submit_order(order_data=order_data) 
            
        elif order_type == 'short':
            order_data = MarketOrderRequest(
                  symbol=ticker,
                  notional=round(float(trading_client.get_account().buying_power) * free_cash_perc,2),
                  side=OrderSide.SELL,
                  time_in_force='day')       
            return trading_client.submit_order(order_data=order_data)      
            
        elif order_type=='close':
            return trading_client.close_position(ticker)
    except:
        pass


