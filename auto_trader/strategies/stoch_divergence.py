from datetime import datetime, timezone
import calculator
import config
from strategy import Strategy
from indicators2 import rsi, sma, stoch, swing
from scipy.stats import linregress

interval = config.interval

ma1_period = 50
ma2_period = 40
swing_period = 7
k_period = 14
k_smooth = 3
d_smooth = 2
rsi_period = 14
sma_period = 14
reg_min = 0.98

stoch_high = 75
stoch_low = 25


class STDV(Strategy):
    def __init__(self):
        self.name = 'stdv'

        self.interval = interval
        self.funcs = {}
        self.side = 0
        self.over_bs = 0
        self.trend = 0
        self.up = []
        self.down = []
        self.reg = []
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        self.up, self.down = swing(ohlc, swing_period)
        ohlc['ma1'] = sma(ohlc['close'], period=ma1_period)
        ohlc['ma2'] = sma(ohlc['close'], period=ma2_period)
        ohlc['rsi'] = rsi(ohlc, period=rsi_period)
        ohlc['sma'] = sma(ohlc['rsi'], period=sma_period)
        ohlc['k'], ohlc['d'] = stoch(ohlc, k_period=k_period, smooth=k_smooth,
                                     d_period=d_smooth)

    def check(self, ohlc, time):
        side = self.side
        i = ohlc.index.get_loc(time)
        if (ohlc['close'][time] - ohlc['open'][time]) * side > 0\
                and (ohlc['k'][i] - ohlc['d'][i]) * side > 0:
            dt = datetime.now(timezone.utc)
            utc_time = str(dt.replace(tzinfo=timezone.utc))
            if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 2:
                return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close']
        open = ohlc['open']
        ma1 = ohlc['ma1']
        ma2 = ohlc['ma2']
        k = ohlc['k']
        d = ohlc['d']
        rsi = ohlc['rsi']
        sma = ohlc['sma']
        up = self.up
        down = self.down
        up_trend = False
        down_trend = False

        if down[-3][-1] < down[-2][-1] < down[-1][-1]:
            x = [down[-3][0], down[-2][0], down[-1][0]]
            y = [down[-3][-1], down[-2][-1], down[-1][-1]]
            reg = linregress(x, y)
            if reg[2] > reg_min:
                up_trend = True
                self.reg = reg
        if up[-3][-1] > up[-2][-1] > up[-1][-1]:
            x = [up[-3][0], up[-2][0], up[-1][0]]
            y = [up[-3][-1], up[-2][-1], up[-1][-1]]
            reg = linregress(x, y)
            if reg[2] < -reg_min:
                down_trend = True
                self.reg = reg

        if up_trend and not down_trend and ma2[i] > ma1[i]:
            self.trend = 1
        elif down_trend and not up_trend and ma2[i] < ma1[i]:
            self.trend = -1
        else:
            self.trend = 0

        if self.trend == 1 and close[i] > ma1[i]:# and min(ohlc['low'][-10:]) == down[-1][-1]:
            if k[i] > d[i] and k[i - 1] <= d[i - 1]:
                self.message = 'buy detected'
                self.side = 1
                return 1
        elif self.trend == -1 and close[i] < ma1[i]: #and max(ohlc['high'][-10:]) == up[-1][-1]:
            if k[i] < d[i] and k[i - 1] >= d[i - 1]:
                self.message = 'sell detected'
                self.side = -1
                return -1

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
            stop_loss0 = max(high[-stop_bars:])
            stop_loss = stop_loss0
            target = min(low[-target_bars:])

        else:
            stop_loss0 = min(low[-stop_bars:])
            stop_loss = stop_loss0
            target = max(high[-target_bars:])

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
        stop_loss = max(high[-stop_bars:])
        target = min(low[-target_bars:])
    else:
        stop_loss = min(low[-stop_bars:])
        target = max(high[-target_bars:])
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