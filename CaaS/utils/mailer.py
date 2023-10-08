
import smtplib
from CaaS.config import SENDERMAIL,SENDERPASS


def sendMail(email,content):
    
    connection = smtplib.SMTP("smtp.gmail.com", port=587)
    connection.starttls()
    connection.login(user=SENDERMAIL, password=SENDERPASS)
    connection.sendmail(from_addr=SENDERMAIL, to_addrs=email, msg=content)
    connection.close()