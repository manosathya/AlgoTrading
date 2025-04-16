from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
import os

import getpass
import psycopg
import json

client = TradingClient(os.getenv("API_KEY"), os.getenv("SECRET_KEY"))
assets = client.get_all_assets(GetAssetsRequest(status='active'))

def parse_alpaca_assets(assets):
    parsed = []

    for asset in assets:
        row = (
            str(asset.id),  # UUID as string
            asset.symbol,
            asset.name,
            asset.asset_class.value if asset.asset_class else None,
            asset.exchange.value if asset.exchange else None,
            asset.tradable,
            asset.marginable,
            asset.shortable,
            asset.easy_to_borrow,
            asset.fractionable,
            asset.maintenance_margin_requirement,
            asset.min_order_size,
            asset.min_trade_increment,
            asset.price_increment,
            json.dumps(asset.attributes)
        )
        parsed.append(row)

    return parsed
    
def insert_assets(symbols):
    """
    Insert the S&P500 symbols into the MySQL database.
    """
    # Connect to the Postgres
    con = psycopg.connect(f"dbname='securities_master' user='postgres' host='localhost' password={getpass.getpass('dbpassword')}")
    # Create the insert strings
    column_str = """
    id, symbol, name, asset_class, exchange,
    tradable, marginable, shortable, easy_to_borrow, fractionable,
    maintenance_margin_requirement, min_order_size, min_trade_increment,
    price_increment, attributes
    """.replace("\n", "").replace("  ", "").strip()
    
    insert_str = ("%s, " * len(column_str.split(',')))[:-2]    
    final_str = f"INSERT INTO assets ({column_str}) VALUES ({insert_str})"

    # Using the MySQL connection, carry out
    # an INSERT INTO for every symbol
    with con:
        cur = con.cursor()
        cur.execute("TRUNCATE TABLE assets;")
        cur.executemany(final_str, symbols)

parsed_assets = parse_alpaca_assets(assets)
insert_assets(parsed_assets)
print(f"{len(parsed_assets)} assets were successfully added.")