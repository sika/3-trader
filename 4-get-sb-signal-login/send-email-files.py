from pdb import set_trace as BP
import yaml
import os
import smtplib
import inspect
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

pathFile = os.path.dirname(os.path.abspath(__file__))
sPathOutput = "/output/"
sPathInput = "/input/"
glo_file_this = os.path.basename(__file__)

gloCredGmailAutotrading = 'credGmailAutotrading'

def getCredentials(domain):
    try:
        if domain == gloCredGmailAutotrading:
            conf = yaml.load(open(pathFile + sPathInput + 'credentials.yml'))
            username = conf['gmail_autotrade']['username']
            pwd = conf['gmail_autotrade']['password']
            return {'username': username, 'pwd': pwd}
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))

def send_mail(send_to, subject, text, files):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        for file in files:
            with open (file, 'rb') as csvFile:
                part = MIMEApplication(csvFile.read(),Name=os.path.basename(file))
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file)
            msg.attach(part)

        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        credGmailAutotrading = getCredentials(gloCredGmailAutotrading)
        smtp.login(credGmailAutotrading.get('username'), credGmailAutotrading.get('pwd'))
        smtp.sendmail(credGmailAutotrading.get('username'), send_to, msg.as_string())
        smtp.close()

    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e)) 

files= [
pathFile + sPathOutput + 'confirmationStatistics.csv',
pathFile + sPathOutput + 'orderStatistics.csv'
]
send_mail('simon.autotrading@gmail.com', 'autotrade files', '', files)