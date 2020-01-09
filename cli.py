import argparse
import sys

from exchrate import query_rates


def formatted(rate):
    header = f'                             SGD : {rate.name}'
    buy_template = ''
    sell_template = ''

    fmt = fmt_float

    if rate.sell:
        buy_per_sgd = rate.unit / rate.sell

        buy_500sgd = 500 * buy_per_sgd
        buy_500sgd_2sf = int(float('%.1g' % buy_500sgd))
        adjust = buy_500sgd_2sf - buy_500sgd
        adjusted_500sgd = 500 + (adjust / buy_per_sgd)

        buy_per_unit = rate.sell if rate.sell > (1 / rate.unit) else 0

        buy_template = f"""
        Buying from DBS        1 : {buy_per_sgd:.03f}
        Buying from DBS    {fmt(buy_per_unit)} : {rate.unit}
        Buying from DBS  {fmt(adjusted_500sgd)} : {buy_500sgd_2sf:.2f}"""

    if rate.buy:
        sell_per_sgd = rate.unit / rate.buy
        adjust = rate.unit - sell_per_sgd
        adjusted_2sf = 1 + (adjust / sell_per_sgd)

        sell_template = f"""
        Selling to DBS         1 : {sell_per_sgd:.2f}
        Selling to DBS     {fmt(adjusted_2sf)} : {rate.unit}"""

    if not (rate.buy or rate.sell):
        header = ''

    return f'{header}{buy_template}{sell_template}'


def fmt_float(num):
    mag, suffix = magnitude(num)
    num = num / mag

    fmt = '{number:> 3.02f}{suffix}'
    # if num >= 1:
    #     fmt = '{int(number)}{suffix}'

    return fmt.format(number=num, suffix=suffix)



def magnitude(n):
    magnitude = 1
    suffix = ''

    for mag, sfx in [
        # (1000, 'k'),
        (1000000, ' mil.')
    ]:
        if n > mag:
            magnitude = mag
            suffix = sfx
        else:
            break

    return magnitude, suffix



def main():
    parser = argparse.ArgumentParser(description='Currency calculator for DBS '
                                                 'exchange rates')

    parser.add_argument('-l', '--list',
                        action='store_true',
                        help='lists available currencies and exits')

    parser.add_argument('currencies',
                        metavar='CUR',
                        nargs='+',
                        help='currencies to calculate, in 3-letter code form '
                             '(use -l to list); examples: jpy usd hkd')

    args = parser.parse_args()

    rates = query_rates()

    if args.list:
        print('Available currencies:')
        print(', '.join(sorted(rates)))
        sys.exit(0)

    print()
    for curr in args.currencies:
        curr = curr.upper()
        
        fmt = f'        (No data available for {curr})'
        
        if curr in rates:
            data = rates[curr]
            fmt = formatted(data)

        print(fmt)
        print()


if __name__ == '__main__':
    main()

