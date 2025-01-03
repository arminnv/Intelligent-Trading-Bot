import math
from datetime import datetime, timezone

#import bot
import calculator
from strategy import Strategy
from indicators2 import ema

w = 0.1
d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01

ema_period = 20


class EMA(Strategy):
    def __init__(self):
        self.name = 'ema'

        self.periods = {
            'ema': 20
        }

        self.cycle = 100
        self.interval = 15

        self.funcs = {}
        self.side = 0
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        ohlc['ema'] = ema(ohlc, period=ema_period)

    def check(self, ohlc, time):
        side = self.side
        if side != 0:
            if (ohlc['close'][time] - ohlc['ema'][time]) * side > 0:
                dt = datetime.now(timezone.utc)
                utc_time = str(dt.replace(tzinfo=timezone.utc))
                if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 45:
                    return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close'][-1]
        open = ohlc['open'][-1]
        ema = ohlc['ema'][-1]

        if open <= ema < close:
            self.message = 'buy detected'
            self.side = 1
            return 1
        elif open >= ema > close:
            self.message = 'sell detected'
            self.side = -1
            return -1

        self.message = 'declined'
        self.side = 0
        return 0

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]
        ema = ohlc['ema'][-1]
        high = ohlc['high']
        low = ohlc['low']

        if close > ema:
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