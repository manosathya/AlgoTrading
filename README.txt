configs/
----------------------
    publisher_configs.yaml
    ----------------------
        - Contains configs of ticker groups for the publisher to pull from alpaca and publish to redis
        
    strategy_configs.yaml
    ----------------------
        - Contains stratgy configs: name of strategy, which redis stream to act on and entry/exit values, period over which to calculate etc.


alpaca_publisher.py
----------------------
    - Loads config list from publisher_configs.yaml
    - Select ticker group from publisher config to pull from alpaca
    - Input stream key to push to on redis (alpaca, test)

test_publisher.ipynb
----------------------
    - Pushes fake OHLC data for a given group of tickers to the test stream on redis

