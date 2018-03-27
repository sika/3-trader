from pdb import set_trace as BP
import inspect
import os
import csv
import requests
import re
import datetime
import time
import fnmatch
import yaml
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup
from statistics import median
from collections import OrderedDict
from  more_itertools import unique_everseen
from pprint import pprint
from pprint import pformat

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

glo_stockInfo_input_str = 'input-stock-info.csv'
glo_stockInfo_input_test_str = 'input-stock-info-'
glo_stockInfo_output_str = 'output-stock-info.csv'
glo_stockToBuy_output_str = 'stock-to-buy.csv'
glo_stockInfo_output_noFileEnd_str = 'output-stock-info'
glo_blacklist_input_str = 'blacklist.csv'
glo_complimentary_input_str = 'complimentary-list.csv'
glo_stockInfo_list = []
glo_sbGeneralUrl_str = 'https://www.swedishbulls.com/SignalPage.aspx?lang=en&Ticker='

glo_stockInfoColName_sbNameshort = 'NAMESHORT_SB'
glo_stockInfoColName_sbName = 'NAME_SB'
glo_stockInfoColName_price = 'PRICE'
glo_stockInfoColName_6_percent = 'MONTH_6_PERCENT_CORRECT'
glo_stockInfoColName_6_value = 'MONTH_6_VALUE'
glo_stockInfoColName_12_percent = 'MONTH_12_PERCENT_CORRECT'
glo_stockInfoColName_12_value = 'MONTH_12_VALUE'
glo_stockInfoColName_24_percent = 'MONTH_24_PERCENT_CORRECT'
glo_stockInfoColName_24_value = 'MONTH_24_VALUE'
glo_stockInfoColName_percentAverage = 'AVERAGE_PERCENT_CORRECT'
glo_stockInfoColName_valueAverage = 'AVERAGE_VALUE'
glo_stockInfoColName_24_buys_correct_percent = 'BUYS_24_PERCENT_CORRECT'
glo_stockInfoColName_buysTotal = 'BUYS_TOTAL'
glo_stockInfoColName_pricePercentChange_average = 'PRICE_CHANGE_PERCENT_AVERAGE'
glo_stockInfoColName_pricePercentChange_median = 'PRICE_CHANGE_PERCENT_MEDIAN'
glo_stockInfoColName_buyAverageFailedPerChange = 'BUY_AVERAGE_FAILED_PER_CHANGE'
glo_stockInfoColName_buyAverageSuccessPerChange = 'BUY_AVERAGE_SUCCESS_PER_CHANGE'
glo_stockInfoColName_buyMedianFailedPerChange = 'BUY_MEDIAN_FAILED_PER_CHANGE'
glo_stockInfoColName_buyMedianSuccessPerChange = 'BUY_MEDIAN_SUCCESS_PER_CHANGE'
glo_stockInfoColName_buyAndFailMedian_keyValue = 'BUYANDFAIL_MEDIAN_KEYVALUE'
glo_stockInfoColName_buyAndFailAverage_keyValue = 'BUYANDFAIL_AVERAGE_KEYVALUE'
glo_stockInfoColName_percentChange_highestThroughCurrent = 'PER_CHANGE_HIGHEST_THROUGH_CURRENT'
glo_stockInfoColName_stockToBuy_group = 'GROUP_BUY'
glo_stockInfoColName_url_sb = 'URL_SB'
glo_stockInfoColName_market_id = 'MARKET_ID'
glo_stockInfoColName_identifier_id = 'IDENTIFIER_ID'
glo_stockInfoColName_url_nn = 'URL_NN'

glo_filteredStockInfo_list = []
glo_costOfBuy = 0.8

glo_stockInfo_value_notAvailable = 'N/A'

glo_iterations_limit = 1000

glo_blacklist = []

glo_complimentary_list = []

gloCredSb = 'credSb'
gloCredNordnet = 'credNordnet'
gloCredGmailAutotrading = 'credGmailAutotrading'

gloSbLoginFormUser = 'ctl00$MainContent$uEmail'
gloSbLoginFormPass = 'ctl00$MainContent$uPassword'
gloSbLoginFormSubmit = 'ctl00$MainContent$btnSubmit'

def getCredentials(domain):
    try:
        if domain == gloCredNordnet:
            conf = yaml.load(open(pathFile + sPathInput + 'credentials.yml'))
            username = conf['nordnet']['username']
            pwd = conf['nordnet']['password']
            return {'username': username, 'password': pwd}
        elif domain == gloCredSb:
            conf = yaml.load(open(pathFile + sPathInput + 'credentials.yml'))
            username = conf['sb']['username']
            pwd = conf['sb']['password']
            return {'username': username, 'pwd': pwd}
        elif domain == gloCredGmailAutotrading:
            conf = yaml.load(open(pathFile + sPathInput + 'credentials.yml'))
            username = conf['gmail_autotrade']['username']
            pwd = conf['gmail_autotrade']['password']
            return {'username': username, 'pwd': pwd}
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def getDateTodayStr():
    return datetime.date.today().strftime('%Y-%m-%d')

