from pdb import set_trace as BP
import os
import inspect
import time
import yaml
import smtplib

pathFile = os.path.dirname(os.path.abspath(__file__))
sPathInput = "/input/"
sPathPidFile = '/pid.txt'

gloCredGmailAutotrading = 'credGmailAutotrading'

def getCredentials(domain):
    try:
        if domain == gloCredGmailAutotrading:
            conf = yaml.load(open(pathFile + sPathInput + 'credentials.yml'))
            username = conf['gmail_autotrade']['username']
            pwd = conf['gmail_autotrade']['password']
            return {'username': username, 'pwd': pwd}
    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def getPidFileNumber():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        with open(pathFile + sPathPidFile) as file:
            pidNumberStr = file.read()
            return int(pidNumberStr)
    except Exception as e:
            print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def monitorPidNumber(pidNumberInt):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        while True:
            try:
                if os.getpgid(pidNumberInt):
                    print(pidNumberInt, 'exist!')
                # time.sleep(300)
                time.sleep(10)
            except OSError:
                print(pidNumberInt, 'does NOT exist!')
                sendEmail('script might have CRASHED', '')
                break
    except Exception as e:
            print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def sendEmail(sbj, body):
    print ('\nSTART', inspect.stack()[0][3])
    try:
        msg = 'Subject: {}\n\n{}'.format(sbj, body)
        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        credGmailAutotrading = getCredentials(gloCredGmailAutotrading)
        smtp.login(credGmailAutotrading.get('username'), credGmailAutotrading.get('pwd'))
        smtp.sendmail(credGmailAutotrading.get('username'), credGmailAutotrading.get('username'), msg) # 1 from, 2 to
    except Exception as e:
        print ("ERROR in function", inspect.stack()[0][3] +': '+ str(e))

pidNumberInt = getPidFileNumber()
monitorPidNumber(pidNumberInt)