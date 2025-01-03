import json
from types import SimpleNamespace

from statistics import Order


def save():
    json_str = json.dumps([ob.__dict__ for ob in Order.list])
    f = open("trades.txt", "w")
    # a append w overwrite
    f.write(json_str)
    f.close()


def dict_to_obj(dict):# e, max_rr, symbol, target, entry_price, stop_loss, side, time
    order = Order(dict['e'], dict['max_rr'], dict['symbol'], dict['target'], dict['entry_price'], dict['stop_loss'],
                  dict['side'], dict['time'])
    order.leverage = dict['leverage']
    order.trade_side = dict['trade_side']
    order.stop_losses = dict['stop_losses']
    order.targets = dict['targets']
    order.profit = dict['profit']
    order.exit_price = dict['exit_price']
    order.exit_rr = dict['exit_rr']
    order.exit_fee_rate = dict['exit_fee_rate']
    order.entry_fee_rate = dict['entry_fee_rate']
    order.fee = dict['fee']

    return order


def load():
    try:
        f = open("trades.txt", "r")
        json_str = f.read()
        #statistics.Order.list = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))
        #Elist = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))
        list = json.loads(json_str)
        for x in list:
            Order.list.append(dict_to_obj(x))


        #u = statistics.Order(**list[0])
        #print(u, 1)
       # for order in list:
        #    #j = json.loads(jsonstr)
        #    u = statistics.Order(**order)
         #   print(1)
         #   statistics.Order.list.append(u)
         #   print(u.symbol)
            #print(u.name)
    except Exception as e:
        print(e)
        #j = json.loads(jsonstr)
        #u = Stu(**j)
        #print(u.name)
        #x = json.loads(jsonstr, object_hook=lambda d: SimpleNamespace(**d))

