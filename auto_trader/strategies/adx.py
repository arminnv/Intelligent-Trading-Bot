from datetime import datetime, timezone
import calculator
import config
from strategy import Strategy
from indicators2 import adx, sma, swing

interval = config.interval

swing_period = 7
adx_period = 3
ma1_period = 100
ma2_period = 40
ma3_period = 20

trend_level = 50


class ADX(Strategy):
    def __init__(self):
        self.name = 'adx'

        self.interval = interval
        self.trend = 0
        self.side = 0
        self.up = []
        self.down = []
        self.crossed = False
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        self.up, self.down = swing(ohlc, swing_period)
        ohlc['ma1'] = sma(ohlc['close'], period=ma1_period)
        ohlc['ma2'] = sma(ohlc['close'], period=ma2_period)
        ohlc['ma3'] = sma(ohlc['close'], period=ma3_period)
        ohlc['adx'], ohlc['di+'], ohlc['di-'] = adx(ohlc, period=adx_period)

    def check(self, ohlc, time):
        side = self.side
        if (ohlc['close'][time] - ohlc['open'][time]) * side > 0:
            dt = datetime.now(timezone.utc)
            utc_time = str(dt.replace(tzinfo=timezone.utc))
            if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 2:
                return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close']
        open = ohlc['open']
        high = ohlc['high']
        low = ohlc['low']
        ma1 = ohlc['ma1']
        ma2 = ohlc['ma2']
        ma3 = ohlc['ma3']
        dip = ohlc['di+']
        din = ohlc['di-']
        adx = ohlc['adx']
        up = self.up
        down = self.down

        if close[i] > ma3[i] > ma1[i] and dip[i] > din[i] and adx[i] >= trend_level:
            self.trend = 1
        elif close[i] < ma3[i] < ma1[i] and dip[i] < din[i] and adx[i] >= trend_level:
            self.trend = -1
        else:
            self.trend = 0
            self.crossed = False

        if self.trend == 1:
            if open[i - 3] > close[i - 3] < close[i - 2] < close[i - 1] < close[i] and max(high[-30:-5]) > close[i]:
                self.message = 'buy detected'
                self.side = 1
                return 1
            elif open[i - 3] < close[i - 3] < close[i - 2] < close[i - 1]:
                self.crossed = True
        elif self.trend == -1:
            if open[i - 3] < close[i - 3] > close[i - 2] > close[i - 1] > close[i] and min(low[-30:-5]) < close[i]:
                self.message = 'sell detected'
                self.side = -1
                return -1
            elif open[i - 3] > close[i - 3] > close[i - 2] > close[i - 1]:
                self.crossed = True

        self.message = 'declined'
        self.side = 0
        return 0

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]
        high = ohlc['high']
        low = ohlc['low']

        if ohlc['close'][-1] < ohlc['open'][-1]:
            stop_loss = max(high[-2:])
            # stop_loss = high[-1]
            stop_loss0 = stop_loss
            target = min(low[-target_bars:])

        else:
            stop_loss = min(low[-2:])
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
