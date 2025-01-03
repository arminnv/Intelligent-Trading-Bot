from strategies.kc_range import KC


def run(new_strategy):
    new_cycle = int(input())
    new_strategy.set_periods(new_cycle)
    for key in new_strategy.periods:
        print(key + ' : ', new_strategy.periods[key])
    print('--------------')


while True:
    new_strategy = KC()
    print('enter cycle :')
    #print('multiplier :', round((float(input()) * 0.01) / new_strategy.band_width * new_strategy.multiplier, 1))
    run(new_strategy)
