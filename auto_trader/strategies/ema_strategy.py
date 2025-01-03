import indicators
from strategy import Strategy
from indicators import stoch, ema, bbands

ema0_period = 300
ema1_period = 40
ema2_period = 25
bb_period = 20

d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01
# 80 20


class EMA(Strategy):
    def __init__(self):
        self.funcs = ['ema0', 'ema1', 'ema2']

    def add_indicators(self, ohlc):
        ohlc['ema0'] = ema(ohlc, ema0_period)
        ohlc['ema1'] = ema(ohlc, ema1_period)
        ohlc['ema2'] = ema(ohlc, ema2_period)
        ohlc['upper'], ohlc['middle'], ohlc['lower'] = bbands(ohlc, bb_period)

    def check(self, ohlc, time):
        side = check_trend(ohlc, time)
        if side == 0:
            return False, side
        return True, side

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


def check_trend(ohlc, time):
    if ohlc['ema2'][time] - ohlc['ema1'][time] >= 0 and\
            ohlc['ema2'][ohlc.index.get_loc(time) - 1] - ohlc['ema1'][ohlc.index.get_loc(time) - 1] < 0:
            #ohlc['ema0'][time] - ohlc['ema0'][ohlc.index.get_loc(time) - 180] > -1.25 * 0.01:
        return 1
    elif ohlc['ema2'][time] - ohlc['ema1'][time] <= 0 and\
            ohlc['ema2'][ohlc.index.get_loc(time) - 1] - ohlc['ema1'][ohlc.index.get_loc(time) - 1] > 0:
            #ohlc['ema0'][time] - ohlc['ema0'][ohlc.index.get_loc(time) - 180] < 1.25 * 0.01:
        return -1
    return 0
