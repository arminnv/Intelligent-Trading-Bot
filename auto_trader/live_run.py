import threading
import time
from datetime import datetime, timezone
import alert
import config
import live_data
import live_trade
import trade_journal
from auto_trader.strategies.ppo import PPO
from strategies.adx import ADX
from strategies.double_ema import EMA2
from strategies.ma import MA
from strategies.ma_stoch import MST
from strategies.rsi import RSI
from strategies.rsi_dc import RSDC
from strategies.stoch_dc import STDC
from strategies.stoch_divergence import STDV
from strategies.trendline_breakout import TLBO
from strategies.triple_ema import EMA3
from strategies.bb_breakout import BB
from strategies.kc import KC
from strategies.macd_kc import MACD
from strategies.stochastic import STOCH
from strategies.breakout import BO
from strategies.dc import DC
from strategies.ema_cross import EMA
from strategies.trend import TREND
from live_data import primary_values, get_last_bar

symbols_strategies = {}
symbols_ohlc = {}
strategies_dict = {'tlbo': TLBO, 'stdv': STDV, 'adx': ADX, 'ma': MA, 'mst': MST, 'trend': TREND, 'stoch': STOCH, 'dc': DC,
                   'rsdc': RSDC, 'stdc': STDC, 'rsi': RSI, 'kc': KC, 'ppo': PPO}
symbols = config.symbols
t_data = {}
t_check = {}

telegram_messages = []
discord_messages = []
symbols_state = {}
sent = []

checking = False
check_symbol = {}


def initialize(update, cycle):
    strategy = strategies_dict[config.strategy]
    for x in symbols:
        symbols_strategies[x] = strategy()


def get_data(symbol, update, context):
    while check_symbol[symbol] and checking:
        new_ohlc = get_last_bar(symbols_ohlc[symbol], symbol, symbols_strategies[symbol].interval)
        if new_ohlc is not None:
            symbols_ohlc[symbol] = new_ohlc
            t_check[symbol] = threading.Thread(target=check_conditions, args=(symbol, update, context))
            t_check[symbol].start()


def check_conditions(symbol, update, context):
    global discord_message
    alert.check_alert(update=update, symbol=symbol)
    strategy = symbols_strategies[symbol]

    ohlc = symbols_ohlc[symbol]
    strategy.add_indicators(ohlc)
    side = strategy.check_indicators(ohlc, time=ohlc.index[-1])

    if not live_trade.trading:
        if side != 0:
            if strategy.check(ohlc, time=ohlc.index[-1], test=False):
                if live_trade.check_params(symbol):
                    if not live_trade.trading:
                        live_trade.trading = True
                        t = threading.Thread(target=live_trade.main, args=(update, context, symbol,))
                        t.start()

    if strategy.message != strategy.last_message:
        if strategy.message != 'declined':
            symbols_state[symbol] = strategy.message
        strategy.last_message = strategy.message

    if len(alert.alerts.keys()) == 0 and symbol in symbols_state.keys():
        dt = datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        message = '/' + symbol + ' : ' + symbols_state[symbol]
        if strategy.interval - 2 <= int(str(utc_time)[14:16]) % strategy.interval \
                or int(str(utc_time)[14:16]) % strategy.interval <= 0:
            if symbol not in sent:
                sent.append(symbol)
                update.message.reply_text(message)
                discord_messages.append(message)
                symbols_state.pop(symbol)

        else:
            if symbol in sent:
                sent.remove(symbol)
            if strategy.message == 'declined':
                symbols_state.pop(symbol)


def run(update, context, cycle):
    global discord_message, checking
    checking = True
    t = threading.Thread(target=start, args=(update, context, cycle,))
    t.start()


def start(update, context, cycle):
    live_trade.losts = 0
    trade_journal.load()
    initialize(update, cycle)
    print('initialized')
    update.message.reply_text('checking markets')

    for symbol in symbols:
        check_symbol[symbol] = True
        symbols_ohlc[symbol] = primary_values(symbol, symbols_strategies[symbol].interval)
        t_data[symbol] = threading.Thread(target=get_data, args=(symbol, update, context))
        t_data[symbol].start()

    while True:
        for symbol in symbols:
            if not live_data.check_index(symbols_ohlc[symbol], update, symbols_strategies[symbol].interval):
                check_symbol[symbol] = False
                time.sleep(30)
                check_symbol[symbol] = True
                symbols_ohlc[symbol] = primary_values(symbol, symbols_strategies[symbol].interval)
                t_data[symbol] = threading.Thread(target=get_data, args=(symbol, update, context))
                t_data[symbol].start()
        time.sleep(60)


def stop():
    try:
        global checking
        checking = False
        live_trade.force_close()
        live_trade.trading = False
        print('shut down')
    except:
        pass