def getStockList():
    try:
        fieldnames = [glo_stockInfoColName_sbNameshort, glo_stockInfoColName_sbName]
        
        # for file in os.listdir('.'):
        fileNamePath_stock_info_test = ''
        for file in os.listdir(pathFile + sPathInput): #if test file exist, use that
            if fnmatch.fnmatch(file, glo_stockInfo_input_test_str+'*'):
                fileNamePath_stock_info_test = pathFile + sPathInput + file
        test_file_exists = os.path.isfile(fileNamePath_stock_info_test)
        fileNamePath_stock_info = pathFile + sPathInput + glo_stockInfo_input_str
        
        if test_file_exists:
            with open (fileNamePath_stock_info_test) as csvFile:
                records = csv.DictReader(csvFile, fieldnames=fieldnames, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
                next(csvFile) #SKIP header
                for rowDict in records:
                    order_of_keys = fieldnames
                    setStockList(getOrderedDictFromDict(rowDict, order_of_keys))
                temp_glo_stockInfo_list = glo_stockInfo_list
                return temp_glo_stockInfo_list
        else: #original file with all stocks
            with open (fileNamePath_stock_info) as csvFile:
                records = csv.DictReader(csvFile, fieldnames=fieldnames, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
                next(csvFile) #SKIP header
                for rowDict in records:
                    order_of_keys = fieldnames
                    setStockList(getOrderedDictFromDict(rowDict, order_of_keys))
                temp_glo_stockInfo_list = glo_stockInfo_list
                return temp_glo_stockInfo_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def setStockList(rowDict):
    try:
        global glo_stockInfo_list
        glo_stockInfo_list.append(rowDict)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def updateStockList(dict, sbNameshort):
    try:
        global glo_stockInfo_list
        temp_glo_stockInfo_list = glo_stockInfo_list
        for row in temp_glo_stockInfo_list:
            if row.get(glo_stockInfoColName_sbNameshort) == sbNameshort:
                row.update(dict)
                break
        glo_stockInfo_list = temp_glo_stockInfo_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e)) 

def getBlacklist():
    try:
        fieldnames = [glo_stockInfoColName_sbNameshort, glo_stockInfoColName_sbName]
        fileNamePath_blacklist = pathFile + sPathInput + glo_blacklist_input_str
        with open (fileNamePath_blacklist) as csvFile:
            records = csv.DictReader(csvFile, fieldnames=fieldnames, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
            next(csvFile) #SKIP header
            for rowDict in records:
                order_of_keys = fieldnames
                setBlacklist(getOrderedDictFromDict(rowDict, order_of_keys))
            temp_glo_blacklist = glo_blacklist
            return temp_glo_blacklist
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def setBlacklist(rowDict):
    try:
        global glo_blacklist
        glo_blacklist.append(rowDict)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))  

def getComplimentaryList():
    try:
        # fieldnames = [glo_stockInfoColName_sbNameshort, glo_stockInfoColName_sbName, glo_stockInfoColName_url_nn]
        fileNamePath_complimentary = pathFile + sPathInput + glo_complimentary_input_str
        with open (fileNamePath_complimentary) as csvFile:
            records = csv.DictReader(csvFile, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
            fieldnames = records.fieldnames
            next(csvFile) #SKIP header
            for rowDict in records:
                order_of_keys = fieldnames
                setComplimentaryList(getOrderedDictFromDict(rowDict, order_of_keys))
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def setComplimentaryList(rowDict):
    try:
        global glo_complimentary_list
        glo_complimentary_list.append(rowDict)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e)) 

def getListFromCsv(name):
    try:
        temp_list = []
        fileNamePath = pathFile + sPathInput + name
        with open (fileNamePath) as csvFile:
            records = csv.DictReader(csvFile, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
            fieldnames = records.fieldnames
            next(csvFile) #SKIP header
            for rowDict in records:
                order_of_keys = fieldnames
                orderedDict = getOrderedDictFromDict(rowDict, order_of_keys)
                temp_list.append(orderedDict)
        return temp_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def removeListFromList(listToKeep, listToRemove):
    try:
        new_list = list(listToKeep) # create new list rathen than assigning reference
        for itemToKeep in listToKeep:
            for itemToRemove in listToRemove:
                if itemToKeep[glo_stockInfoColName_sbNameshort] == itemToRemove[glo_stockInfoColName_sbNameshort]:
                    new_list.remove(itemToKeep)
                    break
        return new_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))  

def isComplimentaryStock(sbNameshort):
    try:
        for item in glo_complimentary_list:
            if item[glo_stockInfoColName_sbNameshort] == sbNameshort:
                return True
        return False
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))    

def getNnUrl(sbNameshort):
    try:
        for item in glo_complimentary_list:
            if item[glo_stockInfoColName_sbNameshort] == sbNameshort:
                return item[glo_stockInfoColName_url_nn]
        return False
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))       

