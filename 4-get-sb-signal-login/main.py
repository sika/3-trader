import shared as mod_shared
import create_stock_lists as mod_list
import watchlist as mod_watch
from pdb import set_trace as BP
import re
from robobrowser import RoboBrowser
import yaml
import os
import requests
import sys
from bs4 import BeautifulSoup
import inspect
# import smtplib
import schedule
import time
import datetime
import csv
import json
from collections import OrderedDict
from pprint import pprint
from pprint import pformat

# Static price update at setStockStatus?
# Only use stop-loss?
glo_file_this = os.path.basename(__file__)

# --- Global variables

# stock status values
glo_status_tempValue_ActiveNnSell = 'Sälj'
glo_status_tempValue_ActiveNnBuy = 'Köp'
glo_status_value_activeBuy = 'BUY'
glo_status_value_activeSell = 'SELL'
glo_status_value_heldYes = 'YES'
glo_status_value_heldDefault = glo_status_value_activeDefault = glo_status_value_activeTempDefault = glo_status_value_amountHeldDefault = glo_status_value_priceDefault = glo_status_value_priceTempDefault = ''

# payloadOrder- Keys
glo_orderNn_key_identifier = 'identifier'
glo_orderNn_key_marketId = 'market_id'
glo_orderNn_key_side = 'side'
glo_orderNn_key_price = 'price'
glo_orderNn_key_currency = 'currency'
glo_orderNn_key_volume = 'volume'
glo_orderNn_key_openVolume = 'open_volume'
glo_orderNn_key_orderType = 'order_type'
glo_orderNn_key_smartOrder = 'smart_order'
glo_orderNn_key_validUntil = 'valid_until'

# payloadOrder- Values
glo_orderNn_value_currencySek = 'SEK'
glo_orderNn_value_openVolume = '0'
glo_orderNn_value_orderType = 'LIMIT'
glo_orderNn_value_smartOrder = '0'

# whatchlist
glo_sbSignalBuy = 'BUY'
glo_sbSignalSell = 'SELL'
glo_sbSignalShort = 'SHORT'
glo_sbArrowUp_green = 'UPGreen'
glo_sbArrowUp_yellow = 'UPYellow'
glo_sbArrowUp_orange = 'UPOrange'
glo_sbArrowUp_red = 'UPRed'
glo_sbArrowDown_green = 'DOWNGreen'
glo_sbArrowDown_yellow = 'DOWNYellow'
glo_sbArrowDown_orange = 'DOWNOrange'
glo_sbArrowDown_red = 'DOWNRed'
glo_sb_arrow_total_list = [
    glo_sbArrowUp_green,
    glo_sbArrowUp_yellow,
    glo_sbArrowUp_orange,
    glo_sbArrowUp_red,
    glo_sbArrowDown_green,
    glo_sbArrowDown_yellow,
    glo_sbArrowDown_orange,
    glo_sbArrowDown_red]
glo_sb_arrow_confirmedBuyOrSell_list = [
    # glo_sbArrowUp_green,
    # glo_sbArrowUp_yellow,
    # glo_sbArrowUp_orange,
    # glo_sbArrowUp_red,
    glo_sbArrowDown_green,
    glo_sbArrowDown_yellow,
    glo_sbArrowDown_orange,
    glo_sbArrowDown_red]

# time condition
glo_timeConditionRerunStockFile = {
    'days': 7,
    'hours': 0,
    'minutes': 0,
    'seconds': 0,
}

# time
glo_marketOpeningTime = datetime.time(9,0)
glo_marketClosingTime = datetime.time(17,29)
glo_afterMarketHoursOpen = datetime.time(20,30)
glo_afterMarketHoursClosed = datetime.time(21,00)

# amount to deal with
glo_currentNumberOfStocksHeld = glo_maxNumberOfStocks = glo_maxNumberOfActiveAboveMaxHeld = None # saftey reason: will not trade if something goes wrong
glo_amountAvailable = glo_amountAvailableStatic = None

# statistics
# glo_confirmationStatList = []
glo_confStat_fileName_str = 'confirmationStatistics.csv'
glo_stat_key_date = 'DATE'
glo_stat_key_time = 'TIME'
glo_stat_key_day = 'DAY'
# glo_stat_key_nameShortSb = 'NAMESHORT_SB'
glo_stat_key_nameShortSb = mod_shared.glo_colName_sbNameshort
glo_stat_key_signal = 'SIGNAL'
glo_stat_key_confirmation = 'CONFIRMATION'
glo_stat_key_priceLast = 'PRICE_LAST'
glo_stat_key_priceLevel = 'PRICE_LEVEL'
glo_stat_key_priceDifference = 'LAST_LEVEL_DIFFERENCE'

# error
# glo_counter_error = 0

# red days
glo_redDays = {
    'Mar_29_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Mar 29 13 00', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Mar 29 17 30', '%Y %b %d %H %M')
    },
    'Mar_30_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Mar 30 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Mar 30 17 30', '%Y %b %d %H %M')
    },
    'Apr_02_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Apr 02 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Apr 02 17 30', '%Y %b %d %H %M')
    },
    'May_01_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 May 01 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 May 01 17 30', '%Y %b %d %H %M')
    },
    'May_09_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 May 09 13 00', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 May 09 17 30', '%Y %b %d %H %M')
    },
    'May_10_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 May 10 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 May 10 17 30', '%Y %b %d %H %M')
    },
    'Jun_06_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Jun 06 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Jun 06 17 30', '%Y %b %d %H %M')
    },
    'Jun_22_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Jun 22 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Jun 22 17 30', '%Y %b %d %H %M')
    },
    'Nov_02_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Nov 02 13 00', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Nov 02 17 30', '%Y %b %d %H %M')
    },
    'Dec_24_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Dec 24 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Dec 24 17 30', '%Y %b %d %H %M')
    },
    'Dec_25_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Dec 25 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Dec 25 17 30', '%Y %b %d %H %M')
    },
    'Dec_26_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Dec 26 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Dec 26 17 30', '%Y %b %d %H %M')
    },
    'Dec_31_2018': {
    'CLOSE_START' : datetime.datetime.strptime('2018 Dec 31 08 55', '%Y %b %d %H %M'),
    'CLOSE_END' : datetime.datetime.strptime('2018 Dec 31 17 30', '%Y %b %d %H %M')
    }
}
# --- END Global variables

