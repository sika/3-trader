# NOTE! have set only 3 STOCK ROWS to get in getStocks
# only get SELL for stocks held
# emails being sent even if already sent before
# set (get) real names in getStocks csv file
import sys
import imaplib
import email
import os
import csv
import json
import pdb
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import datetime
import smtplib
import schedule
import time as timeToSleep
import yaml

date = datetime.date # assigning object for quicker handling
time = datetime.time
timeDateStampStr = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") # don't use ":", it will crash script
dateStamp = date.today()
dateStampStr = dateStamp.strftime('%d.%m.%Y') # today's date in SB format
daysPast = 5
dateStampPast = (dateStamp - datetime.timedelta(days=daysPast)) #for testing with days back
dateStampPastStr = (dateStamp - datetime.timedelta(days=daysPast)).strftime('%d.%m.%Y') #for testing with days back
emailsSent = []
global stocksBought
stocksBought = []
global stocksSold
stocksSold = []
errorCounter = 0

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))


def writeErrorLog (e, data):
    global errorCounter
    e = str(e)
    if errorCounter < 100: # to prevent too big files in case of endless loop
        with open (pathFile + sPathError + 'errorLog ' +timeDateStampStr+'-errorLog.txt', 'a', encoding='ISO-8859-1') as file:
            file.write(str(errorCounter)+': '+timeDateStampStr + ': ' + data + ': ' + e + '\r\n')
            errorCounter += 1

def getCredentials():
    conf = yaml.load(open(pathFile + sPathInput + 'credentials.yml'))
    email = conf['cred_gmail']['email']
    pwd = conf['cred_gmail']['password']
    cred = {'email': email, 'pwd': pwd}
    return cred

def setDailyVariables():
    print ("SETDAILYVARIABLES")
    global dateStamp
    dateStamp = date.today()
    global timeDateStampStr
    timeDateStampStr =  getTimeNowStr()
    global dateStampStr
    dateStampStr = dateStamp.strftime('%d.%m.%Y')
    global errorCounter
    errorCounter = 0
    global emailsSent
    emailsSent = []
    global stocksBought
    stocksBought = []
    global stocksSold
    stocksSold = []

def getTimeNowStr():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def emailSent(stockSignalDataTemp):
    global emailsSent
    emailsSent.append(stockSignalDataTemp)
    return

def isEmailSent(stockSignalDataTemp):
    global emailsSent
    for item in emailsSent:
        if (item.get('signal') == stockSignalDataTemp.get('signal') and item.get('nameShort') == stockSignalDataTemp.get('nameShort')):
            return True
        else:
            return False

def getLocalStocks(): # get 30 highest stocks (NOTE! sort before running script)
    colNames = ('nameShort', 'name', 'url', 'value', 'nameNordnet')
    listTemp = []
    with open(pathFile + sPathInput + 'stockValue.csv', 'rt', encoding='ISO-8859-1') as file:
        dReader = csv.DictReader(file, colNames, delimiter = ';')
        counter = 0;
        for row in dReader: # row is dict;
            if counter == 0:
                counter += 1
                continue # skip first row
            listTemp.append(row)
            counter += 1
            if counter == 30:
                return listTemp
                break

def monitorStocks(stockListTemp):
    print ("monitorStocks function:", getTimeNowStr())
    for item in stockListTemp: # item is type dict
        try:
            urlTemp = item.get('url')
            htmlCode = urlopen(urlTemp).read() # get the html from website
            soup = BeautifulSoup(htmlCode, 'html.parser')

            signal = soup.find_all('td', text=re.compile("€100"))[2].parent.parent.parent.parent.parent.next_sibling.contents[3].get_text()

            price = soup.find_all('td', text=re.compile("€100"))[2].parent.parent.parent.parent.parent.next_sibling.contents[2].get_text()

            dateStr = soup.find_all('td', text=re.compile("€100"))[2].parent.parent.parent.parent.parent.next_sibling.contents[1].get_text()

            if dateStr == dateStampStr:
                stockSignalData = {'nameNordnet': item.get('nameNordnet'), 'nameShort': item.get('nameShort'), 'signal': signal, 'price': price, 'url': item.get('url')}
                notify(stockSignalData)

            print ("stock: " + item.get('nameNordnet') + "\t signal: " + signal + "\t price: " + price + "\t date: " + dateStr)

        except Exception as e: # catch error
                print ("ERROR in monitorStocks: " + str(e))
                writeErrorLog(e, '(monitorStocks)' + item.get('url'))

