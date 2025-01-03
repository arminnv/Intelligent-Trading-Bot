from strategy import Strategy
from indicators2 import ema


d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01
ema1_period = 400
ema2_period = 80
ema3_period = 20
# 80 20
delta_ema = 0.13 * 0.01
delta_ema = 0.2 * 0.01



class EMA3(Strategy):

    def __init__(self, ema1_period, ema2_period, ema3_period):
        self.funcs = ['ema1', 'ema2', 'ema3']
        self.ema1_period = ema1_period
        self.ema2_period = ema2_period
        self.ema3_period = ema3_period
        self.alert = 0
        self.in_range = 0

    def add_indicators(self, ohlc):
        ohlc['ema1'] = ema(ohlc, self.ema1_period)
        ohlc['ema2'] = ema(ohlc, self.ema2_period)
        ohlc['ema3'] = ema(ohlc, self.ema3_period)

    def check(self, ohlc, time):
        side = self.check_trend(ohlc, time)
        if side == 0:
            return False, side
        return True, side

    def check_range(self, ohlc, time):
        if ohlc['ema2'][time] < ohlc['ema1'][time]:
            if 0 < ohlc['ema2'][time] - ohlc['ema3'][time] < delta_ema * ohlc['close'][time]:
                self.in_range = 1
                return
        elif ohlc['ema2'][time] > ohlc['ema1'][time]:
            if 0 > ohlc['ema2'][time] - ohlc['ema3'][time] > -delta_ema * ohlc['close'][time]:
                self.in_range = -1
                return
        self.in_range = 0

    def check_trend(self, ohlc, time):
        self.check_range(ohlc, time)
        if self.in_range == 0:
            return 0
        elif self.in_range == 1:
            if ohlc['ema3'][time] > ohlc['ema2'][time]:
                return 1
        elif self.in_range == -1:
            if ohlc['ema3'][time] < ohlc['ema2'][time]:
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


