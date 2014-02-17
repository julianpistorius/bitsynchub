import smtplib
from email.mime.text import MIMEText


def send_message(to, message, subject=None):

    sender ='bitsynchub@metallapan.se'
    msg = MIMEText(message)
    msg['Subject'] = subject or "BitSyncHub Status Ḿessage"
    msg['From'] = sender
    msg['To'] = to

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, [to], msg.as_string())
    s.quit()
