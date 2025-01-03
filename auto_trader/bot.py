import asyncio
import logging
import threading

#import discord
import requests

import bybit_api
import time
from datetime import datetime, timezone

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

import calculator
import chart
import config
import live_run


import live_trade
import proxy
import statistics
from alert import Alert
from calculator import get_params
from flask import Flask, render_template, request, flash

PORT = int(os.environ.get('PORT', 5000))
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config.TELEGRAM_TOKEN
DISCORD_TOKEN = config.DISCORD_TOKEN
#client = discord.Client(intents=discord.Intents.default())
#channel = client.get_channel(config.discord_channel_number)

state = 'off'
default_symbol = 'ADA'

STOP_BARS = config.STOP_BARS
TARGET_BARS = config.TARGET_BARS

app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"


@app.route("/hello")
def index():
    flash("what's your name?")
    return render_template("index.html")


@app.route("/start")
def start():
    t = threading.Thread(target=main, args=())
    t.start()
    print('started')
    main()


@app.route("/greet", methods=['POST', 'GET'])
def greeter():
    flash("Hi " + str(request.form['name_input']) + ", great to see you!")
    return render_template("index.html")


"""
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    input = message.content.split()

    if input[0] == 'c':
        leverage, take_profit = get_params(input[1], input[2])
        await channel.send('leverage : ' + str(leverage) + '\n' + 'take profit : ' + str(take_profit))
    elif input[0] == 'state':
        if state == 'checking':
            await channel.send('checking')
        elif state == 'off':
            await channel.send('off')
    else:
        await channel.send(message.content)


async def check_for_alerts():
    while True:
        # do something
        if len(live_run.discord_messages) != 0:
            await channel.send(live_run.discord_messages[0])
            live_run.discord_messages.pop(0)
        await asyncio.sleep(1)


@client.event
async def on_ready():
    global channel
    channel = client.get_channel(880845115936084018)
    client.loop.create_task(check_for_alerts())
    print("Bot is ready!")
"""


def proxies(update, context):
    proxy.main()


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def get_balance(update, context):
    if not check_id(update, context):
        return
    bybit_api.main(update)


def get_position(update, context):
    update.message.reply_text(str(bybit_api.get_position(statistics.Order.list[-1].symbol)))


def trade(update, context):
    update.message.reply_text(live_trade.trade_status(statistics.Order.list[-1]))


def check_markets(update, context):
    global state
    if not check_id(update, context):
        return
    state = 'checking'
    # t = threading.Thread(target=wake_up())
    # t.start()
    input = update.message.text.split()
    cycle = 0
    if len(input) > 1:
        cycle = int(input[1])
    if not live_run.checking:
        live_run.checking = True
        live_run.run(update, context, cycle)
    else:
        update.message.reply_text('already checking')


def wake_up():
    while True:
        requests.get('http://' + config.heroku_app_name + '.herokuapp.com')
        time.sleep(1200)


def get_state(update, context):
    if live_trade.trading:
        update.message.reply_text('trading')
    elif state == 'checking':
        update.message.reply_text('checking')
    elif state == 'off':
        update.message.reply_text('off')


def calculate(update, context):
    input = update.message.text.split()
    x = '1'
    leverage, take_profit, rr, rr2 = get_params(x, e=input[1])
    update.message.reply_text('leverage : ' + str(leverage))
    # + '\n' + 'take profit : ' + str(take_profit))


def get_profit(update, context):
    profit = (statistics.calculate_total_profit(live_trade.RR) - 1) * 100
    update.message.reply_text('profit : ' + str(profit) + '%')


def calculate_trade_params(symbol, stop_bars, target_bars):
    leverage, rr, e, stop_index, target_index, stop_loss, target, stop_loss0 = live_run.symbols_strategies[
        symbol].get_e(ohlc=live_run.symbols_ohlc[symbol], stop_bars=stop_bars,
                      target_bars=target_bars)
    message = 'leverage = ' + str(leverage) + '\nrr = ' + str(rr) + '\nstop loss = ' + str(stop_loss0) + '\ne = ' + str(
        e) + '%'
    return message


def trade_params(update, context):
    input = update.message.text.split()
    symbol = input[1]
    if len(input) > 2:
        stop_bars = int(input[2])
    else:
        stop_bars = STOP_BARS

    if len(input) > 3:
        target_bars = int(input[3])
    else:
        target_bars = TARGET_BARS
    update.message.reply_text(calculate_trade_params(symbol, stop_bars, target_bars))


