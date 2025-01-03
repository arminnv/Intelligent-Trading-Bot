from datetime import datetime, timezone
import calculator
import config
from strategy import Strategy
from indicators2 import rsi, sma, swing, adx, stoch, kc, ema

interval = config.interval

ma1_period = 190
ma2_period = 180
ma3_period = 60
kc_period = 100
atr_period = 10
multiplier = 2
rsi_period = 14
sma_period = 14
k_period = 14
k_smooth = 3
d_smooth = 3
adx_period = 14
trend_level = 20
swing_period = 7
cross_gap = 10

stoch_high = 80
stoch_low = 20
rr_min = 1


class KC(Strategy):
    def __init__(self):
        self.name = 'kc'

        self.interval = interval
        self.side = 0
        self.over_bs = 0
        self.up = []
        self.down = []

        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        self.up, self.down = swing(ohlc, swing_period)
        ohlc['ma1'] = ema(ohlc, period=ma1_period)
        ohlc['ma2'] = ema(ohlc, period=ma2_period)
        ohlc['ma3'] = ema(ohlc, period=ma3_period)
        ohlc['ma3'] = ema(ohlc['close'], period=ma3_period)
        ohlc['kch'], kcm, ohlc['kcl'] = kc(ohlc, kc_period, atr_period, multiplier)
        ohlc['rsi'] = rsi(ohlc, period=rsi_period)
        ohlc['sma'] = sma(ohlc['rsi'], period=sma_period)
        ohlc['k'], ohlc['d'] = stoch(ohlc, k_period=k_period, smooth=k_smooth,
                                     d_period=d_smooth)
        ohlc['adx'], ohlc['di+'], ohlc['di-'] = adx(ohlc, period=adx_period)

    def check(self, ohlc, time, test):
        side = self.side
        i = ohlc.index.get_loc(time)
        if (ohlc['close'][time] - ohlc['open'][time]) * side > 0 \
                and (ohlc['rsi'][i] - ohlc['sma'][i]) * side > 0:
            if test:
                return True
            dt = datetime.now(timezone.utc)
            utc_time = str(dt.replace(tzinfo=timezone.utc))
            if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 2:
                return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)
        close = ohlc['close']
        open = ohlc['open']
        kch = ohlc['kch']
        kcl = ohlc['kcl']
        rsi = ohlc['rsi']
        sma = ohlc['sma']
        k = ohlc['k']
        ma1 = ohlc['ma1']
        ma2 = ohlc['ma2']
        ma3 = ohlc['ma3']
        adx = ohlc['adx']
        up = self.up
        down = self.down
        up_trend = False
        down_trend = False

        if down[-3][-1] < down[-2][-1] < down[-1][-1]:
            up_trend = True
        if up[-3][-1] > up[-2][-1] > up[-1][-1]:
            down_trend = True

        if close[i] > kch[i] and adx[i] >= trend_level and ma2[i] - ma1[i] >= ma2[i - 1] - ma1[i - 1]:
            self.trend = 1
        elif close[i] < kcl[i] and adx[i] >= trend_level and ma2[i] - ma1[i] <= ma2[i - 1] - ma1[i - 1]:
            self.trend = -1
        else:
            self.trend = 0

        """
        if close[i] > kch[i] and adx[i] >= trend_level:
            self.trend = 1
        elif close[i] < kcl[i] and adx[i] >= trend_level:
            self.trend = -1
        else:
            self.trend = 0
        """

        if k[i - 1] < stoch_low:
            self.over_bs = 1
        elif k[i - 1] > stoch_high:
            self.over_bs = -1

        if self.trend == 1 and self.over_bs == 1:
            if close[i] > open[i] and rsi[i] > sma[i] and rsi[i - 1] <= sma[i - 1] and check_cross(ohlc, 1):
                self.message = 'buy detected'
                self.side = 1
                return 1

        elif self.trend == -1 and self.over_bs == -1:
            if close[i] < open[i] and rsi[i] < sma[i] and rsi[i - 1] >= sma[i - 1] and check_cross(ohlc, -1):
                self.message = 'sell detected'
                self.side = -1
                return -1

        if (self.over_bs == 1 and rsi[i - 1] > sma[i - 1] and rsi[i - 2] <= sma[i - 2]) \
                or (self.over_bs == -1 and rsi[i - 1] < sma[i - 1] and rsi[i - 2] >= sma[i - 2]):
            self.over_bs = 0

        self.message = 'declined'
        self.side = 0
        return 0

    def check_tail(self, side):
        up = self.up
        down = self.down
        if side == 1:
            if up[-1][0] < down[-1][0]:
                if up[-2][-1] <= up[-1][-1]:
                    return True
            elif up[-3][-1] <= up[-2][-1]:
                return True
        else:
            if down[-1][0] < up[-1][0]:
                if down[-2][-1] >= down[-1][-1]:
                    return True
            elif down[-3][-1] >= down[-2][-1]:
                return True
        return False

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]
        high = ohlc['high']
        low = ohlc['low']

        if ohlc['close'][-1] < ohlc['open'][-1]:
            #stop_loss0 = high[-1]
            stop_loss0 = max(high[-config.STOP_BARS:])
            stop_loss = stop_loss0
            target = min(low[-target_bars:])

        else:
            #stop_loss0 = low[-1]
            stop_loss0 = min(low[-config.STOP_BARS:])
            stop_loss = stop_loss0
            target = max(high[-target_bars:])

        stop_index = -1
        target_index = -1

        e = -(stop_loss0 / close - 1)
        e1 = -(stop_loss / close - 1)
        rr = round(abs((target / close - 1) / e1), 2)
        leverage, take_profit, rr1, rr2 = calculator.calculate_leverage(close, e, target)
        return round(leverage, 1), rr, round(e * 100, 2), stop_index + len(high) - stop_bars - 1 \
            , target_index + len(high) - target_bars - 1, stop_loss, target, stop_loss0