def setFilteredStockList(rowDict):
    try:
        global glo_filteredStockInfo_list
        glo_filteredStockInfo_list.append(rowDict)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))  

def filterFilteredStockInfo(column_key, criteria, temp_glo_filteredStockInfo_list):
    try:
        temp_list= []
        if column_key == glo_stockInfoColName_buysTotal: #total buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == glo_stockInfoColName_24_buys_correct_percent: # percent correct buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == glo_stockInfoColName_buyAndFailMedian_keyValue: # percent correct buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == glo_stockInfoColName_buyAndFailAverage_keyValue: # percent correct buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    # if row.get(column_key) >= criteria:
                    temp_list.append(row)
        temp_glo_filteredStockInfo_list = temp_list
        return temp_glo_filteredStockInfo_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))     

def getOrderedDictFromDict(dictTemp, order_of_keys):
    try:
        list_of_tuples = [(key, dictTemp[key]) for key in order_of_keys]
        return OrderedDict(list_of_tuples)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))     

def writeStockList(listTemp, name):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        if name == glo_stockToBuy_output_str:
            file_confStat = pathFile + sPathInput + glo_stockToBuy_output_str
        elif name == glo_stockInfo_output_str:
            file_confStat = pathFile + sPathOutput + glo_stockInfo_output_str
        with open (file_confStat, 'w') as csvFile:
            fieldnames = []
            indexWithMaxNumOfKeys = 0
            maxNumOfKeys = 0
            counter = 0
            # get index with most number of keys to get correct fieldnames
            for dictTemp in listTemp:
                if len(dictTemp.keys()) > maxNumOfKeys:
                    maxNumOfKeys = len(dictTemp.keys())
                    indexWithMaxNumOfKeys = counter
                if counter == len(listTemp)-1:
                    break
                else:
                    counter += 1
            for key in listTemp[indexWithMaxNumOfKeys]:
                fieldnames.append(key)
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
            writer.writeheader()
            for row in listTemp:
                writer.writerow(row)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def getStocksFromSb(temp_glo_stockInfo_list):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        counter = 2
        with requests.Session() as s:
            for row in temp_glo_stockInfo_list:
                if counter > glo_iterations_limit:
                    break
                sbNameshort = row.get(glo_stockInfoColName_sbNameshort)
                print (counter, ':' ,sbNameshort)
                counter += 1
                url_postfix = sbNameshort
                url = glo_sbGeneralUrl_str + url_postfix
                r = s.get(url)
                if r.status_code != 200:
                    print('something when wrong in URL request:', r.status_code)
                    print('URL:', url)
                url_response = r.url
                if url_response.find('SignalPage') == -1:
                    print('NOT FOUND, skipping:', r.url)
                    continue
                soup = BeautifulSoup(r.content, 'html.parser')
                
                # break if stock's last signal is QUIT
                rows_months_24 = soup.find_all(id=re.compile("MainContent_signalpagehistory_PatternHistory24_DXDataRow"))
                array_length_24 = len(rows_months_24)
                if array_length_24 == 0: # page returned contained no stock list
                    print('page returned contained no stock list - skipping')
                    continue
                
                signal_quit = rows_months_24[0].find_all('td')[2].get_text() # stock is QUIT
                if signal_quit == 'QUIT':
                    print('Stock list last signal was', signal_quit ,'- skipping')
                    continue

                percent_6 = percent_12 = percent_24 = percent_average = price_last_close = 'N/A'

                try:
                    price_last_close = float(soup.find(id='MainContent_lastpriceboxsub').get_text(strip=True).replace(',', ''))
                except Exception as e:
                    print('price_last_close FAILED')
                    print ("ERROR in", inspect.stack()[0][3], ':', str(e))
                    pass

                # get value and total percent correct for last 6 months
                all_imgTags_6_month = soup.find_all(id=re.compile("MainContent_signalpagehistory_PatternHistory6_cell"))
                if not all_imgTags_6_month: #list is empty
                    print('returned empty list with SOUP')
                    continue
                value_6 = soup.find(id=re.compile("MainContent_signalpagehistory_PatternHistory6_cell")).parent.parent.next_sibling.get_text()                
                value_6 = int(float(value_6.replace(",", "")))
                total_checks = len(all_imgTags_6_month)
                counter_uncheck = 0
                if all_imgTags_6_month is not None and total_checks != 0:
                    for imgtag in all_imgTags_6_month:
                        srcName = imgtag['src'].lower() #'img/Uncheck.gif' in lower case 
                        if srcName.find('uncheck') != -1: # "uncheck" spelling more reliable than "check"
                            counter_uncheck += 1
                    counter_check = total_checks-counter_uncheck
                    percent_6 = round(100*(float(counter_check)/float(total_checks)), 1)

                # get value and total percent correct for last 12 months
                all_imgTags_12_month = soup.find_all(id=re.compile("MainContent_signalpagehistory_PatternHistory12_cell"))
                value_12 = soup.find(id=re.compile("MainContent_signalpagehistory_PatternHistory12_cell")).parent.parent.next_sibling.get_text()
                value_12 = int(float(value_12.replace(",", "")))
                total_checks = len(all_imgTags_12_month)
                counter_uncheck = 0
                if all_imgTags_12_month is not None and total_checks != 0:
                    for imgtag in all_imgTags_12_month:
                        srcName = imgtag['src'].lower() #'img/Uncheck.gif' in lower case 
                        if srcName.find('uncheck') != -1: # "uncheck" spelling more reliable than "check"
                            counter_uncheck += 1
                    counter_check = total_checks-counter_uncheck
                    percent_12 = round(100*(float(counter_check)/float(total_checks)), 1)

                # get value and total percent correct for last 24 months
                all_imgTags_24_month = soup.find_all(id=re.compile("MainContent_signalpagehistory_PatternHistory24_cell"))
                value_24 = soup.find(id=re.compile("MainContent_signalpagehistory_PatternHistory24_cell")).parent.parent.next_sibling.get_text()
                value_24 = int(float(value_24.replace(",", "")))
                total_checks = len(all_imgTags_24_month)
                counter_uncheck = 0
                if all_imgTags_24_month is not None and total_checks != 0:
                    for imgtag in all_imgTags_24_month:
                        srcName = imgtag['src'].lower() #'img/Uncheck.gif' in lower case 
                        if srcName.find('uncheck') != -1: # "uncheck" spelling more reliable than "check"
                            counter_uncheck += 1
                    counter_check = total_checks-counter_uncheck
                    percent_24 = round(100*(float(counter_check)/float(total_checks)), 1)

                # buy percentage correct
                counter_buys = 0
                counter_buys_uncheck = 0
                for i in range(0,array_length_24-1):
                    srcName = rows_months_24[i].find_all('td')[3].img['src'].lower()
                    if srcName.find('boschecked') != -1: # signal result not yet confirmed
                        continue
                    signal = rows_months_24[i].find_all('td')[2].get_text()
                    # total buys
                    if signal == 'BUY':
                        counter_buys +=1
                    if signal == 'BUY' and srcName.find('uncheck') != -1: # "uncheck" spelling more reliable than "check"
                        counter_buys_uncheck += 1

                counter_buys_check = counter_buys - counter_buys_uncheck
                buys_correct_percent_24 = round(100*(float(counter_buys_check)/float(counter_buys)), 1)
                # average percent
                percent_list = [percent_6, percent_12, percent_24]
                counter_percent_items = 0
                percent_sum = 0
                for percent in percent_list:
                    if percent != 'N/A':
                        percent_sum += percent
                        counter_percent_items += 1
                if counter_percent_items != 0:
                    percent_average = round(percent_sum/counter_percent_items, 1)

                # average value
                value_list = [value_6, value_12, value_24]
                value_sum = 0
                for value in value_list:
                    value_sum += value
                value_average = int(value_sum/len(value_list))

                # average buy percentage change and median value for success and failed results
                buy_total_failed_per_change = 0
                buy_total_success_per_change = 0
                buys_failed = 0
                buys_success = 0
                buy_median_failed_per_change = []
                buy_median_success_per_change = []
                for i in range(0, array_length_24-1):
                    signalConfirmationFormer = rows_months_24[i+1].find_all('td')[3].img['src'].lower()
                    if signalConfirmationFormer.find('boschecked') != -1: # signal result not yet confirmed
                        continue        
                    signalCurrent = rows_months_24[i].find_all('td')[2].get_text()
                    priceCurrent = float(rows_months_24[i].find_all('td')[1].get_text().replace(',', ''))
                    signalFormer = rows_months_24[i+1].find_all('td')[2].get_text()
                    priceFormer = float(rows_months_24[i+1].find_all('td')[1].get_text().replace(',', ''))

                    if signalCurrent == 'SHORT' or signalCurrent == 'SELL' and signalFormer == 'BUY':
                        if signalConfirmationFormer.find('uncheck') != -1: # failed buy
                            buy_median_failed_per_change.append(((priceCurrent/priceFormer)-1)*100)
                            buy_total_failed_per_change += ((priceCurrent/priceFormer)-1)*100
                            buys_failed += 1
                        else:
                            buy_median_success_per_change.append(((priceCurrent/priceFormer)-1)*100)
                            buy_total_success_per_change += ((priceCurrent/priceFormer)-1)*100
                            buys_success += 1

                average_buy_failed_per_change = round(buy_total_failed_per_change/buys_failed, 2)
                median_buy_failed_per_change = round(median(buy_median_failed_per_change), 2)
                average_buy_success_per_change = round(buy_total_success_per_change/buys_success, 2)
                median_buy_success_per_change = round(median(buy_median_success_per_change), 2)

                buys_correct_decimal_24 = buys_correct_percent_24/100
                median_buyAndFail_keyValue_cost08Percent = round(((median_buy_success_per_change - glo_costOfBuy)*buys_correct_decimal_24) - ((abs(median_buy_failed_per_change) + glo_costOfBuy)*(1-buys_correct_decimal_24)), 2)
                average_buyAndFail_keyValue_cost08Percent = round(((average_buy_success_per_change - glo_costOfBuy)*buys_correct_decimal_24) - ((abs(average_buy_failed_per_change) + glo_costOfBuy)*(1-buys_correct_decimal_24)), 2)


                buys_total = buys_success + buys_failed
                # current price compared to highest price percentage change
                price_high = 0
                price_current = 0
                for i in range(0, array_length_24-1):
                    if i == 0:
                        price_current = float(rows_months_24[i].find_all('td')[1].get_text().replace(',', ''))
                    temp_price = float(rows_months_24[i].find_all('td')[1].get_text().replace(',', ''))
                    if temp_price > price_high:
                        price_high = temp_price

                price_highest_through_current = round((price_high/price_current), 2) # 4/2 = (2-1)*100

                # average percent change between signals (neutral +- sign)
                percent_change_total = 0
                for i in range(0, array_length_24-1):
                    price_new = float(rows_months_24[i].find_all('td')[1].get_text().replace(',', ''))
                    price_old = float(rows_months_24[i+1].find_all('td')[1].get_text().replace(',', ''))
                    price_change = abs(((price_new-price_old)/price_old)*100)
                    percent_change_total += price_change

                percent_change_price_average = round(percent_change_total/(array_length_24-1), 2)

                # median percent change between signals (neutral +- sign)
                percent_change_total = 0
                percent_change_list = []
                for i in range(0, array_length_24-1):
                    price_new = float(rows_months_24[i].find_all('td')[1].get_text().replace(',', ''))
                    price_old = float(rows_months_24[i+1].find_all('td')[1].get_text().replace(',', ''))
                    price_change = abs(((price_new-price_old)/price_old)*100)
                    percent_change_list.append(price_change)

                # percent_change_price_average = round(percent_change_total/(array_length-1), 2)
                percent_change_price_median = round(median(percent_change_list), 2)

                list_of_tuples = [(glo_stockInfoColName_price, price_last_close),
                (glo_stockInfoColName_6_percent, percent_6),
                (glo_stockInfoColName_6_value, value_6),
                (glo_stockInfoColName_12_percent, percent_12),
                (glo_stockInfoColName_12_value, value_12),
                (glo_stockInfoColName_24_percent, percent_24),
                (glo_stockInfoColName_24_value, value_24),
                (glo_stockInfoColName_percentAverage, percent_average),
                (glo_stockInfoColName_valueAverage, value_average),
                (glo_stockInfoColName_buysTotal, buys_total),
                (glo_stockInfoColName_24_buys_correct_percent, buys_correct_percent_24),
                (glo_stockInfoColName_pricePercentChange_average, percent_change_price_average),
                (glo_stockInfoColName_pricePercentChange_median, percent_change_price_median),
                (glo_stockInfoColName_buyAverageFailedPerChange, average_buy_failed_per_change),
                (glo_stockInfoColName_buyMedianFailedPerChange, median_buy_failed_per_change),
                (glo_stockInfoColName_buyAverageSuccessPerChange, average_buy_success_per_change),
                (glo_stockInfoColName_buyMedianSuccessPerChange, median_buy_success_per_change),
                (glo_stockInfoColName_buyAndFailMedian_keyValue, median_buyAndFail_keyValue_cost08Percent),
                (glo_stockInfoColName_buyAndFailAverage_keyValue, average_buyAndFail_keyValue_cost08Percent),
                (glo_stockInfoColName_percentChange_highestThroughCurrent, price_highest_through_current),
                (glo_stockInfoColName_url_sb, url)]

                dictOrdered = OrderedDict(list_of_tuples)
                updateStockList(dictOrdered, sbNameshort)
        temp_glo_stockInfo_list = glo_stockInfo_list
        return temp_glo_stockInfo_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def getStocksFromNn(temp_glo_stockInfo_list):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        counter = 2 
        with requests.Session() as s:
            for row in temp_glo_stockInfo_list:
                sbNameshort = row.get(glo_stockInfoColName_sbNameshort)
                if counter > glo_iterations_limit:
                    break
                print(counter,':',sbNameshort)
                counter += 1

                if row.get(glo_stockInfoColName_url_sb) is None:
                    print(glo_stockInfoColName_url_sb, 'was None - skipping')
                    continue

                # checking complimentary list
                if isComplimentaryStock(row.get(glo_stockInfoColName_sbNameshort)):
                    url_stock = getNnUrl(row.get(glo_stockInfoColName_sbNameshort))
                    result = re.search('identifier=(.*)&', url_stock)
                    identifier_id = result.group(1)

                    result = re.search('marketid=(.*)', url_stock)
                    market_id = result.group(1)

                    list_of_tuples = [(glo_stockInfoColName_market_id, market_id),
                  (glo_stockInfoColName_identifier_id, identifier_id),
                  (glo_stockInfoColName_url_nn, url_stock)]

                    dictOrdered = OrderedDict(list_of_tuples)
                    updateStockList(dictOrdered, sbNameshort)
                    continue

                sbNameshortList = re.findall(r"[\w']+", sbNameshort)
                sbNameshortSplit = ''
                array_length = len(sbNameshortList)
                for i in range(0, array_length-1): # skip last word (e.g., 'ST', 'NGM')
                    if i < array_length-1:
                        sbNameshortSplit += ' ' + sbNameshortList[i]
                # remove leading ' '
                sbNameshortSplit = sbNameshortSplit[1:]
                sbNameshortList = sbNameshortSplit.split()
                # get query:
                query = ''
                for word in sbNameshortList:
                    # will yield ex '+AGORA+PREF'
                    query += '+' + word
                # remove leading '+'
                query = query[1:]
                urlNn = 'https://www.nordnet.se'
                urlNnSearch = 'https://www.nordnet.se/search/load.html'
                payload = {
                'query': query,
                'type': 'instrument'
                }

                # Initial stock search
                r = s.post('https://www.nordnet.se/search/load.html', data=payload)
                if r.status_code != 200:
                    print('something when wrong in URL request:', r.status_code)
                    print('URL:', urlNnSearch)
                soup = BeautifulSoup(r.content, 'html.parser')
                nnNameshort = ''
                try: #checking 3 top results in search result list
                    urlNnStock_rel = soup.find(id=re.compile('search-results-container')).a['href'] # first href (relative), such as '/mux/web/marknaden/aktiehemsidan/index.html?identifier=1007&marketid=11'
                    urlNnStock_rel_list = soup.find(id=re.compile('search-results-container')).find_all('div', class_='instrument-name') # all divs (containing a tags) in search result
                    if urlNnStock_rel_list: # if list not empty
                        for i in range(0,2):
                            # get IDs
                            result = re.search('identifier=(.*)&', urlNnStock_rel_list[i].a['href'])
                            identifier_id = result.group(1)

                            result = re.search('marketid=(.*)', urlNnStock_rel_list[i].a['href'])
                            market_id = result.group(1)

                            # getting and going to first stock in result
                            url_stock = urlNn + urlNnStock_rel_list[i].a['href']
                            r = s.get(url_stock)
                            if r.status_code != 200:
                                print('something when wrong in URL request:', r.status_code)
                                print('URL:', url_stock)
                            soup = BeautifulSoup(r.content, 'html.parser')
                            stock_heading_sentence = soup.find('h1', class_="title").get_text(strip=True)
                            nnNameshort = re.search(r'\((.*?)\)',stock_heading_sentence).group(1)
                            if nnNameshort == sbNameshortSplit:
                                break
                except Exception as e:
                    print ("ERROR in", inspect.stack()[0][3], ':', str(e))
                    list_of_tuples = [(glo_stockInfoColName_market_id, glo_stockInfo_value_notAvailable),
                  (glo_stockInfoColName_identifier_id, glo_stockInfo_value_notAvailable),
                  (glo_stockInfoColName_url_nn, glo_stockInfo_value_notAvailable)]

                    dictOrdered = OrderedDict(list_of_tuples)
                    updateStockList(dictOrdered, sbNameshort)
                    continue                
                if sbNameshortSplit == nnNameshort:
                    list_of_tuples = [(glo_stockInfoColName_market_id, market_id),
                  (glo_stockInfoColName_identifier_id, identifier_id),
                  (glo_stockInfoColName_url_nn, url_stock)]

                    dictOrdered = OrderedDict(list_of_tuples)
                    updateStockList(dictOrdered, sbNameshort)
                else:
                    list_of_tuples = [(glo_stockInfoColName_market_id, glo_stockInfo_value_notAvailable),
                  (glo_stockInfoColName_identifier_id, glo_stockInfo_value_notAvailable),
                  (glo_stockInfoColName_url_nn, glo_stockInfo_value_notAvailable)]

                    dictOrdered = OrderedDict(list_of_tuples)
                    updateStockList(dictOrdered, sbNameshort)
                    # updateStockList(nn_info_dict, sbNameshort)
        temp_glo_stockInfo_list = glo_stockInfo_list
        return temp_glo_stockInfo_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def getStockListFromFile():
    try:
        file_all_stocks = pathFile + sPathOutput + glo_stockInfo_output_str
        fieldname_list = []
        file_exists = os.path.isfile(file_all_stocks)
        if file_exists:
            with open (file_all_stocks) as csvFile:
                records = csv.DictReader(csvFile, delimiter=';')
                for fieldname in records.fieldnames:
                    fieldname_list.append(fieldname)
                records = csv.DictReader(csvFile, fieldnames=fieldname_list,delimiter=';')
                for rowDict in records:
                    order_of_keys = fieldname_list
                    setFilteredStockList(getOrderedDictFromDict(rowDict, order_of_keys))
            temp_glo_filteredStockInfo_list = glo_filteredStockInfo_list
            return temp_glo_filteredStockInfo_list 
        else:
            print(file_all_stocks, 'was NOT found')
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))       

