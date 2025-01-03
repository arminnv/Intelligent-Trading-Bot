import math
from datetime import datetime, timezone
import calculator
from strategy import Strategy
from indicators2 import dc

dc_period = 40


class DC(Strategy):
    def __init__(self):
        self.name = 'dc'

        self.periods = {
        }

        self.cycle = 100
        self.interval = 30
        #30
        #5
        # 15
        self.funcs = {}
        self.side = 0
        self.previous_side = 0
        self.last_message = 'declined'
        self.message = 'declined'
        self.state = ''
        self.breakout = False

    def add_indicators(self, ohlc):
        ohlc['h'], ohlc['l'] = dc(ohlc, dc_period)
        return

    def check(self, ohlc, time):
        side = self.side
        if side != 0:
            if (ohlc['close'][time] - ohlc['open'][time]) * side > 0:
                #dt = datetime.now(timezone.utc)
                #utc_time = str(dt.replace(tzinfo=timezone.utc))
                #if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 50:
                    return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)

        mid = (ohlc['h'][-1] + ohlc['l'][-1]) / 2
        delta = (ohlc['h'][-1] - ohlc['l'][-1])

        #if ohlc['high'][-1] < ohlc['h'][-1] and ohlc['low'][-1] > ohlc['l'][-1]:
        if ohlc['high'][-1] >= mid >= ohlc['low'][-1]:
            self.breakout = False

        if not self.breakout:
            if ohlc['close'][-1] > ohlc['h'][-1] or ohlc['close'][-1] < ohlc['l'][-1]:
                self.breakout = True

            if ohlc['h'][-1] > ohlc['h'][-2] <= ohlc['h'][-3]:
                if ohlc['close'][-1] > ohlc['open'][-1] and ohlc['low'][-1] > mid:
                    d2 = abs(ohlc['close'][-1] - ohlc['h'][-1])
                    if d2 <= delta * 0.1:
                        self.message = 'buy detected'
                        self.state = 'dc'
                        self.side = 1
                        return 1

            elif ohlc['l'][-1] < ohlc['l'][-2] >= ohlc['l'][-3]:
                if ohlc['close'][-1] < ohlc['open'][-1] and ohlc['high'][-1] < mid:
                    d2 = abs(ohlc['close'][-1] - ohlc['l'][-1])
                    if d2 <= delta * 0.1:
                        self.message = 'sell detected'
                        self.state = 'dc'
                        self.side = -1
                        return -1

        self.message = 'declined'
        self.side = 0
        return 0

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]
        open = ohlc['open'][-1]

        if close > open:
            stop_loss = ohlc['low'][-1]
            target = max(ohlc['high'][-100:])
        else:
            stop_loss = ohlc['high'][-1]
            target = min(ohlc['low'][-100:])
        stop_index = -1
        target_index = -1
        e = -(stop_loss / close - 1)
        rr = round(abs((target / close - 1) / e), 1)
        leverage, take_profit, rr1, rr2 = calculator.calculate_leverage(close, e, target)
        return round(leverage, 1), rr, round(e * 100, 2), stop_index\
            , target_index, stop_loss, target


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