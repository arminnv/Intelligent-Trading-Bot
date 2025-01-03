from abc import ABC

from strategy import Strategy
from indicators2 import ema, kc

w = 0.1
d = 0.6 * 0.01
e_stop = 0.4 * 0.01
e_goal = 1 * 0.01


class EMA2(Strategy):
    def __init__(self):

        self.periods = {
            'ema_fast_period': 5,
            'ema_slow_period': 20,
            'stochastic': 40,
            'kc_period': 60,
            'atr_period': 50}

        self.cycle = 100
        self.multiplier = 1.6
        self.interval = 1

        self.funcs = {'kch': 'green', 'kcl': 'green', 'ema': 'yellow'}
        self.last_message = 'declined'
        self.message = 'declined'

        self.kc_period = self.periods['kc_period']
        self.ema_fast_period = self.periods['ema_fast_period']
        self.ema_slow_period = self.periods['ema_slow_period']
        self.atr_period = self.periods['atr_period']

        self.position = 0
        self.previous_position = 0

        """
        0
        1
        -1
        0
        """
    def add_indicators(self, ohlc):
        ohlc['ema_fast'] = ema(ohlc, self.ema_fast_period)
        ohlc['ema_slow'] = ema(ohlc, self.ema_slow_period)
        ohlc['kch'], ohlc['kcl'] = kc(ohlc, period=self.kc_period, atr_period=self.atr_period, multiplier=self.multiplier)

    def check(self, ohlc, time):
        side = self.check_indicators(ohlc, time)
        if side == 0:
            return False, side
        return True, side

    def check_indicators(self, ohlc, time):
        delta = (ohlc['kch'][time] - ohlc['kcl'][time]) * w

        if 0 < ohlc['ema_fast'][time] - ohlc['ema_slow'][time] < delta:
            self.position = 1
        elif 0 > ohlc['ema_fast'][time] - ohlc['ema_slow'][time] > -delta:
            self.position = -1
        else:
            self.position = 0

        if self.position != self.previous_position:
            if self.position == 0:
                self.message = 'declined'
            elif self.position == 1 and self.previous_position == -1:
                self.message = 'buy detected'
            elif self.position == -1 and self.previous_position == 1:
                self.message = 'sell detected'
            elif self.position == -1 and self.previous_position == 0:
                self.message = 'close to buy'
            elif self.position == 1 and self.previous_position == 0:
                self.message = 'close to sell'

        self.previous_position = self.position


"""
measure last cycle's period
set periods according to the cycle

ema cross -> enter, exit
stop, target -> last swings

remove target and exit after crossover
"""