def stringToFLoat(temp_glo_filteredStockInfo_list, columnsToFloat_list):
    try:
        for row in temp_glo_filteredStockInfo_list:
            for column in columnsToFloat_list:
                if row[column]: #true if string is not empty 
                    row[column] = float(row[column])
        return temp_glo_filteredStockInfo_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))   

def filterStocksToWatch():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        temp_glo_filteredStockInfo_list = getStockListFromFile()
        columnsToFloat_list = [glo_stockInfoColName_price, 
        glo_stockInfoColName_6_percent,
        glo_stockInfoColName_6_value,
        glo_stockInfoColName_12_percent,
        glo_stockInfoColName_12_value,
        glo_stockInfoColName_24_percent,
        glo_stockInfoColName_24_value,
        glo_stockInfoColName_percentAverage,
        glo_stockInfoColName_valueAverage,
        glo_stockInfoColName_24_buys_correct_percent,
        glo_stockInfoColName_buysTotal,
        glo_stockInfoColName_percentChange_highestThroughCurrent,
        glo_stockInfoColName_pricePercentChange_average,
        glo_stockInfoColName_pricePercentChange_median,
        glo_stockInfoColName_buyAverageFailedPerChange,
        glo_stockInfoColName_buyMedianFailedPerChange,
        glo_stockInfoColName_buyAverageSuccessPerChange,
        glo_stockInfoColName_buyMedianSuccessPerChange,
        glo_stockInfoColName_buyAndFailMedian_keyValue,
        glo_stockInfoColName_buyAndFailAverage_keyValue
        ]

        temp_glo_filteredStockInfo_list = stringToFLoat(temp_glo_filteredStockInfo_list, columnsToFloat_list)

        # GROUP1: Stable
        # filter out minimum x percent buy correct
        temp_glo_filteredStockInfo_gorup1_list = filterFilteredStockInfo(glo_stockInfoColName_24_buys_correct_percent, 
            65, temp_glo_filteredStockInfo_list)

        # filter out minumum x buyAndFail_median_keyvalue
        temp_glo_filteredStockInfo_gorup1_list = filterFilteredStockInfo(glo_stockInfoColName_buyAndFailMedian_keyValue, 
            3, temp_glo_filteredStockInfo_gorup1_list)

        # sort highest MEDIAN (overall) percent change
        sorted_buyAndFail_median_keyvalue_list = []
        sorted_buyAndFail_median_keyvalue_list = sorted(temp_glo_filteredStockInfo_gorup1_list, 
            key=lambda k: k[glo_stockInfoColName_buyAndFailMedian_keyValue], 
            reverse=True) # (list to sort; column to sort on; order)

        # get 30 highest of those
        sortedFiltered_buyAndFail_median_keyvalue_list = []
        for row in sorted_buyAndFail_median_keyvalue_list[:30]:
            sortedFiltered_buyAndFail_median_keyvalue_list.append(row)

        # sort with most amount of buys
        sortedFiltered_buyAndFail_median_keyvalue_list = sorted(sortedFiltered_buyAndFail_median_keyvalue_list, 
            key=lambda k: k[glo_stockInfoColName_buysTotal], 
            reverse=True) 

        # get top 10 of those
        group1_median_list = []
        nameOfGroup_1 = 'GROUP 1_mediumRisk'
        for row in sortedFiltered_buyAndFail_median_keyvalue_list[:15]:
            # add "column with type: group1
            row[glo_stockInfoColName_stockToBuy_group] = nameOfGroup_1
            group1_median_list.append(row)

        print('\nTOP 10 GROUP 1')
        for row in group1_median_list:
            print(row[glo_stockInfoColName_sbNameshort],':', 
                row[glo_stockInfoColName_buysTotal],':', 
                row[glo_stockInfoColName_buyAndFailMedian_keyValue],':', 
                row[glo_stockInfoColName_24_buys_correct_percent], ':', 
                row[glo_stockInfoColName_stockToBuy_group])

        # GROUP2: High risk
        # remove empty cells
        temp_glo_filteredStockInfo_group2_list = filterFilteredStockInfo(glo_stockInfoColName_buyAndFailAverage_keyValue, 
            '', temp_glo_filteredStockInfo_list)
        
        # sort highest AVERAGE (overall) percent change
        sorted_buyAndFail_average_keyvalue_list = []
        sorted_buyAndFail_average_keyvalue_list = sorted(temp_glo_filteredStockInfo_group2_list, 
            key=lambda k: k[glo_stockInfoColName_buyAndFailAverage_keyValue], 
            reverse=True) 

        # get top x of those
        sortedFiltered_buyAndFail_average_keyvalue_list = []
        for row in sorted_buyAndFail_average_keyvalue_list[:30]:
            sortedFiltered_buyAndFail_average_keyvalue_list.append(row)

        # sort highest buy amount
        sortedFiltered_buyAndFail_average_keyvalue_list = sorted(sortedFiltered_buyAndFail_average_keyvalue_list, 
            key=lambda k: k[glo_stockInfoColName_buysTotal], 
            reverse=True) 

        # get top x of those
        sortedFiltered_buyAndFail_average_keyvalue_list_2 = []
        for row in sortedFiltered_buyAndFail_average_keyvalue_list[:20]:
            sortedFiltered_buyAndFail_average_keyvalue_list_2.append(row)

        # sort highest diff between current and highest price (try to catch stock in historic low)
        sortedFiltered_buyAndFail_average_keyvalue_list_2 = sorted(sortedFiltered_buyAndFail_average_keyvalue_list_2, 
            key=lambda k: k[glo_stockInfoColName_percentChange_highestThroughCurrent], 
            reverse=True) 

        # get top x of those
        group2_average_list = []
        nameOfGroup_2 = 'GROUP 2_highRisk'
        for row in sortedFiltered_buyAndFail_average_keyvalue_list_2[:5]:
            row[glo_stockInfoColName_stockToBuy_group] = nameOfGroup_2
            group2_average_list.append(row)

        print('\nTOP 10 GROUP 2')
        for row in group2_average_list:
            print(row[glo_stockInfoColName_sbNameshort],':', 
                row[glo_stockInfoColName_buysTotal],':', 
                row[glo_stockInfoColName_buyAndFailAverage_keyValue],':', 
                row[glo_stockInfoColName_percentChange_highestThroughCurrent], ':', 
                row[glo_stockInfoColName_stockToBuy_group])
   
        # merge lists 
        stockToBuy_list = group1_median_list + group2_average_list # merging
        stockToBuy_list = list(unique_everseen(stockToBuy_list)) # remove duplicates

        # set final columns

        return stockToBuy_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))    

