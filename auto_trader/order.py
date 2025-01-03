import analysis


class Order:
    orders = {}
    profit = 1
    exit_price = 0
    result = ''

    def __init__(self, symbol, leverage, side, entry_price, stop_loss, take_profit, time):
        self.symbol = symbol
        self.leverage = leverage
        self.side = side
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.time = time

    def calculate_profit(self):
        self.profit = (self.exit_price - self.entry_price) / self.entry_price * self.leverage * self.side \
                      - self.calculate_fee()

    def calculate_fee(self):
        return self.leverage * analysis.fee_rate * (2 + abs(self.exit_price - self.entry_price) / self.entry_price)


def profit_per_trade(symbol):
    if not symbol in Order.orders.keys():
        return None, None, None, None
    profit = 1
    n = 0
    wins = 0.0
    losses = 0.0
    for i in Order.orders[symbol]:
        o = i
        profit *= 1 + o.profit
        n += 1
        if o.result == 'won':
            wins += 1
        if o.result == 'lost':
            losses += 1
    if wins == 0 and losses == 0:
        return None, None, None, None
    return pow(profit, 1 / n) - 1, n, wins / (wins + losses), profit-1
