from pdb import set_trace as BP
import inspect
import os
import yaml
from robobrowser import RoboBrowser
import requests
import smtplib
import time
import datetime
import csv
from collections import OrderedDict
from pprint import pprint

# paths
path_base = os.path.dirname(os.path.abspath(__file__))
path_output = '/output/'
path_input = '/input/'
path_input_main = path_input + 'main/'
path_input_createList = path_input + 'create-stock-lists/'
path_input_monitorProcess = path_input + 'main-process-monitor/'
path_input_template = path_input + 'templates/'

# files
glo_file_this = os.path.basename(__file__)
glo_errorLog_file = 'errorLog.csv'

glo_stockInfo_file_raw = 'stock-info-raw.csv'
glo_blacklist_file = 'blacklist.csv'
glo_complimentary_file = 'nn-complimentary-list.csv'
glo_stockInfo_file_updated = 'stock-info-updated.csv'
glo_stockToBuy_allData_file = 'stock-to-buy-all-data.csv'
glo_stockToBuy_file = 'stock-to-buy.csv'

glo_fileToRunIfCrash_main = 'main.py'
glo_pid_file = 'pid.txt'

glo_colName_sbNameshort = 'NAMESHORT_SB'
glo_colName_sbName = 'NAME_SB'
glo_colName_nameShortNordnet = 'NAMESHORT_NORDNET'
glo_colName_nameNordnet = 'NAME_NORDNET'
glo_colName_market_id = 'MARKET_ID'
glo_colName_identifier_id = 'IDENTIFIER_ID'
glo_colName_url_sb = 'URL_SB'
glo_colName_url_nn = 'URL_NN'
glo_colName_active = 'ACTIVE'
glo_colName_activeTemp = 'ACTIVE_TEMP'
glo_colName_amountHeld = 'AMOUNT_HELD'
glo_colName_price = 'PRICE'
glo_colName_priceTemp = 'PRICE_TEMP'

glo_colName_6_percent = 'MONTH_6_PERCENT_CORRECT'
glo_colName_6_value = 'MONTH_6_VALUE'
glo_colName_12_percent = 'MONTH_12_PERCENT_CORRECT'
glo_colName_12_value = 'MONTH_12_VALUE'
glo_colName_24_percent = 'MONTH_24_PERCENT_CORRECT'
glo_colName_24_value = 'MONTH_24_VALUE'
glo_colName_percentAverage = 'AVERAGE_PERCENT_CORRECT'
glo_colName_valueAverage = 'AVERAGE_VALUE'
glo_colName_24_buys_correct_percent = 'BUYS_24_PERCENT_CORRECT'
glo_colName_buysTotal = 'BUYS_TOTAL'
glo_colName_pricePercentChange_average = 'PRICE_CHANGE_PERCENT_AVERAGE'
glo_colName_pricePercentChange_median = 'PRICE_CHANGE_PERCENT_MEDIAN'
glo_colName_buyAverageFailedPerChange = 'BUY_AVERAGE_FAILED_PER_CHANGE'
glo_colName_buyAverageSuccessPerChange = 'BUY_AVERAGE_SUCCESS_PER_CHANGE'
glo_colName_buyMedianFailedPerChange = 'BUY_MEDIAN_FAILED_PER_CHANGE'
glo_colName_buyMedianSuccessPerChange = 'BUY_MEDIAN_SUCCESS_PER_CHANGE'
glo_colName_buyAndFailMedian_keyValue = 'BUYANDFAIL_MEDIAN_KEYVALUE'
glo_colName_buyAndFailAverage_keyValue = 'BUYANDFAIL_AVERAGE_KEYVALUE'
glo_colName_percentChange_highestThroughCurrent = 'PER_CHANGE_HIGHEST_THROUGH_CURRENT'
glo_colName_stockToBuy_group = 'GROUP_BUY'
glo_colName_compList = 'COMPLIMENTARY_LIST'

# mainly trader
glo_stockStatus_list = []
glo_stockStatus_list_name = 'glo_stockStatus_list'

# mainly create lists
# glo_stockInfo_list_name = 'glo_stockInfo_list'
glo_nn_complimentary_list_name = 'glo_nn_complimentary_list'
glo_blacklist_name = 'glo_blacklist'

