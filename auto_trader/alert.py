import live_run

alerts = {}


class Alert:
    def __init__(self, symbol, price):
        self.symbol = symbol
        self.price = price
        entry_price = live_run.symbols_ohlc[symbol]['close'][-1]
        if price >= entry_price:
            self.side = 1
        elif price < entry_price:
            self.side = -1
        alerts[symbol] = self


def check_alert(update, symbol):
    if symbol not in alerts:
        return
    a = alerts[symbol]
    price = live_run.symbols_ohlc[symbol]['close'][-1]
    if a.side == 1 and price >= a.price:
        message = symbol + ' has passed the limit'
        update.message.reply_text(message)
        live_run.discord_messages.append(message)
        alerts.pop(symbol)
    elif a.side == -1 and price <= a.price:
        message = symbol + ' has passed the limit'
        update.message.reply_text(message)
        live_run.discord_messages.append(message)
        alerts.pop(symbol)
