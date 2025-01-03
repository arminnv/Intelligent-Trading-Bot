from datetime import datetime, timezone
import calculator
import config
from strategy import Strategy
from indicators2 import swing
from scipy.stats import linregress

interval = config.interval

swing_period = 7
reg_min = 0.98


class TLBO(Strategy):
    def __init__(self):
        self.name = 'tlbo'

        self.interval = interval
        self.side = 0
        self.trend = 0
        self.up = []
        self.down = []
        self.reg = []
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        self.up, self.down = swing(ohlc, swing_period)

    def check(self, ohlc, time):
        side = self.side
        i = ohlc.index.get_loc(time)
        if (ohlc['close'][time] - ohlc['open'][time]) * side > 0:
            #dt = datetime.now(timezone.utc)
            #utc_time = str(dt.replace(tzinfo=timezone.utc))
            #if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 2:
            return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close']
        open = ohlc['open']
        up = self.up
        down = self.down

        if down[-1][0] < up[-1][0]:
            if down[-3][1] < down[-2][1] < down[-1][1]:
                x = [down[-3][0], down[-2][0], down[-1][0]]
                y = [down[-3][1], down[-2][1], down[-1][1]]
                reg = linregress(x, y)
                if reg[2] > reg_min:
                    self.trend = 1
                    self.reg = reg
            elif up[-4][1] > up[-3][1] > up[-2][1]:
                x = [up[-4][0], up[-3][0], up[-2][0]]
                y = [up[-4][1], up[-3][1], up[-2][1]]
                reg = linregress(x, y)
                if reg[2] < -reg_min:
                    self.trend = -1
                    self.reg = reg
            else:
                self.trend = 0
        else:
            if up[-3][1] > up[-2][1] > up[-1][1]:
                x = [up[-3][0], up[-2][0], up[-1][0]]
                y = [up[-3][1], up[-2][1], up[-1][1]]
                reg = linregress(x, y)
                if reg[2] < -reg_min:
                    self.trend = -1
                    self.reg = reg
            elif down[-4][1] < down[-3][1] < down[-2][1]:
                x = [down[-4][0], down[-3][0], down[-2][0]]
                y = [down[-4][1], down[-3][1], down[-2][1]]
                reg = linregress(x, y)
                if reg[2] > reg_min:
                    self.trend = 1
                    self.reg = reg
            else:
                self.trend = 0

        if self.trend == -1:
            reg = self.reg
            if close[i] > reg[0] * i + reg[1] >= open[i]:
                self.message = 'buy detected'
                self.side = 1
                return 1
        elif self.trend == 1:
            reg = self.reg
            if close[i] < reg[0] * i + reg[1] <= open[i]:
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
            stop_loss0 = self.up[-1][1]
            stop_loss = stop_loss0
            target = min(low[-target_bars:])

        else:
            stop_loss0 = self.down[-1][1]
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