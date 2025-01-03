import matplotlib.pyplot as plt
import numpy as np
from mpl_finance import candlestick2_ohlc
import mplfinance as mpf
import config
from strategies import adx, stoch_dc, stoch_divergence, rsi, stochastic, kc
#from strategies.stochastic import stoch_high, stoch_low
import live_run

# STOP_BARS = 10
# TARGET_BARS = 16

STOP_BARS = config.STOP_BARS
TARGET_BARS = config.TARGET_BARS


def save_chart(symbol, order):
    ohlc = live_run.symbols_ohlc[symbol]
    path = symbol + '.png'
    strategy = live_run.symbols_strategies[symbol]
    name = strategy.name
    a = list(range(0, len(ohlc['close'])))

    if name == 'kc':
        fig = plt.figure()
        ax1 = plt.subplot(311)
        plt.title(symbol)
        ax2 = plt.subplot(312, sharex=ax1)
        ax2.set_ylabel('Stochastic')
        ax3 = plt.subplot(313, sharex=ax1)
        ax3.set_ylabel('RSI')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        ax1.plot(a, ohlc['ma1'], color='darkviolet', linewidth=1)
        ax1.plot(a, ohlc['ma2'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma3'], color='teal', linewidth=1)
        ax1.plot(a, ohlc['kch'], color='lightgreen', linewidth=1)
        ax1.plot(a, ohlc['kcl'], color='lightgreen', linewidth=1)
        ax2.plot(a, ohlc['k'], color='teal', linewidth=1)
        ax2.plot(a, ohlc['d'], color='purple', linewidth=1)
        ax2.axhline(y=kc.stoch_low, color='gray', linestyle='--', linewidth=1)
        ax2.axhline(y=kc.stoch_high, color='gray', linestyle='--', linewidth=1)
        ax3.plot(a, ohlc['rsi'], color='purple', linewidth=1)
        ax3.plot(a, ohlc['sma'], color='darkgoldenrod', linewidth=1)
        ax3.plot(a, ohlc['adx'], color='orange', linewidth=1)
        ax3.axhline(y=kc.trend_level, color='gray', linestyle='--', linewidth=1)
    elif name == 'mst':
        fig = plt.figure()
        ax1 = plt.subplot(311)

        plt.title(symbol)
        ax2 = plt.subplot(312, sharex=ax1)
        ax2.set_ylabel('Stochastic')
        ax3 = plt.subplot(313, sharex=ax1)
        ax3.set_ylabel('ADX')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        ax1.plot(a, ohlc['ma1'], color='darkviolet', linewidth=1)
        ax1.plot(a, ohlc['ma2'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma3'], color='blue', linewidth=1)
        ax2.plot(a, ohlc['k'], color='teal', linewidth=1)
        ax2.plot(a, ohlc['d'], color='purple', linewidth=1)
        ax2.axhline(y=stochastic.stoch_low, color='gray', linestyle='--', linewidth=1)
        ax2.axhline(y=stochastic.stoch_high, color='gray', linestyle='--', linewidth=1)
        ax3.plot(a, ohlc['adx'], color='orange', linewidth=1)
        ax3.plot(a, ohlc['di+'], color='green', linewidth=1)
        ax3.plot(a, ohlc['di-'], color='red', linewidth=1)
        ax3.axhline(y=stochastic.trend_level, color='gray', linestyle='--', linewidth=1)
        ax3.axhline(y=25, color='gray', linestyle='--', linewidth=1)
    elif name == 'ma':
        fig = plt.figure()
        ax1 = plt.subplot(311)

        plt.title(symbol)
        ax2 = plt.subplot(312, sharex=ax1)
        ax2.set_ylabel('Stochastic')
        ax3 = plt.subplot(313, sharex=ax1)
        ax3.set_ylabel('ADX')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        """
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        """
        ax1.plot(a, ohlc['ma1'], color='darkviolet', linewidth=1)
        ax1.plot(a, ohlc['ma2'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma3'], color='darkgoldenrod', linewidth=1)
        ax2.plot(a, ohlc['k'], color='teal', linewidth=1)
        ax2.plot(a, ohlc['d'], color='purple', linewidth=1)
        ax2.axhline(y=stochastic.stoch_low, color='gray', linestyle='--', linewidth=1)
        ax2.axhline(y=stochastic.stoch_high, color='gray', linestyle='--', linewidth=1)
        ax3.plot(a, ohlc['adx'], color='orange', linewidth=1)
        ax3.plot(a, ohlc['di+'], color='green', linewidth=1)
        ax3.plot(a, ohlc['di-'], color='red', linewidth=1)
        ax3.axhline(y=stochastic.trend_level, color='gray', linestyle='--', linewidth=1)
        ax3.axhline(y=25, color='gray', linestyle='--', linewidth=1)
    elif name == 'stoch':
        fig = plt.figure()
        ax1 = plt.subplot(311)
        plt.title(symbol)
        ax2 = plt.subplot(312, sharex=ax1)
        ax2.set_ylabel('Stochastic')
        ax3 = plt.subplot(313, sharex=ax1)
        ax3.set_ylabel('ADX')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        ax1.plot(a, ohlc['ma1'], color='darkviolet', linewidth=1)
        ax1.plot(a, ohlc['ma2'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma3'], color='darkgoldenrod', linewidth=1)
        ax2.plot(a, ohlc['k'], color='teal', linewidth=1)
        ax2.plot(a, ohlc['d'], color='purple', linewidth=1)
        ax2.axhline(y=stochastic.stoch_low, color='gray', linestyle='--', linewidth=1)
        ax2.axhline(y=stochastic.stoch_high, color='gray', linestyle='--', linewidth=1)
        ax3.plot(a, ohlc['adx'], color='orange', linewidth=1)
        ax3.plot(a, ohlc['di+'], color='green', linewidth=1)
        ax3.plot(a, ohlc['di-'], color='red', linewidth=1)
        ax3.axhline(y=stochastic.trend_level, color='gray', linestyle='--', linewidth=1)
        ax3.axhline(y=25, color='gray', linestyle='--', linewidth=1)
    elif name == 'rsi':
        fig = plt.figure()
        ax1 = plt.subplot(311)
        plt.title(symbol)
        ax2 = plt.subplot(312, sharex=ax1)
        ax2.set_ylabel('RSI')
        ax3 = plt.subplot(313, sharex=ax1)
        ax3.set_ylabel('ADX')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        ax1.plot(a, ohlc['ma1'], color='darkviolet', linewidth=1)
        ax1.plot(a, ohlc['ma2'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma3'], color='teal', linewidth=1)
        ax2.plot(a, ohlc['rsi'], color='purple', linewidth=1)
        ax2.plot(a, ohlc['sma'], color='darkgoldenrod', linewidth=1)
        ax3.plot(a, ohlc['adx'], color='orange', linewidth=1)
        ax3.plot(a, ohlc['di+'], color='green', linewidth=1)
        ax3.plot(a, ohlc['di-'], color='red', linewidth=1)
        ax3.axhline(y=rsi.trend_level, color='gray', linestyle='--', linewidth=1)
    elif name == 'tlbo':
        fig = plt.figure()
        ax1 = plt.subplot(111)
        plt.title(symbol)
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        if strategy.trend != 0:
            reg = strategy.reg
            if strategy.trend == 1:
                x = np.linspace(strategy.down[-3][0], strategy.down[-1][0], 2)
            else:
                x = np.linspace(strategy.up[-3][0], strategy.up[-1][0], 2)
            y = reg[0] * x + reg[1]
            ax1.plot(x, y, color='darkviolet', linewidth=1)
    elif name == 'stdv':
        fig = plt.figure()
        ax1 = plt.subplot(311)
        plt.title(symbol)
        ax2 = plt.subplot(312, sharex=ax1)
        ax2.set_ylabel('Stochastic')
        ax3 = plt.subplot(313, sharex=ax1)
        ax3.set_ylabel('RSI')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        if strategy.trend != 0:
            reg = strategy.reg
            if strategy.trend == 1:
                x = np.linspace(strategy.down[-3][0], strategy.down[-1][0], 2)
            else:
                x = np.linspace(strategy.up[-3][0], strategy.up[-1][0], 2)
            y = reg[0] * x + reg[1]
            ax1.plot(x, y, color='darkviolet', linewidth=1)
        ax1.plot(a, ohlc['ma1'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma2'], color='gray', linewidth=1)
        ax2.plot(a, ohlc['k'], color='teal', linewidth=1)
        ax2.plot(a, ohlc['d'], color='purple', linewidth=1)
        ax2.axhline(y=stoch_divergence.stoch_high, color='gray', linestyle='--', linewidth=1)
        ax2.axhline(y=stoch_divergence.stoch_low, color='gray', linestyle='--', linewidth=1)
        ax3.plot(a, ohlc['rsi'], color='purple', linewidth=1)
        ax3.plot(a, ohlc['sma'], color='darkgoldenrod', linewidth=1)
    elif name == 'adx':
        fig = plt.figure()
        ax1 = plt.subplot(211)
        plt.title(symbol)
        ax2 = plt.subplot(212, sharex=ax1)
        ax2.set_ylabel('ADX')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        ax1.plot(a, ohlc['ma1'], color='darkviolet', linewidth=1)
        ax1.plot(a, ohlc['ma2'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma3'], color='darkgoldenrod', linewidth=1)
        ax2.plot(a, ohlc['adx'], color='orange', linewidth=1)
        ax2.plot(a, ohlc['di+'], color='green', linewidth=1)
        ax2.plot(a, ohlc['di-'], color='red', linewidth=1)
        ax2.axhline(y=adx.trend_level, color='gray', linestyle='--', linewidth=1)
    elif name == 'trend':
        fig = plt.figure()
        ax1 = plt.subplot(311)
        plt.title(symbol)
        ax2 = plt.subplot(312, sharex=ax1)
        ax2.set_ylabel('Stochastic')
        ax3 = plt.subplot(313, sharex=ax1)
        ax3.set_ylabel('RSI')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        for p in strategy.down:
            ax1.plot(p[0], p[-1], marker=6, markersize=4, markeredgecolor="seagreen", markerfacecolor="seagreen")
        for p in strategy.up:
            ax1.plot(p[0], p[-1], marker=7, markersize=4, markeredgecolor="crimson", markerfacecolor="crimson")
        ax1.plot(a, ohlc['ma1'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma2'], color='gray', linewidth=1)
        ax2.plot(a, ohlc['k'], color='teal', linewidth=1)
        ax2.plot(a, ohlc['d'], color='purple', linewidth=1)
        ax2.axhline(y=stoch_divergence.stoch_high, color='gray', linestyle='--', linewidth=1)
        ax2.axhline(y=stoch_divergence.stoch_low, color='gray', linestyle='--', linewidth=1)
        ax3.plot(a, ohlc['rsi'], color='purple', linewidth=1)
        ax3.plot(a, ohlc['sma'], color='darkgoldenrod', linewidth=1)

    elif name == 'rsdc' or name == 'rsi':
        fig = plt.figure()
        ax1 = plt.subplot(211)
        plt.title(symbol)
        ax2 = plt.subplot(212, sharex=ax1)
        ax2.set_ylabel('RSI')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        if name == 'rsdc':
            ax1.plot(a, ohlc['h'], color='blue', linewidth=1)
            ax1.plot(a, ohlc['l'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['ma'], color='blue', linewidth=1)
        plt.subplot(2, 1, 2)
        ax2.plot(a, ohlc['rsi'], color='purple', linewidth=1)
        ax2.plot(a, ohlc['sma'], color='darkgoldenrod', linewidth=1)
        ax2.axhline(y=50, color='gray', linestyle='--', linewidth=1)

    elif name == 'stdc':
        fig = plt.figure()
        ax1 = plt.subplot(211)
        plt.title(symbol)
        ax2 = plt.subplot(212, sharex=ax1)
        ax2.set_ylabel('Stochastic')
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        ax1.plot(a, ohlc['h'], color='blue', linewidth=1)
        ax1.plot(a, ohlc['l'], color='blue', linewidth=1)
        plt.subplot(2, 1, 2)
        plt.plot(a, ohlc['k'], color='blue', linewidth=1)
        plt.plot(a, ohlc['d'], color='purple', linewidth=1)
        ax2.axhline(y=stoch_dc.stoch_high, color='gray', linestyle='--', linewidth=1)
        ax2.axhline(y=stoch_dc.stoch_low, color='gray', linestyle='--', linewidth=1)

    elif name == 'dc':
        fig, ax1 = plt.subplots(nrows=1, ncols=1)
        plt.title(symbol)
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        plt.plot(a, ohlc['h'], color='blue', linewidth=1)
        plt.plot(a, ohlc['l'], color='blue', linewidth=1)
    elif name == 'ema':
        fig, ax1 = plt.subplots(nrows=1, ncols=1)
        plt.title(symbol)
        candlestick2_ohlc(ax1, ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.5, colorup='seagreen',
                          colordown='crimson')
        plt.plot(a, ohlc['ema'], color='blue', linewidth=1)
    if order is None:
        leverage, rr, e, stop_index, target_index, stop_loss, target, stop_loss0 = live_run.symbols_strategies[symbol].get_e(live_run.symbols_ohlc[symbol],
                                                                                         STOP_BARS, TARGET_BARS)
    else:
        stop_loss = order.stop_losses[0]
        target = order.targets[-1]
        entry_price = order.entry_price
        exit_price = order.exit_price
        if exit_price > 0:
            ax1.axhline(y=exit_price, color='black', linestyle='--', linewidth=0.75)
        ax1.axhline(y=entry_price, color='gray', linestyle='--', linewidth=0.75)
    ax1.axhline(y=target, color='seagreen', linestyle='--', linewidth=0.75)
    ax1.axhline(y=stop_loss, color='crimson', linestyle='--', linewidth=0.75)

    plt.savefig(path)
    # plt.plot(stop_index, stop_loss, marker="^", markersize=4, markeredgecolor="red", markerfacecolor="red")
    # Empf.plot(ohlc, type='candle', style='charles', ax=ax1)
