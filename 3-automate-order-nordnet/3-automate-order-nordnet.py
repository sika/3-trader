import pdb
import yaml
import os
import requests
import sys

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

def getCredentials():
    conf = yaml.load(open(pathFile + sPathInput + 'credentials-mailinator.yml'))
    username = conf['cred_mailinator']['username']
    pwd = conf['cred_mailinator']['password']
    cred = {'username': username, 'pwd': pwd}
    return cred

def getCredentialsNord():
    conf = yaml.load(open(pathFile + sPathInput + 'credentials-nord.yml'))
    username = conf['cred_nordnet']['username']
    pwd = conf['cred_nordnet']['password']
    cred = {'username': username, 'pwd': pwd}
    return cred

cred = getCredentialsNord()

payload = {
    'username': cred.get('username'),
    'password': cred.get('pwd')
}
payloadOrder = {
    'identifier':'76848',
    'market_id':'11',
    'side':'BUY',
    'price':'2.63',
    'currency':'SEK',
    'volume':'1',
    'open_volume':'0',
    'order_type': 'LIMIT',
    'smart_order':'0',
    'valid_until': '2017-10-16'
}
payloadOrderSell = {
    'identifier':'76848',
    'market_id':'11',
    'side':'SELL',
    'price':'2.59',
    'currency':'SEK',
    'volume':'1',
    'open_volume':'0',
    'order_type':'LIMIT',
    'smart_order':'0',
    'valid_until':'2017-10-16'
}

header = {
    'Accept': 'application/json'
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

with requests.Session() as c:
    try:
        print('\nGet LOGINPAGE:')
        urlGetLoginPage = 'https://www.nordnet.se/mux/login/start.html?cmpi=start-loggain&state=signin'
        r = c.get(urlGetLoginPage)
        if r.status_code != 200:
            print(urlGetLoginPage, 'failed!')
            pdb.set_trace()
        # cookieGet = requests.utils.dict_from_cookiejar(r.cookies)
        # print ('COOKIE_GET:', cookieGet)
        print('\nr.headers\n', r.headers)
        print('\nr.cookies\n', requests.utils.dict_from_cookiejar(r.cookies))
        print('\nc.cookies\n', requests.utils.dict_from_cookiejar(c.cookies))
        # print('\nc.headers\n', c.headers)
        # pdb.set_trace()
        # Anonymous to get cookie
        urlPostAnonymous = 'https://www.nordnet.se/api/2/login/anonymous'
        print ('\nPost Anonymous')
        r = c.post(urlPostAnonymous, headers=header) #cookies=cookieGet,
        if r.status_code != 200:
            print(urlPostAnonymous, 'failed!')
            pdb.set_trace()
        # cookiePostAno = requests.utils.dict_from_cookiejar(r.cookies)
        # print('COOKIE_POST_ANO:', cookiePostAno)
        print('\nr.headers\n', r.headers)
        print('\nr.cookies\n', requests.utils.dict_from_cookiejar(r.cookies))
        print('\nc.cookies\n', requests.utils.dict_from_cookiejar(c.cookies))
        # print('\nc.headers\n', c.headers)
        # pdb.set_trace()
        # Login post
        print ('\nPost LOGIN')
        urlPostLogin = 'https://www.nordnet.se/api/2/authentication/basic/login'
        # cookiePostAno.update(cookieGet)
        # header['ntag'] = r.headers['ntag']
        print ('headers', header)
        print ('payload', payload)
        r = c.post(urlPostLogin, headers=header, data=payload) #cookies=cookiePostAno,
        if r.status_code != 200:
            print(urlPostLogin, 'failed!')
            pdb.set_trace()
        print('\nr.headers\n', r.headers)
        print('\nr.cookies\n', requests.utils.dict_from_cookiejar(r.cookies))
        print('\nc.cookies\n', requests.utils.dict_from_cookiejar(c.cookies))
        # print('\nc.headers\n', c.headers)
        pdb.set_trace()
        print('\nPLACING ORDER')
        header['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        header['ntag'] = r.headers['ntag']
        print('\nheader\n', header)
        urlOrder = 'https://www.nordnet.se/api/2/accounts/18272500/orders'
        r = c.post(urlOrder, headers=header, data=payloadOrderSell)
        if r.status_code != 200:
            print('PLACING ORDER', 'failed!')
            print('status_code:', r.status_code)
            print('status_code:', r.text)
            pdb.set_trace()
        print('\nr.headers\n', r.headers)
        print('\nr.cookies\n', requests.utils.dict_from_cookiejar(r.cookies))
        print('\nc.headers\n', requests.utils.dict_from_cookiejar(c.cookies))
    except Exception as e: # catch error
            print ("ERROR in requests.Session(): " + str(e))
    else:
        print('SUCCESS in requests.Session()')
print('end of script')
