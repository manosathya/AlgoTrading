from database_query import get_price_data

def create_portfolio(start_money=1000, max_trade_perc=0.05,t_cost=0):
    portfolio = {'money':start_money, 'max_initial_trade':start_money*max_trade_perc, 'max_trade_perc':max_trade_perc,
                 'stocks':{}, 'b_count':0, 's_count':0, 
                 'val_hist':[start_money], 
                 't_cost':t_cost}
    return portfolio
    
def trade(order, portfolio):
    """
    order = [ticker, price, buy/sell] 
    portfolio:   dict --> {start_val: float, free_cash:float, stock: no.shares}
    """
    
    ticker, stock_price, signal = order[0], order[1], order[2]
    
    if (signal=='buy') & (portfolio['money'] != 0):
        
        trade_amount = min(max(portfolio['max_initial_trade'], portfolio['money']*portfolio['max_trade_perc']), portfolio['money'])
        shares_to_buy = trade_amount/stock_price
        
        portfolio['stocks'][ticker] = portfolio['stocks'].get(ticker, 0) + shares_to_buy
        portfolio['money'] -= (trade_amount + portfolio['t_cost'])

        portfolio['b_count'] += 1
        
    elif signal=='sell':        
        owned_shares = portfolio['stocks'].get(ticker, 0)

        if owned_shares != 0:
            portfolio['money']+= ((owned_shares * stock_price) - portfolio['t_cost'])
            portfolio['stocks'][ticker] = 0
            portfolio['s_count'] += 1
            
    return portfolio

def portfolio_value(portfolio, final_day_data):
    val = {'breakdown':{}}
    val['Total'] = portfolio['money']
    val['breakdown']['money'] = portfolio['money']
    for key in portfolio['stocks']:
        stock_value = portfolio['stocks'][key] * final_day_data[key]
        val['Total'] +=  stock_value
        val['breakdown'][key] = stock_value
    return val