glo_sbBaseStockPageUrl = 'https://www.swedishbulls.com/SignalPage.aspx?lang=en&Ticker='

glo_complimentary_colNames = {}
glo_stockInfoUpdated_colNames = {}
glo_stockToBuy_colNames = {}

glo_urlHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

glo_credSb = 'credSb'
glo_credNordnet = 'credNordnet'
glo_credGmailAutotrading = 'credGmailAutotrading'

glo_sbLoginFormUser = 'ctl00$MainContent$uEmail'
glo_sbLoginFormPass = 'ctl00$MainContent$uPassword'
glo_sbLoginFormSubmit = 'ctl00$MainContent$btnSubmit'

glo_clearWatchlist = 'ctl00$MainContent$DeleteAll'

glo_counter_error = 0

def incrCounterError():
    try:
        global glo_counter_error
        glo_counter_error += 1
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))    

def getCounterError():
    try:
        return glo_counter_error
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))    

def resetCounterError():
    try:
        global glo_counter_error
        glo_counter_error += 0
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))    

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
        file_errorLog = path_base + path_output + glo_errorLog_file
        file_exists = os.path.isfile(file_errorLog)
        if getCounterError() <= 100:
            with open (file_errorLog, 'a') as csvFile:
                fieldnames = [errorDate, errorTime, errorDay, errorCounter, errorMsg, errorCallingFunction]
                writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
                if not file_exists:
                    writer.writeheader()
                writer.writerow({errorDate: getDateTodayStr(), 
                    errorTime: getTimestampCustomStr('%H:%M'), 
                    errorDay: getDateTodayCustomStr('%A'), 
                    errorCounter: str(glo_counter_error),
                    errorCallingFunction: callingFunction,
                    errorMsg: eStr})
                sendEmail('ERROR: ' + callingFunction, eStr)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

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
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def getCredentials(domain):
    try:
        if domain == glo_credNordnet:
            conf = yaml.load(open(path_base + path_input + 'credentials.yml'))
            username = conf['nordnet']['username']
            pwd = conf['nordnet']['password']
            return {'username': username, 'password': pwd}
        elif domain == glo_credSb:
            conf = yaml.load(open(path_base + path_input + 'credentials.yml'))
            username = conf['sb']['username']
            pwd = conf['sb']['password']
            return {'username': username, 'pwd': pwd}
        elif domain == glo_credGmailAutotrading:
            conf = yaml.load(open(path_base + path_input + 'credentials.yml'))
            username = conf['gmail_autotrade']['username']
            pwd = conf['gmail_autotrade']['password']
            return {'username': username, 'pwd': pwd}
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def sbLogin():
    # print ('\nSTART', inspect.stack()[0][3])
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
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        # print('END', inspect.stack()[0][3], '\n')
        return (browser)

def nordnetLogin():
    # print ('\nSTART', inspect.stack()[0][3])    
    try:
        s = requests.session()
        
        header = {'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

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
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        msg = 'status code: ' + r.status_code + '; ' + r.text
        writeErrorLog(inspect.stack()[0][3], msg)
    else:
        # print('END', inspect.stack()[0][3], '\n')
        return (r, header, s)

def getDateTodayStr():
    return datetime.date.today().strftime('%Y-%m-%d')

def getTimestampCustomStr(custom):
    return datetime.datetime.now().strftime(custom)

def getDateTodayCustomStr(custom):
    return datetime.date.today().strftime(custom)

def getSecondsFromTime(days, hours, minutes, seconds):
    try:
        day_sec = 24*60*60
        hour_sec = 60*60
        min_sec = 60
        
        return days*day_sec + hours*hour_sec + minutes*min_sec + seconds
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getTimestamp():
    return datetime.datetime.now()

def getTimestampStr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

def getOrderedDictFromDict(dictTemp, order_of_keys_list):
    try:
        list_of_tuples = [(key, dictTemp[key]) for key in order_of_keys_list]
        return OrderedDict(list_of_tuples)
    except Exception as e:
        print ('ERROR in', inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e)) 