def notify(stockSignalDataTemp):
    print ("notify function:", getTimeNowStr())
    try:
        if isEmailSent(stockSignalDataTemp): # email already sent, return to calling function
            return

        signalStr = stockSignalDataTemp.get('signal')

        if signalStr == 'SHORT' or signalStr == 'SELL':
            if isStockHeld(stockSignalDataTemp):
                pass
            else: #if stock is not held, don't want SELL/SHORT signal
                return

        cred = getCredentials() #get login credentials

        sbj = 'sb-notify:\t' + (stockSignalDataTemp.get('nameNordnet') + '\t' + stockSignalDataTemp.get('nameShort') + '\t' + stockSignalDataTemp.get('signal') + '\t' + stockSignalDataTemp.get('price'))

        body = (stockSignalDataTemp.get('nameNordnet') + '\t' + stockSignalDataTemp.get('nameShort') + '\t' + stockSignalDataTemp.get('signal') + '\t' + stockSignalDataTemp.get('price') + '\t' + stockSignalDataTemp.get('url'))

        msg = 'Subject: {}\n\n{}'.format(sbj, body)

        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        smtp.login(cred.get('email'), cred.get('pwd'))
        smtp.sendmail(cred.get('email'), "simon.noworkemail@icloud.com", msg) # 1 from, 2 to
    except Exception as e:
        print ("ERROR in notify(): " + str(e))
        writeErrorLog(e, '(notify) ' + stockSignalDataTemp.get('nameShort'))
    else:
        emailSent(stockSignalDataTemp) # add data to list of sent emails
        print ('EMAIL SENT FOR: ', stockSignalDataTemp.get('nameShort'))

def getEmailsBoughtSoldStocks():
    print ("getEmailsBoughtSoldStocks function:", getTimeNowStr())
    cred = getCredentials()
    M = imaplib.IMAP4_SSL('imap.gmail.com') #create imap object
    try:
        M.login(cred.get('email'), cred.get('pwd'))
        M.select('autotrade') # select mailbox/label (inbox default)
        # typ, data = M.search(None, 'ALL') #getting all emails
        typ, data = M.search(None, '(FROM "nordnet")') #get filtered from nordnet. Add M.search for more email/filter
        for num in data[0].split():
            typ, data = M.fetch(num, '(RFC822)') # Get whole email
            msg = email.message_from_string(data[0][1].decode('utf-8')) # get message as message list object
            # get date
            date_tuple = email.utils.parsedate_tz(msg['Date']) # parse email date to tuple
            stockDateTsmp = email.utils.mktime_tz(date_tuple) # create timestamp in seconds
            # replace byte codes with å,ä,ö and Å, Ä, Ö
            bodyStr = msg.get_payload() # get bodyStr as string
            bodyStr = bodyStr.replace('=', '') #remove '='
            bodyStr = bodyStr.replace('C3B6','ö').replace('C3A5','å').replace('C3A4','ä') # replace byte chars with å,ä,ö
            # get number of stocks
            stockAmountObj = re.search('av (.*) st', bodyStr) # find match between 'av' and 'st'

            stockAmountStr = stockAmountObj.group(1) # convert result to string
            stockAmountInt = int(stockAmountStr) # convert string to int
            # get name
            stockNameObj = re.search('st (.*) på', bodyStr) # find match between 'av' and 'st'
            stockNameStr = stockNameObj.group(1) # convert result to string
            # get signal and append to list: köp; försäljning

            isBuy = False
            isSold = False

            if bodyStr.find('köp') != -1:
                signalStr = 'buy'
                isBuy = True
            elif bodyStr.find('försäljning') != -1:
                signalStr = 'sold'
                isSold = True

            global stocksBought
            global stocksSold

            isExistingStock = False

            if isBuy:
                for iBought in range(len(stocksBought)):
                    if stocksBought[iBought].get('nameNordnet') == stockNameStr:
                        stocksBought[iBought]['stockAmount'] += stockAmountInt
                        isExistingStock = True
                        break;
                if isExistingStock == False:
                    stocksBought.append({'nameNordnet': stockNameStr, 'signal': signalStr, 'stockAmount': stockAmountInt, 'date': stockDateTsmp})

            if isSold:
                for iSold in range(len(stocksSold)):
                    if stocksSold[iSold].get('nameNordnet') == stockNameStr:
                        stocksBought[iSold]['stockAmount'] += stockAmountInt
                        isExistingStock = True
                        break;
                if isExistingStock == False:
                    stocksSold.append({'nameNordnet': stockNameStr, 'signal': signalStr, 'stockAmount': stockAmountInt, 'date': stockDateTsmp})
    except Exception as e: # catch error
            print ("ERROR in getEmailsBoughtSoldStocks(): " + str(e))
            writeErrorLog(e, '(getEmailsBoughtSoldStocks) ' + stockNametStr+ ' ' +str(stockAmountInt))
    else:
        M.close()
        M.logout()
        print ('SUCCESS in getEmailsBoughtSoldStocks()')

def getStocksHeld():
    print ("getStocksHeld function:", getTimeNowStr())
    global stocksBought
    global stocksSold
    try:
        for iBought in range(len(stocksBought)):
            for iSold in range(len(stocksSold)):
                if stocksBought[iBought].get('nameNordnet') == stocksSold[iSold].get('nameNordnet'):
                    stocksBought[iBought]['stockAmount'] -= stocksSold[iSold].get('stockAmount')
    except Exception as e: # catch error
        print ("ERROR in getStocksHeld(): " + str(e))
        writeErrorLog(e, '(getStocksHeld) NO DATA PARAMETER')
    else:
        print ('SUCCESS in getStocksHeld()')

def setStocksHeld():
    print ("setStocksHeld function:", getTimeNowStr())
    try:
        with open(pathFile + sPathOutput + 'stocksHeld.csv', 'w', encoding='ISO-8859-1') as file:
            colNames = ['stock', 'amount']
            writer = csv.DictWriter(file, fieldnames=colNames, delimiter=';')
            writer.writeheader()
            for bought in stocksBought:
                stock = bought.get('nameNordnet')
                amount = bought.get('stockAmount')
                if amount != 0:
                    writer.writerow({'stock': stock, 'amount': amount})
    except Exception as e: # catch error
        print ("ERROR in setStocksHeld(): " + str(e))
        writeErrorLog(e, '(setStocksHeld) NO DATA PARAMETER')
    else:
        print ('SUCCESS in setStocksHeld()')

def isStockHeld(stockSignalDataTemp):
    try:
        for bought in stocksBought:
            stockSoldName = bought.get('nameNordnet')
            stockSoldAmount = bought.get('stockAmount')
            stockSignalName = stockSignalDataTemp.get('nameNordnet')
            if stockSoldName == stockSignalName and stockSoldAmount != 0:
                return True
        return False
    except Exception as e: # catch error
        print ("ERROR in setStocksHeld(): " + str(e))
        writeErrorLog(e, '(setStocksHeld) NO DATA PARAMETER')
    else:
        print ('SUCCESS in setStocksHeld()')

def scriptFunction():
    print ("scriptFunction function:", getTimeNowStr())
    try:
        getEmailsBoughtSoldStocks()
        getStocksHeld()
        setStocksHeld()
        stockList = getLocalStocks()
        monitorStocks(stockList)
    except Exception as e: # catch error
        print ("ERROR in scriptFunction(): " + str(e))
        writeErrorLog(e, '(scriptFunction) NO DATA PARAMETER')
    else:
        print ('SUCCESS in scriptFunction()')

# script start
# scriptFunction()

# schedule.every(20).seconds.do(scriptFunction)
schedule.every().day.at("20:45").do(scriptFunction)

while True:
    if dateStamp != date.today(): # if new day, reset global variables
        setDailyVariables()
    schedule.run_pending()
    timeToSleep.sleep(1)
