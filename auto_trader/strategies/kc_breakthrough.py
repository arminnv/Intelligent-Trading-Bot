from strategy import Strategy
from indicators2 import ema, kc

w = 1 / 3
d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01


kc_period = 60
atr_period = 50
ema_period = 10
multiplier = 1.6
#delta = 0.2 * 0.01

"""
kc_period = 60
atr_period = 50
ema_period = 20
multiplier = 2

kc_period = 30
atr_period = 15
ema_period = 5
multiplier = 2

kc_period = 60
atr_period = 50
ema_period = 12
multiplier = 2.5
"""


class KC(Strategy):

    def __init__(self):
        self.funcs = {'kch': 'green', 'kcl': 'green', 'ema': 'yellow'}
        self.last_message = 'declined'
        self.message = 'declined'

        self.kc_period = kc_period
        self.ema_period = ema_period

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
        ohlc['kch'], ohlc['kcl'] = kc(ohlc, period=self.kc_period, atr_period=atr_period, multiplier=multiplier)

    def check(self, ohlc, time):
        side = self.check_trend(ohlc, time)
        if side == 0:
            return False, side
        return True, side

    def check_trend(self, ohlc, time):
        delta = (ohlc['kch'][time] - ohlc['kcl'][time]) * w

        self.previous_position = self.position

        if ohlc['kcl'][time] <= ohlc['ema'][time] <= ohlc['kch'][time]:
            self.position = 0
        elif 0 < ohlc['kcl'][time] - ohlc['ema'][time] < delta:
            self.position = 1
        elif 0 > ohlc['kch'][time] - ohlc['ema'][time] > -delta:
            self.position = -1
        elif ohlc['ema'][time] < ohlc['kcl'][time]:
            self.position = 2
        elif ohlc['ema'][time] > ohlc['kch'][time]:
            self.position = -2

        if self.previous_position == 1 and self.position == 0:
            self.message = 'bullish trend detected'
            return 1
        elif self.previous_position == -1 and self.position == 0:
            self.message = 'bearish trend detected'
            return -1
        elif self.position == 1:
            self.message = 'close to bullish breakthrough'
        elif self.position == -1:
            self.message = 'close to bearish breakthrough'
        elif self.position != 0:
            self.message = 'declined'
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


"""
range market :

ema cross band -> enter
if price > rr = 1:
    stop = max(0.25, rr2 ) 
ema cross band -> exit
price > take profit : stop -> rr = 1
price > target : stop -> take profit
2 -> 1

trend market :

detection : failed ema breakout + 3 jumps
entry : candle over band in opposite side of the trend
exit : ema cross mid line 


!!!!!! IN DIRECTION OF THE MAIN TREND !!!!!!   (if not range)

"""