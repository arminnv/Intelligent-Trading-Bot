import talib
from talib import STOCH
from talib import EMA
from talib.abstract import *

def adx(ohlc, period):
     adx = talib.ADX(ohlc['high'], ohlc['low'], ohlc['close'], timeperiod=period)
     pdi = talib.PLUS_DI(ohlc['high'], ohlc['low'], ohlc['close'], timeperiod=period)
     mdi = talib.MINUS_DI(ohlc['high'], ohlc['low'], ohlc['close'], timeperiod=period)
     return adx, pdi, mdi


def stoch(ohlc, period):
    inputs = {
        'high': ohlc['high'],
        'low': ohlc['low'],
        'close': ohlc['close'],
    }
    slowk, slowd = STOCH(inputs, period, 3, 0, 3, 0)
    return slowk, slowd,


def stochastic(ohlc, period):
    inputs = {
        'high': ohlc['high'],
        'low': ohlc['low'],
        'close': ohlc['close'],
    }
    slowk, slowd = STOCH(inputs, period, 3, 0, 3, 0)
    return slowk


def aroon(ohlc, period):
    return talib.AROON(ohlc['high'], ohlc['low'], timeperiod=period)


def macd(ohlc, period):
    macd, macdsignal, macdhist = talib.MACD(ohlc['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return macdhist


def ema(ohlc, period):
    return EMA(ohlc, timeperiod=period, price='close')


def rsi(ohlc, period):
    return talib.RSI(ohlc['close'], timeperiod=period)


def ma(ohlc, period):
    return talib.MA(ohlc['close'], timeperiod=period)


def bbands(ohlc, period):
    upper, middle, lower = talib.BBANDS(ohlc['close'].values, timeperiod=period, nbdevup=2, nbdevdn=2, matype=0)
    return upper, middle, lower
