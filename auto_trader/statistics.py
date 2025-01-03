import numpy as np
import config

maker_fee = 0.01 * 0.01
taker_fee = 0.06 * 0.01

# maker_fee = 0.02 * 0.01
# taker_fee = 0.06 * 0.01
max_leverage = config.max_leverage
#max_total_loss = config.max_total_loss
max_total_loss = config.max_total_loss


class Order:
    list = []

    def __init__(self, e, max_rr, symbol, target, entry_price, stop_loss, side, time):
        # self.entry = entry
        self.e = e
        self.leverage = 0
        self.max_rr = max_rr
        self.exit_rr = 0
        self.profit = 0
        self.entry_fee_rate = taker_fee
        self.exit_fee_rate = taker_fee
        self.fee = 0

        self.symbol = symbol
        self.target = target
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.stop_losses = [stop_loss]
        self.side = side
        self.time = time
        self.exit_price = 0
        self.lost = False
        self.won = False

    def calculate_leverage(self):
        leverage = round(max_total_loss / (abs(self.e) + self.entry_fee_rate + self.exit_fee_rate * (1 + self.e)), 0)
        if leverage > max_leverage:
            leverage = max_leverage
        self.leverage = leverage

    def calculate_profit(self, rr):
        if self.entry_price == 0:
            self.calculate_leverage()
            if self.max_rr >= rr and self.max_rr >= 1:
                self.exit_rr = rr
                self.exit_fee_rate = maker_fee
            elif self.max_rr >= 1:
                self.exit_rr = 0.2
                self.exit_fee_rate = taker_fee

            # elif self.max_rr >= 0.5:
            #    self.exit_rr = 0.1
            #    self.exit_fee_rate = taker_fee
            else:
                self.exit_rr = -1
                self.exit_fee_rate = taker_fee
        else:
            self.exit_rr = (self.exit_price - self.entry_price) / (self.entry_price - self.stop_losses[0])

        #if self.exit_rr >= rr * 0.95:
        #    self.exit_fee_rate = maker_fee

        self.profit = self.leverage * (self.exit_rr * abs(self.e)) - self.calculate_fee()
        return self.profit

    def calculate_fee(self):
        # F = lf (2 + e)  F = l ( f1 + f2(1+e) )
        self.fee = self.leverage * (self.entry_fee_rate + self.exit_fee_rate * (1 + self.e))
        return self.fee


def get_inputs():
    while True:
        e, max_rr = [float(x) for x in input().split()]
        if e == 0:
            break
        e *= 0.01
        Order.list.append(Order(e, max_rr, 0, 0, 0, 0, 0, 0))


def maximize_profit(RR):
    max_profit = 0
    best_rr = 0
    for rr in np.arange(1, 6, 0.25):
        #RR = 0
        if RR <= 0:
            rr = -RR
        profit = calculate_total_profit(rr)
        show_orders(rr)
        print('--------------')
        print('profit :', round(profit, 4))
        print('--------------')
        if profit > max_profit:
            best_rr = rr
            max_profit = profit
        if RR <= 0:
            break

    average_profit_per_trade = pow(max_profit, 1 / len(Order.list)) - 1
    return max_profit, best_rr, average_profit_per_trade


def calculate_total_profit(rr):
    profit = 1
    for order in Order.list:
        profit *= (1 + order.calculate_profit(rr))
    return profit


def calculate_win_rate():
    wins = 0
    rr_sum = 0
    n = len(Order.list)
    for order in Order.list:
        if order.exit_rr > 0:
            rr_sum += order.max_rr
            wins += 1
    average_rr = rr_sum / n
    return wins / n * 100, average_rr


def show_orders(rr):
    print('   e    | max rr |exit rr |leverage|  fee   | profit |   rr  |')
    for order in Order.list:
        a = [round(order.e, 4), round(order.max_rr, 4), round(order.exit_rr, 4), order.leverage, round(order.fee, 4),
             round(order.profit, 4), rr]

        for x in a:
            print(str(x) + str_n(' ', 8 - len(str(x))) + '|', end="")
        print()


def str_n(ch, n):
    st = ""
    for i in range(n):
        st += ch
    return st


def run():
    get_inputs()
    max_profit, best_rr, average_profit_per_trade = maximize_profit(1)
    win_rate, average_rr = calculate_win_rate()
    print('best rr : ', best_rr)
    print('max profit : ', max_profit)
    print('win rate : ', win_rate)
    print('average max rr : ', average_rr)
    print('average profit per trade : ', average_profit_per_trade)


def average():
    s = 0
    n = 0
    av = 0
    while True:
        x = float(input())
        if x == 0:
            print('average :', av)
            break
        n += 1
        s += x
        av = s / n


def multiply():
    profit = 1
    while True:
        x = float(input())
        if x == 0:
            print(profit)
        profit *= 1 + x

# main()