def writeOrderStatistics(sbStockNameShort, payloadOrder):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        statDate = 'DATE'
        statTime = 'TIME'
        statDay = 'DAY'
        statNameshortSb = 'NAMESHORT_SB'
        statSignal = 'SIGNAL'
        statPrice = 'PRICE'
        file_orderStat = mod_shared.path_base + mod_shared.path_output + 'orderStatistics.csv'
        file_exists = os.path.isfile(file_orderStat)
        with open (file_orderStat, 'a') as csvFile:
            fieldnames = [statDate, statTime, statDay, statNameshortSb, statSignal, statPrice]
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
            if not file_exists:
                writer.writeheader()
            writer.writerow({statDate: mod_shared.getDateTodayStr(), 
                statTime: mod_shared.getTimestampCustomStr("%H:%M"), 
                statDay: mod_shared.getDateTodayCustomStr('%A'), 
                statNameshortSb: sbStockNameShort,
                statSignal: payloadOrder[glo_orderNn_key_side], 
                statPrice: payloadOrder[glo_orderNn_key_price]})
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def writeConfirmationStatistics(sbStockNameShort, sbSignalType, sbSignalConf, sbLastPrice, sbPriceLevel):
    try:
        file_confStat = None
        file_confStat = mod_shared.path_base + mod_shared.path_output + glo_confStat_fileName_str
        file_exists = os.path.isfile(file_confStat)
        with open (file_confStat, 'a') as csvFile:
            fieldnames = [glo_stat_key_date, 
            glo_stat_key_time, 
            glo_stat_key_day, 
            glo_stat_key_nameShortSb, 
            glo_stat_key_signal, 
            glo_stat_key_confirmation,
            glo_stat_key_priceLast,
            glo_stat_key_priceLevel,
            glo_stat_key_priceDifference]
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
            if not file_exists:
                writer.writeheader()
            statDict = {glo_stat_key_date: mod_shared.getDateTodayStr(), 
                glo_stat_key_time: mod_shared.getTimestampCustomStr("%H:%M"), 
                glo_stat_key_day: mod_shared.getDateTodayCustomStr('%A'), 
                glo_stat_key_nameShortSb: sbStockNameShort,
                glo_stat_key_signal: sbSignalType, 
                glo_stat_key_confirmation: sbSignalConf,
                glo_stat_key_priceLast: sbLastPrice,
                glo_stat_key_priceLevel: sbPriceLevel,
                glo_stat_key_priceDifference: str(round(100*(float(sbLastPrice)/float(sbPriceLevel)), 3))}
            writer.writerow(statDict)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))   

def isConfirmationStatSet(sbStockNameShort, sbSignalConf):
    try:
        file_confStat = None
        file_confStat = mod_shared.path_base + mod_shared.path_output + glo_confStat_fileName_str
        # file_exists = os.path.isfile(file_confStat)
        with open (file_confStat) as csvFile:
            rows = csv.DictReader(csvFile, delimiter=';')
            for row in rows:
                if (
                    row.get(glo_stat_key_nameShortSb) == sbStockNameShort and 
                    row.get(glo_stat_key_confirmation) == sbSignalConf and
                    row.get(glo_stat_key_date) == mod_shared.getDateTodayStr()
                    ):
                    return True
            return False
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))  

# def initStockStatus():
    #     print ('\nSTART', inspect.stack()[0][3])
    #     try:
    #         with open(mod_shared.path_base + mod_shared.pathInput_main + mod_shared.glo_stockToBuy_file, 'rt', encoding='ISO-8859-1') as file:
    #             records = csv.DictReader(file, delimiter=';')
    #             for row in records:
    #                 setStockList(row)
    #     except Exception as e:
    #             print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
    #             mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    #     else:
    #         print('END', inspect.stack()[0][3], '\n')

# def setStockList(rowDict):
#     try:
#         global glo_stockStatus_list
#         glo_stockStatus_list.append(rowDict)
#     except Exception as e:
#         print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
#         mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getRemovalList(list_to_keep, list_to_remove, key_selector):
    try:
        removal_list = []
        for dict_keep in list_to_keep:
            for dict_remove in list_to_remove:
                if dict_keep.get(key_selector) == dict_remove.get(key_selector):
                    temp_ordered = OrderedDict()
                    temp_ordered[key_selector] = dict_remove.get(key_selector)
                    removal_list.append(temp_ordered)
        return removal_list
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getStockStatus():
    try:
        r, header, s = mod_shared.nordnetLogin() # login to nordnet

        # test = True
        test = False
        
        # get HELD
        temp_nNHeld_list = []
        if test:
            print(inspect.stack()[0][3], 'in TEST MODE!')
            temp_nNHeld_dict = OrderedDict()
            temp_nNHeld_dict[mod_shared.glo_colName_nameNordnet] = 'G5 Entertainment AB'
            temp_nNHeld_dict[mod_shared.glo_colName_amountHeld] = '100'
            temp_nNHeld_list.append(temp_nNHeld_dict)
            
            temp_nNHeld_dict = OrderedDict()
            temp_nNHeld_dict[mod_shared.glo_colName_nameNordnet] = 'Biotage AB'
            temp_nNHeld_dict[mod_shared.glo_colName_amountHeld] = '100'
            temp_nNHeld_list.append(temp_nNHeld_dict)
        else:
            soup = BeautifulSoup(s.get('https://www.nordnet.se/mux/web/depa/mindepa/depaoversikt.html', headers=mod_shared.glo_urlHeader).content, 'html.parser')
            stockTable = soup.find(id='aktier')
            stockHeldAndAmount = stockTable.find_all('tr', id=re.compile('tr')) # find <tr> where id='tr[x]'
            if stockHeldAndAmount:
                for stock in stockHeldAndAmount:
                    temp_nNHeld_dict = {}
                    nameNordnet = stock.find(class_='truncate18').get_text(strip=True)
                    temp_nNHeld_dict[mod_shared.glo_colName_nameNordnet] = nameNordnet

                    # get number of stocks
                    amountHeld = stock.find_all('td')[3].get_text(strip=True)
                    temp_nNHeld_dict[mod_shared.glo_colName_amountHeld] = amountHeld

                    temp_nNHeld_list.append(temp_nNHeld_dict)

        # get ACTIVE
        temp_nNActive_list = []
        if test:
            temp_nNActive_dict = OrderedDict()
            temp_nNActive_dict[mod_shared.glo_colName_nameNordnet] = 'Old Mutual Plc'
            temp_nNActive_dict[mod_shared.glo_colName_active] = glo_status_value_activeBuy
            temp_nNActive_list.append(temp_nNActive_dict)
            
            temp_nNActive_dict = OrderedDict()
            temp_nNActive_dict[mod_shared.glo_colName_nameNordnet] = 'G5 Entertainment AB'
            temp_nNActive_dict[mod_shared.glo_colName_active] = glo_status_value_activeSell
            temp_nNActive_list.append(temp_nNActive_dict)
        else:
            soup = BeautifulSoup(s.get('https://www.nordnet.se/mux/ajax/trade/orders/auto?accountNumber=18272500', headers=mod_shared.glo_urlHeader).content, 'html.parser') # active are placed in "share"
            newDict = json.loads(str(soup))
            newList = newDict.get('share')
            for item in newList:
                temp_nNActive_dict = {}
                temp_nNActive_dict[mod_shared.glo_colName_nameNordnet] = item.get('longName')
                temp_nnStockActiveType = item.get('buyOrSell')
                if temp_nnStockActiveType == glo_status_tempValue_ActiveNnBuy: #active BUY
                    temp_nNActive_dict[mod_shared.glo_colName_active] = glo_status_value_activeBuy
                elif temp_nnStockActiveType == glo_status_tempValue_ActiveNnSell: #active SELL
                    temp_nNActive_dict[mod_shared.glo_colName_active] = glo_status_value_activeSell
                temp_nNActive_list.append(temp_nNActive_dict)

        # update held with active if same stock exist in both
        list_of_key_selectors = [mod_shared.glo_colName_nameNordnet]
        list_of_key_overwriters = [mod_shared.glo_colName_active]
        temp_nNHeld_list = mod_shared.updateListFromListByKeys(temp_nNHeld_list, temp_nNActive_list, list_of_key_selectors, list_of_key_overwriters)
        
        key_selector = mod_shared.glo_colName_nameNordnet
        removal_list = getRemovalList(temp_nNHeld_list, temp_nNActive_list, key_selector)

        # add to new list if not existing in ACTIVE list
        list_of_key_selectors = [mod_shared.glo_colName_nameNordnet]
        temp_nNActive_list = mod_shared.removeListFromListByKey(temp_nNActive_list, removal_list, list_of_key_selectors)
        
        nNHeld_nNActive_merged = temp_nNHeld_list + temp_nNActive_list
        
        return nNHeld_nNActive_merged
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def setAndGetStockStatusFromNn():
    try:
        nNAmountAvailable_str = getAmountAvailableFromNn()
        setAmountAvailable(int(float(nNAmountAvailable_str)))
        
        stocksToBuy_list = mod_shared.getStockListFromFile(mod_shared.path_input_main, mod_shared.glo_stockToBuy_file) 
        stocksToBuy_list = resetStockStatus(stocksToBuy_list) # set default values to ACTIVE, AMOUNT_HELD etc
        
        nNHeldAndActive_list = getStockStatus()
        
        # update nNHeldAndActive_list to have all keys of stocksToBuy and values of stocks all updated
        stocksAllUpdated_list = mod_shared.getStockListFromFile(mod_shared.path_input_createList, mod_shared.glo_stockInfo_file_updated) 
        stockToBuy_keys = list(mod_shared.glo_stockToBuy_colNames.keys())
        for dict_active_held in nNHeldAndActive_list:
            for dict_all_stocks in stocksAllUpdated_list:
                if dict_active_held.get(mod_shared.glo_colName_nameNordnet) == dict_all_stocks.get(mod_shared.glo_colName_nameNordnet):
                    for key_to_buy in stockToBuy_keys:
                        if key_to_buy not in dict_active_held: # only if key not already existing (to not overwrite held and active)
                            if key_to_buy not in dict_all_stocks: # if key, like TEMP_ACTIVE not in all stocks, set to empty 
                                dict_active_held[key_to_buy] = ''
                            else:
                                dict_active_held[key_to_buy] = dict_all_stocks[key_to_buy]
        
        # those existing in both, set value of dicts in nNHeldAndActive_list to stocksToBuy
        list_of_key_selectors = [mod_shared.glo_colName_nameNordnet]
        list_of_key_overwriters = list(mod_shared.glo_stockToBuy_colNames.keys())
        stocksToBuy_list = mod_shared.updateListFromListByKeys(stocksToBuy_list, nNHeldAndActive_list, list_of_key_selectors, list_of_key_overwriters)

        # list of those to remove from nNHeldAndActive_list: those already updated in stocksToBuy
        key_selector = mod_shared.glo_colName_nameNordnet
        removal_list = getRemovalList(stocksToBuy_list, nNHeldAndActive_list, key_selector)

        # remove stocks from nNHeldAndActive_list
        list_of_key_selectors = [mod_shared.glo_colName_nameNordnet]
        nNHeldAndActive_list = mod_shared.removeListFromListByKey(nNHeldAndActive_list, removal_list, list_of_key_selectors)

        stocksToBuy_list = stocksToBuy_list + nNHeldAndActive_list

        return stocksToBuy_list
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def resetStockStatus(stockStatus_list):
    print ('\n', inspect.stack()[0][3])
    try:
        for row in stockStatus_list:
            row[mod_shared.glo_colName_active] = glo_status_value_activeDefault
            row[mod_shared.glo_colName_activeTemp] = glo_status_value_activeTempDefault
            row[mod_shared.glo_colName_amountHeld] = glo_status_value_amountHeldDefault
            row[mod_shared.glo_colName_price] = glo_status_value_priceDefault
            row[mod_shared.glo_colName_priceTemp] = glo_status_value_priceTempDefault
        return stockStatus_list
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isStockHeld(sbStockNameShort):
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort and row.get(mod_shared.glo_colName_amountHeld) != glo_status_value_amountHeldDefault:
                return True
        return False # if no match
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

