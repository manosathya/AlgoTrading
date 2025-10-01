A trading workflow, to automatically execute trading strategies.

    - Pulls data from alpaca API
    - Publishes data to redis
    - Strategy side pulls data from redis and executes order
    - Monitor trades in terminal, alpaca dashboard, or via the dash application


#####################################
              redis
#####################################

configs:publisher
----------------------
Changes when either publisher script is run

    - Tickers : List of tickers currently being retrieved and published to redis
    - Status  : inactive/active   - current status of publisher
    - stream  : The redis stream that is currrently being published to

configs:consumer
----------------------
Changes when either strategy script is run

    - Status  : inactive/active   - current status of publisher


#####################################
            configs/
#####################################

publisher_configs.yaml
----------------------
    - Contains configs of ticker groups for the publisher to pull from alpaca and publish to redis
    
strategy_configs.yaml
----------------------
    - Contains stratgy configs: name of strategy, which redis stream to act on and entry/exit values, period over which to calculate etc.


#####################################
            publishers
#####################################


alpaca_publisher.py
----------------------
    - Loads config list from publisher_configs.yaml
    - Select ticker group from publisher config to pull from alpaca
    - Input stream key to push to on redis (alpaca, test)

test_publisher.ipynb
----------------------
    - Pushes fake OHLC data for a given group of tickers to the test stream on redis



#####################################
         execute strategy
#####################################

run_strats.py
----------------------
    - Runs a given strategy using flags --strategy, --mode (paper, backtest or test), --submit_order (bool), --plot (dash, jupyter, None)
    - mode flag: 
        - paper loads alpaca positions, reads alpaca redis stream, only executes orders if --submit_order passed
        - test loads empty positions, reads test redis stream, overwrites --submit_order flag to False.


strategy_consumer.ipynb
----------------------
    - As above, only in Jupyter