def check_target(ohlc, side, stop_bars, target_bars, rr_min):
    close = ohlc['close'][-1]
    high = ohlc['high']
    low = ohlc['low']
    if side == -1:
        stop_loss = max(high[-stop_bars:])
        target = min(low[-target_bars:])
    else:
        stop_loss = min(low[-stop_bars:])
        target = max(high[-target_bars:])
    e = -(stop_loss / close - 1)
    rr = abs((target / close - 1) / e)
    if rr >= rr_min:
        return True
    else:
        return False


def check_ma_cross(ohlc, side):
    if side == 1:
        x = ohlc['low'][-10:]
    else:
        x = ohlc['high'][-10:]
    ma = ohlc['ma1'][-10:]

    for i in range(len(x)):
        if (x[i] - ma[i]) * side < 0:
            return False
    return True


def extremum(a, st):
    index = 0
    ext = 0
    if st == 'max':
        max = a[0]
        for i in range(len(a)):
            if a[i] >= max:
                max = a[i]
                index = i
        ext = max
    elif st == 'min':
        min = a[0]
        for i in range(len(a)):
            if a[i] <= min:
                min = a[i]
                index = i
        ext = min
    return ext, index


def get_previous_swing(side, a):
    if side == 1:
        for i in range(len(a) - 3, 2, -1):
            if a[i] <= min(a[i - 1], a[i - 2], a[i + 1], a[i + 2]):
                return i, a[i]
    elif side == -1:
        for i in range(len(a) - 3, 2, -1):
            if a[i] >= max(a[i - 1], a[i - 2], a[i + 1], a[i + 2]):
                return i, a[i]
    else:
        return 0, a[0]


def check_cross(ohlc, side):
    n = 0
    max_crosses = 0
    for i in range(2, 2 + cross_gap):
        if (ohlc['rsi'][-i] - ohlc['sma'][-i]) * side > 0:
            side *= -1
            n += 1
            if n > max_crosses:
                return False
    return True