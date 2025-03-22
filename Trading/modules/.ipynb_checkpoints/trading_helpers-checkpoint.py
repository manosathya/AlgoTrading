import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide

trading_client = TradingClient(os.environ['API_KEY'],os.environ['SECRET_KEY'], paper=True)

def place_market_order(ticker, order_type, val=None):
    try:
        if order_type == 'long':
            order_data = MarketOrderRequest(
                  symbol=ticker,
                  notional=val,
                  side=OrderSide.BUY,
                  time_in_force='day')       
            trading_client.submit_order(order_data=order_data) 
            return order_type
            
        elif order_type == 'short':
            order_data = MarketOrderRequest(
                  symbol=ticker,
                  qty=val,
                  side=OrderSide.SELL,
                  time_in_force='day')       
            trading_client.submit_order(order_data=order_data) 
            return order_type
            
        elif order_type=='close':
            trading_client.close_position(ticker)
            return None
    except:
        print('pass')

def place_market_order_test(ticker, order_type, val=None):
    try:
        if order_type == 'long':
            order_data = MarketOrderRequest(
                  symbol=ticker,
                  notional=val,
                  side=OrderSide.BUY,
                  time_in_force='day')       
            return order_type
            
        elif order_type == 'short':
            order_data = MarketOrderRequest(
                  symbol=ticker,
                  qty=val,
                  side=OrderSide.SELL,
                  time_in_force='day')       
            return order_type
            
        elif order_type=='close':
            return None
    except:
        print('pass')