# def setStocksNumberHeld(sbStockNameShort, amountStr):
#     print ('\n', inspect.stack()[0][3])
#     try:
#         global glo_stockStatus_list
#         temp_glo_stockStatus_list = glo_stockStatus_list
#         for row in temp_glo_stockStatus_list:
#             if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
#                 row.update({mod_shared.glo_colName_amountHeld:amountStr})
#         glo_stockStatus_list = temp_glo_stockStatus_list
#     except Exception as e:
#         print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
#         mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getStocksNumberHeld(sbStockNameShort):
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
                if row.get(mod_shared.glo_colName_amountHeld) != '':
                    return row.get(mod_shared.glo_colName_amountHeld)
                else:
                    raise ValueError(inspect.stack()[0][3] + ': returned empty string')
                    return None
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

# def updateStocksNumberHeld(sbStockNameShort, numberOfStocksStr, sbSignalType): # subtract volume from current held
    # try:
    #     global glo_stockStatus_list
    #     temp_glo_stockStatus_list = glo_stockStatus_list
    #     if sbSignalType == glo_sbSignalBuy: #add stocks
    #         for row in temp_glo_stockStatus_list:
    #             if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
    #                 newStockNumberHeld = str(eval('int(row.get(mod_shared.glo_colName_amountHeld))+int(numberOfStocksStr)'))
    #                 row.update({mod_shared.glo_colName_amountHeld:newStockNumberHeld})
    #     elif sbSignalType == glo_sbSignalSell: #subtract stocks
    #         for row in temp_glo_stockStatus_list:
    #             if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
    #                 newStockNumberHeld = str(eval('int(row.get(mod_shared.glo_colName_amountHeld))-int(numberOfStocksStr)'))
    #                 row.update({mod_shared.glo_colName_amountHeld:newStockNumberHeld})
    #     glo_stockStatus_list = temp_glo_stockStatus_list
    # except Exception as e:
    #     print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

def setStockActive(sbStockNameShort, sbActiveType): #'BUY' or 'SELL'
    print ('\n', inspect.stack()[0][3])
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
                row.update({mod_shared.glo_colName_active:sbActiveType})
        mod_shared.setStockListGlobally(local_glo_stockStatus_list, mod_shared.glo_stockStatus_list_name)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isStockActive(sbStockNameShort, sbActiveType):
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if sbActiveType == glo_sbSignalBuy:
                if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort and row.get(mod_shared.glo_colName_active) == glo_status_value_activeBuy:
                    return True
            elif sbActiveType == glo_sbSignalSell:
                if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort and row.get(mod_shared.glo_colName_active) == glo_status_value_activeSell:
                    return True
        return False # if no match
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def setStockActiveTemp(sbStockNameShort, sbActiveType):
    print ('\n', inspect.stack()[0][3])
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
                row.update({mod_shared.glo_colName_activeTemp:sbActiveType})
        mod_shared.setStockListGlobally(local_glo_stockStatus_list, mod_shared.glo_stockStatus_list_name)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def delStockActiveTemp(sbStockNameShort):
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
                row.update({mod_shared.glo_colName_activeTemp:glo_status_value_activeTempDefault})
        mod_shared.setStockListGlobally(local_glo_stockStatus_list, mod_shared.glo_stockStatus_list_name)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isStockActiveTemp(sbStockNameShort, sbActiveType):
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if sbActiveType == glo_sbSignalBuy:
                if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort and row.get(mod_shared.glo_colName_activeTemp) == glo_status_value_activeBuy:
                    return True
            elif sbActiveType == glo_sbSignalSell:
                if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort and row.get(mod_shared.glo_colName_activeTemp) == glo_status_value_activeSell:
                    return True
        return False # if no match
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

