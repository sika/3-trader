from pdb import set_trace as BP
import re
from robobrowser import RoboBrowser
import yaml
import os
import requests
import sys
from bs4 import BeautifulSoup
import inspect
import smtplib
import schedule
import time
import datetime
import csv
import pprint
import json
from pprint import pprint
from pprint import pformat

# logout between sessions?
# Validate payloadOrder (and other?)
# get email upon error
# possible to change and close script anytime
# on error: continue or exit?
# If max held stocks = 5: max is hold when held is max (5) or active + held = 7?
# Only use stop-loss?
# What if Internet connection drops?
# What if URL request fails?

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

# --- Global variables
# sb login form
gloSbLoginFormUser = 'ctl00$MainContent$uEmail'
gloSbLoginFormPass = 'ctl00$MainContent$uPassword'
gloSbLoginFormSubmit = 'ctl00$MainContent$btnSubmit'

# Cred strings
gloCredSb = 'credSb'
gloCredNordnet = 'credNordnet'
gloCredGmailAutotrading = 'credGmailAutotrading'

# stock status keys
gloStockStatusList = []
gloStatus_Key_NameShortSb = 'NAMESHORT_SB'
gloStatus_Key_NameNordnet = 'NAME_NORDNET'
gloStatus_Key_Held = 'HELD'
gloStatus_Key_Active = 'ACTIVE'
gloStatus_Key_ActiveTemp = 'ACTIVE_TEMP'
gloStatus_Key_MarketId = 'MARKET_ID'
gloStatus_Key_Identifier = 'IDENTIFIER'
gloStatus_Key_UrlNordnet = 'URL_NORDNET'
gloStatus_Key_StocksAmountHeld = 'AMOUNT_HELD'
gloStatus_Key_Price = 'PRICE'
gloStatus_Key_PriceTemp = 'PRICE_TEMP'

# stock status values
gloStatus_tempValue_ActiveNnSell = 'Sälj'
gloStatus_tempValue_ActiveNnBuy = 'Köp'
gloStatus_Value_ActiveBuy = 'BUY'
gloStatus_Value_ActiveSell = 'SELL'
gloStatus_Value_ActiveDefault = ''
gloStatus_Value_HeldYes = 'YES'
gloStatus_Value_HeldDefault = ''
gloStatus_Value_StocksAmountHeldDefault = ''
gloStatus_Value_ActiveTempDefault = ''
gloStatus_Value_PriceDefault = ''

# payloadOrder- Keys
gloOrderNnKeyIdentifier = 'identifier'
gloOrderNnKeyMarketId = 'market_id'
gloOrderNnKeySide = 'side'
gloOrderNnKeyPrice = 'price'
gloOrderNnKeyCurrency = 'currency'
gloOrderNnKeyVolume = 'volume'
gloOrderNnKeyOpenVolume = 'open_volume'
gloOrderNnKeyOrderType = 'order_type'
gloOrderNnKeySmartOrder = 'smart_order'
gloOrderNnKeyValidUntil = 'valid_until'

# payloadOrder- Values
gloOrderNnValueCurrencySek = 'SEK'
gloOrderNnValueOpenVolume = '0'
gloOrderNnValueOrderType = 'LIMIT'
gloOrderNnValueSmartOrder = '0'

# whatchlist
gloSbSignalBuy = 'BUY'
gloSbSignalSell = 'SELL'
gloSbSignalShort = 'SHORT'

# email
gloEmailRuleFw = '(-)'

# time
gloOpeningTime = datetime.time(9,0)
gloClosingTime = datetime.time(17,30)

# amount to deal with
gloCurrentNumberOfStocksHeld = gloMaxNumberOfStocks = None # saftey reason: will not trade if something goes wrong
gloAmountAvailable = gloAmountAvailableStatic = None

# glo_dummyCounter = 0

# error
glo_counter_error = 0

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


def writeErrorLog (callingFunction, eStr):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        global glo_counter_error
        glo_counter_error += 1
        errorDate = 'DATE'
        errorTime = 'TIME'
        errorDay = 'DAY'
        errorCounter = 'ERROR_COUNTER'
        errorCallingFunction = 'CALLING_FUNCTION'
        errorMsg = 'E_MSG'
        file_errorLog = pathFile + sPathError + 'errorLog.csv'
        file_exists = os.path.isfile(file_errorLog)
        if glo_counter_error <= 100:
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
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def writeOrderStatistics(sbStockNameShort, payloadOrder):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        statDate = 'DATE'
        statTime = 'TIME'
        statDay = 'DAY'
        statNameshortSb = 'NAMESHORT_SB'
        statSignal = 'SIGNAL'
        statPrice = 'PRICE'
        file_orderStat = pathFile + sPathOutput + 'orderStatistics.csv'
        file_exists = os.path.isfile(file_orderStat)
        with open (file_orderStat, 'a') as csvFile:
            fieldnames = [statDate, statTime, statDay, statNameshortSb, statSignal, statPrice]
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
            if not file_exists:
                writer.writeheader()
            writer.writerow({statDate: getDateTodayStr(), 
                statTime: getTimestampCustomStr("%H:%M"), 
                statDay: getDateTodayCustomStr('%A'), 
                statNameshortSb: sbStockNameShort,
                statSignal: payloadOrder[gloOrderNnKeySide], 
                statPrice: payloadOrder[gloOrderNnKeyPrice]})
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

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
        writeErrorLog(inspect.stack()[0][3], str(e))        

def initStockStatus():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        with open(pathFile + sPathInput + 'stockStatus.csv', 'rt', encoding='ISO-8859-1') as file:
            records = csv.DictReader(file, delimiter=';')
            for row in records:
                setStockList(row)
        # get held stocks from Nordnet
    except Exception as e:
            print ("ERROR in", inspect.stack()[0][3], ':', str(e))
            writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def setStockList(rowDict):
    try:
        global gloStockStatusList
        gloStockStatusList.append(rowDict)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setStockStatus():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        # Login into to Nordnet
        r, header, s = nordnetLogin() # login to nordnet

        # get amount available
        soup = BeautifulSoup(s.get('https://www.nordnet.se/mux/web/depa/mindepa/depaoversikt.html').content, 'html.parser')
        amountAvailableStr = soup.find("td", string="Tillgängligt").next_sibling.next_sibling.get_text().strip(' SEK')
        setAmountAvailable(int(amountAvailableStr))

        # reset stock status: held; active; amount held
        resetStockStatus() 
        # Get held and number of stocks held
        stockTable = soup.find(id='aktier')
        stockHeldAndAmount = stockTable.find_all('tr', id=re.compile('tr')) # find <tr> where id='tr[x]'
        if stockHeldAndAmount:
            for stock in stockHeldAndAmount:
                # get held
               nnStockName = stock.find(class_='truncate18').get_text(strip=True)
               setStockHeld(getSbNameShortByNnName(nnStockName)) #set Held
               # get number of stocks
               nnStockNumberOfStocks = stock.find_all('td')[3].get_text(strip=True)
               setStocksNumberHeld(getSbNameShortByNnName(nnStockName), nnStockNumberOfStocks) # set number held

        # set stock price
        # setStockPrice(s) # not needed if not cancelling order and placing new with new price 

        # get Active
        soup = BeautifulSoup(s.get('https://www.nordnet.se/mux/ajax/trade/orders/auto?accountNumber=18272500').content, 'html.parser') # active are placed in "share"
        newDict = json.loads(str(soup))
        newList = newDict.get('share')
        for item in newList:
            nnStockName = item.get('longName')
            nnStockActiveType = item.get('buyOrSell')
            if nnStockActiveType == gloStatus_tempValue_ActiveNnBuy: #active BUY
                setStockActive(getSbNameShortByNnName(nnStockName), gloStatus_Value_ActiveBuy) # set active
            elif nnStockActiveType == gloStatus_tempValue_ActiveNnSell: #active SELL
                setStockActive(getSbNameShortByNnName(nnStockName), gloStatus_Value_ActiveSell) # set active
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def resetStockStatus():
    print ('\n', inspect.stack()[0][3])
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            row[gloStatus_Key_Held] = gloStatus_Value_HeldDefault
            row[gloStatus_Key_Active] = gloStatus_Value_ActiveDefault
            row[gloStatus_Key_StocksAmountHeld] = gloStatus_Value_StocksAmountHeldDefault
        gloStockStatusList = tempGloStockStatusList
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setStockHeld(sbStockNameShort):
    print ('\n', inspect.stack()[0][3])
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                row.update({gloStatus_Key_Held:gloStatus_Value_HeldYes})
        gloStockStatusList = tempGloStockStatusList
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def isStockHeld(sbStockNameShort):
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort and row.get(gloStatus_Key_Held) == gloStatus_Value_HeldYes:
                return True
        return False # if no match
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setStocksNumberHeld(sbStockNameShort, amountStr):
    print ('\n', inspect.stack()[0][3])
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                row.update({gloStatus_Key_StocksAmountHeld:amountStr})
        gloStockStatusList = tempGloStockStatusList
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getStocksNumberHeld(sbStockNameShort):
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                if row.get(gloStatus_Key_StocksAmountHeld) != '':
                    return row.get(gloStatus_Key_StocksAmountHeld)
                else:
                    raise ValueError(inspect.stack()[0][3] + ': returned empty string')
                    return None
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

# def updateStocksNumberHeld(sbStockNameShort, numberOfStocksStr, sbSignalType): # subtract volume from current held
    # try:
    #     global gloStockStatusList
    #     tempGloStockStatusList = gloStockStatusList
    #     if sbSignalType == gloSbSignalBuy: #add stocks
    #         for row in tempGloStockStatusList:
    #             if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
    #                 newStockNumberHeld = str(eval('int(row.get(gloStatus_Key_StocksAmountHeld))+int(numberOfStocksStr)'))
    #                 row.update({gloStatus_Key_StocksAmountHeld:newStockNumberHeld})
    #     elif sbSignalType == gloSbSignalSell: #subtract stocks
    #         for row in tempGloStockStatusList:
    #             if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
    #                 newStockNumberHeld = str(eval('int(row.get(gloStatus_Key_StocksAmountHeld))-int(numberOfStocksStr)'))
    #                 row.update({gloStatus_Key_StocksAmountHeld:newStockNumberHeld})
    #     gloStockStatusList = tempGloStockStatusList
    # except Exception as e:
    #     print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def setStockActive(sbStockNameShort, sbActiveType): #'BUY' or 'SELL'
    print ('\n', inspect.stack()[0][3])
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                row.update({gloStatus_Key_Active:sbActiveType})
        gloStockStatusList = tempGloStockStatusList
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def isStockActive(sbStockNameShort, sbActiveType):
    try:
        for row in gloStockStatusList:
            if sbActiveType == gloSbSignalBuy:
                if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort and row.get(gloStatus_Key_Active) == gloStatus_Value_ActiveBuy:
                    return True
            elif sbActiveType == gloSbSignalSell:
                if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort and row.get(gloStatus_Key_Active) == gloStatus_Value_ActiveSell:
                    return True
        return False # if no match
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setStockActiveTemp(sbStockNameShort, sbActiveType):
    print ('\n', inspect.stack()[0][3])
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                row.update({gloStatus_Key_ActiveTemp:sbActiveType})
        gloStockStatusList = tempGloStockStatusList
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def delStockActiveTemp(sbStockNameShort):
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                row.update({gloStatus_Key_ActiveTemp:gloStatus_Value_ActiveTempDefault})
        gloStockStatusList = tempGloStockStatusList
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def isStockActiveTemp(sbStockNameShort, sbActiveType):
    try:
        for row in gloStockStatusList:
            if sbActiveType == gloSbSignalBuy:
                if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort and row.get(gloStatus_Key_ActiveTemp) == gloStatus_Value_ActiveBuy:
                    return True
            elif sbActiveType == gloSbSignalSell:
                if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort and row.get(gloStatus_Key_ActiveTemp) == gloStatus_Value_ActiveSell:
                    return True
        return False # if no match
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

# def setStockPrice(s):
    # try:
    #     global gloStockStatusList
    #     tempGloStockStatusList = gloStockStatusList
    #     for row in tempGloStockStatusList:
    #         if row[gloStatus_Key_ActiveTemp] != gloStatus_Value_ActiveTempDefault:
    #             urlNnStock = row.get(gloStatus_Key_UrlNordnet)
    #             r = s.get(urlNnStock)
    #             if r.status_code != 200:
    #                 print(r.url, 'failed!')
    #             soup = BeautifulSoup(s.get(r.url).content, 'html.parser')
    #             priceStockStr = soup.find(class_='tvaKnapp').parent.find_all('td')[2].get_text()
    #             priceStockStr = priceStockStr.replace(',', '.')
    #             row[gloStatus_Key_Price] = priceStockStr
    #     gloStockStatusList = tempGloStockStatusList
    # except Exception as e:
    #         print ("ERROR in", inspect.stack()[0][3], ':', str(e))

# def setStockPriceTemp(sbStockNameShort, orderNnValuePrice):
    # print ('\n', inspect.stack()[0][3])
    # try:
    #     global gloStockStatusList
    #     tempGloStockStatusList = gloStockStatusList
    #     for row in tempGloStockStatusList:
    #         if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
    #             row.update({gloStatus_Key_PriceTemp:orderNnValuePrice})
    #     gloStockStatusList = tempGloStockStatusList
    # except Exception as e:
    #     print ("ERROR in", inspect.stack()[0][3], ':', str(e))

# def delStockPriceTemp(sbStockNameShort, orderNnValuePrice):
    # try:
    # except Exception as e:
    #     print ("ERROR in", inspect.stack()[0][3], ':', str(e))    

def isStockPriceChanged(sbStockNameShort, sbSignalType):
    try:
        tempGloStockStatusList = gloStockStatusList
        percentageChangeLimit = 0.5
        if sbSignalType == gloSbSignalBuy:
            for row in tempGloStockStatusList:
                if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                    orderPrice = float(tempGloStockStatusList.get(gloStatus_Key_PriceTemp))
                    newPrice = float(tempGloStockStatusList.get(gloStatus_Key_Price))
                    decimalChange = newPrice / orderPrice
                    percentageChange = decimalChange * 100-100
                    if percentageChange > percentageChangeLimit:
                        return True
                    else:
                        return False
        if sbSignalType == gloSbSignalSell:
            for row in tempGloStockStatusList:
                if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                    orderPrice = float(tempGloStockStatusList.get(gloStatus_Key_PriceTemp))
                    newPrice = float(tempGloStockStatusList.get(gloStatus_Key_Price)) 
                    decrease = orderPrice - newPrice
                    decreasePercentage = (decrease / orderPrice) * 100
                    if decreasePercentage > percentageChangeLimit:
                        return True
                    else:
                        return False
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getSbNameShortByNnName(nnStockName):
    try:
        for row in gloStockStatusList:
            if row.get(gloStatus_Key_NameNordnet) == nnStockName:
                return row.get(gloStatus_Key_NameShortSb)
        print ('could not match', nnStockName, 'with', gloStatus_Key_NameShortSb)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def isMaxStockHeldAndActive():
    try:
        maxNumberOfStocks = getMaxNumberOfStocks()
        currentNumberOfStocksHeld = getCurrentNumberOfStocksHeld()
        currentNumberOfStocksActiveBuy = getCurrentNumberOfStocksActiveBuy()
        currentStockHeldAndActive = currentNumberOfStocksHeld + currentNumberOfStocksActiveBuy
        if  currentStockHeldAndActive >= maxNumberOfStocks:
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getTimestamp():
    return datetime.datetime.now()

def getTimestampStr():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def getTimestampCustomStr(custom):
    return datetime.datetime.now().strftime(custom)

def getDateToday():
    return datetime.date.today()

def getDateTodayStr():
    return datetime.date.today().strftime('%Y-%m-%d')

def getDateTodayCustomStr(custom):
    return datetime.date.today().strftime(custom)

def setAmountAvailableStatic(amountInt):
    print ('\n', inspect.stack()[0][3])
    try:
        global gloAmountAvailableStatic
        gloAmountAvailableStatic = amountInt
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setAmountAvailable(amountInt):
    print ('\n', inspect.stack()[0][3])
    try:
        global gloAmountAvailable
        gloAmountAvailable = amountInt
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getAmountAvailable():
    try:
        amountAvailable = gloAmountAvailable
        amountAvailableStatic = gloAmountAvailableStatic
        if amountAvailableStatic is not None:
            return amountAvailableStatic
        else:
            return amountAvailable
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getCurrentNumberOfStocksHeld():
    try:
        counter = 0
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_Held) == gloStatus_Value_HeldYes:
                counter += 1
        return counter
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getCurrentNumberOfStocksActiveBuy():
    try:
        counter = 0
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_ActiveTemp) == gloStatus_Value_ActiveBuy:
                counter += 1
        return counter
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def setMaxNumberOfStocks(numberOfStocksInt):
    print ('\n', inspect.stack()[0][3])
    try:
        global gloMaxNumberOfStocks
        gloMaxNumberOfStocks = numberOfStocksInt
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getMaxNumberOfStocks():
    try:
        maxNumberOfStocks = gloMaxNumberOfStocks
        return maxNumberOfStocks
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getNnStockPrice(sbStockNameShort, sbSignalType, s):
    try:
        sellPercentageChange = 0.05
        urlNnStock = None
        for row in gloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                urlNnStock = row.get(gloStatus_Key_UrlNordnet)
                break
        r = s.get(urlNnStock)
        if r.status_code != 200:
            print(r.url, 'failed!')
        soup = BeautifulSoup(s.get(r.url).content, 'html.parser')
        priceStockStr = soup.find(class_='tvaKnapp').parent.find_all('td')[2].get_text()
        priceStockStr = priceStockStr.replace(',', '.')
        #get number of decimals to match stock (should be dynamic since number can be either 2 or 3)
        dec = str(len(priceStockStr.split('.')[1])) 
        if sbSignalType == gloSbSignalSell:
            priceStockStr = format(float(priceStockStr) - sellPercentageChange*float(priceStockStr), '.' + (dec) + 'f') #lower market price with 0.2%
            return priceStockStr
        elif sbSignalType == gloSbSignalBuy:
            return priceStockStr
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e)) 

def getNnStockVolume(orderNnValuePriceStr):
    try:
        # get amount available
        amountAvailableInt = getAmountAvailable()
        maxNumberOfStocksInt = getMaxNumberOfStocks()
        currentNumberOfStocksHeldInt = getCurrentNumberOfStocksHeld()
        orderNnValuePriceFloat = float(orderNnValuePriceStr)
        orderNnValueVolumeStr = str(int(amountAvailableInt / (maxNumberOfStocksInt - currentNumberOfStocksHeldInt) / orderNnValuePriceFloat))
        return orderNnValueVolumeStr
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getNnStockValidUntil():
    try:
        orderNnStockValidUntil = None
        if isMarketOpen():
            orderNnStockValidUntil = getDateTodayStr()
        return orderNnStockValidUntil

    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def getPayloadOrderValues(sbStockNameShort, sbSignalType, orderNnValuePrice):
    try:
        orderNnValueVolume = 1 # if something goes wrong, buy or sells 1
        if sbSignalType == gloSbSignalBuy:
            orderNnValueVolume = getNnStockVolume(orderNnValuePrice)
        elif sbSignalType == gloSbSignalSell:
            orderNnValueVolume = getStocksNumberHeld(sbStockNameShort)
        if orderNnValueVolume == '0':
            print('orderNnValueVolume was zero. Aborting')
            return None
        orderNnValueValidUntil = getNnStockValidUntil()
        payloadOrder = {
            gloOrderNnKeyCurrency: gloOrderNnValueCurrencySek,
            gloOrderNnKeyOpenVolume: gloOrderNnValueOpenVolume,
            gloOrderNnKeyOrderType: gloOrderNnValueOrderType,
            gloOrderNnKeySmartOrder: gloOrderNnValueSmartOrder,
            gloOrderNnKeyPrice: orderNnValuePrice,
            gloOrderNnKeyVolume: orderNnValueVolume,
            gloOrderNnKeyValidUntil: orderNnValueValidUntil
        }
        for row in gloStockStatusList:
            if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
                payloadOrder.update({gloOrderNnKeyIdentifier:row.get(gloStatus_Key_Identifier), 
                    gloOrderNnKeyMarketId:row.get(gloStatus_Key_MarketId), 
                    gloOrderNnKeySide:sbSignalType})
                return payloadOrder
        return None
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))  

def nordnetPlaceOrder(sbStockNameShort, sbSignalType): #sbSignalType = BUY or SELL
    print ('\nSTART', inspect.stack()[0][3])
    try:
        print('nordnet login\n')        
        r, header, s = nordnetLogin() # login to nordnet

        # nordnet price
        orderNnValuePrice = getNnStockPrice(sbStockNameShort, sbSignalType, s)
        payloadOrder = getPayloadOrderValues(sbStockNameShort, sbSignalType, orderNnValuePrice)
        # validatePayloadOrder(payloadOrder)
        if payloadOrder == None:
            print('payloadOrder returned None, aborting Order')
            return None

        header['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        header['ntag'] = r.headers['ntag']
        urlOrder = 'https://www.nordnet.se/api/2/accounts/18272500/orders'
        r = s.post(urlOrder, headers=header, data=payloadOrder)
        if r.status_code == 200:
            print ('SUCCESS: order placed!')
            print(sbStockNameShort)
            pprint(payloadOrder)
            setStockActiveTemp(sbStockNameShort, sbSignalType)
            writeOrderStatistics(sbStockNameShort, payloadOrder)
            sendEmail(sbStockNameShort + ':' + sbSignalType, sbStockNameShort + '\n'+ pformat(payloadOrder))
        else:
            print('FAILED: order failed!')
            print('status_code:', r.status_code)
            print('text:', r.text)
            responseDict = {
            'status_code': str(r.status_code),
            'reason': r.reason,
            'url': r.url
            }
            writeErrorLog(inspect.stack()[0][3], pformat(responseDict))
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def pretendNordnetPlaceOrder(sbStockNameShort, sbSignalType):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        print('nordnet login\n')        
        r, header, s = nordnetLogin() # login to nordnet

        # nordnet price
        orderNnValuePrice = getNnStockPrice(sbStockNameShort, sbSignalType, s)
        payloadOrder = getPayloadOrderValues(sbStockNameShort, sbSignalType, orderNnValuePrice)
        if payloadOrder == None:
            print('payloadOrder returned None, aborting Order')
            return None

        print ('PRETEND nordnet placing order\n')
        if True: # Success
            print ('PRETEND SUCCESS order\n')
            pprint(payloadOrder)
            setStockActiveTemp(sbStockNameShort, sbSignalType)
            # setStockPriceTemp(sbStockNameShort, payloadOrder.get(orderNnValuePrice))
            # sendEmail(sbStockNameShort + ':' + sbSignalType, sbStockNameShort + '\n'+ pformat(payloadOrder))
        else:
            print('PRETEND order FAILED!')
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')    

def nordnetLogin():
    try:
        s = requests.session()
        print ('nordnetLogin()\n')
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
        credNord = getCredentials(gloCredNordnet)
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
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        msg = 'status code: ' + r.status_code + '; ' + r.text
        writeErrorLog(inspect.stack()[0][3], msg)
    else:
        print('END', inspect.stack()[0][3], '\n')
        return (r, header, s)

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
        writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')
        return (browser)

def sbGetSignal():
    print ('\nSTART', inspect.stack()[0][3])
    # Check SB for stock and signals
    try:
        # Login in to SB, return browser object
        browser = sbLogin()

        # Find and go to Watchlist
        link = browser.find('a', href=re.compile('Watchlist')) # find Watchlist link
        link = browser.follow_link(link)
        # Find stock and signal
        rowWatchlist = browser.find_all('tr', id=re.compile('MainContent_SignalListGrid1_DXDataRow')) #find all <tr> in Watchlist
        if rowWatchlist is not None:
            for row in rowWatchlist:
                sbStockNameShort = row.td.a.get_text()
                sbSignal = row.find_all('td')[7].get_text()
                if sbSignal == gloSbSignalShort: # SELL or SHORT = SELL
                    sbSignal = gloSbSignalSell
                if isStockActiveTemp(sbStockNameShort, sbSignal):
                    print('STOCK', sbStockNameShort, 'already has ACTIVE_TEMP signal', sbSignal)
                    continue
                # if first placed BUY, then signal change to SELL, need to know true status of that stock (held or active)
                if sbSignal == gloSbSignalSell and isStockActiveTemp(sbStockNameShort, gloSbSignalBuy):
                    setStockStatus()
                elif sbSignal == gloSbSignalBuy and isStockActiveTemp(sbStockNameShort, gloSbSignalSell):
                    setStockStatus()
                                    
                if sbSignal == gloSbSignalBuy:
                    if (
                        not isStockHeld(sbStockNameShort) and not 
                        isStockActive(sbStockNameShort, gloSbSignalBuy) and not 
                        isMaxStockHeldAndActive()
                        ):
                        print ('found', sbStockNameShort, gloSbSignalBuy)
                        # pretendNordnetPlaceOrder(sbStockNameShort, sbSignal)
                        nordnetPlaceOrder(sbStockNameShort, sbSignal)

                elif sbSignal == gloSbSignalSell:
                    if (
                        isStockHeld(sbStockNameShort) and not 
                        isStockActive(sbStockNameShort, sbSignal)
                        ):
                        print ('found', sbStockNameShort, gloSbSignalSell)
                        # pretendNordnetPlaceOrder(sbStockNameShort, sbSignal)
                        nordnetPlaceOrder(sbStockNameShort, sbSignal)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def sendEmail(sbj, body):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        sbj = sbj + ' ' + gloEmailRuleFw
        msg = 'Subject: {}\n\n{}'.format(sbj, body)
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        credGmailAutotrading = getCredentials(gloCredGmailAutotrading)
        # form[gloSbLoginFormUser].value = credSb.get('username')
        smtp.login(credGmailAutotrading.get('username'), credGmailAutotrading.get('pwd'))
        smtp.sendmail(credGmailAutotrading.get('username'), credGmailAutotrading.get('username'), msg) # 1 from, 2 to
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def isWeekDay():
    try:
        if 1 <= getTimestamp().isoweekday() <= 5: # mon-fri <-> 1-5
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def isNotRedDay():
    try:
        for date, time in glo_redDays.items():
            if time['CLOSE_START'] < getTimestamp() < time['CLOSE_END']:
                return False # IS red day
        return True # is NOT red day
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def isMarketHours():
    try:
        if gloOpeningTime <= getTimestamp().time() < gloClosingTime:
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def isMarketOpen():
    try:
        if isMarketHours() and isWeekDay() and isNotRedDay():
            return True
        else:
            return False
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def sendEmailIfActive():
    try:
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            if row.get(gloStatus_Key_Active) != gloStatus_Value_ActiveDefault:
                sbj = row.get(gloStatus_Key_NameShortSb) + ' is active: ' + row.get(gloStatus_Key_Active)
                body = pformat(row)
                sendEmail(sbj, body)
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))

def resetTempActive():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        global gloStockStatusList
        tempGloStockStatusList = gloStockStatusList
        for row in tempGloStockStatusList:
            row[gloStatus_Key_ActiveTemp] = gloStatus_Value_ActiveTempDefault
        gloStockStatusList = tempGloStockStatusList
        setStockStatus()
        # global glo_dummyCounter
        # glo_dummyCounter = 0
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))   

def resetDaily():
    print ('\n', inspect.stack()[0][3])
    try:
        # set active temp to empty; setStockStatus()
        resetTempActive()
        sendEmailIfActive()
        # reset error counter
        global glo_errorCounter
        glo_errorCounter = 0
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))
        writeErrorLog(inspect.stack()[0][3], str(e))   

schedule.every().day.at("20:00").do(resetDaily)

setMaxNumberOfStocks(6)
# Leave empty or remove to use real value
setAmountAvailableStatic(100)
initStockStatus()
setStockStatus()
while True:
    schedule.run_pending()
    if isMarketOpen():
        sbGetSignal()
        time.sleep(120)

# # for testing:
# while True:
#     schedule.run_pending()
#     # if isMarketOpen():
#     if glo_dummyCounter < 3:
#         print('glo_dummyCounter:', glo_dummyCounter)
#         sbGetSignal()
#         pprint(gloStockStatusList)
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
#         if getTimestamp().date() == dec_24_2017 or getTimestamp().date() == dec_25_2017 or nov_3_2017_close < getTimestamp() < nov_3_2017_close1:
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
        # tempGloStockStatusList = []
        # for row in gloStockStatusList:
        #     if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
        #         tempDict = row
        #         tempDict[gloStatus_Key_StocksAmountHeld] = amountStr
        #         tempGloStockStatusList.append(row)
        #     else:
        #         tempGloStockStatusList.append(row)
        # global gloStockStatusList
        # gloStockStatusList = tempGloStockStatusList
