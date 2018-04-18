import shared as mod_shared
from pdb import set_trace as BP
from pprint import pprint
import inspect
from robobrowser import RoboBrowser
import re
import os

glo_file_this = os.path.basename(__file__)

def clearSbWatchlist():
    print (inspect.stack()[0][3])
    try:
        # Login in to SB, return browser object
        browser = mod_shared.sbLogin()

        # Find and go to Watchlist
        link = browser.find('a', href=re.compile('Watchlist')) # find Watchlist link
        link = browser.follow_link(link)

        form = browser.get_form() # get form for deleteAll (one big shared form)
        browser.submit_form(form, submit=form[mod_shared.glo_clearWatchlist]) # delete all watchlist

    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

def setSbWatchlist(stocksToBuy_list):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        # Login in to SB, return browser object
        browser = mod_shared.sbLogin()
        print('setting watchlist...')
        test_bool = False
        # test_bool = True
        test_counter = 0
        if test_bool:
            print(inspect.stack()[0][3], 'in TEST MODE!')
        for row in stocksToBuy_list:
            print(row.get(mod_shared.glo_colName_sbNameshort))
            # get non-member URL from list and format to member URL
            url_base = 'https://www.swedishbulls.com/members/'

            url_stock = row.get(mod_shared.glo_colName_url_sb)
            url_stock_rel = url_stock[29:]
            url_stock = url_base + url_stock_rel

            browser.open(url_stock)

            # set form payload
            formData = {'ctl00$ScriptManager1': 'ctl00$MainContent$UpdatePanel1|ctl00$MainContent$AddtoWatchlist',
            '__EVENTTARGET': 'ctl00$MainContent$AddtoWatchlist',
            '__EVENTARGUMENT': 'Click',
            '__ASYNCPOST': 'true'}

            # add new headers
            headers = {'Referer' : url_stock,
            'User-Agent' : mod_shared.glo_urlHeader.get('User-Agent'),
            'X-MicrosoftAjax' : 'Delta=true',
            'X-Requested-With' : 'XMLHttpRequest',
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8'}
            
            # merge current with new headers
            browser.session.headers = {**browser.session.headers, **headers}
            # set watchlist of stock
            browser.open(url_stock, method='post', data=formData)
            
            if test_bool and test_counter >=1:
                break
            test_counter += 1
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))
    else:
        print('END', inspect.stack()[0][3], '\n')

def getUnconfirmedWatchlist(stock_list):
    try:
        # Login in to SB, return browser object
        browser = mod_shared.sbLogin()

        # Find and go to Watchlist
        link = browser.find('a', href=re.compile('Watchlist')) # find Watchlist link
        link = browser.follow_link(link)

        # get list of stocks in watchlist
        rowWatchlist = browser.find_all('tr', id=re.compile('MainContent_SignalListGrid1_DXDataRow')) #find all <tr> in Watchlist
        list_of_sbStockNameShort = []
        if rowWatchlist is not None:
            for row in rowWatchlist:
                list_of_sbStockNameShort.append(row.td.a.get_text())

        list_of_sbStockNameShort_not_in_watchlist = []
        for stock in stock_list:
            if stock.get(mod_shared.glo_colName_sbNameshort) not in list_of_sbStockNameShort:
                list_of_sbStockNameShort_not_in_watchlist.append(stock)

        return list_of_sbStockNameShort_not_in_watchlist
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))    

def main(stocksToBuy_list):
    try:
        clearSbWatchlist()
        setSbWatchlist(stocksToBuy_list)
        stocks_not_confirmed = getUnconfirmedWatchlist(stocksToBuy_list)
        while stocks_not_confirmed: # will run while stocks still not on watchlist
            print('stocks still not on watchlist. Trying again...')
            setSbWatchlist(stocks_not_confirmed)
            stocks_not_confirmed = getUnconfirmedWatchlist(stocks_not_confirmed)
    except Exception as e:
        print ("ERROR in file", glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))
        mod_shared.writeErrorLog(inspect.stack()[0][3], str(e))

# only run when script explicitly called
if __name__ == "__main__":
    # when called from other script DONT run getStockListFromFile (should be sent as parameter from calling script)
    test_bool = False
    # test_bool = True
    if test_bool:
        print(inspect.stack()[0][3], 'in TEST MODE!')
        stocksToBuy_list = mod_shared.getStockListFromFile(mod_shared.path_input_main, mod_shared.glo_stockToBuy_file)
        main(stocksToBuy_list)
    else:
        main()
