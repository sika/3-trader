import shared as mod_shared
from pdb import set_trace as BP
import os
import inspect
import csv
import requests
from bs4 import BeautifulSoup
import re
from statistics import median
from  more_itertools import unique_everseen
import time
from collections import OrderedDict
from pprint import pprint
from pprint import pformat

glo_file_this = os.path.basename(__file__)

glo_costOfBuy = 0.8

glo_colValue_notAvailable = 'N/A'

glo_iterations_limit = 1000

def setFilteredStockList(rowDict):
    try:
        global glo_filteredStockInfo_list
        glo_filteredStockInfo_list.append(rowDict)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))  

def filterFilteredStockInfo(column_key, criteria, temp_glo_filteredStockInfo_list):
    try:
        temp_list= []
        if column_key == mod_shared.glo_colName_buysTotal: #total buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == mod_shared.glo_colName_24_buys_correct_percent: # percent correct buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == mod_shared.glo_colName_buyAndFailMedian_keyValue: # percent correct buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != '':
                    if row.get(column_key) >= criteria:
                        temp_list.append(row)
        elif column_key == mod_shared.glo_colName_buyAndFailAverage_keyValue: # percent correct buys
            for row in temp_glo_filteredStockInfo_list:
                if row.get(column_key) != criteria:
                    temp_list.append(row)
        temp_glo_filteredStockInfo_list = temp_list
        return temp_glo_filteredStockInfo_list
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))     

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

        list_of_tuples = [(mod_shared.glo_colName_nameNordnet, nnName),
        (mod_shared.glo_colName_nameShortNordnet, nnNameshort),
        (mod_shared.glo_colName_market_id, market_id),
        (mod_shared.glo_colName_identifier_id, identifier_id),
        (mod_shared.glo_colName_url_nn, url_stock)]

        return list_of_tuples
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))     

def writeStockList(temp_list, name_path_file):
    try:
        glo_file_thisPath = mod_shared.path_base + name_path_file
        with open (glo_file_thisPath, 'w', encoding='ISO-8859-1') as csvFile:
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
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

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
                url = mod_shared.glo_sbBaseStockPageUrl + url_postfix
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
                    print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
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
                (mod_shared.glo_colName_6_percent, percent_6),
                (mod_shared.glo_colName_6_value, value_6),
                (mod_shared.glo_colName_12_percent, percent_12),
                (mod_shared.glo_colName_12_value, value_12),
                (mod_shared.glo_colName_24_percent, percent_24),
                (mod_shared.glo_colName_24_value, value_24),
                (mod_shared.glo_colName_percentAverage, percent_average),
                (mod_shared.glo_colName_valueAverage, value_average),
                (mod_shared.glo_colName_buysTotal, buys_total),
                (mod_shared.glo_colName_24_buys_correct_percent, buys_correct_percent_24),
                (mod_shared.glo_colName_pricePercentChange_average, percent_change_price_average),
                (mod_shared.glo_colName_pricePercentChange_median, percent_change_price_median),
                (mod_shared.glo_colName_buyAverageFailedPerChange, average_buy_failed_per_change),
                (mod_shared.glo_colName_buyMedianFailedPerChange, median_buy_failed_per_change),
                (mod_shared.glo_colName_buyAverageSuccessPerChange, average_buy_success_per_change),
                (mod_shared.glo_colName_buyMedianSuccessPerChange, median_buy_success_per_change),
                (mod_shared.glo_colName_buyAndFailMedian_keyValue, median_buyAndFail_keyValue_cost08Percent),
                (mod_shared.glo_colName_buyAndFailAverage_keyValue, average_buyAndFail_keyValue_cost08Percent),
                (mod_shared.glo_colName_percentChange_highestThroughCurrent, price_highest_through_current),
                (mod_shared.glo_colName_url_sb, url)]

                row.update(OrderedDict(list_of_tuples))
        return temp_stockInfo_list
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

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
                if row.get(mod_shared.glo_colName_compList) is not None:
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
                            if dict_temp.get(mod_shared.glo_colName_nameShortNordnet) == sbNameshortSplit:
                                row.update(OrderedDict(list_of_tuples))
                                break
                except Exception as e:
                    print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
                    print('error was in nested TRY (around urlNnStock_rel_list)')
                    continue                
        return temp_stockInfo_list
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

def stringToFLoat(temp_glo_filteredStockInfo_list, columnsToFloat_list):
    try:
        for row in temp_glo_filteredStockInfo_list:
            for column in columnsToFloat_list:
                if row[column]: #true if string is not empty 
                    row[column] = float(row[column])
        return temp_glo_filteredStockInfo_list
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))   

