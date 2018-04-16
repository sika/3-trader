import shared as mod_shared
from pdb import set_trace as BP
import os
import inspect
import time
import yaml
import smtplib

glo_file_this = os.path.basename(__file__)

pidNumberInt = 0
errorCounter = 1
errorCounterLimit = 3
secondsToSleepSuccess = 60
secondsToSleepFail = 300

def getPidFileNumber():
    print ('\nSTART', inspect.stack()[0][3])
    try:
        global pidNumberInt
        with open(mod_shared.path_base + mod_shared.path_input_monitorProcess + mod_shared.glo_pid_file) as file:
            pidNumberStr = file.read()
            pidNumberInt = int(pidNumberStr)
    except Exception as e:
            print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

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
                    print(pidNumberInt, 'does NOT exist! Trying restart')
                    mod_shared.sendEmail('script might have CRASHED - trying restart attempt '+ str(errorCounter) + '/'+ str(errorCounterLimit) +' in ' + str(secondsToSleepFail) + ' seconds', '')
                    print('sleeping', str(secondsToSleepFail), 'seconds')
                    time.sleep(secondsToSleepFail)
                    command='python3'
                    os.system(command + ' ' + mod_shared.glo_fileToRunIfCrash_main)
                    getPidFileNumber()
                    errorCounter += 1
                    continue
                else:
                    mod_shared.sendEmail('script might have CRASHED - NO MORE restarts will be tried', '')
                    break
    except Exception as e:
            print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))


getPidFileNumber()
monitorPidNumber()