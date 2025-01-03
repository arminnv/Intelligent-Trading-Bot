from strategy import Strategy
from indicators2 import ema, kc, macd

w = 1 / 3
d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01


kc_period = 160
atr_period = 80
ema_period = 50
multiplier = 2.5
macd_fast_period = 4
macd_slow_period = 8


class MACD(Strategy):

    def __init__(self):
        self.funcs = {'kch': 'green', 'kcl': 'green', 'ema': 'yellow', 'hist': 'purple'}
        self.last_message = 'declined'
        self.message = 'declined'
        self.interval = 5

        self.kc_period = kc_period
        self.ema_period = ema_period

        self.zone = 0

    def add_indicators(self, ohlc):
        ohlc['ema'] = ema(ohlc, self.ema_period)
        ohlc['kch'], ohlc['kcl'] = kc(ohlc, period=self.kc_period, atr_period=atr_period, multiplier=multiplier)
        ohlc['hist'] = macd(ohlc, slow_period=macd_slow_period, fast_period=macd_fast_period)

    def check(self, ohlc, time):
        side = self.check_indicators(ohlc, time)
        if side == 0:
            return False, side
        return True, side

    def check_indicators(self, ohlc, time):

        if ohlc['kcl'][time] < ohlc['ema'][time] < ohlc['kch'][time]:
            if ohlc['close'][time] <= ohlc['kcl'][time]:
                self.zone = 1
            elif ohlc['close'][time] >= ohlc['kch'][time]:
                self.zone = -1
        else:
            self.zone = 0

        if self.zone == 1:
            if ohlc['hist'][time] < 0:
                self.message = 'in buy zone'
            else:
                self.message = 'buy signal detected'
        elif self.zone == -1:
            if ohlc['hist'][time] > 0:
                self.message = 'in sell zone'
            else:
                self.message = 'sell signal detected'
        else:
            self.message = 'declined'

    def get_params(self, ohlc, time, side):
        #entry_price = ohlc['close'][time]
        #e_stop = (ohlc['upper'][time] - ohlc['middle'][time]) / entry_price / 7
        #e_goal = 4 * e_stop
        goal = 0
        stop_loss = 0
        entry_price = ohlc['close'][time]
        if side == 1:
            stop_loss = self.get_low(ohlc, time, e_stop, d)
            goal = self.get_high(ohlc, time, e_goal, d)
        elif side == -1:
            stop_loss = self.get_high(ohlc, time, e_stop, d)
            goal = self.get_low(ohlc, time, e_goal, d)
        if goal != 0:
            ohlc['goal'][time] = goal
        if stop_loss != 0:
            ohlc['stop'][time] = stop_loss

        return stop_loss, entry_price, goal