def filterStocksToWatch():
    try:
        temp_glo_filteredStockInfo_list = mod_shared.getStockListFromFile(mod_shared.path_input_createList, mod_shared.glo_stockInfo_file_updated)
        columnsToFloat_list = [mod_shared.glo_colName_price, 
            mod_shared.glo_colName_6_percent,
            mod_shared.glo_colName_6_value,
            mod_shared.glo_colName_12_percent,
            mod_shared.glo_colName_12_value,
            mod_shared.glo_colName_24_percent,
            mod_shared.glo_colName_24_value,
            mod_shared.glo_colName_percentAverage,
            mod_shared.glo_colName_valueAverage,
            mod_shared.glo_colName_24_buys_correct_percent,
            mod_shared.glo_colName_buysTotal,
            mod_shared.glo_colName_percentChange_highestThroughCurrent,
            mod_shared.glo_colName_pricePercentChange_average,
            mod_shared.glo_colName_pricePercentChange_median,
            mod_shared.glo_colName_buyAverageFailedPerChange,
            mod_shared.glo_colName_buyMedianFailedPerChange,
            mod_shared.glo_colName_buyAverageSuccessPerChange,
            mod_shared.glo_colName_buyMedianSuccessPerChange,
            mod_shared.glo_colName_buyAndFailMedian_keyValue,
            mod_shared.glo_colName_buyAndFailAverage_keyValue
        ]

        temp_glo_filteredStockInfo_list = stringToFLoat(temp_glo_filteredStockInfo_list, columnsToFloat_list)
        # GROUP1: Stable
        # filter out minimum x percent buy correct
        temp_glo_filteredStockInfo_group1_list = filterFilteredStockInfo(mod_shared.glo_colName_24_buys_correct_percent, 
            65, temp_glo_filteredStockInfo_list)

        # filter out minumum x buyAndFail_median_keyvalue
        temp_glo_filteredStockInfo_group1_list = filterFilteredStockInfo(mod_shared.glo_colName_buyAndFailMedian_keyValue, 
            3, temp_glo_filteredStockInfo_group1_list)

        # sort highest MEDIAN (overall) percent change
        sorted_buyAndFail_median_keyvalue_list = []
        sorted_buyAndFail_median_keyvalue_list = sorted(temp_glo_filteredStockInfo_group1_list, 
            key=lambda k: k[mod_shared.glo_colName_buyAndFailMedian_keyValue], 
            reverse=True) # (list to sort; column to sort on; order)

        # get 30 highest of those
        sortedFiltered_buyAndFail_median_keyvalue_list = []
        for row in sorted_buyAndFail_median_keyvalue_list[:30]:
            sortedFiltered_buyAndFail_median_keyvalue_list.append(row)

        # sort with most amount of buys
        sortedFiltered_buyAndFail_median_keyvalue_list = sorted(sortedFiltered_buyAndFail_median_keyvalue_list, 
            key=lambda k: k[mod_shared.glo_colName_buysTotal], 
            reverse=True) 

        # get top 10 of those
        group1_median_list = []
        nameOfGroup_1 = 'GROUP 1_mediumRisk'
        for row in sortedFiltered_buyAndFail_median_keyvalue_list[:15]:
            # add "column with type: group1
            row[mod_shared.glo_colName_stockToBuy_group] = nameOfGroup_1
            group1_median_list.append(row)

        print('\nTOP 10 GROUP 1')
        for row in group1_median_list:
            print(row[mod_shared.glo_colName_sbNameshort],':', 
                row[mod_shared.glo_colName_buysTotal],':', 
                row[mod_shared.glo_colName_buyAndFailMedian_keyValue],':', 
                row[mod_shared.glo_colName_24_buys_correct_percent], ':', 
                row[mod_shared.glo_colName_stockToBuy_group])

        # GROUP2: High risk
        # remove empty cells
        temp_glo_filteredStockInfo_group2_list = filterFilteredStockInfo(mod_shared.glo_colName_buyAndFailAverage_keyValue, '', temp_glo_filteredStockInfo_list)
        # sort highest AVERAGE (overall) percent change
        sorted_buyAndFail_average_keyvalue_list = []
        sorted_buyAndFail_average_keyvalue_list = sorted(temp_glo_filteredStockInfo_group2_list, 
            key=lambda k: k[mod_shared.glo_colName_buyAndFailAverage_keyValue], 
            reverse=True) 

        # get top x of those
        sortedFiltered_buyAndFail_average_keyvalue_list = []
        for row in sorted_buyAndFail_average_keyvalue_list[:30]:
            sortedFiltered_buyAndFail_average_keyvalue_list.append(row)

        # sort highest buy amount
        sortedFiltered_buyAndFail_average_keyvalue_list = sorted(sortedFiltered_buyAndFail_average_keyvalue_list, 
            key=lambda k: k[mod_shared.glo_colName_buysTotal], 
            reverse=True) 

        # get top x of those
        sortedFiltered_buyAndFail_average_keyvalue_list_2 = []
        for row in sortedFiltered_buyAndFail_average_keyvalue_list[:20]:
            sortedFiltered_buyAndFail_average_keyvalue_list_2.append(row)

        # sort highest diff between current and highest price (try to catch stock in historic low)
        sortedFiltered_buyAndFail_average_keyvalue_list_2 = sorted(sortedFiltered_buyAndFail_average_keyvalue_list_2, 
            key=lambda k: k[mod_shared.glo_colName_percentChange_highestThroughCurrent], 
            reverse=True) 

        # get top x of those
        group2_average_list = []
        nameOfGroup_2 = 'GROUP 2_highRisk'
        for row in sortedFiltered_buyAndFail_average_keyvalue_list_2[:5]:
            row[mod_shared.glo_colName_stockToBuy_group] = nameOfGroup_2
            group2_average_list.append(row)

        print('\nTOP 10 GROUP 2')
        for row in group2_average_list:
            print(row[mod_shared.glo_colName_sbNameshort],':', 
                row[mod_shared.glo_colName_buysTotal],':', 
                row[mod_shared.glo_colName_buyAndFailAverage_keyValue],':', 
                row[mod_shared.glo_colName_percentChange_highestThroughCurrent], ':', 
                row[mod_shared.glo_colName_stockToBuy_group])
   
        # merge lists 
        stockToBuy_list = group1_median_list + group2_average_list # merging
        stockToBuy_list = list(unique_everseen(stockToBuy_list)) # remove duplicates

        return stockToBuy_list
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))    

