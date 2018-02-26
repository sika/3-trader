from pdb import set_trace as BP
# import time
# import datetime
import csv
import os
import inspect
import datetime

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------------------------
# def getTimestamp():
#     return datetime.datetime.now()


# glo_redDays = {
# 	'Mar_29_2018': {
# 	'CLOSE_START' : datetime.datetime.strptime('2018 Mar 29 13 00', '%Y %b %d %H %M'),
# 	'CLOSE_END' : datetime.datetime.strptime('2018 Mar 29 17 30', '%Y %b %d %H %M')
# 	},
# 	'Mar_30_2018': {
# 	'CLOSE_START' : datetime.datetime.strptime('2018 Feb 26 08 55', '%Y %b %d %H %M'),
# 	'CLOSE_END' : datetime.datetime.strptime('2018 Feb 26 17 30', '%Y %b %d %H %M')
# 	}
# }


# def isNotRedDay():
#     print ('\nSTART', inspect.stack()[0][3])
#     try:
#         for date, time in glo_redDays.items():
#         	# BP()
#         	if time['CLOSE_START'] < getTimestamp() < time['CLOSE_END']:
#         		return False # IS red day
#         return True
#     except Exception as e:
#         print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))

# print(isNotRedDay())
# -----------------------------------------------------------

# def getDateTodayCustomStr(custom):
#     return datetime.date.today().strftime(custom)
# # def writeOrderStatistics(sbStockNameShort, payloadOrder):
# def writeOrderStatistics():
#     print ('\nSTART', inspect.stack()[0][3])
#     try:
#         file_orderStat = pathFile + sPathOutput + 'orderStatistics.csv'
#         file_exists = os.path.isfile(file_orderStat)
#         with open (file_orderStat, 'a') as csvFile:
#             fieldnames = ['DATE', 'TIME', 'DAY', 'NAMESHORT_SB', 'SIGNAL', 'PRICE']
#             writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter = ';')
#             if not file_exists:
#                 writer.writeheader()
#             writer.writerow({'DATE': getDateTodayCustomStr('%A'), 'TIME': '08:23'})
#             writer.writerow({'DATE': '2018-02-25', 'TIME': '07:23'})
#             writer.writerow({'DATE': '2018-02-25', 'TIME': '08:23'})
#             writer.writerow({'DATE': '2018-02-26', 'TIME': '09:23'})
# # date    time    day     stockname   signal      price
#     except Exception as e:
#             print ("ERROR in", inspect.stack()[0][3], ':', str(e))


# writeOrderStatistics()
# -----------------------------------------------------------

# def isStockPriceChanged(sbSignalType, orderPrice, newPrice):
#     try:
#         percentageChangeLimit = 0.5
#         if sbSignalType == 'BUY':
#             orderPrice = float(orderPrice)
#             newPrice = float(newPrice)
#             decimalChange = newPrice / orderPrice
#             percentageChange = decimalChange * 100-100
#             if percentageChange > percentageChangeLimit:
#                 # print('True')
#                 return True
#             else:
#                 return False
#         if sbSignalType == 'SELL':
#             orderPrice = float(orderPrice)
#             newPrice = float(newPrice) 
#             decrease = orderPrice - newPrice
#             decreasePercentage = (decrease / orderPrice) * 100
#             if decreasePercentage > percentageChangeLimit:
#                 # print('True')
#                 return True
#             else:
#                 return False
#     except Exception as e:
#             print ("ERROR in", inspect.stack()[0][3], ':', str(e))

# print(isStockPriceChanged('BUY', '100', '99'))
# BP()
# test='test'
# -----------------------------------------------------------

# a = '2'
# b = '2'

# print(eval('int(a)-int(b)'))

# BP()

# def getTimestamp():
#     return datetime.datetime.now()

# BP()
# test = 'test'

# -----------------------------------------------------------

# def returnTrue():
#     return True
# def returnFalse():
#     return False

# if (
# 	not returnFalse() and not 
# 	returnFalse() and not 
# 	returnFalse()
# 	):
#     print('true')
# else:
#     print('false')

# if not returnFalse() and not returnFalse() and not returnFalse():
#     print('true')
# else:
#     print('false')