# def setStockPrice(s):
    # try:
    #     global glo_stockStatus_list
    #     temp_glo_stockStatus_list = glo_stockStatus_list
    #     for row in temp_glo_stockStatus_list:
    #         if row[mod_shared.glo_colName_activeTemp] != glo_status_value_activeTempDefault:
    #             urlNnStock = row.get(mod_shared.glo_colName_url_nn)
    #             r = s.get(urlNnStock)
    #             if r.status_code != 200:
    #                 print(r.url, 'failed!')
    #             soup = BeautifulSoup(s.get(r.url).content, 'html.parser')
    #             priceStockStr = soup.find(class_='tvaKnapp').parent.find_all('td')[2].get_text()
    #             priceStockStr = priceStockStr.replace(',', '.')
    #             row[mod_shared.glo_colName_price] = priceStockStr
    #     glo_stockStatus_list = temp_glo_stockStatus_list
    # except Exception as e:
    #         print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

# def setStockPriceTemp(sbStockNameShort, orderNnValuePrice):
    # print ('\n', inspect.stack()[0][3])
    # try:
    #     global glo_stockStatus_list
    #     temp_glo_stockStatus_list = glo_stockStatus_list
    #     for row in temp_glo_stockStatus_list:
    #         if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
    #             row.update({mod_shared.glo_colName_priceTemp:orderNnValuePrice})
    #     glo_stockStatus_list = temp_glo_stockStatus_list
    # except Exception as e:
    #     print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

# def delStockPriceTemp(sbStockNameShort, orderNnValuePrice):
    # try:
    # except Exception as e:
    #     print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))    

# def isStockPriceChanged(sbStockNameShort, sbSignalType):
#     try:
#         local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
#         percentageChangeLimit = 0.5
#         if sbSignalType == glo_sbSignalBuy:
#             for row in local_glo_stockStatus_list:
#                 if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
#                     orderPrice = float(local_glo_stockStatus_list.get(mod_shared.glo_colName_priceTemp))
#                     newPrice = float(local_glo_stockStatus_list.get(mod_shared.glo_colName_price))
#                     decimalChange = newPrice / orderPrice
#                     percentageChange = decimalChange * 100-100
#                     if percentageChange > percentageChangeLimit:
#                         return True
#                     else:
#                         return False
#         if sbSignalType == glo_sbSignalSell:
#             for row in local_glo_stockStatus_list:
#                 if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
#                     orderPrice = float(local_glo_stockStatus_list.get(mod_shared.glo_colName_priceTemp))
#                     newPrice = float(local_glo_stockStatus_list.get(mod_shared.glo_colName_price)) 
#                     decrease = orderPrice - newPrice
#                     decreasePercentage = (decrease / orderPrice) * 100
#                     if decreasePercentage > percentageChangeLimit:
#                         return True
#                     else:
#                         return False
#     except Exception as e:
#         print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
#         mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getSbNameShortByNnName(nnStockName):
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_nameNordnet) == nnStockName:
                return row.get(mod_shared.glo_colName_sbNameshort)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        msg = 'could not match', nnStockName, 'with', mod_shared.glo_colName_sbNameshort
        print (msg)
        mod_shared.writeErrorLog(inspect.stack()[0][3], msg)

def isMaxStockHeldAndActive():
    try:
        maxNumberOfStocks = getMaxNumberOfStocks()
        currentNumberOfStocksHeld = getCurrentNumberOfStocksHeld()
        currentNumberOfStocksActiveBuy = getCurrentNumberOfStocksActiveBuy()
        currentNumberOfStocksActiveSell = getCurrentNumberOfStocksActiveSell()
        currentStockHeldAndActive = currentNumberOfStocksHeld + currentNumberOfStocksActiveBuy - currentNumberOfStocksActiveSell 
        if  currentStockHeldAndActive >= maxNumberOfStocks:
            return True
        else:
            return False
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

# def getAmountAvailableStaticFromNn(amountInt):
#     print ('\n', inspect.stack()[0][3])
#     try:
#         global glo_amountAvailableStatic
#         glo_amountAvailableStatic = amountInt
#     except Exception as e:
#         print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
#         mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def setAmountAvailable(amountInt):
    print ('\n', inspect.stack()[0][3])
    try:
        global glo_amountAvailable
        glo_amountAvailable = amountInt
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def setAmountAvailableStatic(amountInt):
    print ('\n', inspect.stack()[0][3])
    try:
        global glo_amountAvailableStatic
        glo_amountAvailableStatic = amountInt
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def updateAmountAvailable(sbSignalType, payloadOrder):
    print ('\n', inspect.stack()[0][3])
    try:
        global glo_amountAvailable
        global glo_amountAvailableStatic
        if sbSignalType == glo_sbSignalBuy:
            if glo_amountAvailableStatic != None:
                glo_amountAvailableStatic -= int(float(payloadOrder.get(glo_orderNn_key_price)) * float(payloadOrder.get(glo_orderNn_key_volume)))
            else:
                glo_amountAvailable -= int(float(payloadOrder.get(glo_orderNn_key_price)) * float(payloadOrder.get(glo_orderNn_key_volume)))
        elif sbSignalType == glo_sbSignalSell:
            if glo_amountAvailableStatic != None:
                glo_amountAvailableStatic += int(float(payloadOrder.get(glo_orderNn_key_price)) * float(payloadOrder.get(glo_orderNn_key_volume)))
            else:
                glo_amountAvailable += int(float(payloadOrder.get(glo_orderNn_key_price)) * float(payloadOrder.get(glo_orderNn_key_volume)))
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getAmountAvailable():
    try:
        amountAvailable = glo_amountAvailable
        amountAvailableStatic = glo_amountAvailableStatic
        if amountAvailableStatic is not None:
            return amountAvailableStatic
        else:
            return amountAvailable
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getCurrentNumberOfStocksHeld():
    try:
        counter = 0
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_amountHeld) != glo_status_value_amountHeldDefault:
                counter += 1
        return counter
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getCurrentNumberOfStocksActiveBuy():
    try:
        counter = 0
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_activeTemp) == glo_status_value_activeBuy:
                counter += 1
        return counter
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getCurrentNumberOfStocksActiveSell():
    try:
        counter = 0
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_activeTemp) == glo_status_value_activeSell:
                counter += 1
        return counter
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def setMaxNumberOfStocks(numberOfStocksInt):
    try:
        global glo_maxNumberOfStocks
        glo_maxNumberOfStocks = numberOfStocksInt
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getMaxNumberOfStocks():
    try:
        return glo_maxNumberOfStocks
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def setMaxNumberOfActiveAboveMaxHeld(numberOfStocksInt):
    try:
        global glo_maxNumberOfActiveAboveMaxHeld
        glo_maxNumberOfActiveAboveMaxHeld = numberOfStocksInt
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getMaxNumberOfActiveAboveMaxHeld():
    try:
        return glo_maxNumberOfActiveAboveMaxHeld
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getNnStockPrice(sbStockNameShort, sbSignalType, s):
    try:
        sellPercentageChange = 5
        sellDecimalChange = sellPercentageChange/100
        urlNnStock = None
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
                urlNnStock = row.get(mod_shared.glo_colName_url_nn)
                break
        r = s.get(urlNnStock)
        if r.status_code != 200:
            print(r.url, 'failed!')
        soup = BeautifulSoup(s.get(r.url).content, 'html.parser')
        priceStockStr = soup.find(class_='tvaKnapp').parent.find_all('td')[2].get_text()
        priceStockStr = priceStockStr.replace(',', '.')
        #get number of decimals to match stock (should be dynamic since number can be either 2 or 3)
        dec = str(len(priceStockStr.split('.')[1])) 
        if sbSignalType == glo_sbSignalSell:
            priceStockStr = format(float(priceStockStr) - sellDecimalChange*float(priceStockStr), '.' + (dec) + 'f') #lower market price with x%
            return priceStockStr
        elif sbSignalType == glo_sbSignalBuy:
            return priceStockStr
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e)) 

