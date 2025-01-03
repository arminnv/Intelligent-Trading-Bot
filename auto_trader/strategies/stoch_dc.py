from datetime import datetime, timezone
import calculator
import config
from strategy import Strategy
from indicators2 import stoch, dc

interval = config.interval

dc_period = 40
k_period = 14
k_smooth = 3
d_smooth = 3

stoch_high = 80
stoch_low = 20


class STDC(Strategy):
    def __init__(self):
        self.name = 'stdc'

        self.interval = interval
        self.side = 0
        self.trend = 0
        self.over_bs = 0
        self.crossed = False
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        ohlc['h'], mid, ohlc['l'] = dc(ohlc, period=dc_period)
        ohlc['k'], ohlc['d'] = stoch(ohlc, k_period=k_period, smooth=k_smooth,
                                     d_period=d_smooth)

    def check(self, ohlc, time):
        side = self.side
        if (ohlc['close'][time] - ohlc['open'][time]) * side > 0 and (
                ohlc['k'][time] - ohlc['d'][time]) * side > 0:
            dt = datetime.now(timezone.utc)
            utc_time = str(dt.replace(tzinfo=timezone.utc))
            if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 2:
                return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close']
        open = ohlc['open']
        k = ohlc['k']
        d = ohlc['d']

        if ohlc['high'][i] >= ohlc['h'][i]:
            self.trend = 1
        elif ohlc['low'][i] <= ohlc['l'][i]:
            self.trend = -1

        if k[i] < stoch_low:
            self.over_bs = 1
        elif k[i] > stoch_high:
            self.over_bs = -1
        elif stoch_low < d[i] < stoch_high:
            self.over_bs = 0
            self.crossed = False

        if self.over_bs == 1:
            if self.trend == 1 and k[i] > d[i] and close[i] > open[i] and not self.crossed \
                    and (k[i - 1] <= d[i - 1]):
                self.message = 'buy detected'
                self.side = 1
                return 1
            elif k[i - 2] > d[i - 2] and k[i - 3] <= d[i - 3] and d[i - 2] < stoch_low:
                self.crossed = True

        elif self.over_bs == -1:
            if self.trend == -1 and k[i] < d[i] and close[i] < open[i] and not self.crossed \
                    and (k[i - 1] >= d[i - 1]):
                self.message = 'sell detected'
                self.side = -1
                return -1
            elif k[i - 2] < d[i - 2] and k[i - 3] >= d[i - 3] and d[i - 2] > stoch_high:
                self.crossed = True

        self.message = 'declined'
        self.side = 0
        return 0

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]
        high = ohlc['high']
        low = ohlc['low']

        if ohlc['close'][-1] < ohlc['open'][-1]:
            stop_loss = max(high[-stop_bars:])
            # stop_loss = high[-1]
            stop_loss0 = stop_loss
            target = min(low[-target_bars:])

        else:
            stop_loss = min(low[-stop_bars:])
            # stop_loss = low[-1]
            stop_loss0 = stop_loss
            target = max(high[-target_bars:])

        stop_index = -1
        target_index = -1

        e = -(stop_loss0 / close - 1)
        e1 = -(stop_loss / close - 1)
        rr = round(abs((target / close - 1) / e1), 2)
        leverage, take_profit, rr1, rr2 = calculator.calculate_leverage(close, e, target)
        return round(leverage, 1), rr, round(e * 100, 2), stop_index + len(high) - stop_bars - 1 \
            , target_index + len(high) - target_bars - 1, stop_loss, target, stop_loss0


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


def count_crosses(k, d):
    n = 0
    if k[-1] > d[-1]:
        s = 1
    else:
        s = -1
    for i in range(2, 50):
        if stoch_low < d[-i] < stoch_high:
            break
        if s * (k[-i] - d[-i]) < 0:
            s *= -1
            n += 1
    return n
