import trader_shared as mod_shared
from pdb import set_trace as BP
import os
import inspect
import csv
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup
import re
from statistics import median
from  more_itertools import unique_everseen
from pprint import pprint
from pprint import pformat

pathInputThis = "/input_" + os.path.splitext(os.path.basename(__file__))[0] + '/'
pathFileThis = os.path.dirname(os.path.abspath(__file__))
fileName = os.path.basename(__file__)

glo_stockInfo_file_raw_str = 'stock-info-raw.csv'
glo_blacklist_file_str = 'blacklist.csv'
glo_complimentary_file_str = 'nn-complimentary-list.csv'
glo_stockInfo_file_updated_str = 'stock-info-updated.csv'
glo_stockToBuy_allData_file_str = 'stock-to-buy-all-data.csv'

glo_stockInfo_list = []
glo_stockInfo_list_str = 'glo_stockInfo_list'
glo_filteredStockInfo_list = []
glo_nn_complimentary_list = []
glo_nn_complimentary_list_str = 'glo_nn_complimentary_list'
glo_blacklist = []
glo_blacklist_str = 'glo_blacklist'

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

gloSbLoginFormUser = 'ctl00$MainContent$uEmail'
gloSbLoginFormPass = 'ctl00$MainContent$uPassword'
gloSbLoginFormSubmit = 'ctl00$MainContent$btnSubmit'

glo_sbGeneralUrl_str = 'https://www.swedishbulls.com/SignalPage.aspx?lang=en&Ticker='

glo_costOfBuy = 0.8

glo_colValue_notAvailable = 'N/A'

glo_iterations_limit = 1000

def getStockList(name_of_list_and_path):
    try:
        temp_list = []
        fileNamePath = pathFileThis + name_of_list_and_path
        with open (fileNamePath, encoding='ISO-8859-1') as csvFile:
            records = csv.DictReader(csvFile, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
            fieldnames = records.fieldnames
            for rowDict in records:
                order_of_keys = fieldnames
                temp_list.append(getOrderedDictFromDict(rowDict, order_of_keys))
            return temp_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def setStockListGlobally(temp_list, name_of_list):
    try:
        if name_of_list == glo_stockInfo_list_str:
            global glo_stockInfo_list
            glo_stockInfo_list = temp_list
        elif name_of_list == glo_blacklist_str:
            global glo_blacklist
            glo_blacklist = temp_list
        elif name_of_list == glo_nn_complimentary_list_str:
            global glo_nn_complimentary_list
            glo_nn_complimentary_list = temp_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def updateListFromList(list_to_update, list_to_update_from):
    try:
        # global glo_stockInfo_list
        # temp_glo_stockInfo_list = glo_stockInfo_list
        for rowTo in list_to_update:
            for rowFrom in list_to_update_from:
                if rowTo[mod_shared.glo_colName_sbNameshort] == rowFrom[mod_shared.glo_colName_sbNameshort]:
                    rowTo.update(rowFrom)
                    break
        return list_to_update
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e)) 

def removeListFromList(listToKeep, listToRemove):
    try:
        new_list = list(listToKeep) # create new list rathen than assigning reference
        for itemToKeep in listToKeep:
            for itemToRemove in listToRemove:
                if itemToKeep[mod_shared.glo_colName_sbNameshort] == itemToRemove[mod_shared.glo_colName_sbNameshort]:
                    new_list.remove(itemToKeep)
                    break
        return new_list
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
        if column_key == glo_colName_buysTotal: #total buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == glo_colName_24_buys_correct_percent: # percent correct buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == glo_colName_buyAndFailMedian_keyValue: # percent correct buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == glo_colName_buyAndFailAverage_keyValue: # percent correct buys
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