def getNnStockVolume(orderNnValuePriceStr):
    try:
        # get amount available
        amountAvailableInt = getAmountAvailable()
        maxNumberOfStocksInt = getMaxNumberOfStocks()
        maxNumberOfActiveAboveMaxHeldInt = getMaxNumberOfActiveAboveMaxHeld() # to have loose cash to pay stock if both sell and buy at same time
        currentNumberOfTotalHeldAndActive = getCurrentNumberOfStocksHeld() + getCurrentNumberOfStocksActiveBuy() - getCurrentNumberOfStocksActiveSell()
        orderNnValuePriceFloat = float(orderNnValuePriceStr)
        orderNnValueVolumeStr = str(int(amountAvailableInt / (maxNumberOfStocksInt + maxNumberOfActiveAboveMaxHeldInt - currentNumberOfTotalHeldAndActive) / orderNnValuePriceFloat))
        
        return orderNnValueVolumeStr
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getNnStockValidUntil():
    try:
        orderNnStockValidUntil = None
        if isMarketOpenNow():
            orderNnStockValidUntil = mod_shared.getDateTodayStr()
        else:
            noMatch = True
            day = 1
            while noMatch:
                dateTodayStr = mod_shared.getDateTodayStr()
                timeStr = '10:00' # red day open half day always 9-13
                timestampToday = datetime.datetime.strptime(dateTodayStr + ' ' + timeStr, '%Y-%m-%d %H:%M')
                timestampOtherday = timestampToday + datetime.timedelta(day)
                if isMarketOpenCustom(timestampOtherday):
                    timestampPosix = time.mktime(timestampOtherday.timetuple())
                    dateStr = datetime.date.fromtimestamp(timestampPosix).strftime('%Y-%m-%d')
                    orderNnStockValidUntil = dateStr
                    noMatch = False
                else:
                    day += 1
        return orderNnStockValidUntil
        # if not marketopen, valid until next day open
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def getPayloadOrderValues(sbStockNameShort, sbSignalType, orderNnValuePrice):
    try:
        orderNnValueVolume = 1 # if something goes wrong, buy or sells 1
        if sbSignalType == glo_sbSignalBuy:
            orderNnValueVolume = getNnStockVolume(orderNnValuePrice)
        elif sbSignalType == glo_sbSignalSell:
            orderNnValueVolume = getStocksNumberHeld(sbStockNameShort)
        if orderNnValueVolume == '0': # if price of stock higher than amount available
            print('orderNnValueVolume was zero. Aborting')
            return None
        orderNnValueValidUntil = getNnStockValidUntil()
        payloadOrder = {
            glo_orderNn_key_currency: glo_orderNn_value_currencySek,
            glo_orderNn_key_openVolume: glo_orderNn_value_openVolume,
            glo_orderNn_key_orderType: glo_orderNn_value_orderType,
            glo_orderNn_key_smartOrder: glo_orderNn_value_smartOrder,
            glo_orderNn_key_price: orderNnValuePrice,
            glo_orderNn_key_volume: orderNnValueVolume,
            glo_orderNn_key_validUntil: orderNnValueValidUntil
        }
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
                payloadOrder.update({glo_orderNn_key_identifier:row.get(mod_shared.glo_colName_identifier_id), 
                    glo_orderNn_key_marketId:row.get(mod_shared.glo_colName_market_id), 
                    glo_orderNn_key_side:sbSignalType})
                return payloadOrder
        return None
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))  

def isWeekDay():
    try:
        if 1 <= mod_shared.getTimestamp().isoweekday() <= 5: # mon-fri <-> 1-5
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isNotRedDay():
    try:
        for date, time in glo_redDays.items():
            if time['CLOSE_START'] < mod_shared.getTimestamp() < time['CLOSE_END']:
                return False # IS red day
        return True # is NOT red day
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isWeekDayCustom(timestamp):
    try:
        if 1 <= timestamp.isoweekday() <= 5: # mon-fri <-> 1-5
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isNotRedDayCustom(timestamp):
    try:
        for date, time in glo_redDays.items():
            if time['CLOSE_START'] < timestamp < time['CLOSE_END']:
                return False # IS red day
        return True # is NOT red day
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isMarketHours():
    try:
        if glo_marketOpeningTime <= mod_shared.getTimestamp().time() < glo_marketClosingTime:
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isSbHours():
    try:
        if glo_afterMarketHoursOpen <= mod_shared.getTimestamp().time() < glo_afterMarketHoursClosed:
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))    

def isMarketOpenNow():
    try:
        if isMarketHours() and isWeekDay() and isNotRedDay():
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isMarketOpenCustom(timestamp):
    try:
        if isWeekDayCustom(timestamp) and isNotRedDayCustom(timestamp):
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

# def isAfterMarketHours():
    # try:
    #     if isSbHours() and isWeekDay() and isNotRedDay():
    #         return True
    #     else:
    #         return False
    # except Exception as e:
    #     print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
    #     mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def isLastPriceWithinBuyLevel(sbPriceLevelStr, sbLastPriceStr, sbStockNameShort):
    try:
        print(sbStockNameShort)
        percentageChangeLimit = 0.8
        decimalChangeLimit = (percentageChangeLimit/100) + 1
        sbLastPriceFloat = float(sbLastPriceStr)
        sbPriceLevelFloat = float(sbPriceLevelStr)
        print('sbPriceLevelStr:', sbPriceLevelStr)
        print('sbPriceLevelFloat:', sbPriceLevelFloat)
        print('sbLastPriceStr:', sbLastPriceStr)
        print('sbLastPriceFloat:', sbLastPriceFloat)
        print('sbPriceLevelFloat * decimalChangeLimit (if sbLastPriceFloat is less -> True):', sbPriceLevelFloat * decimalChangeLimit)
        if sbLastPriceFloat < sbPriceLevelFloat * decimalChangeLimit:
            return True
        else:
            return False
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))   

def createPidFile(path_rel, name_of_file):
    try:
        pidInt = os.getpid()
        file_pid = mod_shared.path_base + path_rel + name_of_file
        with open(file_pid, "w") as file:
            file.write(str(pidInt))
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def resetTempActive():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        local_glo_stockStatus_list = mod_shared.getGlobalList(mod_shared.glo_stockStatus_list_name)
        for row in local_glo_stockStatus_list:
            row[mod_shared.glo_colName_activeTemp] = glo_status_value_activeTempDefault
        setStockListGlobally(local_glo_stockStatus_list, mod_shared.glo_stockStatus_list_name)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))   