def get_targets(update, context):
    input = update.message.text.split()
    entry_price = float(input[1])
    stop_loss = float(input[2])
    targets, stop_losses = calculator.calculate_targets(entry_price, stop_loss, config.RR)
    text = ""
    for i in range(len(targets)):
        text += "stop loss " + str(i + 1) + ":  " + str(stop_losses[i]) + '  |  '
        text += "target " + str(i + 1) + ":  " + str(targets[i]) + '\n'
    update.message.reply_text(text)


def get_minute(symbol):
    interval = live_run.symbols_strategies[symbol].interval
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    minute = str(interval - int(str(utc_time)[14:16]) % interval)

    return minute


def send_all_charts(update, context):
    for symbol in live_run.symbols:
        minute = get_minute(symbol)
        caption = symbol + ' chart ' + minute + 'min'
        send_chart(update, context, symbol, caption)


def send_chart(update, context, symbol, caption):
    chart.save_chart(symbol, None)
    path = symbol + '.png'
    chat_id = update.message.chat_id
    context.bot.sendPhoto(chat_id=chat_id, photo=open(path, 'rb'), caption=caption)
    os.remove(path)


def send_journal(update, context):
    chat_id = update.message.chat_id
    context.bot.sendDocument(chat_id=chat_id, caption='trades', document=open('trades.txt', 'rb'))


def send_chart2(update, context, symbol, caption, order):
    chart.save_chart(symbol, order)
    path = symbol + '.png'
    chat_id = update.message.chat_id
    context.bot.sendPhoto(chat_id=chat_id, photo=open(path, 'rb'), caption=caption)
    os.remove(path)


def close_trade(update, context):
    if not check_id(update, context):
        return
    live_trade.force_close()


def kill_all(update, context):
    if not check_id(update, context):
        return
    live_trade.kill_all()


def stop(update, context):
    global state
    if not check_id(update, context):
        return
    state = 'off'
    live_run.stop()
    update.message.reply_text('stopped')


def available_pairs(update, context):
    text = 'available pairs :'
    for x in live_run.symbols:
        text += '\n' + x + '/USDT'
    update.message.reply_text(text)


def add_alert(update, context):
    st = update.message.text.split()
    symbol = st[1]
    price = float(st[2])
    Alert(symbol=symbol, price=price)
    update.message.reply_text('alert added successfully')


def remove_symbol(update, context):
    symbol = update.message.text.split()[1]
    live_run.symbols.remove(symbol)
    update.message.reply_text(symbol + ' removed from symbols')


def set_to_test(update, context):
    config.real = False


def check_id(update, context):
    if update.message.from_user.id == config.user_id:
        return True
    else:
        update.message.reply_text('forbidden id')
        return False


def echo(update, context):
    message = update.message.text
    symbol = message.split()[0][1:]
    if symbol in live_run.symbols:
        minute = get_minute(symbol)
        caption = symbol + ' chart ' + minute + 'mins left\n' + \
                  calculate_trade_params(symbol, STOP_BARS, TARGET_BARS).splitlines()[1]
        send_chart(update, context, symbol, caption)
    else:
        update.message.reply_text(update.message.text)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("check", check_markets))
    dp.add_handler(CommandHandler("state", get_state))
    dp.add_handler(CommandHandler("c", calculate))
    dp.add_handler(CommandHandler("all_charts", send_all_charts))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("pairs", available_pairs))
    dp.add_handler(CommandHandler("alert", add_alert))
    dp.add_handler(CommandHandler("remove", remove_symbol))
    dp.add_handler(CommandHandler("l", trade_params))
    dp.add_handler(CommandHandler("t", get_targets))
    dp.add_handler(CommandHandler("trade", trade))
    dp.add_handler(CommandHandler("balance", get_balance))
    dp.add_handler(CommandHandler("proxy", proxies))
    dp.add_handler(CommandHandler("journal", send_journal))
    dp.add_handler(CommandHandler("profit", get_profit))
    dp.add_handler(CommandHandler("close", close_trade))
    dp.add_handler(CommandHandler("kill_all", kill_all))
    dp.add_handler(CommandHandler("position", get_position))
    dp.add_handler(CommandHandler("test", set_to_test))

    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    #client.run(DISCORD_TOKEN, bot=True)

    """
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://' + config.heroku_app_name + '.herokuapp.com/' + TOKEN)
    https://trading-bot-51917.herokuapp.com/1826479237:AAF5cbzRnN66sRIzm_cw1tkd8u9MLxS1gOo
    """

    updater.idle()


if __name__ == '__main__':
    main()
