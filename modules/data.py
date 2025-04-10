import pandas as pd
import numpy as np
import yaml
from datetime import datetime, timedelta

def load_yaml_config(file_path):
    """Load the configuration file."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_historical_data(days, ticker_num, strategy_config):
    try:
        historical_data = pd.read_pickle(f'../../test_hist_data/histdata_{days}D_{ticker_num}T_SHFL.pkl')
        print(f'Loaded df: {days}D/{ticker_num}T, {len(historical_data)} rows')
    except:       
        tickers =  strategy_config['tickers'][0:ticker_num]
        
        start_time = datetime.now() - timedelta(days=100)  
        end_time = datetime.now()
        
        historical_data = generate_historical_data(tickers, start_time, end_time)
        historical_data = historical_data.sample(frac=1)
        historical_data.to_pickle(f'../../test_hist_data/histdata_{days}D_{ticker_num}T_SHFL.pkl')
        print(f'New df: {days}D_{ticker_num}T, {len(historical_data)} rows')
    return historical_data
    
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