def resetDaily():
    print ('\n', inspect.stack()[0][3])
    print(mod_shared.getTimestampStr())
    try:
        # set active temp to empty
        resetTempActive()
        # setStockStatus()
        stocksToBuy_list = setAndGetStockStatusFromNn()
        mod_shared.setStockListGlobally(stocksToBuy_list, mod_shared.glo_stockStatus_list_name)
        if isStockFileOlderThanCondition(glo_timeConditionRerunStockFile, mod_shared.glo_stockToBuy_file):
            mod_list.main()
        # reset error counter
        mod_shared.resetCounterError()
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))   

def nordnetPlaceOrder(sbStockNameShort, sbSignalType): #sbSignalType = BUY or SELL
    print ('\nSTART', inspect.stack()[0][3])
    try:
        print('nordnet login\n')        
        r, header, s = mod_shared.nordnetLogin() # login to nordnet

        # nordnet price
        orderNnValuePrice = getNnStockPrice(sbStockNameShort, sbSignalType, s)
        payloadOrder = getPayloadOrderValues(sbStockNameShort, sbSignalType, orderNnValuePrice)
        # validatePayloadOrder(payloadOrder)
        if payloadOrder == None:
            print('payloadOrder returned None, aborting Order')
            return None

        test_bool = False
        # test_bool = True
        if test_bool:
            print(inspect.stack()[0][3], 'is in TEST MODE - aborting order')
            pprint(payloadOrder)
            setStockActiveTemp(sbStockNameShort, sbSignalType)
            updateAmountAvailable(sbSignalType, payloadOrder)
            writeOrderStatistics(sbStockNameShort, payloadOrder)
            mod_shared.sendEmail(sbStockNameShort + ':' + sbSignalType, sbStockNameShort + '\n'+ pformat(payloadOrder))
            return None

        header['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        header['ntag'] = r.headers['ntag']
        header['User-Agent'] = mod_shared.glo_urlHeader.get('User-Agent')
        urlOrder = 'https://www.nordnet.se/api/2/accounts/18272500/orders'
        r = s.post(urlOrder, headers=header, data=payloadOrder)
        if r.status_code == 200:
            print ('SUCCESS: order placed!')
            print(sbStockNameShort)
            pprint(payloadOrder)
            setStockActiveTemp(sbStockNameShort, sbSignalType)
            updateAmountAvailable(sbSignalType, payloadOrder)
            writeOrderStatistics(sbStockNameShort, payloadOrder)
            mod_shared.sendEmail(sbStockNameShort + ':' + sbSignalType, sbStockNameShort + '\n'+ pformat(payloadOrder))
        else:
            print('FAILED: order failed!')
            print('status_code:', r.status_code)
            print('text:', r.text)
            responseDict = {
            'status_code': str(r.status_code),
            'reason': r.reason,
            'url': r.url
            }
            mod_shared.writeErrorLog(inspect.stack()[0][3], pformat(responseDict))
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def pretendNordnetPlaceOrder(sbStockNameShort, sbSignalType):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        pass
        # print('nordnet login\n')        
        # r, header, s = mod_shared.nordnetLogin() # login to nordnet

        # # nordnet price
        # orderNnValuePrice = getNnStockPrice(sbStockNameShort, sbSignalType, s)
        # payloadOrder = getPayloadOrderValues(sbStockNameShort, sbSignalType, orderNnValuePrice)
        # if payloadOrder == None:
        #     print('payloadOrder returned None, aborting Order')
        #     return None

        # print ('PRETEND nordnet placing order\n')
        # if True: # Success
        #     print ('PRETEND SUCCESS order\n')
        #     pprint(payloadOrder)
        #     setStockActiveTemp(sbStockNameShort, sbSignalType)
        #     # setStockPriceTemp(sbStockNameShort, payloadOrder.get(orderNnValuePrice))
        #     # sendEmail(sbStockNameShort + ':' + sbSignalType, sbStockNameShort + '\n'+ pformat(payloadOrder))
        # else:
        #     print('PRETEND order FAILED!')
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')    

def sbGetSignal_afterMarketHours():
    print ('\nSTART', inspect.stack()[0][3])
    print(mod_shared.getTimestampStr())
    try:
        # Login in to SB, return browser object
        browser = mod_shared.sbLogin()

        # Find and go to Watchlist
        link = browser.find('a', href=re.compile('Watchlist')) # find Watchlist link
        link = browser.follow_link(link)
        # Find stock and signal
        rowWatchlist = browser.find_all('tr', id=re.compile('MainContent_SignalListGrid1_DXDataRow')) #find all <tr> in Watchlist
        if rowWatchlist is not None:
            for row in rowWatchlist:
                sbStockNameShort = row.td.a.get_text()
                sbSignal = row.find_all('td')[7].get_text()
                sbAveragePrice = row.find_all('td')[6].get_text()
                sbLastPrice = row.find_all('td')[12].get_text()
                if sbSignal == glo_sbSignalShort: # SELL or SHORT = SELL
                    sbSignal = glo_sbSignalSell
                
                # confirmation statistics
                if sbSignal == glo_sbSignalSell or sbSignal == glo_sbSignalBuy:
                    if not isConfirmationStatSet(sbStockNameShort, sbSignal):
                        writeConfirmationStatistics(sbStockNameShort, sbSignal, sbSignal, sbLastPrice, sbAveragePrice)

                if isStockActiveTemp(sbStockNameShort, sbSignal):
                    print('STOCK', sbStockNameShort, 'already has ACTIVE_TEMP signal', sbSignal)
                    continue
                if sbSignal == glo_sbSignalBuy:
                    if (
                        not isStockHeld(sbStockNameShort) and not 
                        isStockActive(sbStockNameShort, glo_sbSignalBuy) and not 
                        isMaxStockHeldAndActive() and 
                        isLastPriceWithinBuyLevel(sbAveragePrice, sbLastPrice, sbStockNameShort)
                        ):
                        print ('found', sbStockNameShort, glo_sbSignalBuy)
                        # pretendNordnetPlaceOrder(sbStockNameShort, sbSignal)
                        nordnetPlaceOrder(sbStockNameShort, sbSignal)

                elif sbSignal == glo_sbSignalSell:
                    if (
                        isStockHeld(sbStockNameShort) and not 
                        isStockActive(sbStockNameShort, sbSignal)
                        ):
                        print ('found', sbStockNameShort, glo_sbSignalSell)
                        # pretendNordnetPlaceOrder(sbStockNameShort, sbSignal)
                        nordnetPlaceOrder(sbStockNameShort, sbSignal)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def sbGetSignal():
    print ('\nSTART', inspect.stack()[0][3])
    print(mod_shared.getTimestampStr())
    try:
        # Login in to SB, return browser object
        browser = mod_shared.sbLogin()

        # Find and go to Watchlist
        link = browser.find('a', href=re.compile('Watchlist')) # find Watchlist link
        link = browser.follow_link(link)
        # Find stock and signal
        rowWatchlist = browser.find_all('tr', id=re.compile('MainContent_SignalListGrid1_DXDataRow')) #find all <tr> in Watchlist
        if rowWatchlist is not None:
            for row in rowWatchlist:
                # test = True
                test = False
                sbStockNameShort = row.td.a.get_text()
                sbLastPrice = row.find_all('td')[12].get_text()
                sbBenchmarkPrice = row.find_all('td')[8].get_text()
                sbSignal = row.find_all('td')[10].img['src'] # ex "../img/DOWNRed.png" or "[...]ONWHITE[...]""
                sbSignalConf = sbSignal[7:-4] # remove first 7 and last 4 chars (for stat use) -> ex: "DOWNRed"

                if test:
                    sbStockNameShort = 'DIVI-B.NGM'
                    # sbLastPrice = row.find_all('td')[12].get_text()
                    sbLastPrice = '0.3280'
                    # sbBenchmarkPrice = row.find_all('td')[8].get_text()
                    sbBenchmarkPrice = '0.3470'
                    # sbSignal = row.find_all('td')[10].img['src'] # ex "../img/DOWNRed.png" or "[...]ONWHITE[...]""
                    sbSignal = '../img/DOWNRed.png' # ex "../img/DOWNRed.png" or "[...]ONWHITE[...]""
                    sbSignalConf = sbSignal[7:-4] # remove first 7 and last 4 chars (for stat use) -> ex: "DOWNRed"

                # confirmation statistics
                if sbSignal.find('UP') != -1:
                    sbSignal = glo_sbSignalBuy
                elif sbSignal.find('DOWN') != -1:
                    sbSignal = glo_sbSignalSell
                else:
                    continue # sbSignal does not contain 'UP' or 'DOWN'; could ex be 'ONWhite'
                
                # set stat log
                if not isConfirmationStatSet(sbStockNameShort, sbSignalConf):
                    writeConfirmationStatistics(sbStockNameShort, sbSignal, sbSignalConf, sbLastPrice, sbBenchmarkPrice) 

                if isStockActiveTemp(sbStockNameShort, sbSignal):
                    print('STOCK', sbStockNameShort, 'already has ACTIVE_TEMP signal', sbSignal)
                    continue

                # looking for arrows and their colors. Continue to SELL/BUY if stock is in list of glo_sb_arrow_confirmedBuyOrSell_list
                confirmed_stat = False
                for item in glo_sb_arrow_confirmedBuyOrSell_list:
                    if item == sbSignalConf:
                        confirmed_stat = True

                if confirmed_stat == True:
                    if sbSignal == glo_sbSignalBuy:
                        if (
                            not isStockHeld(sbStockNameShort) and not 
                            isStockActive(sbStockNameShort, glo_sbSignalBuy) and not 
                            isMaxStockHeldAndActive() and 
                            isLastPriceWithinBuyLevel(sbBenchmarkPrice, sbLastPrice, sbStockNameShort)
                            ):
                            print ('found', sbStockNameShort, glo_sbSignalBuy)
                            # pretendNordnetPlaceOrder(sbStockNameShort, sbSignal)
                            nordnetPlaceOrder(sbStockNameShort, sbSignal)

                    elif sbSignal == glo_sbSignalSell:
                        if (
                            isStockHeld(sbStockNameShort) and not 
                            isStockActive(sbStockNameShort, sbSignal)
                            ):
                            print ('found', sbStockNameShort, glo_sbSignalSell)
                            # pretendNordnetPlaceOrder(sbStockNameShort, sbSignal)
                            nordnetPlaceOrder(sbStockNameShort, sbSignal)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')    

def triggerError():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        test = test
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def getAmountAvailableFromNn():
    try:
        r, header, s = mod_shared.nordnetLogin() # login to nordnet

        # get amount available
        soup = BeautifulSoup(s.get('https://www.nordnet.se/mux/web/depa/mindepa/depaoversikt.html', headers=mod_shared.glo_urlHeader).content, 'html.parser')
        amountAvailable_str = soup.find("td", string="Tillgängligt").next_sibling.next_sibling.get_text().strip(' SEK')
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        return amountAvailable_str

def isStockFileOlderThanCondition(time_condition_dict, file_name):
    try:
        epochSecSinceLastModification = os.path.getmtime(mod_shared.path_base + mod_shared.path_input_main + file_name)
        epochSecNow = time.time()

        ageSecDelta = epochSecNow - epochSecSinceLastModification

        # ageOfFile = str(datetime.timedelta(seconds=(epochSecNow - epochSecSinceLastModification)) - datetime.timedelta(microseconds=datetime.timedelta(seconds=(epochSecNow - epochSecSinceLastModification)).microseconds))

        ageConditionSec = mod_shared.getSecondsFromTime(days=time_condition_dict.get('days'), 
            hours=time_condition_dict.get('hours'), 
            minutes=time_condition_dict.get('minutes'), 
            seconds=time_condition_dict.get('seconds'))

        if ageConditionSec < ageSecDelta:
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))   

