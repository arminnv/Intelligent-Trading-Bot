import os

import analysis
import data_download
from strategies import ema_strategy
import indicators
import order
import json

import plot
from strategies.double_ema import EMA2
from strategies.ema_strategy import EMA
from strategies.triple_ema import EMA3
#from strategies.bb_cross import BB
from strategies.bb_breakout import BB
from strategies.kc_breakout import KC

symbols = ['XRP', 'ADA']
symbols_strategies = {}



class Params:

    get = {}

    def __init__(self):
        self.max_profit = 0
        self.max_profit_win = 0
        self.max_profit_ema1 = 0
        self.max_profit_ema2 = 0
        self.max_profit_trades = 0
        self.max_profit_ppt = 0
        self.max_win = 0
        self.max_win_profit = 0
        self.max_win_ema1 = 0
        self.max_win_ema2 = 0
        self.max_win_trades = 0
        self.max_win_ppt = 0


def initialize():
    symbols_strategies['ADA'] = KC()
    symbols_strategies['XRP'] = KC()

def run(days):
    try:
        os.mkdir('params')
    except FileExistsError:
        pass
    e1_start = 10
    e1_finnish = 110
    e2_start = 10
    e2_finnish = e1_finnish
    analysis.ema1 = 10
    analysis.ema1 = 10
    for x in symbols:
        Params.get[x] = Params()
    for e1 in range(40, 80, 10):
        for e2 in range(10, e1, 5):
            print('** e1:', e1, '** e2:', e2, '**')
            analysis.ema1 = e1
            analysis.ema2 = e2
            for x in data_download.symbols:
                param = Params.get[x]
                for i in range(days):
                    ohlc = data_download.download_symbol(x, i)
                    ema_strategy.ema1_period = e1
                    ema_strategy.ema2_period = e2
                    analysis.check_previous(symbols_strategies[x], ohlc, x, False)
                    #plot.show_plot(ohlc)
                profit_per_trade, n, win_rate, total_profit = order.profit_per_trade(x)
                if win_rate is None:
                    print(x, None)
                else:
                    print(x)
                    print('win rate:', win_rate)
                    print('profit:', total_profit)
                    print('profit per trade:', profit_per_trade)
                    print('trades:', n)
                if not win_rate is None:
                    if win_rate > param.max_win:
                        param.max_win = win_rate
                        param.max_win_profit = total_profit
                        param.max_win_trades = n
                        param.max_win_ema1 = e1
                        param.max_win_ema2 = e2
                        param.max_win_ppt = profit_per_trade
                        Params.get[x] = param
                        save(param, x)
                    if total_profit > param.max_profit:
                        param.max_profit = total_profit
                        param.max_profit_win = win_rate
                        param.max_profit_trades = n
                        param.max_profit_ema1 = e1
                        param.max_profit_ema2 = e2
                        param.max_profit_ppt = profit_per_trade
                        Params.get[x] = param
                        save(param, x)
                order.Order.orders.clear()


def run2(days):
    rates = {}
    for x in symbols:
        strategy = symbols_strategies[x]
        for i in range(days):
            ohlc = data_download.download_symbol(x,strategy.interval, i)
            initialize()
            analysis.check_previous(strategy, ohlc, x, chart=False)
        pnl, n, rates[x], total_profit = order.profit_per_trade(x)
        if rates[x] is None:
            print(x, None)
        else:
            print(x)
            print('win rate:', rates[x])
            print('profit:', total_profit)
            print('profit per trade:', pnl)
            print('trades:', n)


def save(param, symbol):
    st = json.dumps(param.__dict__, indent=1)
    file_name = 'params/' + symbol + '.txt'
    f = open(file_name, "w")
    f.write(st)
    f.close()
