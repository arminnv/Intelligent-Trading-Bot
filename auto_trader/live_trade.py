import math
import os
import time
from datetime import datetime, timezone
from math import log10

import calculator
import chart
import config
import live_run
import trade_journal
from statistics import Order
import bybit_api
from config import real

STOP_BARS = config.STOP_BARS
#16
TARGET_BARS = config.TARGET_BARS
MAX_LEVERAGE = 25
rr_min = config.rr_min
RR = config.RR
min_e = config.min_e

trading = False
test = False
losts = 0


def main(update, context, symbol):
    global trading, losts
    trading = True
    # update.message.reply_text('checking params /' + symbol)
    try:
        if not start_trade(symbol):
            trading = False
            time.sleep(0.2)
            return

        update.message.reply_text('trade started /' + symbol)
        caption = symbol
        send_chart2(update, context, symbol, caption, Order.list[-1])

        time.sleep(5)
        while trading:
            ohlc = live_run.symbols_ohlc[symbol]
            Order.list[-1] = check_limits(ohlc, Order.list[-1])
            order = Order.list[-1]
            rr = (ohlc['close'][-1] - order.entry_price) / (order.entry_price - order.stop_losses[0])
            if rr > order.max_rr:
                Order.list[-1].max_rr = rr
            if order.exit_price != 0:
                live_run.symbols_strategies[symbol].trading = False
                """
                if order.exit_rr == -1:
                    losts += 2
                elif losts > 0:
                    losts -= 1
                """
                break
        update.message.reply_text(result())
        caption = symbol + ' result'
        send_chart2(update, context, symbol, caption, Order.list[-1])
        print('saving')
        trade_journal.save()
        if losts < 3:
            time.sleep(300)
        else:
            time.sleep(config.interval * 60 * 36)
            losts = 2
        trading = False

    except Exception as e:
        trading = False
        print(e)
        update.message.reply_text(str(e))


def check_params(symbol):
    global RR
    strategy = live_run.symbols_strategies[symbol]
    ohlc = live_run.symbols_ohlc[symbol]
    leverage, rr, e, stop_index, target_index, stop_loss, target, stop_loss0 = strategy.get_e(
        ohlc=ohlc, stop_bars=STOP_BARS, target_bars=TARGET_BARS)

    RR = config.RR
    if strategy.name == 'stoch' or strategy.name == 'rsi' or strategy.name == 'kc':
        #if not strategy.check_SR(ohlc, stop_loss):
         #   return False
        if rr < rr_min:
            return False
        #else:
            #RR = rr * config.a
            #RR = config.RR

    leverage = round(leverage, 0)
    if leverage > MAX_LEVERAGE:
        leverage = MAX_LEVERAGE
    if abs(e) >= min_e and leverage >= 1:
        return True
    else:
        return False


def start_trade(symbol):
    global trading
    ohlc = live_run.symbols_ohlc[symbol]

    if test:
        e = 0.2 * 0.01
        leverage = 17
        entry_price = ohlc['close'][-1]
        stop_loss = entry_price * (1 - e)
        stop_loss = round(stop_loss, str(entry_price)[::-1].find('.'))
        stop_loss0 = stop_loss
    else:
        leverage, rr, e, stop_index, target_index, stop_loss, target, stop_loss0 = live_run.symbols_strategies[symbol].get_e(
            ohlc=ohlc, stop_bars=STOP_BARS,
            target_bars=TARGET_BARS)
        e *= 0.01

    leverage = round(leverage, 0)
    if leverage > MAX_LEVERAGE:
        leverage = MAX_LEVERAGE

    if e == 0:
        trading = False
        return False
    elif e > 0:
        side = 1
        trade_side = 'Buy'
    else:
        side = -1
        trade_side = 'Sell'

    trading = True
    if real:
        minimum_qty, qty_step, tick_size = bybit_api.get_minimum_qty(symbol)
        digits = 1 - int(math.log10(tick_size))

        qty = bybit_api.get_available_balance() / live_run.symbols_ohlc[symbol]['close'][-1] * leverage * 0.95
        qty = round(math.floor(qty / qty_step) * qty_step, 5)
        print(minimum_qty, qty)
        if qty < minimum_qty or qty == 0 or stop_loss == 0 or abs(live_run.symbols_ohlc[symbol]['close'][-1] - stop_loss) <= 2 * tick_size:
            trading = False
            return False

        bybit_api.set_leverage(symbol, leverage)
        #tick_size = float(bybit_api.get_tick_size(symbol))


        print('placing order')
        bybit_api.place_market_order(symbol, qty, trade_side)
        print('setting stop loss')
        stop_loss = round(int(stop_loss / tick_size) * tick_size, digits)
        bybit_api.set_stop_loss(symbol, stop_loss, trade_side)

        #if msg != 'OK':
         #   trading = False
          #  for i in range(4):
           #     bybit_api.close_position(symbol, trade_side)
            #print('error while setting stop loss')
            #return False
        entry_price = bybit_api.get_entry_price(symbol, trade_side)
        targets, stop_losses = calculator.calculate_targets(entry_price, stop_loss, RR, tick_size)
        #stop_losses[0] = stop_loss0
        print('setting take profit')
        bybit_api.set_take_profit(symbol, targets[-1], trade_side)
    else:
        minimum_qty, qty_step, tick_size = bybit_api.get_minimum_qty(symbol)
        entry_price = ohlc['close'][-1]
        targets, stop_losses = calculator.calculate_targets(entry_price, stop_loss, RR, tick_size)
        #stop_losses[0] = stop_loss0

    order = Order(e, 0, symbol, targets[0], entry_price, stop_loss, side, '0')
    order.trade_side = trade_side
    order.leverage = leverage
    order.targets, order.stop_losses = targets, stop_losses
    dt = datetime.now(timezone.utc)
    utc_time = str(dt.replace(tzinfo=timezone.utc))
    order.time = utc_time
    Order.list.append(order)
    live_run.symbols_strategies[symbol].order_list = Order.list.append(order)
    trading = True
    return True