def clearSbWatchlist():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        # Login in to SB, return browser object
        browser = sbLogin()

        # Find and go to Watchlist
        link = browser.find('a', href=re.compile('Watchlist')) # find Watchlist link
        link = browser.follow_link(link)

        form = browser.get_form() # get form for deleteAll (one big shared form)
        browser.submit_form(form, submit=form['ctl00$MainContent$DeleteAll']) # delete all watchlist

    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))    

def setSbWatchlist(stockToBuy_list):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        # Login in to SB, return browser object
        browser = sbLogin()

        # get URL from list
        testUrl = 'https://www.swedishbulls.com/members/SignalPage.aspx?lang=en&Ticker=G5EN.ST'
        browser.open(testUrl)
        form = browser.get_form() # get form for deleteAll (one big shared form)
        # G5EN.ST
        BP()
        browser.submit_form(form, button=form['ctl00$MainContent$AddtoWatchlist'])
        
        BP()
        pass
        # for row in stockToBuy_list:
        #     url_stock = row.get(glo_stockInfoColName_url_sb)
        #     result = re.search('Ticker=(.*)', url_stock)
        #     ticker = result.group(1)

        #     urlBase = 'https://www.swedishbulls.com/members/SignalPage.aspx?lang=en&Ticker='
        #     url = urlBase + ticker
        # urlRequest
        # addToWatchlist
        # Repeat
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

