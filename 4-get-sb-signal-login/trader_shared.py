from pdb import set_trace as BP
import inspect
import os
import yaml
from robobrowser import RoboBrowser
import requests
import smtplib
import time
import datetime
from pprint import pprint
import csv
# from bs4 import BeautifulSoup
# import re
# import datetime
# import time
# import fnmatch
# from statistics import median
# from collections import OrderedDict
# from  more_itertools import unique_everseen
# from pprint import pformat

pathOutput = "/output/"
pathInput = "/input/"
pathError = "/errorlog/"
pathInput_main = "/input_trader_main/"
pathInput_monitorProcess = "/input_trader_monitor_process/"
pathFileThis = os.path.dirname(os.path.abspath(__file__))

glo_stockToBuy_file = 'stock-to-buy.csv'
glo_errorLog_file = 'errorLog.csv'
glo_fileNameThis = os.path.basename(__file__)
glo_pidFile_str = 'pid.txt'

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

glo_credSb = 'credSb'
glo_credNordnet = 'credNordnet'
glo_credGmailAutotrading = 'credGmailAutotrading'

glo_sbLoginFormUser = 'ctl00$MainContent$uEmail'
glo_sbLoginFormPass = 'ctl00$MainContent$uPassword'
glo_sbLoginFormSubmit = 'ctl00$MainContent$btnSubmit'

glo_counter_error = 0

def incrCounterError():
    try:
        global glo_counter_error
        glo_counter_error += 1
    except Exception as e:
        print ("ERROR in file", glo_fileNameThis, 'and function' ,inspect.stack()[0][3], ':', str(e))    

def getCounterError():
    try:
        return glo_counter_error
    except Exception as e:
        print ("ERROR in file", glo_fileNameThis, 'and function' ,inspect.stack()[0][3], ':', str(e))    

def writeErrorLog (callingFunction, eStr):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        incrCounterError()
        errorDate = 'DATE'
        errorTime = 'TIME'
        errorDay = 'DAY'
        errorCounter = 'ERROR_COUNTER'
        errorCallingFunction = 'CALLING_FUNCTION'
        errorMsg = 'E_MSG'
        file_errorLog = pathFileThis + pathError + glo_errorLog_file
        file_exists = os.path.isfile(file_errorLog)
        if getCounterError() <= 100:
            with open (file_errorLog, 'a') as csvFile:
                fieldnames = [errorDate, errorTime, errorDay, errorCounter, errorMsg, errorCallingFunction]
                writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
                if not file_exists:
                    writer.writeheader()
                writer.writerow({errorDate: getDateTodayStr(), 
                    errorTime: getTimestampCustomStr("%H:%M"), 
                    errorDay: getDateTodayCustomStr('%A'), 
                    errorCounter: str(glo_counter_error),
                    errorCallingFunction: callingFunction,
                    errorMsg: eStr})
                sendEmail('ERROR: ' + callingFunction, eStr)
    except Exception as e:
        print ("ERROR in file", glo_fileNameThis, 'and function' ,inspect.stack()[0][3], ':', str(e))

def sendEmail(sbj, body):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        msg = 'Subject: {}\n\n{}'.format(sbj, body)
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        credGmailAutotrading = getCredentials(glo_credGmailAutotrading)
        smtp.login(credGmailAutotrading.get('username'), credGmailAutotrading.get('pwd'))
        smtp.sendmail(credGmailAutotrading.get('username'), credGmailAutotrading.get('username'), msg) # 1 from, 2 to
    except Exception as e:
        print ("ERROR in file", glo_fileNameThis, 'and function' ,inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def getCredentials(domain):
    try:
        if domain == glo_credNordnet:
            conf = yaml.load(open(pathFileThis + pathInput + 'credentials.yml'))
            username = conf['nordnet']['username']
            pwd = conf['nordnet']['password']
            return {'username': username, 'password': pwd}
        elif domain == glo_credSb:
            conf = yaml.load(open(pathFileThis + pathInput + 'credentials.yml'))
            username = conf['sb']['username']
            pwd = conf['sb']['password']
            return {'username': username, 'pwd': pwd}
        elif domain == glo_credGmailAutotrading:
            conf = yaml.load(open(pathFileThis + pathInput + 'credentials.yml'))
            username = conf['gmail_autotrade']['username']
            pwd = conf['gmail_autotrade']['password']
            return {'username': username, 'pwd': pwd}
    except Exception as e:
        print ("ERROR in file", glo_fileNameThis, 'and function' ,inspect.stack()[0][3], ':', str(e))

def sbLogin():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        browser = RoboBrowser(history=True)
        browser.open('https://www.swedishbulls.com/Signin.aspx?lang=en')
        form = browser.get_form()
        # SB login
        credSb = getCredentials(glo_credSb)
        form[glo_sbLoginFormUser].value = credSb.get('username')
        form[glo_sbLoginFormPass].value = credSb.get('pwd')
        browser.submit_form(form, submit=form[glo_sbLoginFormSubmit])
    except Exception as e: # catch error
        print ("ERROR in file", glo_fileNameThis, 'and function' ,inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')
        return (browser)

def nordnetLogin():
    print ('\nSTART', inspect.stack()[0][3])    
    try:
        s = requests.session()
        header = {'Accept': 'application/json'}
        urlGetLoginPage = 'https://www.nordnet.se/mux/login/start.html?cmpi=start-loggain&state=signin'
        r = s.get(urlGetLoginPage)
        if r.status_code != 200:
            print(urlGetLoginPage, 'failed!')
        # Anonymous to get cookie
        urlPostAnonymous = 'https://www.nordnet.se/api/2/login/anonymous'
        r = s.post(urlPostAnonymous, headers=header)
        if r.status_code != 200:
            print(urlPostAnonymous, 'failed!')
        # Login post
        urlPostLogin = 'https://www.nordnet.se/api/2/authentication/basic/login'
        credNord = getCredentials(glo_credNordnet)
        r = s.post(urlPostLogin, headers=header, data=credNord)

        if r.status_code != 200:
            print(urlPostLogin, 'failed!')
            print('status_code:', r.status_code)
            print('text:', r.text)
            responseDict = {
            'status_code': str(r.status_code),
            'reason': r.reason,
            'url': r.url
            }
            writeErrorLog(inspect.stack()[0][3], pformat(responseDict))
    except Exception as e: # catch error
        print ("ERROR in file", glo_fileNameThis, 'and function' ,inspect.stack()[0][3], ':', str(e))
        msg = 'status code: ' + r.status_code + '; ' + r.text
        # writeErrorLog(inspect.stack()[0][3], msg)
    else:
        print('END', inspect.stack()[0][3], '\n')
        return (r, header, s)

def getDateTodayStr():
    return datetime.date.today().strftime('%Y-%m-%d')

def getTimestampCustomStr(custom):
    return datetime.datetime.now().strftime(custom)

def getDateTodayCustomStr(custom):
    return datetime.date.today().strftime(custom)

def getTimestamp():
    return datetime.datetime.now()

def getTimestampStr():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")





# def getDateToday():
#     return datetime.date.today()

# def getDateCustomDayStr(timestamp):
#     return datetime.date.today().strftime('%Y-%m-%d')

# def getTimestampCustom(dayIncrementalInt):
#     return datetime.datetime.strptime()