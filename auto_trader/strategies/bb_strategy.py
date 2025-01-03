import indicators
from strategy import Strategy
from indicators import stoch, ma, bbands

stoch_gap = 30
stoch_period = 30
ma_period = 200
bb_period = 30
min_m = 0.02 * 0.01


class BB(Strategy):
    def __init__(self):
        pass

    def add_indicators(self, ohlc):
        slowk, slowd = stoch(ohlc, stoch_period)
        slowk[0] = 50
        slowd[0] = 50
        ohlc['slowk'], ohlc['slowd'] = slowk, slowd
        ohlc['ma'] = ma(ohlc, ma_period)
        ohlc['upper'], ohlc['middle'], ohlc['lower'] = bbands(ohlc, bb_period)

    def check(self, ohlc, time):
        side = check_trend(ohlc, time)
        if side == 0:
            return False, side
        check = check_stoch(ohlc, side, time)
        return check, side

    def get_params(self, ohlc, time, side):
        goal = 0
        stop_loss = 0
        entry_price = ohlc['close'][time]
        e = (ohlc['upper'][time] - ohlc['middle'][time]) / entry_price
        if side == 1:
            stop_loss = self.get_low(ohlc, time, e)
            goal = self.get_high(ohlc, time, e)
        elif side == -1:
            stop_loss = self.get_high(ohlc, time, e)
            goal = self.get_low(ohlc, time, e)
        return stop_loss, entry_price, goal




def check_trend(ohlc, time):
    m = ohlc['middle'][time] - ohlc['middle'][ohlc.index.get_loc(time) - 2]

    if ohlc['lower'][time] > ohlc['ma'][time] and ohlc['close'][time] > ohlc['ma'][time] and m > min_m:
        return 1
    elif ohlc['upper'][time] < ohlc['ma'][time] and ohlc['close'][time] < ohlc['ma'][time] and m < -min_m:
        return -1
    return 0


def check_stoch(ohlc, side, time):
    if side == 1:
        if ohlc['slowk'][time] < stoch_gap:
            return True
    elif side == -1:
        if ohlc['slowd'][time] > 100 - stoch_gap:
            return True
    return False
