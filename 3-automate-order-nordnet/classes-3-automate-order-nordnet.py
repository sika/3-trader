# de-comment sendEmail() in handleError
# how to check if orders have gone through, and
# what to do if they have not
    # Case BUY: Do nothing (do not buy it)
    # Case SELL:
        # Market closed: SELL at current market price
        # Market open:
            # After 1 hour: If market price is lower than initial selling price, place new marketprice orders
# How to set valid_until?
    # If order is placed within market hours, order is valid  until end of day (market open)
    # If order is placed outside market hours, order is valid until end of next market day
    # Scenarios:
        # Order placed within market hours -> valid current date
        # Order placed outside market hours on a Friday -> valid to date of next opening market day (usually Monday)

from pdb import set_trace as BP
import requests
import os
import yaml
import smtplib
import inspect
import datetime

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

class Time:
    errorCounter = 0
    openingTime = datetime.time(9,0)
    closingTime = datetime.time(17,30)
    dailyTsStr = 0

    def setDailyTs():
        Time.dailyTsStr = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    def incrErrorCounter():
        Time.errorCounter += 1

class Order:
    currency = 'SEK'
    open_volume = '0'
    order_type = 'LIMIT'
    smart_order = '0'

    def __init__(self, identifier, market_id, side, price, volume):
        self.identifier = identifier
        self.market_id = market_id
        self.side = side #buy or sell
        self.price = price
        self.volume = volume
        self.valid_until = datetime.date.today().strftime("%Y-%m-%d")
    def getOrderAsDict(self):
        orderDict = {
            Payload.identifier: self.identifier,
            Payload.market_id: self.market_id,
            Payload.side: self.side,
            Payload.price: self.price,
            Payload.currency: self.currency,
            Payload.volume: self.volume,
            Payload.open_volume: self.open_volume,
            Payload.order_type: self.order_type,
            Payload.smart_order: self.smart_order,
            Payload.valid_until: self.valid_until
        }
        return orderDict

class Payload:
    identifier = 'identifier'
    market_id = 'market_id'
    side = 'side'
    price = 'price'
    currency = 'currency'
    volume = 'volume'
    open_volume = 'open_volume'
    order_type = 'order_type'
    smart_order = 'smart_order'
    valid_until = 'valid_until'

class Request:
    def __init__(self, url, header, data):
        self.url = url
        self.header = header
        self.data = data

def handleError(eStr, dataStr):
    try:
        if Time.errorCounter < 100:
            with open (pathFile + sPathError + Time.dailyTsStr + '-errorLog.txt', 'a', encoding='ISO-8859-1') as file:
                file.write(str(Time.errorCounter) + ':' + getTsStr() + ': ' + 'Calling function: ' + inspect.stack()[1][3] + '; Error: ' + '' + eStr + '; Data: ' + dataStr + '\r\n')
            Time.incrErrorCounter()
            # sendEmail('error in '+ os.path.basename(__file__), inspect.stack()[1][3] + ': ' + eStr + ': ' + dataStr)
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        # sendEmail('error in '+ os.path.basename(__file__), inspect.stack()[0][3] + ': ' + str(e))

def getTs():
    return datetime.datetime.now()

def getTsStr():
    return getTs().strftime("%Y-%m-%d %H-%M-%S")

def isWeekDay():
    if 1 <= getTs().isoweekday() <= 5: # mon-fri <-> 1-5
        return True
    else:
        return False

def isRedDay():
    nov_3_2017_close = datetime.datetime.strptime('2017 Nov 03 13 00', '%Y %b %d %H %M')
    nov_3_2017_close1 = datetime.datetime.strptime('2017 Nov 03 17 30', '%Y %b %d %H %M')
    dec_24_2017 = datetime.datetime.strptime('2017 Dec 24', '%Y %b %d').date()
    dec_25_2017 = datetime.datetime.strptime('2017 Dec 25', '%Y %b %d').date()
    if getTs().date() == dec_24_2017 or getTs().date() == dec_25_2017 or nov_3_2017_close < getTs() < nov_3_2017_close1:
        return True
    else:
        return False

def isMarketOpen():# if current time is between 9-17:30 AND time is not saturday or Sunday AND it is not a RED day
    if Time.openingTime <= getTs().time() < Time.closingTime and isWeekDay() and isRedDay() == False:
        return True
    else:
        return False

def placeOrder():
    with requests.Session() as c:
        try:
            print('\nGet LOGINPAGE')
            r = c.get(RequestLogin.url)
            checkStatus(r)
            BP()
            print ('\nPost Anonymous')
            r = c.post(RequestAnonymous.url, headers=RequestAnonymous.header)
            checkStatus(r)

            print ('\nPost Login')
            r = c.post(RequestLoginLogin.url, headers=RequestLoginLogin.header, data=RequestLoginLogin.data)

            checkStatus(r)

            print ('\nPost Order')
            RequestOrder.header['ntag'] = r.headers['ntag'] #update header with earlier response
            r = c.post(RequestOrder.url, headers=RequestOrder.header, data=RequestOrder.data)
            checkStatus(r)
        except Exception as e:
            print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
            handleError(str(e), '')
def checkStatus(r):
    try:
        if r.status_code != 200:
            print('ERROR', r.url, 'failed!')
            handleError(str(r.status_code)+ ' ' +r.url, '')
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        handleError(str(e), '')

def sendEmail(sbj, body):
    try:
        msg = 'Subject: {}\n\n{}'.format(sbj, body)
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        smtp.login(credGmail['username'], credGmail['password'])
        smtp.sendmail(credGmail['username'], "simon.noworkemail@icloud.com", msg) # 1 from, 2 to
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))
        handleError(str(e), '')
    else:
        print(inspect.stack()[0][3]+ ':' + ' email sent')

def getCredentials(typeStr):
    # typeStr can be 'gmail' or 'nordnet'
    conf = yaml.load(open(pathFile + sPathInput + 'credentials.yml'))
    return conf[typeStr]

identifier = '76848'
market_id = '11'
side = 'SELL'
price = '1.87'
volume = '1'

# Setting start varibles
Time.setDailyTs()
OrderOrder = Order(identifier, market_id, side, price, volume)

credGmail = getCredentials('gmail')
credNord = getCredentials('nordnet')

RequestLogin = Request('https://www.nordnet.se/mux/login/start.html?cmpi=start-loggain&state=signin', 'no header', 'no data')
RequestAnonymous = Request('https://www.nordnet.se/api/2/login/anonymous', {'Accept': 'application/json'}, 'no data')
RequestLoginLogin = Request('https://www.nordnet.se/api/2/authentication/basic/login', {'Accept': 'application/json'}, credNord)
RequestOrder = Request('https://www.nordnet.se/api/2/accounts/18272500/orders', {'Accept': 'application/json, text/javascript, */*; q=0.01'}, OrderOrder.getOrderAsDict())
#END setting start variables

#Start script
placeOrder()
#END script
print('END script')
