from pdb import set_trace as BP
import inspect
import os
import csv
import requests
import re
from bs4 import BeautifulSoup
from pprint import pprint
from pprint import pformat

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

glo_stockInfo_str = 'input-stock-info.csv'
glo_stockInfo_list = []
glo_sbGeneralUrl_str = 'https://www.swedishbulls.com/SignalPage.aspx?lang=en&Ticker='

glo_stockInfoColName_sbNameshort = 'NAMESHORT_SB'
glo_stockInfoColName_sbName = 'NAME_SB'
glo_stockInfoColName_6_month = 'MONTH_6'
glo_stockInfoColName_12_month = 'MONTH_12'
glo_stockInfoColName_12_month = 'MONTH_12'
glo_stockInfoColName_24_month = 'MONTH_24'
# Output:
# 	NAMESHORT_SB	NAME_SB		MONTH_6		MONTH_12 	MONTH_24 	AVERAGE

def getStockList():
    try:
    	# fileNamePath_stock_info = None
        fileNamePath_stock_info = pathFile + sPathInput + glo_stockInfo_str
        # file_exists = os.path.isfile(fileNamePath_stock_info)
        fieldnames = [glo_stockInfoColName_sbNameshort, glo_stockInfoColName_sbName]
        with open (fileNamePath_stock_info) as csvFile:
        	records = csv.DictReader(csvFile, fieldnames=fieldnames, delimiter=';') # omitting "fieldnames" - will make file headers fieldnames
        	next(csvFile) #SKIP header
        	for rowDict in records:
        		setStockList(rowDict)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def setStockList(rowDict):
    try:
    	global glo_stockInfo_list
    	glo_stockInfo_list.append(rowDict)
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))	

def getStocksFromSb(temp_stockInfo_list):
    try:
    	with requests.Session() as s:
    		for row in temp_stockInfo_list:
    			url_postfix = row.get(glo_stockInfoColName_sbNameshort)
    			url = glo_sbGeneralUrl_str + url_postfix
    			r = s.get(url)
    			if r.status_code != 200:
    				print('something when wrong in URL request:', r.status_code)
    				print('URL:', url)
    			soup = BeautifulSoup(r.content, 'html.parser')
    			# all_rows_6_month = soup.find_all('tr', id=re.compile("MainContent_signalpagehistory_PatternHistory6_DXDataRow"))
    			BP()
    			all_imgTags_6_month = soup.find_all(id=re.compile("MainContent_signalpagehistory_PatternHistory6_cell"))
    			total_checks = len(all_imgTags_6_month)
    			counter_uncheck = 0
    			for imgtag in all_imgTags_6_month:
    				srcName = imgtag['src'].lower() #'img/Uncheck.gif' in lower case 
    				if srcName.find('uncheck') != -1: # "uncheck" spelling more reliable than "check"
    					counter_uncheck += 1
    			BP()
    			counter_check = total_checks-counter_uncheck
    			percent_6 = round(float(counter_check)/float(total_checks), 3) * 100
    			percent_months_dict = {
	    			glo_stockInfoColName_6_month: percent_6
    			}
    			updateStockList(percent_months_dict, )

    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))	

getStockList()
getStocksFromSb(glo_stockInfo_list)

# Goal:
	# 1. check best stocks to watch
	# 	- get the success-fail ratio of signals for 6, 12 and 24 months
	# 	- get the success-fail ratio total average between 6, 12 and 24 months
	# 2. get information which can directly be used by 4-robo
	# 	- market Id
	# 	- Identifier Id
	# 	- (sorted by highest?)
	# 3. make it possible for 4-robo to use the output automatically
	# 4. Make 4-robo use the ouput automatically

	# Consider:
	# - If new list of stocks, how to handle of those already held are not in list?