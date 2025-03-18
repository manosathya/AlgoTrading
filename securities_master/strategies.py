import pandas as pd

config = {'mavg1': 5,
          'mavg2': 20,
          'm_window':8,
          'm_th': 0.1}

  
def mean_reverting_pairs(master,s1,s2, config=config, pair_trade=False):

    mavg1 = config['mavg1']
    mavg2= config['mavg2']
    m_window = config['m_window']
    m_th = config['m_th']
    
    stock_1, stock_2 = master.close[s1], master.close[s2]
    spread = stock_1 - stock_2
    
    spread_mavg5 = spread.rolling(window=mavg1, center=False).mean()
    spread_mavg20 = spread.rolling(window=mavg2, center=False).mean()
    std_20 = spread.rolling(window=mavg2, center=False).std()
    
    zscore_20_5 = (spread_mavg5 - spread_mavg20)/std_20
    
    rolling_momentum = zscore_20_5.diff().rolling(window=m_window, center=False).mean()
    
    signals = zscore_20_5.mask((zscore_20_5>-1) & (rolling_momentum>m_th) , 'buy')
    signals = signals.mask((zscore_20_5<1) & (rolling_momentum<-m_th) , 'sell')
    signals = signals[(signals=='buy')|(signals=='sell')]

    order_book = list(zip(signals.index, list(zip([s1]*len(signals), stock_1.loc[signals.index], signals.values))))

    
    if pair_trade:
        ob_s2 = list(zip([s2]*len(signals), stock_2.loc[signals.index].values, signals.map({'buy':'sell','sell':'buy'}).values))
        order_book.extend(list(zip(signals.index, ob_s2)))    
        
    return sorted(order_book, key=lambda x: x[0])


def mean_reverting_multi_group(master, s1, stock_group, mavg1=config['mavg1'], mavg2=config['mavg2'], m_window=config['m_window'], m_th=config['m_th']):
    stock_1 = master.close[s1]
    zscore_r = pd.DataFrame(columns=stock_group, index=stock_1.index)    
    
    for s2 in stock_group:
        spread = stock_1 - master.close[s2]
    
        spread_mavg1 = spread.rolling(window=mavg1, center=False).mean()
        spread_mavg2 = spread.rolling(window=mavg2, center=False).mean()
        std_r2 = spread.rolling(window=mavg2, center=False).std()
    
        zscore_r[s2] = (spread_mavg1 - spread_mavg2)/std_r2
        
    zscore_r_av = zscore_r.mean(axis=1)
    
    rolling_momentum = zscore_r_av.diff().rolling(window=m_window, center=False).mean()
    
    signals = zscore_r_av.mask((zscore_r_av>-1) & (rolling_momentum>m_th) , 'buy')
    signals = signals.mask((zscore_r_av<1) & (rolling_momentum<-m_th) , 'sell')
    signals = signals[(signals=='buy')|(signals=='sell')]

    order_book = list(zip(signals.index, zip([s1]*len(signals), stock_1.loc[signals.index], signals.values)))
    
    return order_book