def askIfToRerunStockFile():
    try:
        # if ask if to run for for new list
            while True:
                answer = input(mod_shared.glo_stockToBuy_file + ' was older than time condition. Do you wish to create new file? (y/n): ')
                if answer == 'n':
                    break
                elif answer == 'y':
                    mod_list.main()
                    break
                else: 
                    print('"' + answer +'"'+ ' was not recognized. Please only use "y" or "n"')
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))   

schedule.every().day.at("19:00").do(resetDaily) # remove activetemp (active intraday orders not gone through are removed after closing)
schedule.every().day.at("19:45").do(sbGetSignal_afterMarketHours)
schedule.every().day.at("20:00").do(sbGetSignal_afterMarketHours) # repeat in case failure at first
schedule.every().day.at("22:00").do(resetDaily)

# --------------
# - separate files for
#     - trader
#     - create new lists
#     - reset Watchlist
#     - trader-monitor
#     (- send email files)
# - if stock to buy older than x: 
#     - get new stocks auto
#     - rest Watchlist
# - during run: every x day: get new stocks auto
#     - get new stocks auto
#     - rest Watchlist

# always use 'User-Agent' header

# --------------

# triggerError()

# for surverying script (in case of crash)
createPidFile(mod_shared.path_input_monitorProcess, mod_shared.glo_pid_file)

setMaxNumberOfStocks(5)
setMaxNumberOfActiveAboveMaxHeld(2)

# Leave empty or remove to use real value
setAmountAvailableStatic(140)

if isStockFileOlderThanCondition(glo_timeConditionRerunStockFile, mod_shared.glo_stockToBuy_file):
    askIfToRerunStockFile()

# !!!!! setStockStatusFromNn in test mode
stocksToBuy_list = setAndGetStockStatusFromNn()
mod_shared.setStockListGlobally(stocksToBuy_list, mod_shared.glo_stockStatus_list_name)

# clear and set new watchlist:
mod_watch.main(stocksToBuy_list)

while True:
    schedule.run_pending()
    if isMarketOpenNow():
        sbGetSignal()
        time.sleep(120)

# # for testing:
# while True:
#     schedule.run_pending()
#     # if isMarketOpen():
#     if glo_dummyCounter < 3:
#         print('glo_dummyCounter:', glo_dummyCounter)
#         sbGetSignal()
#         pprint(glo_stockStatus_list)
#         glo_dummyCounter += 1
#         time.sleep(30)

# OR?:
# schedule.every(30).seconds.do(sbGetSignal)
# schedule.every(1).minutes.do(sbGetSignal)


# while True:
#     if isMarketOpen():
#     # schedule.run_pending()
#         sbGetSignal()
#     time.sleep(1)
print ('END of script')

