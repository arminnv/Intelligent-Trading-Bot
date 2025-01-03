from strategy import Strategy
from indicators2 import ema, bb


d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01

bb_period = 80
ema_period = 5
delta = 0.2 * 0.01
# bb 100 10 20


class BB(Strategy):

    def __init__(self):
        self.funcs = {'bbh': 'blue', 'bbl': 'blue', 'ema': 'yellow'}
        self.last_message = 'trend declined'
        self.message = 'trend declined'

        self.bb_period = bb_period
        self.ema_period = ema_period

        self.in_range = 0
        self.breakout = 0

    def add_indicators(self, ohlc):
        ohlc['ema'] = ema(ohlc, self.ema_period)
        ohlc['bbh'], ohlc['bbl'] = bb(ohlc, self.bb_period)

    def check(self, ohlc, time):
        side = self.check_trend(ohlc, time)
        if side == 0:
            return False, side
        return True, side

    def check_range(self, ohlc, time):
        if ohlc['bbh'][time] - ohlc['ema'][time] <= delta * ohlc['close'][time]:
            self.in_range = 1
            if self.breakout == 0:
                self.message = 'close to bullish break out'
                ohlc['cross'][time] = ohlc['close'][time]
        elif ohlc['bbl'][time] - ohlc['ema'][time] >= -delta * ohlc['close'][time]:
            self.in_range = -1
            if self.breakout == 0:
                self.message = 'close to bearish break out'
                ohlc['cross'][time] = ohlc['close'][time]
        else:
            self.in_range = 0
            self.message = 'declined'

    def check_breakout(self, ohlc, time):
        if ohlc['ema'][time] - ohlc['bbh'][time] >= 0:
            self.breakout = 1
            self.message = 'bullish trend detected'
            ohlc['check'][time] = ohlc['close'][time]
        elif ohlc['ema'][time] - ohlc['bbl'][time] <= 0:
            self.breakout = -1
            ohlc['check'][time] = ohlc['close'][time]
            self.message = 'bearish trend detected'
        else:
            self.breakout = 0
            self.message = 'trend declined'
        self.check_range(ohlc, time)

    def check_trend(self, ohlc, time):
        self.check_breakout(ohlc, time)
        if self.breakout == 1:
            return 1
        elif self.breakout == -1:
            return -1
        return 0

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