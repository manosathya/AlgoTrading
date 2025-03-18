import getpass
import psycopg

import pandas as pd

# Obtain a database connection
db_host = 'localhost'
db_user = 'postgres'
db_name = 'securities_master'
db_pass = getpass.getpass('db password')

def convert_symbol(symbol, symbol_type):
    
    con = psycopg.connect(f"host={db_host} user={db_user} password={db_pass} dbname={db_name}") 
    with con:
        cur = con.cursor()
        
        if symbol_type.lower() == 'id': 
            cur.execute(f"SELECT ticker FROM symbol WHERE id='{symbol}'")
        elif symbol_type.lower() == 'ticker': 
            cur.execute(f"SELECT id FROM symbol WHERE ticker='{symbol}'")
            
        idx = cur.fetchall()
    return idx[0][0]

def get_symbols_with_pd():
    con = psycopg.connect(f"host={db_host} user={db_user} password={db_pass} dbname={db_name}") 
    with con:
        cur = con.cursor()
        
        query = f"""SELECT DISTINCT ticker 
                    FROM price_data 
                    INNER JOIN symbol on symbol_id = symbol.id"""
        
        cur.execute(query)
        data = cur.fetchall()
    return [d[0] for d in data]
    
def get_price_data(tickers, date_range=False, df=True, ticker_name=True, default_cols = ['open','high','low','close'], add_cols=[], con=None):
    
    """
    tickers:        str/list of ticker(s)
    date_range:     yyyy-mm-dd hh:mm:ss or yyyy-mm-dd hh:mm:ss::yyyy-mm-dd hh:mm:ss
                    Can replace any of yyyy/mm/dd with * for selecting all. Time not required
    df:             Bool, return df
    ticker_name:    Bool, return ticker. 
                    If FALSE, return symbol_id
    add_cols:       List of cols to add from default column retrieval (date,o hlc)
    """

    #Select Columns to retrieve from Table
    identifier = 'symbol_id'
    if ticker_name: identifier = 'ticker'

        
    select_cols = ['price_date', identifier] + default_cols + add_cols

    
    #Select price dates/date range to retrieve if required
    date_query= f""
    if date_range:
        if '::' in date_range:
            start, end = date_range.split('::')
            date_query = f" AND '[{start},{end}]'::daterange @> price_date::date"
        else:
            if len(date_range.split(' '))>1:
                date_query += f" AND price_date='{date_range}'"
            else:       
                year, month, day = date_range.split('-')
                if year  != '*': date_query += f" AND EXTRACT(year from price_date)='{year}'"
                if month != '*': date_query += f" AND EXTRACT(month from price_date)='{month}'"
                if day   != '*': date_query += f" AND EXTRACT(day from price_date)='{day}'"

    #Create string of tickers to query the table with
    if isinstance(tickers,list):
        tickers = f"'{"','".join(tickers)}'"
    elif isinstance(tickers,str):
        tickers = f"'{tickers}'"
        

    #Connect and execute query
    if con is None:
        con = psycopg.connect(f"host={db_host} user={db_user} password={db_pass} dbname={db_name}") 
    with con:
        cur = con.cursor()
        
        query = f"""SELECT {','.join(select_cols)} 
                    FROM price_data 
                    INNER JOIN symbol on symbol_id = symbol.id 
                    WHERE ticker in ({tickers})""" + date_query
        
        cur.execute(query)
        data = cur.fetchall()

    #Create dataframe if required
    if df: 
        data = pd.DataFrame(data, columns=select_cols).sort_index()
        
    return data 