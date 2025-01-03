from strategy import Strategy
from indicators2 import ema, kc

w = 1 / 3
d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01

class KC(Strategy):

    def __init__(self):
        self.periods = {'kc_period': 160,
                        'atr_period': 80,
                        'ema_period': 50}
        self.cycle = 100
        self.multiplier = 2.5
        self.band_width = 1.3 * 0.01

        self.funcs = {'kch': 'green', 'kcl': 'green', 'ema': 'yellow'}
        self.last_message = 'declined'
        self.message = 'declined'

        self.kc_period = self.periods['kc_period']
        self.ema_period = self.periods['ema_period']
        self.atr_period = self.periods['atr_period']

        self.position = 0
        self.previous_position = 0
        """
        -2
        -1
        0
        1
        2
        """

    def add_indicators(self, ohlc):
        ohlc['ema'] = ema(ohlc, self.ema_period)
        ohlc['kch'], ohlc['kcl'] = kc(ohlc, period=self.kc_period, atr_period=self.atr_period, multiplier=self.multiplier)

    def check(self, ohlc, time):
        side = self.check_trend(ohlc, time)
        if side == 0:
            return False, side
        return True, side

    def check_trend(self, ohlc, time):
        delta = (ohlc['kch'][time] - ohlc['kcl'][time]) * w

        self.previous_position = self.position

        if ohlc['kcl'][time] <= ohlc['close'][time] <= ohlc['kch'][time]:
            self.position = 0
        elif 0 < ohlc['kcl'][time] - ohlc['close'][time] < delta:
            self.position = 1
        elif 0 > ohlc['kch'][time] - ohlc['close'][time] > -delta:
            self.position = -1
        elif ohlc['close'][time] < ohlc['kcl'][time]:
            self.position = 2
        elif ohlc['close'][time] > ohlc['kch'][time]:
            self.position = -2

        if not ohlc['kcl'][time] < ohlc['ema'][time] < ohlc['kch'][time]:
            return 0

        if self.previous_position == 1 and self.position == 0:
            self.message = 'buy zone detected'
            return 1
        elif self.previous_position == -1 and self.position == 0:
            self.message = 'sell zone detected'
            return -1
        elif self.position == 1:
            self.message = 'close to buy zone'
        elif self.position == -1:
            self.message = 'close to sell zone'
        elif self.position != 0:
            self.message = 'declined'
        return 0

    def set_indicators(self, new_cycle):
        a = new_cycle / self.cycle
        self.ema_period *= a
        self.atr_period *= a
        self.kc_period *= a

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

