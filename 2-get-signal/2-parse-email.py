import sys
import imaplib
import getpass
import email
import datetime
import yaml
import os
import pdb

pathFile = os.path.dirname(os.path.abspath(__file__))
sPathOutput = "/output/"
sPathInput = "/input/"

def getCredentials():
    conf = yaml.load(open(pathFile + sPathInput + 'credentials.yml'))
    email = conf['cred_gmail']['email']
    pwd = conf['cred_gmail']['password']
    cred = {'email': email, 'pwd': pwd}
    return cred

def checkEmails():
    cred = getCredentials()
    M = imaplib.IMAP4_SSL('imap.gmail.com') #create imap object
    try:
        M.login(cred.get('email'), cred.get('pwd'))
        data = M.select("inbox") #getting all emails
        # str = "Saniona AB"
        # print (str)
        typ, data = M.search(None, 'ALL')
        for num in data[0].split():
            typ, data = M.fetch(num, "(UID BODY[TEXT])")
            # find(str, beg=0 end=len(data[0][1].decode('utf-8')))
            # pdb.set_trace()
            print (num, data[0][1])
            # print('Message %s\n%s\n' % (num, data[0][1]))
    except Exception as e: # catch error
            print ("something went wrong in checkEmail(): " + str(e))
            # writeErrorLog(e, '(monitorStocks)' + item.get('url'))
    else:
        M.close()
        M.logout()
    return


def setStocksHeld():
    return

checkEmails()
