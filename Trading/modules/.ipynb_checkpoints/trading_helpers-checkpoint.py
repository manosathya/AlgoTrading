import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide

trading_client = TradingClient(os.environ['API_KEY'],os.environ['SECRET_KEY'], paper=True)

def place_market_order(order_data):
    ticker, signal, position_size = order_data['ticker'], order_data['signal'], order_data['position_size']
    try:
        if signal == 'long':
            order = MarketOrderRequest(
                  symbol=ticker,
                  notional= position_size,
                  side=OrderSide.BUY,
                  time_in_force='day')       
            trading_client.submit_order(order_data=order) 
            return signal
            
        elif signal == 'short':
            order = MarketOrderRequest(
                  symbol=ticker,
                  qty=position_size,
                  side=OrderSide.SELL,
                  time_in_force='day')       
            trading_client.submit_order(order_data=order) 
            return signal
            
        elif signal=='close':
            trading_client.close_position(ticker)
            return None
    except:
        print('pass')

def place_market_order_test(order_data):
    ticker, signal, position_size = order_data['ticker'], order_data['signal'], order_data['position_size']
    try:
        if signal == 'long':
            order_data = MarketOrderRequest(
                  symbol=ticker,
                  notional=position_size,
                  side=OrderSide.BUY,
                  time_in_force='day')       
            return signal
            
        elif signal == 'short':
            order_data = MarketOrderRequest(
                  symbol=ticker,
                  qty=position_size,
                  side=OrderSide.SELL,
                  time_in_force='day')       
            return signal
            
        elif signal=='close':
            return None
    except:
        print('pass')

async def get_position_size(order_data):    
    signal, price = order_data['signal'], order_data['price']
    if signal =='close':
        return None
    buying_power = float(trading_client.get_account().buying_power)
    free_cash_perc = 0.1
    notional = round(buying_power * free_cash_perc,2)
    
    if signal == 'short':
        #Whole QTY for short posns
        return round(notional/price)
    else:
        return notional
