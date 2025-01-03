import math

import config

max_total_loss = config.max_total_loss
# max_total_loss = 0.05
max_leverage = config.max_leverage
fee_rate = config.fee_rate
min_e = (max_total_loss / max_leverage - 2 * fee_rate) / (1 + fee_rate)
min_rr = 1

# min % : 0.5


def calculate_leverage(entry_price, e, goal):
    # P / e = 1 + 2f * (1 + 2 / e)
    take_profit = 0
    leverage = round(max_total_loss / (abs(e) + fee_rate * (abs(e) + 2)), 1)
    L = max_total_loss
    F = leverage * fee_rate * (2 + e)
    P = (L * min_rr + F) / leverage
    if e > 0:
        take_profit = entry_price * (1 + P)
        # if goal > take_profit:
    elif e < 0:
        take_profit = entry_price * (1 - P)
        # if goal < take_profit:
    if e != 0:
        rr = P / e
        rr2 = F / leverage / e
    else:
        rr = 0
        rr2 = 0
    return leverage, take_profit, rr, rr2


def get_params(entry_price, e):
    entry_price = float(entry_price)
    e = float(e) * 0.01
    goal = entry_price * (1 + min_rr * e)
    leverage, take_profit, rr, rr2 = calculate_leverage(entry_price, e, goal)
    return leverage, take_profit, rr, rr2


def calculate_targets(entry_price, stop_loss, rr, tick_size):
    targets = []
    stop_losses = []

    e = -(stop_loss / entry_price - 1)
    """
    #targets.append((1 + 0.4 * e) * entry_price)
    stop_losses.append(stop_loss)

    targets.append((1 + 0.8 * e) * entry_price)
    #stop_losses.append((1 + -0.2 * e) * entry_price)

    targets.append((1 + 1 * e) * entry_price)
    stop_losses.append((1 + 0.2 * e) * entry_price)

    targets.append((1 + 1.2 * e) * entry_price)
    stop_losses.append((1 + 0.3 * e) * entry_price)

    targets.append((1 + 1.4 * e) * entry_price)
    stop_losses.append((1 + 0.5 * e) * entry_price)

    targets.append((1 + 1.6 * e) * entry_price)
    stop_losses.append((1 + 0.7 * e) * entry_price)

    targets.append((1 + 1.8 * e) * entry_price)
    stop_losses.append((1 + 1 * e) * entry_price)

    targets.append((1 + 2 * e) * entry_price)
    stop_losses.append((1 + 1.2 * e) * entry_price)
    """
    if rr == 0:
        rr = config.RR
    # targets.append((1 + 0.7 * e) * entry_price)
    stop_losses.append(stop_loss)

    # targets.append((1 + 1.1 * e) * entry_price)
    # stop_losses.append((1 + 0.25 * e) * entry_price)

    #targets.append((1 + 1 * e) * entry_price)
    #stop_losses.append((1 + 0.25 * e) * entry_price)

    #targets.append((1 + 1 * e) * entry_price)
    #stop_losses.append((1 + 0.5 * e) * entry_price)

    #targets.append((1 + 1 * e) * entry_price)
    #stop_losses.append((1 + 0.25 * e) * entry_price)

    #targets.append((1 + 3 * e) * entry_price)
    #stop_losses.append((1 + 2 * e) * entry_price)

    targets.append((1 + rr * e) * entry_price)
    # stop_losses.append((1 + 0.3 * e) * entry_price)

    precision = max(str(entry_price)[::-1].find('.'), str(stop_loss)[::-1].find('.'))
    digits = 1 - int(math.log10(tick_size))

    for i in range(len(targets)):
        targets[i] = round(int(targets[i] / tick_size) * tick_size, digits)
        stop_losses[i] = round(int(stop_losses[i] / tick_size) * tick_size, digits)

    return targets, stop_losses


def main():
    while True:
        # print('enter entry, e:')
        print('enter e:')
        # entry_price = float(input())
        entry_price = 1
        e = float(input())
        # r_r = float(input())
        leverage, take_profit, rr, rr2 = get_params(entry_price, e)
        print('leverage :', leverage)
        print('take profit :', round(take_profit, 5))
        print('rr :', round(rr, 2))
        print('rr2 :', round(rr2, 2))
        print('---------------------')


if __name__ == '__main__':
    main()
