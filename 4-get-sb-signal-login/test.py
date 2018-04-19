import shared as mod_shared
import create_stock_lists as mod_list
from pdb import set_trace as BP
from bs4 import BeautifulSoup
import requests
import json
import time
import datetime
from statistics import median
from pprint import pprint
from pprint import pformat


# list_of_stockStatusDicts = []
# OrderedDict([('NAMESHORT_SB', 'ARCT.ST'),
#              ('list_of_dicts',
#               'https://www.swedishbulls.com/SignalPage.aspx?lang=en&Ticker=ARCT.ST')]

glo_history_date_sb = 'date'
glo_history_price_sb = 'price'
glo_history_signal_sb = 'signal'

with requests.Session() as s:
    url = 'https://www.nordnet.se/graph/instrument/11/67373?from=1970-01-01&to=2018-04-19&fields=last,open,high,low,volume'
    r = s.get(url)
    if r.status_code != 200:
        print('something when wrong in URL request:', r.status_code)
        print('URL:', url)
    # BP()
    soup = BeautifulSoup(r.content, 'html.parser') # active are placed in "share"
    list_of_dicts_nn = json.loads(str(soup))
    # remove last item
    # list_of_dicts_nn = list_of_dicts_nn[:-1]

    list_of_dicts_sb = [
        {'date': '13.04.2018', 'price': '0.6920', 'signal': 'SHORT'},
        {'date': '11.04.2018', 'price': '0.7010', 'signal': 'BUY'},
        {'date': '03.04.2018', 'price': '0.7190', 'signal': 'SELL'}
    ]

    buy_percent_changes = []
    sellAndShort_percent_changes = []
    for dict_sb in list_of_dicts_sb:
        # '%d.%m.%Y' -> '%Y-%m-%d'
        date_sb = datetime.datetime.strptime(dict_sb.get(glo_history_date_sb), '%d.%m.%Y').strftime('%Y-%m-%d')
        price_sb = float(dict_sb.get(glo_history_price_sb))
        signal_sb = dict_sb.get(glo_history_signal_sb)
        for dict_date_nn in list_of_dicts_nn:
            # microsec -> sec + 1 (to ensure ends at correct side of date)
            epoch_sec = int(dict_date_nn.get('time')/1000)+1
            # epoch_sec -> 'YYYY-MM-DD'
            date_nn = time.strftime('%Y-%m-%d', time.localtime(epoch_sec))
            price_nn = dict_date_nn.get('last')
            if date_sb == date_nn:
                print('\ndate nn:', date_nn, '\tsignal sb:', signal_sb)
                # positive result: end_value (closing price) is higher than start_value (intraday price)
                if dict_sb.get(glo_history_signal_sb) == 'BUY':
                    print('BUY')
                    percentChange = mod_shared.getPercentChange(price_sb, price_nn) # start value; end value
                    print('percent change:', percentChange)
                    buy_percent_changes.append(percentChange)
                elif dict_sb.get(glo_history_signal_sb) == 'SELL' or dict_sb.get(glo_history_signal_sb) == 'SHORT':
                    print('SELL or SHORT')
                    percentChange = mod_shared.getPercentChange(price_sb, price_nn) # start value; end value
                    print('percent change:', percentChange)
                    sellAndShort_percent_changes.append(percentChange)
    
    median_sellAndShort_change = median(sellAndShort_percent_changes)
    average_sellAndShort_change = sum(sellAndShort_percent_changes)/float(len(sellAndShort_percent_changes))
    median_buy_change = median(buy_percent_changes)
    average_buy_change = sum(buy_percent_changes)/float(len(buy_percent_changes))
    BP()
    pass
        # if time_local != '00:00:00':
        #     pprint(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_sec)))
        #     pprint(dict_date.get('time'))
        #     BP()
        #     pass
        # epoch_sec = int(epoch_sec/1000)

# {'high': 0.54,
#   'last': 0.515,
#   'low': 0.515,
#   'open': 0.54,
#   'time': 1487286000000,
#   'volume': 35935.0},

    # time.strftime('%Y-%m-%d', time.localtime(epoch_sec))
    # soup = BeautifulSoup(s.get('https://www.nordnet.se/mux/ajax/trade/orders/auto?accountNumber=18272500', headers=mod_shared.glo_urlHeader).content, 'html.parser') # active are placed in "share"
    # newList = newDict.get('share')
    
    # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))

    # 13.04.2018  
    # 0.6920  
    # SHORT
