import pandas as pd
import numpy as np
import yaml
from datetime import datetime, timedelta

def load_yaml_config(file_path):
    """Load the configuration file."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
    
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

def rsi_rolling(prices, period=14, prev_avg_gain=None, prev_avg_loss=None):
    prices = np.asarray(prices)
    delta = np.diff(prices, prepend=prices[0])  # Compute price changes
    
    gains = np.where(delta > 0, delta, 0)  # Positive changes
    losses = np.where(delta < 0, -delta, 0)  # Negative changes
    
    # Compute first average gain/loss over the first 14 differences
    if prev_avg_gain is None or prev_avg_loss is None:
        avg_gain = np.mean(gains[:period])  # First 14 gains
        avg_loss = np.mean(losses[:period])  # First 14 losses
    else:
        avg_gain, avg_loss = prev_avg_gain, prev_avg_loss  # Use previous values

    rsi_values = np.full_like(prices, np.nan, dtype=np.float64)  # Initialize RSI with NaNs

    for i in range(period, len(prices)):  # Start at index 14 (0-based)
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        rs = avg_gain / avg_loss if avg_loss != 0 else np.inf
        rsi_values[i] = 100 - (100 / (1 + rs))

    return rsi_values, avg_gain, avg_loss  # Return last avg gain/loss for consistency

def rsi_vectorized(prices, period=14, prev_avg_gain=None, prev_avg_loss=None):
    """
    Computes RSI using vectorized operations. Supports both rolling windows and full dataset calculations.

    Args:
        prices (np.ndarray): Array of closing prices.
        period (int): RSI period (default: 14).
        prev_avg_gain (float, optional): Previous window's avg gain (for rolling consistency).
        prev_avg_loss (float, optional): Previous window's avg loss (for rolling consistency).

    Returns:
        np.ndarray: RSI values with NaNs for the first (period - 1) entries.
        float: Last avg gain (for rolling window continuity).
        float: Last avg loss (for rolling window continuity).
    """
    prices = np.asarray(prices, dtype=np.float64)
    delta = np.diff(prices, prepend=prices[0])  # Compute price changes

    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)

    # Initialize RSI array with NaNs
    rsi_values = np.full_like(prices, np.nan, dtype=np.float64)

    if len(prices) < period:
        return rsi_values, None, None  # Not enough data to compute RSI

    # Compute initial average gain/loss using simple mean (first period)
    if prev_avg_gain is None or prev_avg_loss is None:
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
    else:
        avg_gain, avg_loss = prev_avg_gain, prev_avg_loss  # Use rolling values

    # Vectorized Wilder’s smoothing
    smoothing_factor = (period - 1) / period

    gain_window = gains[period:]  # Exclude first period
    loss_window = losses[period:]  # Exclude first period

    gain_factors = (1 - smoothing_factor) ** np.arange(len(gain_window))  # Decay factor
    loss_factors = (1 - smoothing_factor) ** np.arange(len(loss_window))  # Decay factor

    avg_gain_values = avg_gain * smoothing_factor + np.cumsum(gain_window * gain_factors)
    avg_loss_values = avg_loss * smoothing_factor + np.cumsum(loss_window * loss_factors)

    # Store values in RSI array
    avg_gain_series = np.concatenate(([avg_gain], avg_gain_values))
    avg_loss_series = np.concatenate(([avg_loss], avg_loss_values))

    avg_loss_series[avg_loss_series == 0] = np.inf  # Prevent division by zero
    rs = avg_gain_series / avg_loss_series
    rsi_values[period:] = 100 - (100 / (1 + rs))

    return rsi_values, avg_gain_series[-1], avg_loss_series[-1]  # Return last gains/losses for rolling consistency