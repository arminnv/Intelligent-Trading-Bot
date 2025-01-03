import json
import requests
from datetime import datetime, timezone, timedelta
import pandas as pd
# from kucoin.client import Client


def get_bybit_bars(symbol, interval, start_bars, end_bars, time):
    market = symbol + 'USDT'

    url = "https://api.bybit.com/public/linear/kline?"

    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    if time == 0:
        time = utc_time

    start_datetime = time - timedelta(minutes=start_bars * interval)
    end_datetime = time - timedelta(minutes=end_bars * interval)
    # print(utc_time)
    # print(utc_timestamp)
    # print(datetime.utcfromtimestamp(utc_time.timestamp()))

    startTime = str(int(start_datetime.timestamp()))
    endTime = str(int(end_datetime.timestamp()))

    req_params = {"symbol": market, 'interval': interval, 'from': startTime, 'to': endTime}

    df = pd.DataFrame(json.loads(requests.get(url, params=req_params).text)['result'])

    if len(df.index) == 0:
        return None

    df.index = [datetime.utcfromtimestamp(x) for x in df.open_time]

    return df


"""
def get_kucoin_bars(symbol, interval, start_bars, end_bars):
    market = symbol + '-USDT'

    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    start_datetime = utc_time - timedelta(minutes=start_bars * interval)
    end_datetime = utc_time - timedelta(minutes=end_bars * interval)

    startTime = int(start_datetime.timestamp())
    endTime = int(end_datetime.timestamp())

    df = pd.DataFrame(columns=['open_time', 'open', 'high', 'low', 'close'])
    client = Client("", "", "")

    kline_res = client.get_kline_data(market, str(interval) + 'min', startTime, endTime)

    for i in range(1, len(kline_res)):
        a = [kline_res[i][0], kline_res[i][1], kline_res[i][3], kline_res[i][4], kline_res[i][2]]
        df.loc[len(df)] = a

    if len(df.index) == 0:
        return None
    df.index = [datetime.utcfromtimestamp(int(x)) for x in df.open_time]
    return df
"""
