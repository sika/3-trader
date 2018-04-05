from pdb import set_trace as BP
# import inspect
# import csv
# import requests
# import re
# import datetime
# import time
# import fnmatch
# import yaml
# from robobrowser import RoboBrowser
# from bs4 import BeautifulSoup
# from statistics import median
# from collections import OrderedDict
# from  more_itertools import unique_everseen
# from pprint import pprint
# from pprint import pformat

pathOutput = "/output/"
pathInput = "/input/"
pathError = "/errorlog/"
pathInput_main = "/input_trader_main/"
pathInput_monitorProcess = "/input_trader_monitor_process/"

glo_stockToBuy_file_str = 'stock-to-buy.csv'
pidFile_str = 'pid.txt'

glo_colName_sbNameshort = 'NAMESHORT_SB'
glo_colName_sbName = 'NAME_SB'
glo_colName_NameShortNordnet = 'NAMESHORT_NORDNET'
glo_colName_NameNordnet = 'NAME_NORDNET'
glo_colName_price = 'PRICE'
glo_colName_market_id = 'MARKET_ID'
glo_colName_identifier_id = 'IDENTIFIER_ID'
glo_colName_url_sb = 'URL_SB'
glo_colName_url_nn = 'URL_NN'
glo_colName_held = 'HELD'
glo_colName_active = 'ACTIVE'
glo_colName_activeTemp = 'ACTIVE_TEMP'
glo_colName_amountHeld = 'AMOUNT_HELD'
glo_colName_priceTemp = 'PRICE_TEMP'

gloCredSb = 'credSb'
gloCredNordnet = 'credNordnet'
gloCredGmailAutotrading = 'credGmailAutotrading'

def getCredentials(domain):
    try:
        if domain == gloCredNordnet:
            conf = yaml.load(open(pathFileThis + pathInput + 'credentials.yml'))
            username = conf['nordnet']['username']
            pwd = conf['nordnet']['password']
            return {'username': username, 'password': pwd}
        elif domain == gloCredSb:
            conf = yaml.load(open(pathFileThis + pathInput + 'credentials.yml'))
            username = conf['sb']['username']
            pwd = conf['sb']['password']
            return {'username': username, 'pwd': pwd}
        elif domain == gloCredGmailAutotrading:
            conf = yaml.load(open(pathFileThis + pathInput + 'credentials.yml'))
            username = conf['gmail_autotrade']['username']
            pwd = conf['gmail_autotrade']['password']
            return {'username': username, 'pwd': pwd}
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def sbLogin():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        browser = RoboBrowser(history=True)
        browser.open('https://www.swedishbulls.com/Signin.aspx?lang=en')
        form = browser.get_form()
        # SB login
        credSb = getCredentials(gloCredSb)
        form[gloSbLoginFormUser].value = credSb.get('username')
        form[gloSbLoginFormPass].value = credSb.get('pwd')
        browser.submit_form(form, submit=form[gloSbLoginFormSubmit])
    except Exception as e: # catch error
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')
        return (browser)