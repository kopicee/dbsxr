from collections import namedtuple
from datetime import datetime, timedelta
# import json

from bs4 import BeautifulSoup
import requests

# URL = "https://www.dbs.com.sg/personal/rates-online/foreign-currency-foreign-exchange.page"
API_URL = 'https://www.dbs.com.sg/sg-rates-api/v1/api/sgrates/getSGFXRates'

CACHE_FILE = 'exch-rates.json'

Rate = namedtuple('Rate', 'name unit buy sell')



def timestamp(dtobj=None):
    dt = dtobj or datetime.utcnow()
    return dt.timestamp() * 1000


def get_rates(api, timestamp, cachefile=None) -> dict:
    params = {'FETCH_LATEST': timestamp}
    resp = requests.get(api, params=params)
    
    js = resp.json()

    list_single_dict = [{}]

    exch_data = js.get('results', {}) \
                  .get('assets', list_single_dict) \
                  [0] \
                  .get('recData', list_single_dict) \
                  [0]
    
    assert exch_data, \
           f'failed to fetch exchange rates from {api}, params={params}'

    main = exch_data['mainCurrencies']
    other = exch_data['otherCurrencies']

    last_update = ''
    output = {}
    
    for currency_grp in [main, other]:
        updated = currency_grp.get('lastUpdated', '')
        if updated > last_update:
            last_update = updated  # ISO 8601 string

        rateslist = currency_grp.get('rates', list_single_dict)
        for d in rateslist:
            curr_code = d['currency']
            rate = Rate(
                name=curr_code,
                unit=int(d['unit']),
                buy=float(d['amtLessThan50']['odBuy']),
                sell=float(d['amtLessThan50']['ttodSell'])
            )
            output[curr_code] = rate
    
    output['lastUpdated'] = last_update

    # if cachefile:
    #     with open(cachefile, 'w', encoding='utf-8') as f:
    #         json.dump(exch_data, f, indent=2)
    
    return output


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


def query_rates():
    return get_rates(API_URL, timestamp(), CACHE_FILE)
