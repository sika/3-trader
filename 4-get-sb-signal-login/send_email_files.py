import shared as mod_shared
from pdb import set_trace as BP
import os
import smtplib
import inspect
from pprint import pprint
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

glo_file_this = os.path.basename(__file__)

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
        credGmailAutotrading = mod_shared.getCredentials(mod_shared.glo_credGmailAutotrading)
        smtp.login(credGmailAutotrading.get('username'), credGmailAutotrading.get('pwd'))
        smtp.sendmail(credGmailAutotrading.get('username'), send_to, msg.as_string())
        smtp.close()
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e)) 

def getListOfFiles():
    try:
        path = mod_shared.path_base + mod_shared.path_output
        files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
        files_with_path = []
        for file in files:
            files_with_path.append(path+file)
        files_custom = [
            mod_shared.path_base + mod_shared.path_input_main + mod_shared.glo_stockToBuy_file,
            mod_shared.path_base + mod_shared.path_input_createList + mod_shared.glo_stockInfo_file_updated
        ]
        files_with_path += files_custom
        return files_with_path
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))     

def main():
    try:
        files_with_path = getListOfFiles()
        pprint(files_with_path)
        send_mail('simon.autotrading@gmail.com', 'autotrade files', '', files_with_path)
    except Exception as e:
        print ('ERROR in file', glo_file_this, 'and function' ,inspect.stack()[0][3], ':', str(e))     

if __name__ == "__main__":
   main()


