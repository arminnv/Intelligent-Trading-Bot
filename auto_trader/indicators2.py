from ta.trend import EMAIndicator, MACD, sma_indicator, ADXIndicator
from ta.volatility import BollingerBands, KeltnerChannel, AverageTrueRange, DonchianChannel
from ta.momentum import StochasticOscillator, RSIIndicator


def swing(ohlc, period):
    ohlc['lin'] = [None] * len(ohlc['high'])
    up = []
    down = []
    last_index = 0
    for i in range(period, len(ohlc['close']) - 2 * period):
        #ohlc['lin'][i] = last_index
        if max(ohlc['high'][i - period: i + 2 * period]) == ohlc['high'][i]:
            if len(up) > 0:
                if ohlc['high'][i] != up[-1][1]:
                    up.append([i, ohlc['high'][i]])
                    last_index = i
            else:
                up.append([i, ohlc['high'][i]])
                last_index = i
        if min(ohlc['low'][i - period: i + 2 * period]) == ohlc['low'][i]:
            if len(down) > 0:
                if ohlc['low'][i] != down[-1][1]:
                    down.append([i, ohlc['low'][i]])
                    last_index = i
            else:
                down.append([i, ohlc['low'][i]])
                last_index = i
    for i in range(len(ohlc['close']) - 2 * period, len(ohlc['close'])):
        #ohlc['lin'][i] = last_index
        if max(ohlc['high'][i - period:]) == ohlc['high'][i]:
            if len(up) > 0:
                if ohlc['high'][i] != up[-1][1]:
                    up.append([i, ohlc['high'][i]])
                    last_index = i
            else:
                up.append([i, ohlc['high'][i]])
                last_index = i
        if min(ohlc['low'][i - period:]) == ohlc['low'][i]:
            if len(down) > 0:
                if ohlc['low'][i] != down[-1][1]:
                    down.append([i, ohlc['low'][i]])
                    last_index = i
            else:
                down.append([i, ohlc['low'][i]])
                last_index = i
    return up, down


def swing2(ohlc, period):
    up = []
    down = []
    for i in range(period, len(ohlc['close']) - 2 * period):
        if max(ohlc['high'][i - period: i + 2 * period]) == ohlc['high'][i]:
            if len(up) > 0:
                if ohlc['high'][i] != up[-1][1]:
                    up.append([i, ohlc['high'][i]])
            else:
                up.append([i, ohlc['high'][i]])
        if min(ohlc['low'][i - period: i + 2 * period]) == ohlc['low'][i]:
            if len(down) > 0:
                if ohlc['down'][i] != down[-1][1]:
                    down.append([i, ohlc['low'][i]])
            else:
                down.append([i, ohlc['low'][i]])
    for i in range(len(ohlc['close']) - 2 * period, len(ohlc['close']) - period):
        if max(ohlc['high'][i - period: -period]) == ohlc['high'][i]:
            if len(up) > 0:
                if ohlc['high'][i] != up[-1][1]:
                    up.append([i, ohlc['high'][i]])
            else:
                up.append([i, ohlc['high'][i]])
        if min(ohlc['low'][i - period: -period]) == ohlc['low'][i]:
            if len(down) > 0:
                if ohlc['down'][i] != down[-1][1]:
                    down.append([i, ohlc['low'][i]])
            else:
                down.append([i, ohlc['low'][i]])
    return up, down


def sma(close, period):
    return sma_indicator(close=close, window=period, fillna=False)


def ema(ohlc, period):
    return EMAIndicator(close=ohlc['close'], window=period, fillna=False).ema_indicator()


def adx(ohlc, period):
    adx_indicator = ADXIndicator(ohlc['high'], ohlc['low'], ohlc['close'], period, fillna=False)
    return adx_indicator.adx(), adx_indicator.adx_pos(), adx_indicator.adx_neg()


def rsi(ohlc, period):
    return RSIIndicator(close=ohlc['close'], window=period, fillna=False).rsi()


def bb(ohlc, period):
    indicator_bb = BollingerBands(close=ohlc['close'], window=period, window_dev=1)
    # df['bb_bbm'] = indicator_bb.bollinger_mavg()
    return indicator_bb.bollinger_hband(), indicator_bb.bollinger_lband()


def dc(ohlc, period):
    dc = DonchianChannel(high=ohlc['high'], low=ohlc['low'], close=ohlc['close'], window=period, fillna=False)
    return dc.donchian_channel_hband(), dc.donchian_channel_mband(), dc.donchian_channel_lband()


