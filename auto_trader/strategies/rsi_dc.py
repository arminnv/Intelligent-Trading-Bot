from datetime import datetime, timezone
import calculator
from strategy import Strategy
from indicators2 import rsi, dc, sma

interval = 30

rsi_period = 14
sma_period = 14
dc_period = 100


class RSDC(Strategy):
    def __init__(self):
        self.name = 'rsdc'

        self.interval = interval
        self.funcs = {}
        self.side = 0
        self.trend = 2
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        ohlc['rsi'] = rsi(ohlc, period=rsi_period)
        ohlc['sma'] = sma(ohlc['rsi'], period=sma_period)
        ohlc['h'], ohlc['l'] = dc(ohlc, dc_period)

    def check(self, ohlc, time):
        side = self.side
        if side != 0:
            if (ohlc['close'][time] - ohlc['open'][time]) * side > 0 and (ohlc['rsi'][time] - ohlc['sma'][time]) * side > 0:
                dt = datetime.now(timezone.utc)
                utc_time = str(dt.replace(tzinfo=timezone.utc))
                if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 8:
                    return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close']
        open = ohlc['open']

        mid = (ohlc['h'][i] + ohlc['l'][i]) / 2

        if ohlc['high'][i] > ohlc['h'][i]:
            self.trend = 1
        elif ohlc['low'][i] < ohlc['l'][i]:
            self.trend = -1
        elif ohlc['low'][i] <= mid <= ohlc['high'][i]:
            self.trend = 0

        if ohlc['rsi'][i] > ohlc['sma'][i] and ohlc['rsi'][i - 1] <= ohlc['sma'][i - 1] and close[i] > open[i]:
            if self.trend == 0:
                if close[i] < mid:
                    self.message = 'buy detected'
                    self.side = 1
                    return 1
            elif self.trend == 1:
                self.message = 'buy detected'
                self.side = 1
                return 1

        elif ohlc['rsi'][i] < ohlc['sma'][i] and ohlc['rsi'][i - 1] >= ohlc['sma'][i - 1] and close[i] < open[i]:
            if self.trend == 0:
                if close[i] > mid:
                    self.message = 'sell detected'
                    self.side = -1
                    return -1
            elif self.trend == -1:
                self.message = 'sell detected'
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
        return round(leverage, 1), rr, round(e * 100, 2), stop_index \
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
