import pandas as pd
import matplotlib.pyplot as plt

import plot
from strategies.bb_strategy import BB
from strategies.ma_strategy import MA
from strategies.double_ema import EMA2
from strategies.triple_ema import EMA3
import order
from strategy import Strategy

#df = pd.DataFrame

max_total_loss = 0.16
max_leverage = 25
fee_rate = 0.00075
#fee_rate = 0.0006
#min_e = (max_total_loss / max_leverage - 2 * fee_rate) / (1 + fee_rate)
min_e_t = 1 * 0.01
min_e_s = 1 * 0.01
max_e = 10000 * 0.01
#min_e = 0.3
rr = 1
#d = 0.2 * 0.01
# ~0.24
wins = 0.0
losses = 0.0


def get_high(ohlc, time, min_e, d):
    a = ohlc['high'][:time]
    price = ohlc['close'][time]
    high = 0
    for i in range(len(a)-2, 0, -1):
        if i < len(a) - 100:
            break
        if a[i] > a[i+1] and a[i] > a[i-1]:
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


def get_low(ohlc, time, min_e, d):
    a = ohlc['low'][:time]
    price = ohlc['close'][time]
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


def calculate_leverage(entry_price, stop_loss, goal):
    if goal <= 0:
        return 0, 0
    e = (entry_price - stop_loss)/entry_price
    leverage = max_total_loss / (abs(e) + fee_rate * (abs(e) + 2))
    if entry_price > stop_loss:
        take_profit = entry_price * (1 + (fee_rate * (2 + abs(e)) + rr * max_total_loss / leverage))
        #take_profit = entry_price * (1 + abs(e))
        if goal > take_profit:
            return int(leverage), goal
        else:
            return int(leverage), take_profit
    elif entry_price < stop_loss:
        take_profit = entry_price * (1 - (fee_rate * (2 + abs(e)) + rr * max_total_loss / leverage))
        #take_profit = entry_price * (1 - abs(e))
        if goal < take_profit:
            return int(leverage), goal
        else:
            return int(leverage), take_profit
    return 0, 0


def calculate_params(ohlc, time, side, strategy):
    stop_loss, entry_price, goal = strategy.get_params(ohlc, time, side)
    leverage, take_profit = calculate_leverage(entry_price, stop_loss, goal)
    return leverage, entry_price, stop_loss, take_profit


def check_limits(ohlc, time, order):
    global wins, losses
    stop_loss = order.stop_loss
    take_profit = order.take_profit
    price_low = ohlc['low'][time]
    price_high = ohlc['high'][time]
    price_high = ohlc['close'][time]
    price_low = ohlc['close'][time]
    if order.side == 1:
        if price_low <= stop_loss:
            losses += 1
            order.exit_price = stop_loss
            return "lost"
        elif price_high >= take_profit:
            wins += 1
            order.exit_price = take_profit
            return "won"
        else:
            return "open"

    elif order.side == -1:
        if price_high >= stop_loss:
            losses += 1
            order.exit_price = stop_loss
            return "lost"
        elif price_low <= take_profit:
            wins += 1
            order.exit_price = take_profit
            return "won"
        else:
            return "open"


def check_previous(strategy, ohlc, symbol, chart):
    strategy.add_indicators(ohlc)
    trade = "off"
    new_order = None
    for time in ohlc.index:
        if trade == "off":
            check, side = strategy.check(ohlc, time)
            if check:
                leverage, entry_price, stop_loss, take_profit = calculate_params(ohlc, time, side, strategy)
                new_order = order.Order(symbol, leverage, side, entry_price, stop_loss, take_profit, time)
                if leverage > 25 or leverage < 1:
                    continue
                trade = "on"
        elif trade == "on":
            result = check_limits(ohlc, time, new_order)
            if not result == "open":
                if not symbol in order.Order.orders:
                    order.Order.orders[symbol] = []
                order.Order.orders[symbol].append(new_order)
                new_order.result = result
                #if(new_order.stop_loss > new_order.take_profit):
                new_order.calculate_profit()

                print(new_order.symbol, result, new_order.time, new_order.leverage, new_order.side,
                      new_order.stop_loss, new_order.entry_price, new_order.take_profit,new_order.leverage, new_order.profit)
                trade = "off"
    if chart:
        plot.show_plot(ohlc, symbol, strategy)


def win_rate():
    global wins, losses
    #result = wins / (losses + wins)
    wins = 0
    losses = 0





