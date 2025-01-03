from datetime import datetime, timezone

import calculator
import config
from strategy import Strategy
from indicators2 import sma, swing, adx, stoch, dc

interval = config.interval

TARGET_BARS = 50

ma1_period = 100
ma2_period = 60
ma3_period = 30
dc_period = 60
k_period = 14
k_smooth = 3
d_smooth = 3
adx_period = 14
trend_level = 20
swing_period = 7

stoch_high = 80
stoch_low = 20

cross_gap = 20


class STOCH(Strategy):
    def __init__(self):
        self.name = 'stoch'

        self.interval = interval
        self.side = 0
        self.trend = 0
        self.up = []
        self.down = []
        self.crossed = True
        self.up_crossed = True
        self.down_crossed = True
        self.first = True
        self.over_bs = 0
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        self.up, self.down = swing(ohlc, swing_period)
        ohlc['h'], mid, ohlc['l'] = dc(ohlc, period=dc_period)
        ohlc['ma1'] = sma(ohlc['close'], period=ma1_period)
        ohlc['ma2'] = sma(ohlc['close'], period=ma2_period)
        ohlc['ma3'] = sma(ohlc['close'], period=ma3_period)
        ohlc['adx'], ohlc['di+'], ohlc['di-'] = adx(ohlc, period=adx_period)
        ohlc['k'], ohlc['d'] = stoch(ohlc, k_period=k_period, smooth=k_smooth,
                                     d_period=d_smooth)

    def check(self, ohlc, time, test):
        side = self.side
        i = ohlc.index.get_loc(time)
        if (ohlc['close'][time] - ohlc['open'][time]) * side > 0:
            if test:
                return True
            dt = datetime.now(timezone.utc)
            utc_time = str(dt.replace(tzinfo=timezone.utc))
            if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 2:
                return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close']
        open = ohlc['open']
        low = ohlc['low']
        high = ohlc['high']
        ma1 = ohlc['ma1']
        ma2 = ohlc['ma2']
        ma3 = ohlc['ma3']
        k = ohlc['k']
        d = ohlc['d']
        dip = ohlc['di+']
        din = ohlc['di-']
        adx = ohlc['adx']
        up = self.up
        down = self.down
        up_trend = False
        down_trend = False

        if down[-3][-1] < down[-2][-1] < down[-1][-1]:
            up_trend = True
        if up[-3][-1] > up[-2][-1] > up[-1][-1]:
            down_trend = True

        if close[i] > ma1[i] and ma3[i] > ma1[i] and adx[i] >= trend_level:
            self.trend = 1
        elif close[i] < ma1[i] and ma3[i] < ma1[i] and adx[i] >= trend_level:
            self.trend = -1
        else:
            self.trend = 0

        if ma2[i] > ma1[i] and ma2[i - 1] <= ma1[i - 1]:
            self.down_crossed = False
        elif ma2[i] < ma1[i] and ma2[i - 1] >= ma1[i - 1]:
            self.up_crossed = False

        if self.trend == 1 and not self.up_crossed:
            if close[i] > open[i] and k[i] > d[i] and k[i - 1] <= d[i - 1] and k[i - 1] < stoch_low\
                    and check_target(ohlc, 1, config.STOP_BARS, config.TARGET_BARS, config.rr_min):
                self.message = 'buy detected'
                self.side = 1
                return 1
            elif close[i - 1] > open[i - 1] and k[i - 1] > d[i - 1] and k[i - 2] <= d[i - 2] and k[i - 2] < stoch_low\
                    and check_target(ohlc.iloc[:-1], 1, config.STOP_BARS, config.TARGET_BARS, config.rr_min):
                self.up_crossed = True


        elif self.trend == -1 and not self.down_crossed:
            if close[i] < open[i] and k[i] < d[i] and k[i - 1] >= d[i - 1] and k[i - 1] > stoch_high\
                    and check_target(ohlc, -1, config.STOP_BARS, config.TARGET_BARS, config.rr_min):
                self.message = 'sell detected'
                self.side = -1
                return -1
            elif close[i - 1] < open[i - 1] and k[i - 1] < d[i - 1] and k[i - 2] >= d[i - 2] and k[i - 2] > stoch_high\
                    and check_target(ohlc.iloc[:-1], -1, config.STOP_BARS, config.TARGET_BARS, config.rr_min):
                self.down_crossed = True

        if self.first:
            self.first = False
            if ma2[i] > ma1[i]:
                self.down_crossed = False
            else:
                self.up_crossed = False

        self.message = 'declined'
        self.side = 0
        return 0

    def check_tail(self, side):
        up = self.up
        down = self.down
        if side == 1:
            if up[-1][0] < down[-1][0]:
                if up[-2][-1] <= up[-1][-1]:
                    return True
            elif up[-3][-1] <= up[-2][-1]:
                return True
        else:
            if down[-1][0] < up[-1][0]:
                if down[-2][-1] >= down[-1][-1]:
                    return True
            elif down[-3][-1] >= down[-2][-1]:
                return True
        return False

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]
        high = ohlc['high']
        low = ohlc['low']

        if ohlc['close'][-1] < ohlc['open'][-1]:
            #stop_loss0 = high[-1]
            stop_loss0 = max(high[-stop_bars:])
            target = min(low[-target_bars:])
        else:
            #stop_loss0 = low[-1]
            stop_loss0 = min(low[-stop_bars:])
            target = max(high[-target_bars:])

        #stop_loss0 = ohlc['ma1'][-1]
        stop_loss = stop_loss0
        stop_index = -1
        target_index = -1

        e = -(stop_loss0 / close - 1)
        e1 = -(stop_loss / close - 1)
        rr = round(abs((target / close - 1) / e1), 2)
        leverage, take_profit, rr1, rr2 = calculator.calculate_leverage(close, e, target)
        return round(leverage, 1), rr, round(e * 100, 2), stop_index + len(high) - stop_bars - 1 \
            , target_index + len(high) - target_bars - 1, stop_loss, target, stop_loss0


