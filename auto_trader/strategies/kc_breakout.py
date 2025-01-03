from datetime import datetime, timezone
import calculator
from strategy import Strategy
from indicators2 import kc

w = 1 / 3
d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01

kc_period = 20
atr_period = 10
multiplier = 0.6
#0.8
"""
kc_period = 160
atr_period = 80
ema_period = 100
multiplier = 0.8
"""
#delta = 0.2 * 0.01
"""
kc_period = 20
ema_period = 5

kc_period = 60
atr_period = 50
ema_period = 10
multiplier = 0.5
"""


class KC(Strategy):
    def __init__(self):
        self.name = 'kc'

        self.periods = {
            'kc': 20,
            'atr': 10
        }

        self.cycle = 100
        self.interval = 15

        self.funcs = {}
        self.side = 0
        self.trend = 0
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        ohlc['kch'], ohlc['kcm'], ohlc['kcl'] = kc(ohlc, kc_period, atr_period, multiplier)

    def check(self, ohlc, time):
        side = self.side
        if side != 0:
            if (ohlc['close'][time] - ohlc['open'][time]) * side > 0:
                dt = datetime.now(timezone.utc)
                utc_time = str(dt.replace(tzinfo=timezone.utc))
                if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 45:
                    return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close'][-1]
        open = ohlc['open'][-1]
        kcl = ohlc['kcl'][-1]
        kch = ohlc['kch'][-1]
        kcm = ohlc['kcm'][-1]

        if open <= kch < close:
            if self.trend != 2:
                self.trend = 1
            else:
                self.message = 'buy detected'
                self.side = 1
                return 1

        elif open >= kcl > close:
            if self.trend != -2:
                self.trend = -1
            else:
                self.message = 'sell detected'
                self.side = -1
                return -1

        elif self.trend == 1 and open > kch > close > kcl:
            self.trend = 2

        elif self.trend == -1 and open < kcl < close < kch:
            self.trend = -2

        if self.trend == 2 and open <= kcm < close:
            self.message = 'buy detected'
            self.side = 1
            return 1
        elif self.trend == -2 and open >= kcm > close:
            self.message = 'sell detected'
            self.side = -1
            return -1

        self.message = 'declined'
        self.side = 0
        return 0

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]

        kcl = ohlc['kcl'][-1]
        kch = ohlc['kch'][-1]
        mid = (kcl + kch)/2

        high = ohlc['high']
        low = ohlc['low']

        if self.trend >= 0:
            stop_loss = ohlc['low'][-1]
            target, target_index = extremum(high[-target_bars:], 'max')

        else:
            stop_loss = ohlc['high'][-1]
            target, target_index = extremum(low[-target_bars:], 'min')

        stop_index = -1
        e = -(stop_loss / close - 1)
        rr = round(abs((target / close - 1) / e), 1)
        leverage, take_profit, rr1, rr2 = calculator.calculate_leverage(close, e, target)
        return round(leverage,1), rr, round(e*100,2), stop_index + len(high) - stop_bars - 1\
            ,target_index + len(high) - target_bars - 1, stop_loss, target


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


"""
ema break out of band + chop(14,0) < 38.2 -> enter
ema cross mid band -> exit
"""


"""
ema cross band -> enter
if price > rr = 1:
    stop +0.5
    candle cross other band -> exit
price > take profit : stop -> rr = 1
price > target : stop -> take profit
"""