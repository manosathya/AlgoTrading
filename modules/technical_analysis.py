import numpy as np

def rsi (close_prices, period=14):

    delta = np.diff(close_prices)
    
    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)
    
    avg_gain = np.convolve(gains, np.ones(period), mode='valid')/period
    avg_loss = np.convolve(losses, np.ones(period), mode='valid')/period
    
    avg_gain = np.concatenate((np.full(period, np.nan), avg_gain))
    avg_loss = np.concatenate((np.full(period, np.nan), avg_loss))
    
    
    avg_loss[avg_loss == 0] = np.inf
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi