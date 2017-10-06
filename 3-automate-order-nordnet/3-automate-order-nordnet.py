import pdb
import yaml
import os
import webbrowser

import requests

sPathOutput = "/output/"
sPathInput = "/input/"
sPathError = "/errorlog/"
pathFile = os.path.dirname(os.path.abspath(__file__))

def getCredentials():
    conf = yaml.load(open(pathFile + sPathInput + 'credentials-nord.yml'))
    username = conf['cred_nordnet']['username']
    pwd = conf['cred_nordnet']['password']
    cred = {'username': username, 'pwd': pwd}
    return cred

cred = getCredentials()

payload = {
    'action': 'login',
    'username': cred.get('username'),
    'password': cred.get('pwd')
}
# url = 'https://www.nordnet.se/api/2/login/anonymous'
# r = requests.post(url)
pdb.set_trace()
