import json
import bybit
import requests
import config

client = bybit.bybit(test=False, api_key=config.api_key, api_secret=config.api_secret)


def set_leverage(symbol, leverage):
    print(client.LinearPositions.LinearPositions_switchIsolated(symbol=symbol + "USDT", is_isolated=True,
                                                                buy_leverage=leverage,
                                                                sell_leverage=leverage).result())
    print(client.LinearPositions.LinearPositions_saveLeverage(symbol=symbol + "USDT", buy_leverage=leverage,
                                                              sell_leverage=leverage).result())


def get_position_size(symbol, side):
    n = 0
    if side == 'Sell':
        n = 1
    result = client.LinearPositions.LinearPositions_myPosition(symbol=symbol + "USDT").result()
    print(result)
    return result[0]['result'][n]['size']


def get_minimum_qty(symbol):
    url = 'https://api.bybit.com/v2/public/symbols'
    result = json.loads(requests.get(url).text)['result']
    result = next(item for item in result if item["name"] == symbol + "USDT")
    return result['lot_size_filter']['min_trading_qty'], result['lot_size_filter']['qty_step'],\
        float(result['price_filter']['tick_size'])


def get_qty_step(symbol):
    url = 'https://api.bybit.com/v2/public/symbols'
    result = json.loads(requests.get(url).text)['result']
    return next(item for item in result if item["name"] == symbol + "USDT")['lot_size_filter']['qty_step']


def get_tick_size(symbol):
    url = 'https://api.bybit.com/v2/public/symbols'
    result = json.loads(requests.get(url).text)['result']
    return next(item for item in result if item["name"] == symbol + "USDT")['price_filter']['tick_size']


def place_limit_order(symbol, price, qty, side):
    result = client.LinearOrder.LinearOrder_new(
        side=side,
        symbol=symbol + "USDT",
        order_type="Limit",
        qty=qty,
        price=price,
        time_in_force="PostOnly",
        reduce_only=False,
        close_on_trigger=False
    ).result()
    print(result)

    return result[0]['ret_msg']


def place_market_order(symbol, qty, side):
    result = client.LinearOrder.LinearOrder_new(
        side=side,
        symbol=symbol + "USDT",
        order_type="Market",
        qty=qty,
        #price=10000,
        time_in_force="GoodTillCancel",
        reduce_only=False,
        close_on_trigger=False
    ).result()
    print(result)

    return result[0]['ret_msg']


def cancel_order(symbol):
    print(client.LinearConditional.LinearConditional_cancelAll(symbol=symbol + "USDT").result())


def set_stop_loss(symbol, stop_loss, side):
    print(client.LinearPositions.LinearPositions_switchMode(symbol=symbol + "USDT", tp_sl_mode="Full").result())
    result = client.LinearPositions.LinearPositions_tradingStop(
        symbol=symbol + "USDT",
        side=side,
        stop_loss=stop_loss).result()

    print(result)

    return result[0]['ret_msg']


def set_take_profit(symbol, take_profit, side):
    qty = get_position_size(symbol, side)
    print('take profit qty', qty)

    if side == "Buy":
        side = 'Sell'
    else:
        side = 'Buy'
    print(client.LinearOrder.LinearOrder_new(
        side=side,
        symbol=symbol + "USDT",
        order_type="Limit",
        qty=qty,
        price=take_profit,
        time_in_force="GoodTillCancel",
        reduce_only=True,
        close_on_trigger=False
    ).result())


def close_position(symbol, side):
    qty = get_position_size(symbol, side)

    if side == "Buy":
        side = 'Sell'
    else:
        side = 'Buy'
    print(client.LinearOrder.LinearOrder_new(
        side=side,
        symbol=symbol + "USDT",
        order_type="Market",
        qty=qty,
        time_in_force="GoodTillCancel",
        reduce_only=True,
        close_on_trigger=False
    ).result())


def used_margin():
    return float(client.Wallet.Wallet_getBalance(coin='USDT').result()[0]['result']['USDT']['used_margin'])


def get_available_balance():
    result = client.Wallet.Wallet_getBalance(coin='USDT').result()
    print(result)
    return float(result[0]['result']['USDT']['available_balance'])


def get_position(symbol):
    return client.LinearPositions.LinearPositions_myPosition(symbol=symbol + "USDT").result()


def get_entry_price(symbol, side):
    if side == 'Buy':
        n = 0
    else:
        n = 1
    return float(client.LinearPositions.LinearPositions_myPosition(symbol=symbol + "USDT").result()[0]['result'][n]['entry_price'])


def main(update):
    update.message.reply_text(str(client.Wallet.Wallet_getBalance(coin='USDT').result()))

"""
print(client.LinearPositions.LinearPositions_tradingStop(
    symbol="XRPUSDT",
    side="Buy",
    #order_type="Limit",
    take_profit=1).result())
"""
# # Conditional Orders
# Place Conditional Order
# print(client.LinearConditional.LinearConditional_new(stop_px=9989, side="Sell",symbol="BTCUSDT",order_type="Limit",qty=0.22,base_price=9900, price=10000,time_in_force="GoodTillCancel",reduce_only=False, close_on_trigger=False).result())
# Get Conditional Order
# print(client.LinearConditional.LinearConditional_getOrders(symbol="BTCUSDT").result())
# Cancel Conditional Order
# print(client.LinearConditional.LinearConditional_cancel(symbol="BTCUSDT", stop_order_id="52095ff7-b080-498e-b3a4-8b3e76c42f5e").result())
# Cancel all Conditional Orders
# print(client.LinearConditional.LinearConditional_cancelAll(symbol="BTCUSDT").result())
# Replace Conditional Order
# print(client.LinearConditional.LinearConditional_replace(symbol="BTCUSDT", stop_order_id="52095ff7-b080-498e-b3a4-8b3e76c42f5e", p_r_qty="2").result())
# Query Conditional Order(real-time)
# print(client.LinearConditional.LinearConditional_query(symbol="BTCUSDT",stop_order_id="eed0915f-d2e5-4e7d-9908-1c73d792c659").result())

# # Position
# My Position
# print(client.LinearPositions.LinearPositions_myPosition(symbol="BTCUSDT").result())
# Set Auto Add Margin
# print(client.LinearPositions.LinearPositions_setAutoAddMargin(symbol="BTCUSDT", side="Sell", auto_add_margin=False).result())
# Cross/Isolated Margin Switch
# print(client.LinearPositions.LinearPositions_switchIsolated(symbol="BTCUSDT",is_isolated=True, buy_leverage=1, sell_leverage=1).result())
# Full/Partial Position SL/TP Switch
# print(client.LinearPositions.LinearPositions_switchMode(symbol="BTCUSDT",tp_sl_mode="Full").result())
# Add/Reduce Margin
# print(client.LinearPositions.LinearPositions_changeMargin(symbol="BTCUSDT", side="Buy", margin=0.01).result())
# Set Leverage
# print(client.LinearPositions.LinearPositions_saveLeverage(symbol="BTCUSDT", buy_leverage=10, sell_leverage=10).result())
# Set Trading-Stop
# print(client.LinearPositions.LinearPositions_tradingStop(symbol="BTCUSDT", side="Buy", take_profit=10).result())
# User Trade Records
# print(client.LinearExecution.LinearExecution_getTrades(symbol="BTCUSDT").result())
# Closed Profit and Loss
# print(client.LinearPositions.LinearPositions_closePnlRecords(symbol="BTCUSDT").result())
