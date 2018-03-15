from pdb import set_trace as BP
import inspect
import os
import csv
import requests
import re
import datetime
from bs4 import BeautifulSoup
from statistics import median
from collections import OrderedDict
from pprint import pprint
from pprint import pformat

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

glo_stockInfo_input_str = 'input-stock-info.csv'
glo_stockInfo_output_str = 'output-stock-info.csv'
glo_stockInfo_output_noFileEnd_str = 'output-stock-info'
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
glo_stockInfoColName_buyAveragePercentChange = 'BUY_AVERAGE_PERCENT_CHANGE'
glo_stockInfoColName_buyMedianPercentChange = 'BUY_MEDIAN_PERCENT_CHANGE'
glo_stockInfoColName_buysTotal = 'BUYS_TOTAL'
glo_stockInfoColName_url_sb = 'URL_SB'
glo_stockInfoColName_market_id = 'MARKET_ID'
glo_stockInfoColName_identifier_id = 'IDENTIFIER_ID'
glo_stockInfoColName_url_nn = 'URL_NN'

glo_stockInfo_value_notAvailable = 'N/A'

glo_iterations_limit = 1000
# Output:
#   NAMESHORT_SB    NAME_SB     MONTH_6     MONTH_12    MONTH_24    AVERAGE

def getDateTodayStr():
    return datetime.date.today().strftime('%Y-%m-%d')

def getStockList():
    try:
        # fileNamePath_stock_info = None
        fileNamePath_stock_info = pathFile + sPathInput + glo_stockInfo_input_str
        # file_exists = os.path.isfile(fileNamePath_stock_info)
        fieldnames = [glo_stockInfoColName_sbNameshort, glo_stockInfoColName_sbName]
        with open (fileNamePath_stock_info) as csvFile:
            records = csv.DictReader(csvFile, fieldnames=fieldnames, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
            next(csvFile) #SKIP header
            for rowDict in records:
                order_of_keys = fieldnames
                # list_of_tuples = [(key, rowDict[key]) for key in order_of_keys]
                # dictOrdered = OrderedDict(list_of_tuples)
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

def getOrderedDictFromDict(dictTemp, order_of_keys):
    try:
        list_of_tuples = [(key, dictTemp[key]) for key in order_of_keys]
        return OrderedDict(list_of_tuples)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))     

def writeStockList(temp_glo_stockInfo_list):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        file_confStat = pathFile + sPathOutput + glo_stockInfo_output_noFileEnd_str + ' ' + getDateTodayStr() + '.csv'
        file_exists = os.path.isfile(file_confStat)
        with open (file_confStat, 'w') as csvFile:
            fieldnames = []
            indexWithMaxNumOfKeys = 0
            maxNumOfKeys = 0
            counter = 0
            # get index with most number of keys to get correct fieldnames
            for dictTemp in glo_stockInfo_list:
                if len(dictTemp.keys()) > maxNumOfKeys:
                    maxNumOfKeys = len(dictTemp.keys())
                    indexWithMaxNumOfKeys = counter
                if counter == len(glo_stockInfo_list)-1:
                    break
                else:
                    counter += 1
            for key in glo_stockInfo_list[indexWithMaxNumOfKeys]:
                fieldnames.append(key)
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
            writer.writeheader()
            for row in temp_glo_stockInfo_list:
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
                months_dict = {}
                percent_6 = percent_12 = percent_24 = percent_average = price_last_close = 'N/A'
                # percent_12 = 'N/A'
                # percent_24 = 'N/A'
                # percent_average = 'N/A'

                try:
                    price_last_close = float(soup.find(id='MainContent_lastpriceboxsub').get_text(strip=True).replace(',', ''))
                except Exception as e:
                    print ("ERROR in", inspect.stack()[0][3], ':', str(e))
                    pass

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

                # average buy percentage change and median value
                rows_months_24 = soup.find_all(id=re.compile("MainContent_signalpagehistory_PatternHistory24_DXDataRow"))
                array_length = len(rows_months_24)
                percent_total_change = 0
                buys_total = 0
                median_percentChange_list = []
                for i in range(0, array_length):
                    if array_length-i != array_length:
                        signalCurrent = rows_months_24[array_length-1-i].find_all('td')[2].get_text()
                        priceCurrent = float(rows_months_24[array_length-1-i].find_all('td')[1].get_text().replace(',', ''))
                        signalFormer = rows_months_24[array_length-i].find_all('td')[2].get_text()
                        priceFormer = float(rows_months_24[array_length-i].find_all('td')[1].get_text().replace(',', ''))
                        if signalCurrent == 'SHORT' or signalCurrent == 'SELL' and signalFormer == 'BUY':
                            median_percentChange_list.append(((priceCurrent/priceFormer)-1)*100)
                            percent_total_change += ((priceCurrent/priceFormer)-1)*100
                            buys_total += 1

                average_buy_percent_change = round(percent_total_change/buys_total, 2)
                median_buy_percent_change = round(median(median_percentChange_list), 2)

                list_of_tuples = [(glo_stockInfoColName_price, price_last_close),
                (glo_stockInfoColName_6_percent, percent_6),
                (glo_stockInfoColName_6_value, value_6),
                (glo_stockInfoColName_12_percent, percent_12),
                (glo_stockInfoColName_12_value, value_12),
                (glo_stockInfoColName_24_percent, percent_24),
                (glo_stockInfoColName_24_value, value_24),
                (glo_stockInfoColName_percentAverage, percent_average),
                (glo_stockInfoColName_valueAverage, value_average),
                (glo_stockInfoColName_buyAveragePercentChange, average_buy_percent_change),
                (glo_stockInfoColName_buyMedianPercentChange, median_buy_percent_change),
                (glo_stockInfoColName_buysTotal, buys_total),
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
                sbNameshortList = sbNameshort.split('.') #get rid of '.ST'
                sbNameshortSplit = sbNameshortList[0]
                sbName = row.get(glo_stockInfoColName_sbName)
                sbNameList = sbName.split(' ')
                # get query:
                query = ''
                for nameSplit in sbNameList:
                    # will yeild ex '+stockwik+folvaltning'
                    query += '+' + nameSplit
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
                # BP()
                try:
                    urlNnStock_rel = soup.find(id=re.compile('search-results-container')).a['href'] # first href (relative), such as '/mux/web/marknaden/aktiehemsidan/index.html?identifier=1007&marketid=11'

                    # get IDs
                    result = re.search('identifier=(.*)&', urlNnStock_rel)
                    identifier_id = result.group(1)

                    result = re.search('marketid=(.*)', urlNnStock_rel)
                    market_id = result.group(1)

                    # getting and going to first stock in result           
                    url_stock = urlNn + urlNnStock_rel
                    r = s.get(url_stock)
                    if r.status_code != 200:
                        print('something when wrong in URL request:', r.status_code)
                        print('URL:', url_stock)
                    soup = BeautifulSoup(r.content, 'html.parser')
                    allStockWordsList = soup.find('h1', class_="title").get_text(strip=True).split(' ')
                    nnNameshort = allStockWordsList[len(allStockWordsList)-1] # will give ex '(STWK)'
                    nnNameshort = nnNameshort[1:-1] #remove '(' and ')' at beginning and end respectively
                
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

temp_glo_stockInfo_list = getStockList()
temp_glo_stockInfo_list = getStocksFromSb(temp_glo_stockInfo_list)
temp_glo_stockInfo_list = getStocksFromNn(temp_glo_stockInfo_list)
# pprint(temp_glo_stockInfo_list)
writeStockList(temp_glo_stockInfo_list)

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