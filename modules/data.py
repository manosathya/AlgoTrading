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