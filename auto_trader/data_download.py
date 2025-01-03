import os

import pandas
import requests
import json
import pandas as pd
import datetime as dt
import matplotlib.dates as mpl_dates
from datetime import datetime, timedelta

from auto_trader.exchanges import get_bybit_bars


#df = pandas.DataFrame
#symbols = ['DOGE', 'ADA', 'ETH', 'BTC', 'XRP', 'XEM', 'EOS', 'DOT', 'XTZ', 'MATIC']
symbols = ['ADA', 'XRP']
symbols_dict = {}
#ohlc = {}


def download_symbol(symbol, interval, days):
    # today = datetime(2022, 11, 1)
    today = datetime(2022, 12, 11)
    today = datetime.today()
    time = today - timedelta(days=days)

    df = get_historical_data(symbol, interval, time, days)


    ohlc = df.loc[:, ['open_time', 'open', 'high', 'low', 'close']]
    ohlc['open_time'] = pd.to_datetime(ohlc['open_time'])
    ohlc['open_time'] = ohlc['open_time'].apply(mpl_dates.date2num)
    ohlc['maximum'] = [None] * len(df['high'])
    ohlc['minimum'] = [None] * len(df['high'])
    ohlc['stoch'] = [None] * len(df['high'])
    ohlc['check'] = [None] * len(df['high'])
    ohlc['stop'] = [None] * len(df['high'])
    ohlc['goal'] = [None] * len(df['high'])
    ohlc['cross'] = [None] * len(df['high'])
    ohlc['distance'] = [0] * len(df['high'])

    ohlc = ohlc.astype(float)
    return ohlc


def get_historical_data(symbol, interval, time, days):
    url = "https://api.bybit.com/public/linear/kline?"

    try:
        os.mkdir('data')
    except FileExistsError:
        pass

    try:
        os.mkdir('data/' + symbol)
    except FileExistsError:
        pass

    try:
        df = pd.DataFrame()
        file_name = 'data/' + symbol + '/' + str(time)[:10] + '.csv'
        file_name = 'data/ADA/2022-07-28.csv'
        #file_name = 'data.csv'
        df1 = pd.read_csv(file_name)
        df = df.append(df1)
        #print(df)
        #print("loaded")
    except:
        print('downloading')
        n = int(1440 * days / interval / 200)
        df = pd.DataFrame()
        for i in range(n):
            print(i)
            df1 = get_bybit_bars(symbol, interval, start_bars=(n-i)*200, end_bars=(n-i-1)*200, time=time)
            df = df.append(df1)

        file_name = 'data/' + symbol + '/' + str(time)[:10] + '.csv'
        df.to_csv(file_name, index=False)

    if len(df.index) == 0:
        return None
    df.index = [dt.datetime.fromtimestamp(x) for x in df.open_time]
    return df