def stoch(ohlc, k_period, d_period, smooth):
    """
    # Adds a "n_high" column with max value of previous 14 periods
    high = ohlc['high'].rolling(k_period).max()
    # Adds an "n_low" column with min value of previous 14 periods
    low = ohlc['low'].rolling(k_period).min()
    # Uses the min/max values to calculate the %k (as a percentage)
    k = (ohlc['close'] - low) * 100 / (high - low)
    k = k.rolling(smooth).mean()
    # Uses the %k to calculates a SMA over the past 3 values of %k
    d = k.rolling(d_period).mean()
    """
    # a = ohlc
    # if a[-1] is not None:
    #    ohlc = ohlc.tail(max(k_period, d_period, smooth))

    indicator_stoch = StochasticOscillator(high=ohlc['high'], low=ohlc['low'], close=ohlc['close'],
                                           window=k_period, smooth_window=1, fillna=False)
    k = indicator_stoch.stoch().rolling(smooth).mean()
    d = k.rolling(d_period).mean()
    # if a[-1] is not None:
    #    a['k'][-1] = k[-1]
    #    a['d'][-1] = d[-1]
    #    return a['k'], a['d']
    return k, d


def kc1(ohlc, period):
    # period = 20
    indicator_kc = KeltnerChannel(high=ohlc['high'], low=ohlc['low'], close=ohlc['close'],
                                  window=period, window_atr=10, fillna=False, original_version=False)
    return indicator_kc.keltner_channel_hband(), indicator_kc.keltner_channel_lband()


def atr(ohlc, period):
    indicator_atr = AverageTrueRange(high=ohlc['high'], low=ohlc['low'], close=ohlc['close'], window=period,
                                     fillna=False)
    return indicator_atr.average_true_range()


def macd(ohlc, fast_period, slow_period):
    indicator_macd = MACD(close=ohlc['close'], window_slow=slow_period, window_fast=fast_period)
    return indicator_macd.macd_diff()


def kc(ohlc, period, atr_period, multiplier):
    kcm = EMAIndicator(close=ohlc['close'], window=period, fillna=False).ema_indicator()
    kc_atr = atr(ohlc, atr_period)
    l = len(ohlc.index)
    kch = [None] * l
    kcl = [None] * l
    for i in range(l):
        if kcm[i] is None or kc_atr[i] is None:
            continue
        kch[i] = kcm[i] + multiplier * kc_atr[i]
        kcl[i] = kcm[i] - multiplier * kc_atr[i]
    return kch, kcm, kcl


def pin_bar(ohlc, index):
    i = index
    open = ohlc['open']
    high = ohlc['high']
    low = ohlc['low']
    close = ohlc['close']

    body = abs(close[i] - open[i])
    upshadow = open[i] > close[i] and (high[i] - open[i]) or (high[i] - close[i])
    downshadow = open[i] > close[i] and (close[i] - low[i]) or (open[i] - low[i])
    pinbar_h = close[i-1]>open[i-1] and (body[i-1]>body and (upshadow>0.5*body and (upshadow>2*downshadow and 1 or 0)or 0)or 0)or 0
    pinbar_l = open[i-1]>close[i-1] and (body[i-1]>body and (downshadow>0.5*body and (downshadow>2*upshadow and 1 or 0)or 0)or 0)or 0
    if pinbar_l == 1:
        return 1
    elif pinbar_h == 1:
        return -1
    else:
        return 0


def hammer(ohlc):
    high = ohlc['high'][-1]
    low = ohlc['low'][-1]
    open = ohlc['open'][-1]
    close = ohlc['close'][-1]

    shadow_h = high - low
    body_h = abs(open - close)
    bodyMid_h = 0.5 * (open + close) - low

    shadow = high - low
    body = abs(open - close)
    bodyMid = 0.5 * (open + close) - low
    bodyRed = open > close and body > (0.3 * shadow)
    bodyGreen = close > open and body > (0.3 * shadow)

    bodyTop = bodyMid_h > (0.7 * shadow_h)
    bodyBottom = bodyMid_h < (0.3 * shadow_h)
    hammerShape = body_h < (0.5 * shadow_h)

    if hammerShape and (bodyTop or bodyBottom):
        if bodyGreen:
            return 1
        elif bodyRed:
            return -1
    return 0


"""
hangingMan = bodyRed and hammerShape and bodyTop ? high_h: na
hammer = bodyGreen and hammerShape and bodyTop ? high_h: na

shootingStar = bodyRed and hammerShape and bodyBottom ? low_h: na
invertedHammer = bodyGreen and hammerShape and bodyBottom ? low_h: na
"""

