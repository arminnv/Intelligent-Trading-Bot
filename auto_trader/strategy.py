from abc import ABC, abstractmethod

import calculator
import config

min_e_t = 1 * 0.01
min_e_s = 1 * 0.01
max_e = 10000 * 0.01

sr_period = 100


def get_stop_loss(ohlc):
    if ohlc['close'][-1] > ohlc['open'][-1]:
        stop_loss = min(ohlc['low'][-4:])
    else:
        stop_loss = max(ohlc['high'][-4:])

    e = -(stop_loss / ohlc['close'][-1] - 1)
    return stop_loss, round(e * 100, 2)


class Strategy(ABC):
    message = ''
    last_message = ''
    interval = 1
    cycle = 1

    periods = {}

    funcs = {}

    @abstractmethod
    def add_indicators(self, ohlc):
        pass

    @abstractmethod
    def check(self, ohlc, time, test):
        pass

    @abstractmethod
    def get_e(self, ohlc, stop_bars, target_bars):
        pass

    @staticmethod
    def check_SR(ohlc, side):
        if side == 1:
            stop_loss = min(ohlc['low'][-config.swing_bars:])
        else:
            stop_loss = max(ohlc['high'][-config.swing_bars:])
        if min(ohlc['low'][-sr_period:]) < stop_loss < max(ohlc['high'][-sr_period:]):
            return True
        else:
            return False

    def get_params(self, ohlc, time, side):

        goal = -1
        stop_loss = -1
        min_e = 0.5 * 0.01

        i = ohlc.index.get_loc(time)
        a = ohlc['high'][max(i - 100, 0):i]
        price = ohlc['close'][time]
        d = (max(a) - min(a)) / price / 20

        if not min(a)*(1-4*d) <= price <= max(a)*(1-4*d):
            return stop_loss, goal

        if side == 1:
            stop_loss = self.get_low(ohlc, time, min_e=min_e)
            goal = self.get_high(ohlc, time, min_e=min_e)
        elif side == -1:
            stop_loss = self.get_high(ohlc, time, min_e=min_e)
            goal = self.get_low(ohlc, time, min_e=min_e)
        return stop_loss, goal

    def set_periods(self, new_cycle):
        a = new_cycle / self.cycle
        text = ''
        for key in self.periods.keys():
            self.periods[key] = int(self.periods[key] * a)
            text = text + key + ' : ' + str(self.periods[key]) + '\n'
        return text

    def get_high(self, ohlc, time, min_e):
        i = ohlc.index.get_loc(time)
        a = ohlc['high'][max(i - 100, 0):i]
        price = ohlc['close'][time]
        d = (max(a)-min(a))/price/20
        high = 0
        for i in range(len(a) - 2, 0, -1):
            if i < len(a) - 100:
                break
            if a[i] > a[i + 1] and a[i] > a[i - 1]:
                high = a[i]
                e = (high - price) / price
                if max_e > e > min_e:
                    for j in range(i + 1, len(a)):
                        if a[i] - a[j] >= d * a[i]:
                            ohlc['maximum'][ohlc['high'].index[i]] = a[i]
                            return high
                        elif a[j] > a[i]:
                            break
                else:
                    continue
        return 0

    def get_low(self, ohlc, time, min_e):
        i = ohlc.index.get_loc(time)
        a = ohlc['high'][max(i - 100, 0):i]
        price = ohlc['close'][time]
        d = (max(a) - min(a)) / price/20
        low = 0
        for i in range(len(a) - 2, 0, -1):
            if i < len(a) - 100:
                break
            if a[i] < a[i + 1] and a[i] < a[i - 1]:
                low = a[i]
                e = (low - price) / price
                if -max_e < e < -min_e:
                    for j in range(i + 1, len(a)):
                        if a[i] - a[j] <= -d * a[i]:
                            ohlc['minimum'][ohlc['low'].index[i]] = a[i]
                            return low
                        elif a[j] < a[i]:
                            break
                else:
                    continue
        return 0