def deleteKeyValuesFromOrderedDict(list_to_update, list_of_keys):
    try:
        for row1 in list_to_update:
            for keyRow in list_of_keys:
                del row1[keyRow]
        return list_to_update
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))  

def addKeyToOrderedDict(list_to_update, list_of_keys):
    try:
        for row1 in list_to_update:
            for keyRow in list_of_keys:
                row1[keyRow] = ''
        return list_to_update
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))      

def setAllStockLists():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        # test_bool = False
        test_bool = True
        test_str = 'test-'
        if test_bool:
            print(inspect.stack()[0][3], 'in TEST MODE!')
            temp_stockInfo_list = mod_shared.getStockListFromFile(mod_shared.path_input_createList, 'stock-info-raw-4.csv')
        else:
            temp_stockInfo_list = mod_shared.getStockListFromFile(mod_shared.path_input_createList,  mod_shared.glo_stockInfo_file_raw)
        print('temp_stockInfo_list:', len(temp_stockInfo_list))
        
        temp_blacklist = mod_shared.getStockListFromFile(mod_shared.path_input_createList, mod_shared.glo_blacklist_file)
        print('temp_blacklist:', len(temp_blacklist))

        # remove rows blacklist from stockInfo list
        temp_stockInfo_list = [dict_item for dict_item in temp_stockInfo_list if dict_item not in temp_blacklist]

        print('temp_stockInfo_list:', len(temp_stockInfo_list))
        temp_complimentary_list = mod_shared.getStockListFromFile(mod_shared.path_input_createList, mod_shared.glo_complimentary_file)
        print('temp_complimentary_list:', len(temp_complimentary_list))

        temp_stockInfo_list = getStocksFromSb(temp_stockInfo_list)
        print('temp_stockInfo_list:', len(temp_stockInfo_list))

        list_of_key_selectors = [mod_shared.glo_colName_sbNameshort]
        list_of_key_overwriters = list(temp_complimentary_list[0].keys())
        temp_stockInfo_list = mod_shared.updateListFromListByKeys(temp_stockInfo_list,
            temp_complimentary_list,
            list_of_key_selectors, 
            list_of_key_overwriters) # list to update, list to update from
        
        temp_stockInfo_list = getStocksFromNn(temp_stockInfo_list)
        
        if test_bool:
            writeStockList(temp_stockInfo_list, mod_shared.path_input_createList + test_str+mod_shared.glo_stockInfo_file_updated)
        else:
            writeStockList(temp_stockInfo_list, mod_shared.path_input_createList + mod_shared.glo_stockInfo_file_updated)
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def setStockToBuyList():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        # test_bool = False
        test_bool = True
        test_str = 'test-'

        stockToBuy_list = filterStocksToWatch()
        if test_bool:
            print(inspect.stack()[0][3], 'in TEST MODE!')
            writeStockList(stockToBuy_list, mod_shared.path_input_createList + test_str+mod_shared.glo_stockToBuy_allData_file)
        else:
            writeStockList(stockToBuy_list, mod_shared.path_input_createList+mod_shared.glo_stockToBuy_allData_file)

        stockToBuy_list = mod_shared.setListKeys(stockToBuy_list, mod_shared.glo_stockToBuy_colNames)
        if test_bool:
            writeStockList(stockToBuy_list, mod_shared.path_input_main + test_str+mod_shared.glo_stockToBuy_file)
        else:
            writeStockList(stockToBuy_list, mod_shared.path_input_main+mod_shared.glo_stockToBuy_file)
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')


def main():
    try:
        setAllStockLists()
        time.sleep(5)
        setStockToBuyList()
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

# only run when script explicitly called
if __name__ == "__main__":
   main()

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

