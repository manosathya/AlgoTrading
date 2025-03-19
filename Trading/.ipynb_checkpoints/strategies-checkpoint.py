import pandas as pd
from pandas_ta.momentum import rsi
from trading_helpers import place_market_order

import asyncio
import nest_asyncio
nest_asyncio.apply()


async def base_rsi(df, ticker):       
    OVERBOUGHT_THRESH = 85
    OVERSOLD_THRESH = 15

    # Need at least 14 bars to calculate RSI_14
    if len(df)<15:
        print('HOLD')
        return
        
    # Calculate Latest RSI
    rsi_value = rsi(df.close.iloc[-15:]).iloc[-1]
    #print(f"{ticker} RSI: {rsi_value}")
    # Trading Logic
    if rsi_value <= OVERSOLD_THRESH:
        # Buy when RSI is below the oversold threshold (enter long position)
        print('buy', ticker)
        await place_market_order(ticker,'buy')
    
    elif rsi_value >= OVERBOUGHT_THRESH:
        # Sell when RSI is above the overbought threshold (enter long position)
        try:
            await place_market_order(ticker, 'sell')
            print('sell', ticker)
        except:
            pass

    #await update_plot(ticker, rsi_value)