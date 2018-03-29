from pdb import set_trace as BP
import os
import inspect
import time
import yaml
import smtplib

pathFile = os.path.dirname(os.path.abspath(__file__))
sPathInput = "/input/"
sPathPidFile = '/pid.txt'
fileToRunIfCrash = '4-robo-get-sb-signal-login.py'

gloCredGmailAutotrading = 'credGmailAutotrading'
pidNumberInt = 0
errorCounter = 1
errorCounterLimit = 3
secondsToSleepSuccess = 300
secondsToSleepFail = 300

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
        global pidNumberInt
        with open(pathFile + sPathPidFile) as file:
            pidNumberStr = file.read()
            pidNumberInt = int(pidNumberStr)
    except Exception as e:
            print ("ERROR in", inspect.stack()[0][3], ':', str(e))

def monitorPidNumber():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        global errorCounter
        while True:
            try:
                if os.getpgid(pidNumberInt):
                    print(pidNumberInt, 'exist!')
                print('sleeping', str(secondsToSleepSuccess), 'seconds')
                time.sleep(secondsToSleepSuccess)
            except OSError:
                if errorCounter <= errorCounterLimit:
                    print('errorCounter:', str(errorCounter))
                    print(pidNumberInt, 'does NOT exist!')
                    sendEmail('script might have CRASHED - trying restart attempt '+ str(errorCounter) + '/'+ str(errorCounterLimit) +' in ' + str(secondsToSleepFail) + ' seconds', '')
                    print('sleeping', str(secondsToSleepFail), 'seconds')
                    time.sleep(secondsToSleepFail)
                    command='python3'
                    os.system(command + ' ' +fileToRunIfCrash)
                    getPidFileNumber()
                    errorCounter += 1
                    continue
                else:
                    sendEmail('script might have CRASHED - NO MORE restarts will be tried', '')
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

getPidFileNumber()
monitorPidNumber()