def getNnStockPageData(url_stock, s):
    try:
        result = re.search('identifier=(.*)&', url_stock)
        identifier_id = result.group(1)
        result = re.search('marketid=(.*)', url_stock)
        market_id = result.group(1)

        # get name
        r = s.get(url_stock)
        if r.status_code != 200:
            print('something when wrong in URL request:', r.status_code)
            print('URL:', url_stock)
        soup = BeautifulSoup(r.content, 'html.parser')

        stock_heading_sentence = soup.find('h1', class_="title").get_text(strip=True)
        # get nordnet name
        nnName = re.search(r'Kursdata för (.*?) \(', stock_heading_sentence).group(1)
        # get nordnet shortname
        nnNameshort = re.search(r'\((.*?)\)',stock_heading_sentence).group(1)

        list_of_tuples = [(mod_shared.glo_colName_NameNordnet, nnName),
        (mod_shared.glo_colName_NameShortNordnet, nnNameshort),
        (mod_shared.glo_colName_market_id, market_id),
        (mod_shared.glo_colName_identifier_id, identifier_id),
        (mod_shared.glo_colName_url_nn, url_stock)]

        return list_of_tuples
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))     

def writeStockList(temp_list, name_path_file):
    try:
        fileNamePath = pathFileThis + name_path_file
        with open (fileNamePath, 'w', encoding='ISO-8859-1') as csvFile:
            fieldnames = []
            indexWithMaxNumOfKeys = 0
            maxNumOfKeys = 0
            counter = 0
            # get index with most number of keys to get correct fieldnames
            for dictTemp in temp_list:
                if len(dictTemp.keys()) > maxNumOfKeys:
                    maxNumOfKeys = len(dictTemp.keys())
                    indexWithMaxNumOfKeys = counter
                if counter == len(temp_list)-1:
                    break
                else:
                    counter += 1
            for key in temp_list[indexWithMaxNumOfKeys]:
                fieldnames.append(key)
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
            writer.writeheader()
            for row in temp_list:
                writer.writerow(row)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def getStocksFromSb(temp_stockInfo_list):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        counter = 2
        with requests.Session() as s:
            for row in temp_stockInfo_list:
                if counter > glo_iterations_limit:
                    break
                sbNameshort = row.get(mod_shared.glo_colName_sbNameshort)
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

                list_of_tuples = [(mod_shared.glo_colName_price, price_last_close),
                (glo_colName_6_percent, percent_6),
                (glo_colName_6_value, value_6),
                (glo_colName_12_percent, percent_12),
                (glo_colName_12_value, value_12),
                (glo_colName_24_percent, percent_24),
                (glo_colName_24_value, value_24),
                (glo_colName_percentAverage, percent_average),
                (glo_colName_valueAverage, value_average),
                (glo_colName_buysTotal, buys_total),
                (glo_colName_24_buys_correct_percent, buys_correct_percent_24),
                (glo_colName_pricePercentChange_average, percent_change_price_average),
                (glo_colName_pricePercentChange_median, percent_change_price_median),
                (glo_colName_buyAverageFailedPerChange, average_buy_failed_per_change),
                (glo_colName_buyMedianFailedPerChange, median_buy_failed_per_change),
                (glo_colName_buyAverageSuccessPerChange, average_buy_success_per_change),
                (glo_colName_buyMedianSuccessPerChange, median_buy_success_per_change),
                (glo_colName_buyAndFailMedian_keyValue, median_buyAndFail_keyValue_cost08Percent),
                (glo_colName_buyAndFailAverage_keyValue, average_buyAndFail_keyValue_cost08Percent),
                (glo_colName_percentChange_highestThroughCurrent, price_highest_through_current),
                (mod_shared.glo_colName_url_sb, url)]

                row.update(OrderedDict(list_of_tuples))
        return temp_stockInfo_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def getStocksFromNn(temp_stockInfo_list):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        counter = 2 
        with requests.Session() as s:
            for row in temp_stockInfo_list:
                sbNameshort = row.get(mod_shared.glo_colName_sbNameshort)
                if counter > glo_iterations_limit:
                    break
                print(counter,':',sbNameshort)
                counter += 1

                if row.get(mod_shared.glo_colName_url_sb) is None:
                    print(mod_shared.glo_colName_url_sb, 'was None - skipping')
                    continue

                # checking complimentary list
                if row.get(glo_colName_compList) is not None:
                    url_stock = row[mod_shared.glo_colName_url_nn]
                    list_of_tuples = getNnStockPageData(url_stock, s)
                    row.update(OrderedDict(list_of_tuples))
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
                try: #checking 3 top results in search result list
                    urlNnStock_rel_list = soup.find(id=re.compile('search-results-container')).find_all('div', class_='instrument-name') # all divs (containing a tags) in search result
                    if urlNnStock_rel_list: # if list not empty
                        for i in range(0,2):
                            url_stock = urlNn + urlNnStock_rel_list[i].a['href']
                            list_of_tuples = getNnStockPageData(url_stock, s)
                            dict_temp = dict(list_of_tuples)
                            if dict_temp.get(mod_shared.glo_colName_NameShortNordnet) == sbNameshortSplit:
                                row.update(OrderedDict(list_of_tuples))
                                break
                except Exception as e:
                    print ("ERROR in", inspect.stack()[0][3], ':', str(e))
                    print('error was in nested TRY (around urlNnStock_rel_list)')
                    continue                
        return temp_stockInfo_list
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
    try:
        # temp_glo_filteredStockInfo_list = getStockListFromFile()
        temp_glo_filteredStockInfo_list = getStockList(pathInputThis+glo_stockInfo_file_updated_str)
        columnsToFloat_list = [mod_shared.glo_colName_price, 
        glo_colName_6_percent,
        glo_colName_6_value,
        glo_colName_12_percent,
        glo_colName_12_value,
        glo_colName_24_percent,
        glo_colName_24_value,
        glo_colName_percentAverage,
        glo_colName_valueAverage,
        glo_colName_24_buys_correct_percent,
        glo_colName_buysTotal,
        glo_colName_percentChange_highestThroughCurrent,
        glo_colName_pricePercentChange_average,
        glo_colName_pricePercentChange_median,
        glo_colName_buyAverageFailedPerChange,
        glo_colName_buyMedianFailedPerChange,
        glo_colName_buyAverageSuccessPerChange,
        glo_colName_buyMedianSuccessPerChange,
        glo_colName_buyAndFailMedian_keyValue,
        glo_colName_buyAndFailAverage_keyValue
        ]

        temp_glo_filteredStockInfo_list = stringToFLoat(temp_glo_filteredStockInfo_list, columnsToFloat_list)

        # GROUP1: Stable
        # filter out minimum x percent buy correct
        temp_glo_filteredStockInfo_gorup1_list = filterFilteredStockInfo(glo_colName_24_buys_correct_percent, 
            65, temp_glo_filteredStockInfo_list)

        # filter out minumum x buyAndFail_median_keyvalue
        temp_glo_filteredStockInfo_gorup1_list = filterFilteredStockInfo(glo_colName_buyAndFailMedian_keyValue, 
            3, temp_glo_filteredStockInfo_gorup1_list)

        # sort highest MEDIAN (overall) percent change
        sorted_buyAndFail_median_keyvalue_list = []
        sorted_buyAndFail_median_keyvalue_list = sorted(temp_glo_filteredStockInfo_gorup1_list, 
            key=lambda k: k[glo_colName_buyAndFailMedian_keyValue], 
            reverse=True) # (list to sort; column to sort on; order)

        # get 30 highest of those
        sortedFiltered_buyAndFail_median_keyvalue_list = []
        for row in sorted_buyAndFail_median_keyvalue_list[:30]:
            sortedFiltered_buyAndFail_median_keyvalue_list.append(row)

        # sort with most amount of buys
        sortedFiltered_buyAndFail_median_keyvalue_list = sorted(sortedFiltered_buyAndFail_median_keyvalue_list, 
            key=lambda k: k[glo_colName_buysTotal], 
            reverse=True) 

        # get top 10 of those
        group1_median_list = []
        nameOfGroup_1 = 'GROUP 1_mediumRisk'
        for row in sortedFiltered_buyAndFail_median_keyvalue_list[:15]:
            # add "column with type: group1
            row[glo_colName_stockToBuy_group] = nameOfGroup_1
            group1_median_list.append(row)

        print('\nTOP 10 GROUP 1')
        for row in group1_median_list:
            print(row[mod_shared.glo_colName_sbNameshort],':', 
                row[glo_colName_buysTotal],':', 
                row[glo_colName_buyAndFailMedian_keyValue],':', 
                row[glo_colName_24_buys_correct_percent], ':', 
                row[glo_colName_stockToBuy_group])

        # GROUP2: High risk
        # remove empty cells
        temp_glo_filteredStockInfo_group2_list = filterFilteredStockInfo(glo_colName_buyAndFailAverage_keyValue, 
            '', temp_glo_filteredStockInfo_list)
        
        # sort highest AVERAGE (overall) percent change
        sorted_buyAndFail_average_keyvalue_list = []
        sorted_buyAndFail_average_keyvalue_list = sorted(temp_glo_filteredStockInfo_group2_list, 
            key=lambda k: k[glo_colName_buyAndFailAverage_keyValue], 
            reverse=True) 

        # get top x of those
        sortedFiltered_buyAndFail_average_keyvalue_list = []
        for row in sorted_buyAndFail_average_keyvalue_list[:30]:
            sortedFiltered_buyAndFail_average_keyvalue_list.append(row)

        # sort highest buy amount
        sortedFiltered_buyAndFail_average_keyvalue_list = sorted(sortedFiltered_buyAndFail_average_keyvalue_list, 
            key=lambda k: k[glo_colName_buysTotal], 
            reverse=True) 

        # get top x of those
        sortedFiltered_buyAndFail_average_keyvalue_list_2 = []
        for row in sortedFiltered_buyAndFail_average_keyvalue_list[:20]:
            sortedFiltered_buyAndFail_average_keyvalue_list_2.append(row)

        # sort highest diff between current and highest price (try to catch stock in historic low)
        sortedFiltered_buyAndFail_average_keyvalue_list_2 = sorted(sortedFiltered_buyAndFail_average_keyvalue_list_2, 
            key=lambda k: k[glo_colName_percentChange_highestThroughCurrent], 
            reverse=True) 

        # get top x of those
        group2_average_list = []
        nameOfGroup_2 = 'GROUP 2_highRisk'
        for row in sortedFiltered_buyAndFail_average_keyvalue_list_2[:5]:
            row[glo_colName_stockToBuy_group] = nameOfGroup_2
            group2_average_list.append(row)

        print('\nTOP 10 GROUP 2')
        for row in group2_average_list:
            print(row[mod_shared.glo_colName_sbNameshort],':', 
                row[glo_colName_buysTotal],':', 
                row[glo_colName_buyAndFailAverage_keyValue],':', 
                row[glo_colName_percentChange_highestThroughCurrent], ':', 
                row[glo_colName_stockToBuy_group])
   
        # merge lists 
        stockToBuy_list = group1_median_list + group2_average_list # merging
        stockToBuy_list = list(unique_everseen(stockToBuy_list)) # remove duplicates

        return stockToBuy_list
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))    

