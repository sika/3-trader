# Get name: soup.find(id="MainContent_Name").get_text() (not needed)
# Continue in getAllStocks and its implications

from bs4 import BeautifulSoup
import re
import os
from urllib.request import urlopen
import pdb
import csv
import datetime

pathFile = os.path.dirname(os.path.abspath(__file__))
sPathOutput = "/output/"
sPathInput = "/input/"
timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") # don't use ":", it will crash script
stockInfoList = []
sbGenericUrl = 'https://www.swedishbulls.com/SignalPage.aspx?lang=en&Ticker='

def writeErrorLog (e, data):
    with open (pathFile + sPathOutput + 'stockValue ' +timeStamp+'-errorLog.txt', 'a') as file:
        file.write(data +": "+e+"\n")

def createCsv():
    with open (pathFile + sPathOutput + 'stockValue ' +timeStamp+'-semiColon.csv', 'w', encoding='utf-8') as newCsvFile:
        newCsvFileTemp = csv.writer(newCsvFile, delimiter = ';') #NOTE! delimiter reading in Excel will depend on windows setting
        newCsvFileTemp.writerow(["NAMESHORT", "NAME", "URL", "VALUE"])

def getAllStocks ():
    stockInfoListTemp = [] #python list
    with open (pathFile + sPathInput + 'allstocks.csv', 'rt', encoding='utf-8') as readFile:
        dReader = csv.DictReader(readFile, delimiter = ';')
        for row in dReader:
            dictTemp = {'NAMESHORT': row['NAMESHORT'], 'NAME': row['NAME']}
            dictTemp['NAMESHORT'] = row['NAMESHORT'].replace(" ", "%20") # if name contains space, update name for URL to work
            stockInfoListTemp.append(dictTemp) # append the first col (name) in current row
    return stockInfoListTemp

def getWebsite(stockNameTemp):
    stockValueAndUrl = {'URL': '', 'value': ''}
    try:
        stockValueAndUrl['URL'] = sbGenericUrl+stockNameTemp
        htmlCode = urlopen(stockValueAndUrl['URL']).read() # get the html from website
        soup = BeautifulSoup(htmlCode, 'html.parser')
        stockValueAndUrl['VALUE'] = soup.find_all('td', text=re.compile("€100"))[0].parent.parent.parent.parent.parent.next_sibling.contents[5].get_text() # return the multiplier value of last 6 (0), 12 (1) or 24 (2) months
    except Exception as e: # catch error
        writeErrorLog(str(e), stockNameTemp)
        stockValueAndUrl['VALUE'] = "0"
        return stockValueAndUrl
    else: # if try went well
        return stockValueAndUrl

def appendCsv(stockInfoTemp, stockValueAndUrlTemp):
    with open (pathFile + sPathOutput + 'stockValue ' +timeStamp+'-semiColon.csv', 'a') as csvFile:
         file = csv.writer(csvFile, delimiter = ';')
         file.writerow([stockInfoTemp.get('NAMESHORT'), stockInfoTemp.get('NAME'), stockValueAndUrlTemp.get('URL'), stockValueAndUrlTemp.get('VALUE')])  #nameshort, name, URL, value

createCsv()
stockInfoList = getAllStocks ()
stockInfoListLength = len(stockInfoList)
num = 1
# iterate through of stockInfoList
for stockInfoTemp in stockInfoList:
    stockValueAndUrl = getWebsite(stockInfoTemp.get('NAMESHORT')) #get multiplier Value
    print(str(num) + "/" + str(stockInfoListLength) + ": \tnameShort: " + stockInfoTemp.get('NAMESHORT') + "\tname: " + stockInfoTemp.get('NAME') + "\tvalueStock: " + stockValueAndUrl.get('VALUE'))
    appendCsv(stockInfoTemp, stockValueAndUrl)
    num += 1
