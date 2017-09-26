# NOTE! have set only 3 STOCK ROWS to get in getStocks
# only get SELL for stocks held
# emails being sent even if already sent before
# set (get) real names in getStocks csv file

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
dateStampPast = (dateStamp - datetime.timedelta(days=2)) #for testing with days back
dateStampPastStr = (dateStamp - datetime.timedelta(days=2)).strftime('%d.%m.%Y') #for testing with days back

sPathOutput = "/output"
sPathInput = "/input"
pathFile = os.path.dirname(os.path.abspath(__file__))

emailsSent = []

errorCounter = 0

def writeErrorLog (e, data):
    global errorCounter
    e = str(e)
    if errorCounter < 100: # to prevent too big files in case of endless loop
        with open (pathFile + sPathOutput + '/errorLog ' +timeDateStampStr+'-errorLog.txt', 'a', encoding='ISO-8859-1') as file:
            file.write(str(errorCounter)+': '+timeDateStampStr + ': ' + data + ': ' + e + '\r\n')
            errorCounter += 1

def getCredentials():
    conf = yaml.load(open(pathFile + sPathInput + '/credentials.yml'))
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

def getStocks(): # get 30 highest stocks (NOTE! sort before running script)
    colNames = ('nameShort', 'name', 'url', 'value', 'nameNordnet')
    listTemp = []
    with open(pathFile + sPathInput + '/stockValue.csv', 'rt', encoding='ISO-8859-1') as file:
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
                stockSignalData = {'name': item.get('name'), 'nameShort': item.get('nameShort'), 'signal': signal, 'price': price, 'url': item.get('url')}
                notify(stockSignalData)

            print ("stock: " + item.get('nameShort') + "\t signal: " + signal + "\t price: " + price + "\t date: " + dateStr)

        except Exception as e: # catch error
                print ("something went wrong in monitorStocks: " + str(e))
                writeErrorLog(e, '(monitorStocks)' + item.get('url'))

def notify(stockSignalDataTemp):
    if isEmailSent(stockSignalDataTemp): # email already sent, return to calling function
        return

    cred = getCredentials() #get login credentials

    sbj = 'sb-notify:\t' + (stockSignalDataTemp.get('name') + '\t' + stockSignalDataTemp.get('nameShort') + '\t' + stockSignalDataTemp.get('signal') + '\t' + stockSignalDataTemp.get('price'))

    body = (stockSignalDataTemp.get('name') + '\t' + stockSignalDataTemp.get('nameShort') + '\t' + stockSignalDataTemp.get('signal') + '\t' + stockSignalDataTemp.get('price') + '\t' + stockSignalDataTemp.get('url'))

    msg = 'Subject: {}\n\n{}'.format(sbj, body)
    try:
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        smtp.login(cred.get('email'), cred.get('pwd'))
        smtp.sendmail(cred.get('email'), "simon.noworkemail@icloud.com", msg) # 1 from, 2 to
    except Exception as e:
        print ("something went wrong in notify: " + str(e))
        writeErrorLog(e, '(notify) ' + stockSignalDataTemp.get('nameShort'))
    else:
        emailSent(stockSignalDataTemp) # add data to list of sent emails
        print ('EMAIL SENT FOR: ', stockSignalDataTemp.get('nameShort'))

# script start
stockList = getStocks()

# schedule.every(20).seconds.do(monitorStocks, stockList)
schedule.every().day.at("09:05").do(monitorStocks, stockList)
schedule.every().day.at("12:00").do(monitorStocks, stockList)
schedule.every().day.at("17:00").do(monitorStocks, stockList)
schedule.every().day.at("19:00").do(monitorStocks, stockList)
schedule.every().day.at("20:00").do(monitorStocks, stockList)
schedule.every().day.at("21:00").do(monitorStocks, stockList)
schedule.every().day.at("21:38").do(monitorStocks, stockList)

while True:
    if dateStamp != date.today(): # if new day, reset global variables
        setDailyVariables()
    schedule.run_pending()
    timeToSleep.sleep(1)
