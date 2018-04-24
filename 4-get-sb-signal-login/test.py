import shared as mod_shared
import create_stock_lists as mod_list
from pdb import set_trace as BP
from bs4 import BeautifulSoup
import json
import time
import datetime
import inspect
from statistics import median
from pprint import pprint
from pprint import pformat
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import sys
import os    

glo_file_this = os.path.basename(__file__)

def test():
    try:
        test = 'shit'
        [][2]
    except Exception as e:
        # print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
        # print ('Error on line', format(sys.exc_info()[-1].tb_lineno), ':', str(e))
        # print ('\nERROR: \n\tFile:', glo_file_this, '\n\tFunction:', inspect.stack()[0][3], '\n\tLine:', format(sys.exc_info()[-1].tb_lineno), '\n\tError:', str(e), '\n')
        print ('\nERROR: \n\tFile:', glo_file_this, '\n\tFunction:', inspect.stack()[0][3], '\n\tLine:', format(sys.exc_info()[-1].tb_lineno), '\n\tError:', str(e), '\n')

test()

# # def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
# def requests_retry_session(retries=3, backoff_factor=0.3, session=None):
#     try:
#         session = session or requests.Session()
#         retry = Retry(
#             total=retries,
#             read=retries,
#             connect=retries,
#             backoff_factor=backoff_factor,
#             # status_forcelist=status_forcelist,
#         )
#         adapter = HTTPAdapter(max_retries=retry)
#         session.mount('http://', adapter)
#         session.mount('https://', adapter)
#         return session
        
#     except Exception as e:
#         print ('ERROR in function' ,inspect.stack()[0][3], ':', str(e))

# try:
#     url1 = 'http://localhost:9999'
#     url2 = 'https://www.swedishbulls.com/Default.aspx?lang=en'
#     urls = [url1, url2]
#     list_of_stocks_failed = []
#     stock_requests_retry = False
#     while urls:
#         list_of_stocks_to_retry = []
#         for url in urls:
#             t0 = time.time()
#             try:
#                 print('\nrequesting', url)
#                 response = requests_retry_session().get(url)
#             except Exception as x:
#                 print('It failed :(', str(x))
#                 if stock_requests_retry:
#                     list_of_stocks_failed.append(url)
#                     pass
#                 else:
#                     list_of_stocks_to_retry.append(url)
#                 continue
#             else:
#                 print('It eventually worked', response.status_code)
#             finally:
#                 t1 = time.time()
#                 print('Took', t1 - t0, 'seconds')
#         if list_of_stocks_to_retry:
#             print('\nstock url requests failed:')
#             pprint(list_of_stocks_to_retry)
#             pprint('trying one more time')
#             urls = list(list_of_stocks_to_retry)
#             stock_requests_retry = True
#         else:
#             urls = False

#     print('\nurls still failed after retry:')
#     pprint(list_of_stocks_failed)
#     # sendEmail

# except Exception as x:
#     print('outer Exception')
#     pass


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

# (median_buy_success_change - glo_costOfBuy)*buys_correct_decimal_24
# + 
# (median_buy_failed_change + glo_costOfBuy)*(1-buys_correct_decimal_24)


# (median_buy_success_change - x)*y + (median_buy_failed_change + x)*(-y+1)

# <->
# (y * (median_buy_success_change - x)*1) + (-y(median_buy_failed_change + x)*1

# <->
# y ((median_buy_success_change - x) + (-(median_buy_failed_change + x)) )

# yx (median_buy_success_change -1 ) + (-median_buy_failed_change)