# def getPayloadOrderValuesPretend(sbStockNameShort, sbSignalType, priceStockStr):
#     try:
#         # orderNnValuePrice = getNnStockPrice(sbStockNameShort, sbSignalType)
#         orderNnValuePrice = priceStockStr
#         orderNnValueVolume = 1 # if something goes wrong, buy or sells 1
#         if sbSignalType == gloSbSignalBuy:
#             orderNnValueVolume = getNnStockVolume(orderNnValuePrice)
#         elif sbSignalType == gloSbSignalSell:
#             orderNnValueVolume = getStocksNumberHeld(sbStockNameShort)
#         orderNnValueValidUntil = getNnStockValidUntil()
#         payloadOrder = {
#             gloOrderNnKeyCurrency: gloOrderNnValueCurrencySek,
#             gloOrderNnKeyOpenVolume: gloOrderNnValueOpenVolume,
#             gloOrderNnKeyOrderType: gloOrderNnValueOrderType,
#             gloOrderNnKeySmartOrder: gloOrderNnValueSmartOrder,
#             gloOrderNnKeyPrice: orderNnValuePrice,
#             gloOrderNnKeyVolume: orderNnValueVolume,
#             gloOrderNnKeyValidUntil: orderNnValueValidUntil
#         }
#         for row in gloStockStatusList:
#             if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
#                 payloadOrder.update({gloOrderNnKeyIdentifier:row.get(gloStatus_Key_Identifier), 
#                     gloOrderNnKeyMarketId:row.get(gloStatus_Key_MarketId), 
#                     gloOrderNnKeySide:sbSignalType})
#                 return payloadOrder
#         return None
#     except Exception as e:
#             print ("ERROR in", inspect.stack()[0][3], ':', str(e))   

# def getNnStockPricePretend(sbStockNameShort, sbSignalType, s):
#     try:
#         urlNnStock = None
#         for row in gloStockStatusList:
#             if row.get(gloStatus_Key_NameShortSb) == sbStockNameShort:
#                 urlNnStock = row.get(gloStatus_Key_UrlNordnet)
#                 break
#         r = s.get(urlNnStock)
#         if r.status_code != 200:
#             print(r.url, 'failed!')
#         soup = BeautifulSoup(s.get(r.url).content, 'html.parser')
#         priceStockStr = soup.find(class_='tvaKnapp').parent.find_all('td')[2].get_text()
#         priceStockStr = priceStockStr.replace(',', '.')
#         #get number of decimals to match stock (should be dynamic since number can be either 2 or 3)
#         dec = str(len(priceStockStr.split('.')[1])) 
#         if sbSignalType == gloSbSignalSell:
#             priceStockStr = format(float(priceStockStr) - 0.002*float(priceStockStr), '.' + (dec) + 'f') #lower market price with 0.2%
#             return priceStockStr
#         elif sbSignalType == gloSbSignalBuy:
#             return priceStockStr
#     except Exception as e:
#             print ("ERROR in", inspect.stack()[0][3], ':', str(e)) 
                # setStockStatus() # only non-tempActive will pass down here

                    # if isStockActiveLongTime((sbStockNameShort, sbSignal))
                    # if not isStockActive(sbStockNameShort, sbSignal):
                    #     delStockActiveTemp(sbStockNameShort)
                #     elif isStockActive(sbStockNameShort, sbSignal):
                        # if isStockPriceChanged(sbStockNameShort, sbSignal):
                    #         cancelActiveStock() #real active (not temp)
                    #         delStockActiveTemp(sbStockNameShort)
                    #         delStockPriceTemp(sbStockNameShort)