def check_limits(ohlc, order):
    global trading
    close = ohlc['close'][-1]

    stop_loss = order.stop_loss
    target = order.target
    side = order.side

    symbol = order.symbol
    strategy = live_run.symbols_strategies[symbol]
    if strategy.check() and strategy.check_indicators(ohlc, time=ohlc.index[-1]) == 2:
        order.exit_price = close
        order.calculate_profit(RR)
        if real:
            bybit_api.close_position(symbol, order.trade_side)

    elif side * (close - stop_loss) <= 0:
        #trading = False
        order.exit_price = order.stop_loss
        order.calculate_profit(RR)
    elif side * (close - target) >= 0:
        i = order.targets.index(target)
        if i == len(order.targets) - 1:
            print('taking profit')
            while True:
                if bybit_api.used_margin() == 0:
                    break
                else:
                    time.sleep(5)

            #trading = False
            order.exit_price = order.target
            order.calculate_profit(RR)
            return order
        else:
            order.target = order.targets[i + 1]
            order.stop_loss = order.stop_losses[i + 1]
            if real:
                bybit_api.set_stop_loss(order.symbol, order.stop_loss, order.trade_side)
    #if not trading:

    return order


def trade_status(order):
    order.exit_price = live_run.symbols_ohlc[order.symbol]['close'][-1]
    order.calculate_profit(RR)
    text = 'symbol : ' + order.symbol + '\ne : ' + str(round(order.e * 100, 4)) + '\nprofit : ' + str(
        round(order.profit * 100, 4)) + \
           '\nleverage : ' + str(order.leverage) + '\nlast price : ' + str(round(order.exit_price, 4)) + \
           '\nentry price : ' + str(round(order.entry_price, 4)) + '\nrr : ' + str(round(order.exit_rr, 4)) \
           + '\nstop loss : ' + str(round(order.stop_losses[0], 4)) + '\nmax rr : ' + str(round(order.max_rr, 4))
    return text


def result():
    """
    text = '   e    | max rr |exit rr |leverage|  fee   | profit |   rr  |'
    for order in Order.list:
        a = [round(order.e, 4), round(order.max_rr, 4), round(order.exit_rr, 4), order.leverage, round(order.fee, 4),
             round(order.profit, 4), 2]

        for x in a:
            text += str(x) + str_n(' ', 8 - len(str(x))) + '|'
        text += '\n'
    """
    order = Order.list[-1]
    text = 'symbol : ' + order.symbol + '\ne : ' + str(round(order.e * 100, 4)) + '\nprofit : ' + str(
        round(order.profit * 100, 4)) + \
           '\nleverage : ' + str(order.leverage) + '\nexit price : ' + str(round(order.exit_price, 4)) + \
           '\nentry price : ' + str(round(order.entry_price, 4)) + '\nexit rr : ' + str(round(order.exit_rr, 4)) \
           + '\nstop loss : ' + str(round(order.stop_losses[0], 4)) + '\nmax rr : ' + str(round(order.max_rr, 4))
    return text


def force_close():
    global trading
    symbol = Order.list[-1].symbol
    Order.list[-1].exit_price = live_run.symbols_ohlc[symbol]['close'][-1]
    Order.list[-1].calculate_profit(RR)
    bybit_api.close_position(symbol, Order.list[-1].trade_side)
    trading = False


def kill_all():
    global trading
    for symbol in config.symbols:
        bybit_api.close_position(symbol, 'Buy')
        bybit_api.close_position(symbol, 'Sell')
    trading = False


def send_chart2(update, context, symbol, caption, order):
    chart.save_chart(symbol, order)
    path = symbol + '.png'
    chat_id = update.message.chat_id
    context.bot.sendPhoto(chat_id=chat_id, photo=open(path, 'rb'), caption=caption)
    os.remove(path)


"""
        n = 0
        print('placing order')
        while True:
            if side == 1:
                price = ohlc['close'][-1] - tick_size
            else:
                price = ohlc['close'][-1] + tick_size

            if bybit_api.place_limit_order(symbol, price, qty, trade_side) == 'OK':
                n = 0
                print('order set')
                while True:
                    if bybit_api.get_position_size(symbol, trade_side) > 0:
                        print('setting stop loss')
                        bybit_api.set_stop_loss(symbol, stop_loss, trade_side)
                        break
                    time.sleep(0.2)
                    n += 1
                    if n > 3000:
                        bybit_api.cancel_order(symbol)
                        return False
            elif n >= 100:
                return False
            else:
                n += 1
        """


