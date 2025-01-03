import numpy as np
import requests
#from pandas._libs import json
from numpy import random

import calculator
import config
import data_download
import plot
from statistics import Order
from strategies.kc import KC
from strategies.ma import MA
from strategies.ma_stoch import MST
from strategies.rsi import RSI
from strategies.stochastic import STOCH
import statistics
import ticksize
trading = False

symbols_strategies = {}
symbols_ohlc = {}
tick_size = {}
#symbols = ['ADA', 'XEM', 'MATIC', 'ETH']
symbols = ['ADA']

#STOP_BARS = 10
TARGET_BARS = 40
MAX_LEVERAGE = 25
rr_min = -1
min_e = 0.2


def initialize():
    url = 'https://api.bybit.com/v2/public/symbols'
    #result = json.loads(requests.get(url).text)['result']
    result = ticksize.result
    for x in symbols:
        symbols_strategies[x] = KC()
        tick_size[x] = float(next(item for item in result if item["name"] == x + "USDT")['price_filter']['tick_size'])

def run(days):
    global trading
    sample_size = 1000
    for x in symbols:
        initialize()
        strategy = symbols_strategies[x]
        OHLC = data_download.download_symbol(x, strategy.interval, days)
    for x in symbols:
        initialize()
        strategy = symbols_strategies[x]
        #for RR in np.arange(0.5, 6, 0.1):
        for m in range(100):
            n = random.randint(0, len(OHLC) - sample_size)
            ohlc = OHLC[n: n + sample_size]
            for i in range(1):
                RR = 3.5
                trading = False
                statistics.Order.list.clear()
                check_previous(RR, strategy, ohlc, x, chart=False)
                max_profit, best_rr, average_profit_per_trade = statistics.maximize_profit(-RR)
                win_rate, average_rr = statistics.calculate_win_rate()
                print('best rr : ', best_rr)
                print('max profit : ', max_profit)
                print('win rate : ', win_rate)
                print('average max rr : ', average_rr)
                print('average profit per trade : ', average_profit_per_trade)
                print('trades : ', len(Order.list))
        plot.show_chart(ohlc, x, strategy, False)


def check_previous(RR, strategy, ohlc, symbol, chart):
    global trading
    Order.list.clear()
    strategy.add_indicators(ohlc)
    OHLC = ohlc
    #plot.show_chart(ohlc, symbol, strategy, True)
    for i in range(200, len(OHLC['close'])-1):
        if OHLC['close'][i - 1] != OHLC['open'][i] and i>0:
            OHLC['open'][i] = OHLC['close'][i - 1]
            print('error *************************')
            print(OHLC.index[i], OHLC.index[i-1])
        time = OHLC.index[i]
        ohlc = OHLC.iloc[:i+1]
        strategy.check_indicators(ohlc, time)
        check = strategy.check(ohlc, time, test=True)
        if not trading:
            if check:
                if not check_params(RR, symbol, ohlc, time):
                    continue
                trading = True

        else:
            Order.list[-1] = check_limits(RR, ohlc, Order.list[-1])
            order = Order.list[-1]
            rr = (ohlc['close'][-1] - order.entry_price) / (order.entry_price * order.e)
            if rr > order.max_rr:
                Order.list[-1].max_rr = rr

            if order.exit_price != 0:
                order.calculate_profit(RR)
                #print(order.symbol, order.time, order.leverage, order.side,
                #      order.stop_loss, order.entry_price, order.exit_rr, order.leverage, order.profit)
                trading = False
    if Order.list[-1].exit_price == 0:
        Order.list.pop(-1)
    #if chart:
        #plot.show_chart(ohlc, symbol, strategy, True)


def check_params(RR, symbol, ohlc, time):
    strategy = symbols_strategies[symbol]
    leverage, rr, e, stop_index, target_index, stop_loss, target, stop_loss0 = strategy.get_e(
        ohlc=ohlc, stop_bars=config.STOP_BARS, target_bars=config.TARGET_BARS)

    leverage = round(leverage, 0)
    if leverage > MAX_LEVERAGE:
        leverage = MAX_LEVERAGE
    if rr >= rr_min and abs(e) >= min_e and leverage >= 1 and abs(ohlc['close'][-1] - stop_loss) > 2 * tick_size[symbol]:
        e *= 0.01
        entry_price = ohlc['close'][-1]
        targets, stop_losses = calculator.calculate_targets(entry_price, stop_loss, RR, tick_size[symbol])
        order = Order(e, 0, symbol, targets[0], entry_price, stop_loss, strategy.side, ohlc.index[-1])
        order.leverage = leverage
        order.targets, order.stop_losses = targets, stop_losses
        Order.list.append(order)
        order.index = ohlc.index.get_loc(time)
        return True
    else:
        return False


def check_limits(RR, ohlc, order):
    global trading
    close = ohlc['close'][-1]

    stop_loss = order.stop_loss
    target = order.target
    side = order.side

    if side * (close - stop_loss) <= 0:
        order.exit_price = order.stop_loss
        order.calculate_profit(RR)
    elif side * (close - target) >= 0:
        i = order.targets.index(target)
        if i == len(order.targets) - 1:
            order.exit_price = order.target
            order.calculate_profit(RR)
            return order
        else:
            order.target = order.targets[i + 1]
            order.stop_loss = order.stop_losses[i + 1]

    return order


"""
        if side * (close - stop_loss) <= 0:
        i = order.stop_losses.index(stop_loss)
        if i == len(order.stop_losses) - 1:
            order.exit_price = order.stop_loss
            order.calculate_profit(RR)
            return order
        else:
            order.target = order.targets[i + 1]
            order.stop_loss = order.stop_losses[i + 1]
    elif side * (close - target) >= 0:
        order.exit_price = order.target
        order.calculate_profit(RR)
        
   
"""
run(200)