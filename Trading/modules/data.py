import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Function to generate a fake historical dataframe
def generate_historical_data(tickers, start_time, end_time, freq='min'):
    timestamps = pd.date_range(start=start_time, end=end_time, freq=freq)  # Minute data
    data = []
    if isinstance(tickers, str):
        tickers = [tickers]
    for ticker in tickers:
        close_price = np.random.uniform(100, 500)  # Start with a random price

        for timestamp in timestamps:
            # Add volatility by using a random walk with large fluctuations
            price_change = np.random.uniform(-10, 10)  # Increase range for volatility
            close_price = max(50, close_price + price_change)  # Ensure price remains >50

            open_price = close_price + np.random.uniform(-5, 5)
            high_price = max(open_price, close_price) + np.random.uniform(0, 5)
            low_price = min(open_price, close_price) - np.random.uniform(0, 5)

            data.append({
                'timestamp': timestamp,
                'ticker': ticker,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2)
            })

    # Create DataFrame
    df = pd.DataFrame(data)
    return df

def wilder_smoothing_rsi(close_prices: np.ndarray, period: int = 14) -> float:
    """
    Computes RSI exactly like pandas_ta.momentum.rsi().
    
    Args:
        close_prices (np.ndarray): Closing prices.
        period (int): RSI period (default: 14).

    Returns:
        float: RSI value exactly matching pandas_ta.
    """
    if len(close_prices) < period + 1:
        return np.nan  # Not enough data

    # Compute price changes
    delta = np.diff(close_prices)
    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)

    # Wilder’s smoothing: Initial avg gain/loss is the mean of first 'period' values
    avg_gain = np.zeros_like(gains, dtype=np.float64)
    avg_loss = np.zeros_like(losses, dtype=np.float64)

    avg_gain[period - 1] = np.mean(gains[:period])
    avg_loss[period - 1] = np.mean(losses[:period])

    alpha = 1 / period  # Matches pandas_ta

    # Compute smoothed values (Wilder's method)
    for i in range(period, len(gains)):
        avg_gain[i] = (1 - alpha) * avg_gain[i - 1] + alpha * gains[i]
        avg_loss[i] = (1 - alpha) * avg_loss[i - 1] + alpha * losses[i]

    # Prevent division by zero
    avg_loss[avg_loss == 0] = 1e-10  

    rs = avg_gain[-1] / avg_loss[-1]
    rsi = 100 - (100 / (1 + rs))

    return rsi