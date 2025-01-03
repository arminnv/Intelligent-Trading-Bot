import math
from datetime import datetime, timezone

import bot
import calculator
from strategy import Strategy
from indicators2 import stoch

w = 0.1
d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01
period = 30

# stochastic 20 6 6

stoch_low = 25
stoch_high = 75


class BO(Strategy):
    def __init__(self):

        self.periods = {
        }

        self.cycle = 100
        self.interval = 15
        # 15
        self.funcs = {}
        self.side = 0
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        return

    def check(self, ohlc, time):
        side = self.side
        if side != 0:
            if (ohlc['close'][time] - ohlc['open'][time]) * side > 0:
                dt = datetime.now(timezone.utc)
                utc_time = str(dt.replace(tzinfo=timezone.utc))
                if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 50:
                    return True
        return False

    def check_indicators(self, ohlc, time):
        ohlc = ohlc.tail(period + 1)
        i = ohlc.index.get_loc(time)

        high = max(ohlc['high'][:period])
        low = min(ohlc['low'][:period])

        if ohlc['high'][-1] > high:
            self.message = 'buy detected'
            self.side = 1
            return 1

        elif ohlc['low'][-1] < low:
            self.message = 'sell detected'
            self.side = -1
            return -1

        self.message = 'declined'
        return 0

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]
        high = ohlc['high']
        low = ohlc['low']
        # print(high.index[-1])
        if self.side == 1:
            stop_loss, stop_index = extremum(high[-1], 'max')
            target, target_index = extremum(low[-100:], 'min')

        else:
            stop_loss, stop_index = extremum(low[-1:], 'min')
            target, target_index = extremum(high[-100:], 'max')

        e = -(stop_loss / close - 1)
        rr = round(abs((target / close - 1) / e), 1)
        leverage, take_profit, rr1, rr2 = calculator.calculate_leverage(close, e, target)
        return round(leverage, 1), rr, round(e * 100, 2), stop_index + len(high) - stop_bars - 1 \
            , target_index + len(high) - target_bars - 1, stop_loss, target


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