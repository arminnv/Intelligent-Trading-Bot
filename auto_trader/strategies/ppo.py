from datetime import datetime, timezone
from auto_trader.strategy import calculator
import config
from auto_trader.strategy import Strategy
from auto_trader.indicators2 import rsi, sma, swing, adx, stoch, kc, ema, macd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
import scipy.signal


@tf.function
def sample_action(observation):
    logits = actor(observation)
    action = tf.squeeze(tf.random.categorical(logits, 1), axis=1)
    return logits, action


def mlp(x, sizes, activation=tf.tanh, output_activation=None):
    # Build a feedforward neural network
    for size in sizes[:-1]:
        x = layers.Dense(units=size, activation=activation)(x)
    return layers.Dense(units=sizes[-1], activation=output_activation)(x)


interval = config.interval

ma2_period = 200
window = 60
model_name = "trading_agent"
max_total_loss = 0.1


observation_dimensions = window * 5
num_actions = 5
hidden_sizes = (64, 64)
observation_input = keras.Input(shape=(observation_dimensions,), dtype=tf.float32)
logits = mlp(observation_input, list(hidden_sizes) + [num_actions], tf.tanh, None)
actor = keras.Model(inputs=observation_input, outputs=logits)
actor.load_weights(model_name + "_actor_best.h5")


class PPO(Strategy):
    def __init__(self):
        self.name = 'ppo'

        self.interval = interval
        self.side = 0
        self.trading = False
        self.order_list = []
        self.last_message = 'declined'
        self.message = 'declined'

    def add_indicators(self, ohlc):
        return


    def check(self, ohlc, time, test):
        side = self.side
        i = ohlc.index.get_loc(time)
        if self.side != 0:
            if test:
                return True
            dt = datetime.now(timezone.utc)
            utc_time = str(dt.replace(tzinfo=timezone.utc))
            if self.interval - 1 <= int(utc_time[14:16]) % self.interval and int(utc_time[17:19]) >= 2:
                return True
        return False

    def check_indicators(self, ohlc, time):
        i = ohlc.index.get_loc(time)

        if self.trading:
            order = self.order_list[-1]
            # (close - entry) / (entry - stop_loss)
            ohlc[time, "distance"] = (ohlc[time, "close"] - order.entry_price)/(order.entry_price - order.stop_loss)

        ohlc['ma2'] = ema(ohlc, period=ma2_period)
        state = np.vstack((ohlc['close'], ohlc['high'], ohlc['low'],
                          ohlc['ma2'], ohlc['distance'])).T.reshape(-1)

        action = actor.predict(state)

        side = 0
        if action == 1:
            side = 1
        elif action == 2:
            side = -1

        e_target, e_stop_loss = 10, max_total_loss

        if self.trading:
            order = self.order_list[-1]
            if (order.side == 1 and action == 3) or (order.side == -1 and action == 4):
                side = 2

        if side == 1:
            self.message = 'buy detected'
            self.side = 1
            return 1

        elif side == -1:
            self.message = 'sell detected'
            self.side = -1
            return -1

        elif action == 3 or action == 4:
            self.side = 2
            return 2

        self.message = 'declined'
        self.side = 0
        return 0

    def get_e(self, ohlc, stop_bars, target_bars):
        close = ohlc['close'][-1]
        high = ohlc['high']
        low = ohlc['low']

        e_target = 10
        e_stop_loss = 0.1

        target = close * (1 + self.side * e_target)
        stop_loss = close * (1 - self.side * min(max_total_loss, e_stop_loss))
        rr = (target - close) / (close - stop_loss)
        if stop_loss < 0:
            stop_loss = 0
        if target < 0:
            target = 0
        e = -(stop_loss / close - 1)
        stop_loss0 = stop_loss
        leverage = 1

        stop_index = -1
        target_index = -1

        #e = -(stop_loss0 / close - 1)
        e1 = -(stop_loss / close - 1)
        rr = round(abs((target - close) / (close - stop_loss)), 2)
        leverage, take_profit, rr1, rr2 = calculator.calculate_leverage(close, e, target)
        return round(leverage, 1), rr, round(e * 100, 2), stop_index + len(high) - stop_bars - 1 \
            , target_index + len(high) - target_bars - 1, stop_loss, target, stop_loss0