def check_target(ohlc, side, stop_bars, target_bars, rr_min):
    close = ohlc['close'][-1]
    high = ohlc['high']
    low = ohlc['low']
    if side == -1:
        #stop_loss = max(high[-stop_bars:])
        target = min(low[-target_bars:])
    else:
        #stop_loss = min(low[-stop_bars:])
        target = max(high[-target_bars:])
    stop_loss = ohlc['ma1'][-1]
    e = -(stop_loss / close - 1)
    rr = abs((target / close - 1) / e)
    if rr >= rr_min:
        return True
    else:
        return False


def extremum(a, st):
    index = 0
    ext = 0
    if st == 'max':
        max = a[0]
        for i in range(len(a)):
            if a[i] >= max:
                max = a[i]
                index = i
        ext = max
    elif st == 'min':
        min = a[0]
        for i in range(len(a)):
            if a[i] <= min:
                min = a[i]
                index = i
        ext = min
    return ext, index


def get_previous_swing(side, a):
    if side == 1:
        for i in range(len(a) - 3, 2, -1):
            if a[i] <= min(a[i - 1], a[i - 2], a[i + 1], a[i + 2]):
                return i, a[i]
    elif side == -1:
        for i in range(len(a) - 3, 2, -1):
            if a[i] >= max(a[i - 1], a[i - 2], a[i + 1], a[i + 2]):
                return i, a[i]
    else:
        return 0, a[0]


def check_ma_cross(ohlc, side):
    if side == 1:
        x = ohlc['low'][-10:]
    else:
        x = ohlc['high'][-10:]
    ma = ohlc['ma1'][-10:]
    for i in range(len(x)):
        if (x[i] - ma[i]) * side < 0:
            return False
    return True


def check_cross(ohlc, side):
    n = 0
    max_crosses = 5
    m = sum(ohlc['close'][-20:]) / len(ohlc['close'][-20:])
    for i in range(3, 1 + cross_gap):
        if (ohlc['close'][-i] - m) * side < 0:
            side *= -1
            n += 1
            if n > max_crosses:
                return False
    return True

"""
ma 30 < ma 50 , close cross ma 50 
"""