# Every working day at 09:00 sbGetSignal should start run
# Run every 5 minutes
# Stop every working day at 17:30

# BUY
# 1. find signal and stock
# 2. find/make sure stock is not already bought or buy is active
# 3. buy stock
# case error: send email;

# print('\nr.headers\n', r.headers)
# print('\nr.cookies\n', requests.utils.dict_from_cookiejar(r.cookies))
# print('\ns.cookies\n', requests.utils.dict_from_cookiejar(s.cookies))

# inspect.stack()[1][3]: caller functipon name
# def isRedDay():
#     print ('\nSTART', inspect.stack()[0][3])
#     try:
#         Mar_29_2018_close = datetime.datetime.strptime('2018 Mar 29 13 00', '%Y %b %d %H %M')
#         May_09_2018_close = datetime.datetime.strptime('2018 May 09 13 00', '%Y %b %d %H %M')
#         Nov_02_2018_close = datetime.datetime.strptime('2018 Nov 02 13 00', '%Y %b %d %H %M')
#         Mar_30_2018 = datetime.datetime.strptime('2018 Mar 30', '%Y %b %d').date()
#         Apr_02_2018 = datetime.datetime.strptime('2018 Apr 02', '%Y %b %d').date()
#         May_01_2018 = datetime.datetime.strptime('2018 May 01', '%Y %b %d').date()
#         May_10_2018 = datetime.datetime.strptime('2018 May 10', '%Y %b %d').date()
#         Jun_06_2018 = datetime.datetime.strptime('2018 Jun 06', '%Y %b %d').date()
#         Jun_22_2018 = datetime.datetime.strptime('2018 Jun 22', '%Y %b %d').date()
#         Dec_24_2017 = datetime.datetime.strptime('2017 Dec 24', '%Y %b %d').date()
#         Dec_25_2017 = datetime.datetime.strptime('2017 Dec 25', '%Y %b %d').date()
#         Dec_26_2017 = datetime.datetime.strptime('2017 Dec 26', '%Y %b %d').date()
#         Dec_31_2017 = datetime.datetime.strptime('2017 Dec 31', '%Y %b %d').date()
#         if mod_shared.getTimestamp().date() == dec_24_2017 or mod_shared.getTimestamp().date() == dec_25_2017 or nov_3_2017_close < mod_shared.getTimestamp() < nov_3_2017_close1:
#             return True
#         else:
#             return False
#     except Exception as e:
#         print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
#         # handleError(str(e), '')

       #     'identifier':'76848',
        #     'market_id':'11',
        #     'side':'BUY',
        #     'price':'2.10',
        #     'currency':'SEK',
        #     'volume':'1',
        #     'open_volume':'0',
        #     'order_type': 'LIMIT',
        #     'smart_order':'0',
        #     'valid_until': '2018-02-05' # if after working hours or friday, set next date when open

# class Stock:
#     def __init__(self, statusList=None):
#      if statusList is None:
#          statusList = []


# setNumberOfStocksHeld():
        # temp_glo_stockStatus_list = []
        # for row in glo_stockStatus_list:
        #     if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
        #         tempDict = row
        #         tempDict[mod_shared.glo_colName_amountHeld] = amountStr
        #         temp_glo_stockStatus_list.append(row)
        #     else:
        #         temp_glo_stockStatus_list.append(row)
        # global glo_stockStatus_list
        # glo_stockStatus_list = temp_glo_stockStatus_list
# def getPayloadOrderValuesPretend(sbStockNameShort, sbSignalType, priceStockStr):
#     try:
#         # orderNnValuePrice = getNnStockPrice(sbStockNameShort, sbSignalType)
#         orderNnValuePrice = priceStockStr
#         orderNnValueVolume = 1 # if something goes wrong, buy or sells 1
#         if sbSignalType == glo_sbSignalBuy:
#             orderNnValueVolume = getNnStockVolume(orderNnValuePrice)
#         elif sbSignalType == glo_sbSignalSell:
#             orderNnValueVolume = getStocksNumberHeld(sbStockNameShort)
#         orderNnValueValidUntil = getNnStockValidUntil()
#         payloadOrder = {
#             glo_orderNn_key_currency: glo_orderNn_value_currencySek,
#             glo_orderNn_key_openVolume: glo_orderNn_value_openVolume,
#             glo_orderNn_key_orderType: glo_orderNn_value_orderType,
#             glo_orderNn_key_smartOrder: glo_orderNn_value_smartOrder,
#             glo_orderNn_key_price: orderNnValuePrice,
#             glo_orderNn_key_volume: orderNnValueVolume,
#             glo_orderNn_key_validUntil: orderNnValueValidUntil
#         }
#         for row in glo_stockStatus_list:
#             if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
#                 payloadOrder.update({glo_orderNn_key_identifier:row.get(mod_shared.glo_colName_identifier_id), 
#                     glo_orderNn_key_marketId:row.get(mod_shared.glo_colName_market_id), 
#                     glo_orderNn_key_side:sbSignalType})
#                 return payloadOrder
#         return None
#     except Exception as e:
#             print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))   

# def getNnStockPricePretend(sbStockNameShort, sbSignalType, s):
#     try:
#         urlNnStock = None
#         for row in glo_stockStatus_list:
#             if row.get(mod_shared.glo_colName_sbNameshort) == sbStockNameShort:
#                 urlNnStock = row.get(mod_shared.glo_colName_url_nn)
#                 break
#         r = s.get(urlNnStock)
#         if r.status_code != 200:
#             print(r.url, 'failed!')
#         soup = BeautifulSoup(s.get(r.url).content, 'html.parser')
#         priceStockStr = soup.find(class_='tvaKnapp').parent.find_all('td')[2].get_text()
#         priceStockStr = priceStockStr.replace(',', '.')
#         #get number of decimals to match stock (should be dynamic since number can be either 2 or 3)
#         dec = str(len(priceStockStr.split('.')[1])) 
#         if sbSignalType == glo_sbSignalSell:
#             priceStockStr = format(float(priceStockStr) - 0.002*float(priceStockStr), '.' + (dec) + 'f') #lower market price with 0.2%
#             return priceStockStr
#         elif sbSignalType == glo_sbSignalBuy:
#             return priceStockStr
#     except Exception as e:
#             print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e)) 
                # setStockStatus() # only non-tempActive will pass down here

                    # if isStockActiveLongTime((sbStockNameShort, sbSignal))
                    # if not isStockActive(sbStockNameShort, sbSignal):
                    #     delStockActiveTemp(sbStockNameShort)
                #     elif isStockActive(sbStockNameShort, sbSignal):
                        # if isStockPriceChanged(sbStockNameShort, sbSignal):
                    #         cancelActiveStock() #real active (not temp)
                    #         delStockActiveTemp(sbStockNameShort)
                    #         delStockPriceTemp(sbStockNameShort)

# def sendEmailIfActive():
#     try:
#         temp_glo_stockStatus_list = glo_stockStatus_list
#         for row in temp_glo_stockStatus_list:
#             if row.get(mod_shared.glo_colName_active) != glo_status_value_activeDefault:
#                 sbj = row.get(mod_shared.glo_colName_sbNameshort) + ' is active: ' + row.get(mod_shared.glo_colName_active)
#                 body = pformat(row)
#                 sendEmail(sbj, body)
#     except Exception as e:
#         print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
#         mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))