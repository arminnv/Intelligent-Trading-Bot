from strategy import Strategy
from indicators2 import ema, bb


d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01

bb_period = 80
ema1_period = 20
ema2_period = 5
delta_ema = 0.5 * 0.01
# bb 100 10 20


class BB(Strategy):

    def __init__(self):
        self.alert_message = 'cross detected'
        self.funcs = {'bbh': 'blue', 'bbl': 'blue', 'ema1': 'yellow', 'ema2': 'lime'}
        self.bb_period = bb_period
        self.ema1_period = ema1_period
        self.ema2_period = ema2_period
        self.alert = 0
        self.in_range = 0
        self.cross = 0
        self.send_message = ''

    def add_indicators(self, ohlc):
        ohlc['ema1'] = ema(ohlc, self.ema1_period)
        ohlc['ema2'] = ema(ohlc, self.ema2_period)
        ohlc['bbh'], ohlc['bbl'] = bb(ohlc, self.bb_period)

    def check(self, ohlc, time):
        side = self.check_trend(ohlc, time)
        if side == 0:
            return False, side
        return True, side

    def check_range(self, ohlc, time):
        if 0 < ohlc['ema1'][time] - ohlc['ema2'][time]:
            self.in_range = 1
            return
        elif 0 > ohlc['ema1'][time] - ohlc['ema2'][time]:
            self.in_range = -1
            return
        self.in_range = 0

    def check_cross(self, ohlc, time):
        if self.in_range == 1 and ohlc['ema2'][time] - ohlc['ema1'][time] >= 0:
            self.cross = 1
            if ohlc['bbh'][time] >= ohlc['ema1'][time] >= ohlc['bbl'][time]:
                ohlc['cross'][time] = ohlc['close'][time]
                self.send_message = self.alert_message
                self.alert = 1
            else:
                self.send_message = 'declined'
                self.alert = 0
        elif self.in_range == -1 and ohlc['ema2'][time] - ohlc['ema1'][time] <= 0:
            self.cross = -1
            if ohlc['bbh'][time] >= ohlc['ema1'][time] >= ohlc['bbl'][time]:
                ohlc['cross'][time] = ohlc['close'][time]
                self.send_message = self.alert_message
                self.alert = -1
            else:
                self.send_message = 'declined'
                self.alert = 0
        self.check_range(ohlc, time)

    def check_trend(self, ohlc, time):
        self.check_cross(ohlc, time)
        if self.alert == 1:
            if ohlc['ema1'][time] > ohlc['bbh'][time]:
                self.alert = 0
                return 1
        elif self.alert == -1:
            if ohlc['ema1'][time] < ohlc['bbl'][time]:
                self.alert = 0
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