def updateListFromListByKeys(list_to_update, list_to_update_from, list_of_key_selectors, list_of_key_overwriters):
    try:
        for rowTo in list_to_update:
            for rowFrom in list_to_update_from:
                for key_selector in list_of_key_selectors:
                    if rowTo[key_selector] == rowFrom[key_selector]:
                        for key_overwriter in list_of_key_overwriters:
                            if key_overwriter in rowFrom: # if key exist in dict
                                rowTo[key_overwriter] = rowFrom[key_overwriter]
                        break
        return list_to_update
    except Exception as e:
        print ('ERROR in', inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e)) 

def removeListFromListByKey(list_to_keep, list_to_remove, list_of_key_selectors):
    try:
        unique_list = []
        for dict_keep in list_to_keep:
            not_in_list = True
            for dict_remove in list_to_remove:
                for key in list_of_key_selectors:
                    if dict_remove.get(key) == dict_keep.get(key):
                        not_in_list = False
            if not_in_list:
                unique_list.append(dict_keep)
        return unique_list
    except Exception as e:
        print ('ERROR in', inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setStockListGlobally(temp_list, name_of_list):
    try:
        # if name_of_list == glo_stockInfo_list_name:
        #     global glo_stockInfo_list
        #     glo_stockInfo_list = temp_list
        if name_of_list == glo_stockStatus_list_name:
            global glo_stockStatus_list
            glo_stockStatus_list = temp_list
    except Exception as e:
        print ('ERROR in', inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getGlobalList(name_of_list):
    try:
        # if name_of_list == glo_stockInfo_list_name:
        #     global glo_stockInfo_list
        #     glo_stockInfo_list = temp_list
        if name_of_list == glo_stockStatus_list_name:
            return glo_stockStatus_list
    except Exception as e:
        print ('ERROR in', inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getStockListFromFile(path_rel, name_of_list):
    try:
        temp_list = []
        fileNamePath = path_base + path_rel + name_of_list
        with open (fileNamePath, encoding='ISO-8859-1') as csvFile:
            records = csv.DictReader(csvFile, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
            fieldnames = records.fieldnames
            for rowDict in records:
                order_of_keys = fieldnames
                temp_list.append(getOrderedDictFromDict(rowDict, order_of_keys))
            return temp_list
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getColNamesFromFile(rel_path_of_file, file_name):
    try:
        path_full = path_base + rel_path_of_file + file_name
        with open (path_full, encoding='ISO-8859-1') as csvFile:
            records = csv.DictReader(csvFile, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
            list_of_colNames = records.fieldnames
            ordered_dict = OrderedDict()
            for colName in list_of_colNames:
                ordered_dict[colName] = ''   
            return ordered_dict
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setListKeys(list_to_set, dict_set_from):
    try:
        # add keys-value pairs to list if not existing
        for dict_to_set in list_to_set:
            for key_from, value_from in dict_set_from.items():
                if key_from not in dict_to_set:
                    dict_to_set[key_from] = value_from

        # add key-value which keys exist in dict_set_from to new list (getting rid of the rest)
        new_list = []
        for dict_to_set in list_to_set:
            new_ordered_dict = OrderedDict()
            for key_to, value_to in dict_to_set.items():
                if key_to in dict_set_from:
                    new_ordered_dict[key_to] = value_to
            new_list.append(new_ordered_dict)

        # arrange keys in new list in same order as dict_set_from
        key_order_list = list(dict_set_from.keys())
        new_ordered_list = []
        for dict_temp in new_list:
            new_ordered_list.append(OrderedDict((k, dict_temp[k]) for k in key_order_list))

        return new_ordered_list

    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setGlobalColNames():
    try:
        dict_colNames = getColNamesFromFile(path_input_template, glo_complimentary_file) # path, file
        global glo_complimentary_colNames
        glo_complimentary_colNames = dict_colNames

        dict_colNames = getColNamesFromFile(path_input_template, glo_stockInfo_file_updated) # path, file
        global glo_stockInfoUpdated_colNames
        glo_stockInfoUpdated_colNames = dict_colNames

        dict_colNames = getColNamesFromFile(path_input_template, glo_stockToBuy_file) # path, file
        global glo_stockToBuy_colNames
        glo_stockToBuy_colNames = dict_colNames

    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def main():
    try:
        setGlobalColNames()
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

main()