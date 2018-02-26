import pdb
import yaml
import os
import requests
from bs4 import BeautifulSoup
import re

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

def getCredentials():
    conf = yaml.load(open(pathFile + sPathInput + 'credentials-sb.yml'))
    email = conf['sb']['username']
    pwd = conf['sb']['password']
    cred = {'username': email, 'pwd': pwd}
    return cred

cred = getCredentials()
# ctl00$MainContent$uEmail
# ctl00$MainContent$uPassword
payload = {
    'ctl00$MainContent$uEmail': cred.get('username'),
    'ctl00$MainContent$uPassword': cred.get('pwd'),
    '__ASYNCPOST':'true',
    'ctl00$MainContent$btnSubmit':'Sign In'
}
header = {
    # 'Accept': '*/*',
    # 'Accept-Encoding':'gzip, deflate, br',
    # 'Accept-Language':'en-US,en;q=0.9,sv;q=0.8',
    # 'Cache-Control':'no-cache',
    # 'Connection':'keep-alive',
    # 'Content-Length':'12322',
    # 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie':'_ga=GA1.2.871314158.1499784666; _gid=GA1.2.236069535.1517317291; SessionToken=SessionTokenID=qumovrsegz30v3cnkhrnafe520180131; _gat=1',
    # 'Host':'www.swedishbulls.com',
    # 'Origin':'https://www.swedishbulls.com',
    # 'Referer':'https://www.swedishbulls.com/Signin.aspx?lang=en',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    # 'X-MicrosoftAjax':'Delta=true',
    # 'X-Requested-With':'XMLHttpRequest'
}
cookie = {
 'cookie': '_ga=GA1.2.871314158.1499784666;  _gid=GA1.2.236069535.1517317291;  SessionToken=SessionTokenID=h1liufjl34czbwzgapshu4ya20180201; _gat=1'
}

with requests.Session() as c:
    try:
        print('\nGet LOGINPAGE:')
        urlGetLoginPage = 'https://www.swedishbulls.com/Signin.aspx?lang=en'
        r = c.get(urlGetLoginPage)
        # if r.status_code != 200:
        #     print (urlGetLoginPage, 'failed...')
        #     pdb.set_trace()
        print ('\nr.headers\n', r.headers)
        print ('\nr.cookies\n', requests.utils.dict_from_cookiejar(r.cookies))
        print ('\nc.cookies\n', requests.utils.dict_from_cookiejar(c.cookies))

        # Post Login creds
        print('\nPost LOGINPAGE:')
        # pdb.set_trace()
        # header = r.headers
        r = c.post(urlGetLoginPage, headers=header, data=payload, cookies=cookie)
        # cookies=cookie
        # , headers=header
        # data=payload
        if r.status_code != 200:
            print(urlGetLoginPage, 'failed!')
            pdb.set_trace()
        print('\nr.headers\n', r.headers)
        print('\nc.headers\n', c.headers)
        print('\nr.cookies\n', requests.utils.dict_from_cookiejar(r.cookies))
        print('\nc.cookies\n', requests.utils.dict_from_cookiejar(c.cookies))
        print('\nr.URL\n', r.url)

        # get Watchlist
        print('\nGet Watchlist:')
        urlGetWatchlist = 'https://www.swedishbulls.com/members/Watchlist.aspx?lang=en'
        r = c.post(urlGetWatchlist)
        if r.status_code != 200:
            print (urlGetLoginPage, 'failed...')
            pdb.set_trace()
        print ('\nr.headers\n', r.headers)
        print ('\nr.cookies\n', requests.utils.dict_from_cookiejar(r.cookies))
        print ('\nc.cookies\n', requests.utils.dict_from_cookiejar(c.cookies))

        soup = BeautifulSoup(r.content, 'html.parser')
        print(soup.body.findAll(text=re.compile('Sign')))
        pdb.set_trace()
        test = 'test'
        # urlTemp = item.get('url')
        # htmlCode = urlopen(urlTemp).read() # get the html from website
        # soup = BeautifulSoup(htmlCode, 'html.parser')

    except Exception as e: # catch error
            print ("ERROR in requests.Session(): " + str(e))
    else:
        print('SUCCESS in requests.Session()\n')

print ('END of script')

# https://www.swedishbulls.com/members/Watchlist.aspx?lang=en
# https://www.swedishbulls.com/Signin.aspx?lang=en

# _ga=GA1.2.871314158.1499784666;
# _gid=GA1.2.236069535.1517317291; SessionToken=SessionTokenID=qumovrsegz30v3cnkhrnafe520180131; ASP.NET_SessionId=h1liufjl34czbwzgapshu4ya; _gat=1

# _ga=GA1.2.871314158.1499784666;
# _gid=GA1.2.236069535.1517317291;  SessionToken=SessionTokenID=h1liufjl34czbwzgapshu4ya20180201; _gat=1
