from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide

def place_market_order(order_data, submit_orders, trading_client):
    ticker, signal, position_size = order_data['ticker'], order_data['signal'], order_data['position_size']
    try:
        if signal=='close':
            if submit_orders:
                trading_client.close_position(ticker)
            return None
       
        kwargs = {"symbol": ticker,
                  "side": OrderSide.BUY if signal == 'long' else OrderSide.SELL,
                  "time_in_force": 'day'}
        
        if signal == 'long':
            kwargs["notional"] = position_size
        elif signal == 'short':
            kwargs["qty"] = position_size
            
        if submit_orders:    
            trading_client.submit_order(order_data=MarketOrderRequest(**kwargs)) 
            
        return signal
        
    except Exception as e:
        print(f"Order error for {ticker}: {e}")

async def get_position_size(order_data, trading_client):    
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
