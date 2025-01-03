import traceback
import pandas as pd
from datetime import timezone, datetime, timedelta
import matplotlib.dates as mpl_dates
from exchanges import get_bybit_bars

bars_in_chart = 200


def get_last_bar(ohlc, symbol, interval):
    try:

        dt = datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        if utc_time > ohlc.index[-1].replace(tzinfo=timezone.utc) + timedelta(minutes=interval):
            t = ohlc.index[-1].replace(tzinfo=timezone.utc) + timedelta(minutes=interval)

            df = get_bybit_bars(symbol, interval, start_bars=1, end_bars=-1, time=t)
            last_two = df.loc[:, ['open_time', 'open', 'high', 'low', 'close']]
            last_two['open_time'] = pd.to_datetime(last_two['open_time'], unit='s')
            last_two['open_time'] = last_two['open_time'].apply(mpl_dates.date2num)
            #print(last_two.index[0], last_two.index[-1])
            if last_two.index[-1] != ohlc.index[-1] and last_two.index[0] == ohlc.index[-1]:
                distance = ohlc.loc[ohlc.index[-1], "distance"]
                ohlc = ohlc.drop([ohlc.index[-1], ohlc.index[0]])
                ohlc = ohlc.append(last_two)
                ohlc.loc[ohlc.index[-2], "distance"] = distance
            return ohlc

        else:
            df = get_bybit_bars(symbol, interval, start_bars=1, end_bars=0, time=0)
            ohlc_end = df.loc[:, ['open_time', 'open', 'high', 'low', 'close']]
            ohlc_end['open_time'] = pd.to_datetime(ohlc_end['open_time'], unit='s')
            ohlc_end['open_time'] = ohlc_end['open_time'].apply(mpl_dates.date2num)

            i = ohlc.index[-1]
            ohlc.loc[i, 'close'] = ohlc_end['close'][-1]
            ohlc.loc[i, 'high'] = ohlc_end['high'][-1]
            ohlc.loc[i, 'low'] = ohlc_end['low'][-1]
            return ohlc
    except Exception as err:
        traceback.print_exc()

        return None


def primary_values(symbol, interval):
    df = get_bybit_bars(symbol, interval, start_bars=bars_in_chart, end_bars=0, time=0)

    ohlc = df.loc[:, ['open_time', 'open', 'high', 'low', 'close']]
    ohlc['open_time'] = pd.to_datetime(ohlc['open_time'], unit='s')
    ohlc['open_time'] = ohlc['open_time'].apply(mpl_dates.date2num)
    a = [None] * len(ohlc['high'])
    ohlc['up'] = a
    ohlc['down'] = a
    ohlc['mid'] = a
    ohlc['ma'] = a
    ohlc['ma1'] = a
    ohlc['ma2'] = a
    ohlc['ma3'] = a
    ohlc['ma4'] = a
    ohlc['ma5'] = a
    ohlc['rsi'] = a
    ohlc['sma'] = a
    ohlc['k'] = a
    ohlc['d'] = a
    ohlc['adx'] = a
    ohlc['di+'] = a
    ohlc['di-'] = a
    ohlc['h'] = a
    ohlc['l'] = a
    ohlc['lin'] = a
    ohlc['kcl'] = a
    ohlc['kch'] = a
    ohlc['hist'] = a

    ohlc = ohlc.astype(float)

    return ohlc


def check_index(ohlc, update, interval):
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    t1 = utc_time - timedelta(minutes=2 * interval)
    t2 = utc_time + timedelta(minutes=2 * interval)
    t = ohlc.index[-1].replace(tzinfo=timezone.utc)
    if not t1 <= t <= t2:
        print(t, t1)
        return False
    else:
        return True


def crop(t):
    return str(t)[:16]
