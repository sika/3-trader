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

def send_mail(send_from, send_to, subject, text, files):
    # files=None
    try:
        # BP()
        # assert isinstance(send_to, list)

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        # msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        # file_orderStat = pathFile + sPathOutput + 'confirmationStatistics.csv'
        # file_exists = os.path.isfile(file_orderStat)
        for file in files:
            with open (file, 'rb') as csvFile:
                part = MIMEApplication(csvFile.read(),Name=os.path.basename(file))
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file)
            msg.attach(part)

        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.starttls()
        credGmailAutotrading = getCredentials(gloCredGmailAutotrading)
        smtp.login(credGmailAutotrading.get('username'), credGmailAutotrading.get('pwd'))
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()

    except Exception as e:
        print ("ERROR in", inspect.stack()[0][3], ':', str(e)) 


files= [
pathFile + sPathOutput + 'confirmationStatistics.csv',
pathFile + sPathOutput + 'orderStatistics.csv'
]
send_mail('simon.autotrading@gmail.com', 'simon.autotrading@gmail.com', 'subj', 'text', files)