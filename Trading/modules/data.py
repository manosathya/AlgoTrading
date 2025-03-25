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

def wilder_smoothing_rsi(close_prices: np.ndarray, period: int = 15) -> np.ndarray:
    """
    Vectorized RSI computation for an entire dataset.
    
    Args:
        close_prices (np.ndarray): Array of closing prices.
        period (int): RSI period (default: 14).

    Returns:
        np.ndarray: RSI values for each row in the dataset.
    """
    if len(close_prices) < period:
        return np.full(len(close_prices), np.nan)  # Return NaN for all if not enough data

    # Compute price changes
    delta = np.diff(close_prices, prepend=close_prices[0])  # Ensure same length
    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)

    # Initial average gain/loss using simple mean
    avg_gain = np.convolve(gains, np.ones(period) / period, mode='valid')
    avg_loss = np.convolve(losses, np.ones(period) / period, mode='valid')

    # Expand to match the original array size with NaN for the first period-1 values
    avg_gain = np.concatenate((np.full(period-1, np.nan), avg_gain))
    avg_loss = np.concatenate((np.full(period-1, np.nan), avg_loss))

    # Apply Wilder's smoothing for each value after the initial period
    for i in range(period, len(close_prices)):
        avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gains[i]) / period
        avg_loss[i] = (avg_loss[i - 1] * (period - 1) + losses[i]) / period

    # Prevent division by zero
    avg_loss[avg_loss == 0] = 1e-10  # Prevent division by zero
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi
    