start = time.time()

# temp_glo_stockInfo_list = getStockList()
# temp_glo_blacklist = getBlacklist()

# temp_glo_stockInfo_list = removeListFromList(temp_glo_stockInfo_list, temp_glo_blacklist)

# getComplimentaryList()

# temp_glo_stockInfo_list = getStocksFromSb(temp_glo_stockInfo_list)

# temp_glo_stockInfo_list = getStocksFromNn(temp_glo_stockInfo_list)

# writeStockList(temp_glo_stockInfo_list, glo_stockInfo_output_str)

# time.sleep(5)
# stockToBuy_list = filterStocksToWatch()
# writeStockList(stockToBuy_list, glo_stockToBuy_output_str)

# clearSbWatchlist()
stockToBuy_list = getListFromCsv(glo_stockToBuy_output_str)
setSbWatchlist(stockToBuy_list)

end = time.time()
timeElapsed = datetime.timedelta(seconds=(end - start))
timeElapsed = str(timeElapsed - datetime.timedelta(microseconds=timeElapsed.microseconds))
print('Time elapsed (H:M:S):', timeElapsed)
# Goal:
    # 1. check best stocks to watch
    #   - get the success-fail ratio of signals for 6, 12 and 24 months
    #   - get the success-fail ratio total average between 6, 12 and 24 months
    # 2. get information which can directly be used by 4-robo
    #   - market Id
    #   - Identifier Id
    #   - (sorted by highest?)
    # 3. make it possible for 4-robo to use the output automatically
    # 4. Make 4-robo use the ouput automatically

    # Consider:
    # - If new list of stocks, how to handle of those already held are not in list?