def deleteKeyValuesFromOrderedDict(list_to_update, list_of_keys):
    try:
        for row1 in list_to_update:
            for keyRow in list_of_keys:
                del row1[keyRow]
        return list_to_update
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))  

def addKeyToOrderedDict(list_to_update, list_of_keys):
    try:
        for row1 in list_to_update:
            for keyRow in list_of_keys:
                row1[keyRow] = ''
        return list_to_update
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))      




def setAllStockLists():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        # temp_stockInfo_list = getStockList(pathInputThis + glo_stockInfo_file_raw_str)
        temp_stockInfo_list = getStockList(pathInputThis + 'stock-info-raw-4.csv')
        setStockListGlobally(temp_stockInfo_list, glo_stockInfo_list_str)
        print('temp_stockInfo_list:', len(temp_stockInfo_list))
        
        temp_blacklist = getStockList(pathInputThis + glo_blacklist_file_str)
        setStockListGlobally(temp_blacklist, glo_blacklist_str)
        print('temp_blacklist:', len(temp_blacklist))

        temp_stockInfo_list = removeListFromList(temp_stockInfo_list, temp_blacklist)
        print('temp_stockInfo_list:', len(temp_stockInfo_list))

        temp_complimentary_list = getStockList(pathInputThis + glo_complimentary_file_str)
        setStockListGlobally(temp_complimentary_list, glo_nn_complimentary_list_str)
        print('temp_complimentary_list:', len(temp_complimentary_list))

        temp_stockInfo_list = getStocksFromSb(temp_stockInfo_list)
        print('temp_stockInfo_list:', len(temp_stockInfo_list))

        temp_stockInfo_list = updateListFromList(temp_stockInfo_list, temp_complimentary_list) # list to update, list to update from

        temp_stockInfo_list = getStocksFromNn(temp_stockInfo_list)

        writeStockList(temp_stockInfo_list, pathInputThis + glo_stockInfo_file_updated_str)
    except Exception as e:
        print ("ERROR in file", fileName, 'and function' ,inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def setStockToBuyList():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        stockToBuy_list = filterStocksToWatch()
        writeStockList(stockToBuy_list, pathInputThis+glo_stockToBuy_allData_file_str)

        list_of_keys_to_remove = [mod_shared.glo_colName_price,
        glo_colName_6_percent,
        glo_colName_6_value,
        glo_colName_12_percent,
        glo_colName_12_value,
        glo_colName_24_percent,
        glo_colName_24_value,
        glo_colName_percentAverage,
        glo_colName_valueAverage,
        glo_colName_24_buys_correct_percent,
        glo_colName_buysTotal,
        glo_colName_pricePercentChange_average,
        glo_colName_pricePercentChange_median,
        glo_colName_buyAverageFailedPerChange,
        glo_colName_buyAverageSuccessPerChange,
        glo_colName_buyMedianFailedPerChange,
        glo_colName_buyMedianSuccessPerChange,
        glo_colName_buyAndFailMedian_keyValue,
        glo_colName_buyAndFailAverage_keyValue,
        glo_colName_percentChange_highestThroughCurrent,
        glo_colName_compList
        ]

        stockToBuy_forOutputFolder_list = deleteKeyValuesFromOrderedDict(stockToBuy_list, list_of_keys_to_remove)

        list_of_keys_to_add = [mod_shared.glo_colName_held,
        mod_shared.glo_colName_active,
        mod_shared.glo_colName_activeTemp,
        mod_shared.glo_colName_amountHeld,
        mod_shared.glo_colName_price,
        mod_shared.glo_colName_priceTemp
        ]

        stockToBuy_forOutputFolder_list = addKeyToOrderedDict(stockToBuy_forOutputFolder_list, list_of_keys_to_add)
        
        writeStockList(stockToBuy_forOutputFolder_list, mod_shared.pathInput_main+mod_shared.glo_stockToBuy_file_str)
    except Exception as e:
        print ("ERROR in file", fileName, 'and function' ,inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

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
        print ("ERROR in file", fileName, 'and function' ,inspect.stack()[0][3], ':', str(e))

def setSbWatchlist():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        # Login in to SB, return browser object
        browser = sbLogin()

        url_base = 'https://www.swedishbulls.com/members/'
        for row in stockToBuy_list:
            # get non-member URL from list and format to member URL
            url_stock = row.get(glo_stockInfoColName_url_sb)
            url_stock_rel = url_stock[29:]
            url_stock = url_base + url_stock_rel

            browser.open(url_stock)

            # set form payload
            formData = {'ctl00$ScriptManager1': 'ctl00$MainContent$UpdatePanel1|ctl00$MainContent$AddtoWatchlist',
            '__EVENTTARGET': 'ctl00$MainContent$AddtoWatchlist',
            '__EVENTARGUMENT': 'Click',
            '__ASYNCPOST': 'true'}
            # add new headers
            headers = {'Referer' : 'https://www.swedishbulls.com/members/SignalPage.aspx?lang=en&Ticker=TETY.ST',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'X-MicrosoftAjax' : 'Delta=true',
            'X-Requested-With' : 'XMLHttpRequest',
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8'}
            # merge current with new headers
            browser.session.headers = {**browser.session.headers, **headers}
            browser.open(url_stock, method='post', data=formData)
    except Exception as e:
        print ("ERROR in file", fileName, 'and function' ,inspect.stack()[0][3], ':', str(e))

# setSbWatchlist
# - get stock list to watch
# - add stocks held
    # - check what is held
    # - check if held exist in new list
    # - add found from stock-info-updated (only needed keys)
# - add stocks with active signal (buy or sell)
    # - see above
# - remove watchlist
# - set new watchlist
# - confirm new watchlist match with new stock list